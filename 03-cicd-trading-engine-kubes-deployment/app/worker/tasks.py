# app/worker/tasks.py
# ─────────────────────────────────────────────────────────────────
# Celery Tasks — Data Ingestion, Analysis, Signal Generation
#
# FIX: yf.download() is unreliable and gets blocked by Yahoo Finance
# returning empty responses (JSONDecodeError on empty body).
# Solution:
#   1. Use yf.Ticker().history() — more stable API path
#   2. Inject a real browser User-Agent into the requests session
#   3. Use a 6-month window (instead of 3mo) to ensure enough rows
#      even if Yahoo throttles some days
#   4. Exponential backoff on retries (15s → 45s → 135s)
# ─────────────────────────────────────────────────────────────────
import logging
import time
import random
from datetime import datetime, timezone

import requests
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD

from app.worker import celery_app
from app.database import SessionLocal
from app.models_db import TradingSignal

logger = logging.getLogger(__name__)

# ── Realistic browser headers — prevents Yahoo Finance 401/empty body ──
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection":      "keep-alive",
}


def _build_session() -> requests.Session:
    """Return a requests.Session with headers that Yahoo Finance accepts."""
    session = requests.Session()
    session.headers.update(_HEADERS)
    return session


def _fetch_ohlcv(ticker: str) -> pd.DataFrame:
    """
    Download OHLCV data using yf.Ticker().history().

    Tries four strategies in order, moving on if any returns empty data:
      1. Custom session (browser UA) + 6-month window
      2. Custom session (browser UA) + 1-year window
      3. Default session              + 6-month window
      4. Default session              + 1-year window

    Raises ValueError if all strategies fail.
    """
    strategies = [
        {"session": _build_session(), "period": "6mo", "label": "session+6mo"},
        {"session": _build_session(), "period": "1y",  "label": "session+1y"},
        {"session": None,             "period": "6mo", "label": "default+6mo"},
        {"session": None,             "period": "1y",  "label": "default+1y"},
    ]

    last_error = None
    for s in strategies:
        try:
            logger.info(f"[{ticker}] Trying strategy: {s['label']}")

            # Small random jitter to avoid rate-limiting
            time.sleep(random.uniform(0.5, 1.5))

            tkr = yf.Ticker(ticker, session=s["session"])
            df  = tkr.history(
                period=s["period"],
                interval="1d",
                auto_adjust=True,
                actions=False,      # Skip dividends / splits columns
                timeout=20,
            )

            # yfinance >= 0.2.x can return MultiIndex columns — flatten them
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Strip timezone from DatetimeIndex (some versions return tz-aware)
            if hasattr(df.index, "tz") and df.index.tz is not None:
                df.index = df.index.tz_localize(None)

            if df.empty or "Close" not in df.columns:
                logger.warning(f"[{ticker}] Strategy '{s['label']}' → empty DataFrame")
                continue

            close = df["Close"].dropna()
            if len(close) < 30:
                logger.warning(
                    f"[{ticker}] Strategy '{s['label']}' → only {len(close)} rows "
                    f"(need 30+)"
                )
                continue

            logger.info(
                f"[{ticker}] Strategy '{s['label']}' succeeded — "
                f"{len(close)} rows, "
                f"{close.index[0].date()} → {close.index[-1].date()}"
            )
            return df

        except Exception as exc:
            last_error = exc
            logger.warning(f"[{ticker}] Strategy '{s['label']}' raised: {exc}")
            continue

    raise ValueError(
        f"All data-fetch strategies failed for '{ticker}'. "
        f"Last error: {last_error}. "
        f"Verify the symbol on https://finance.yahoo.com "
        f"(NSE examples: HDFCBANK.NS, RELIANCE.NS, TCS.NS, INFY.NS)."
    )


# ── Signal Generation Logic ───────────────────────────────────────
def generate_signal(rsi: float, macd_value: float, macd_signal: float) -> str:
    """
    Strategy rules:
      STRONG_BUY  — RSI < 30 (oversold)  AND MACD line > signal line
      STRONG_SELL — RSI > 70 (overbought) AND MACD line < signal line
      BUY         — RSI < 45 AND MACD value > 0
      SELL        — RSI > 55 AND MACD value < 0
      HOLD        — everything else
    """
    macd_diff = macd_value - macd_signal

    if rsi < 30 and macd_diff > 0:
        return "STRONG_BUY"
    elif rsi > 70 and macd_diff < 0:
        return "STRONG_SELL"
    elif rsi < 45 and macd_value > 0:
        return "BUY"
    elif rsi > 55 and macd_value < 0:
        return "SELL"
    else:
        return "HOLD"


# ── Main Celery Task ──────────────────────────────────────────────
@celery_app.task(
    name="app.worker.tasks.run_analysis",
    bind=True,
    max_retries=3,
    default_retry_delay=15,     # base delay — overridden below with exponential backoff
    soft_time_limit=180,        # SIGXCPU after 3 min
    time_limit=210,             # SIGKILL after 3.5 min
)
def run_analysis(self, ticker: str) -> dict:
    """
    Full analysis pipeline:
      1. Fetch OHLCV via yf.Ticker().history() with session headers
      2. Compute RSI-14 and MACD(12, 26, 9)
      3. Apply signal logic
      4. Persist result to PostgreSQL
      5. Return result dict
    """
    retry_count = self.request.retries
    retry_delay = 15 * (3 ** retry_count)   # 15s → 45s → 135s

    logger.info(
        f"[{self.request.id}] Starting analysis for {ticker} "
        f"(attempt {retry_count + 1}/{self.max_retries + 1})"
    )

    try:
        # ── Step 1: Data Ingestion ────────────────────────────────
        df = _fetch_ohlcv(ticker)
        close_prices: pd.Series = df["Close"].dropna()

        # ── Step 2: Technical Indicators ─────────────────────────
        logger.info(
            f"[{ticker}] Calculating RSI and MACD on {len(close_prices)} rows..."
        )

        rsi_indicator = RSIIndicator(close=close_prices, window=14)
        rsi_series    = rsi_indicator.rsi()

        macd_indicator     = MACD(
            close=close_prices,
            window_slow=26,
            window_fast=12,
            window_sign=9,
        )
        macd_series        = macd_indicator.macd()
        macd_signal_series = macd_indicator.macd_signal()

        rsi_clean  = rsi_series.dropna()
        macd_clean = macd_series.dropna()
        msig_clean = macd_signal_series.dropna()

        if rsi_clean.empty or macd_clean.empty or msig_clean.empty:
            raise ValueError(
                f"Indicators produced all-NaN for {ticker}. "
                f"Data rows={len(close_prices)} — possibly too short."
            )

        rsi_value   = float(rsi_clean.iloc[-1])
        macd_value  = float(macd_clean.iloc[-1])
        macd_signal = float(msig_clean.iloc[-1])

        logger.info(
            f"[{ticker}] RSI={rsi_value:.2f} | "
            f"MACD={macd_value:.6f} | Signal={macd_signal:.6f}"
        )

        # ── Step 3: Signal Generation ─────────────────────────────
        signal = generate_signal(rsi_value, macd_value, macd_signal)
        logger.info(f"[{ticker}] Generated signal: {signal}")

        # ── Step 4: Persist to PostgreSQL ─────────────────────────
        timestamp = datetime.now(timezone.utc)
        db = SessionLocal()
        try:
            record = TradingSignal(
                ticker=ticker,
                signal=signal,
                rsi=round(rsi_value, 4),
                macd=round(macd_value, 6),
                macd_signal_line=round(macd_signal, 6),
                created_at=timestamp,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            logger.info(f"[{ticker}] Persisted signal record ID={record.id}")
        except Exception as db_err:
            db.rollback()
            logger.error(f"[{ticker}] DB write failed: {db_err}")
            raise
        finally:
            db.close()

        # ── Step 5: Return Result ─────────────────────────────────
        return {
            "ticker":    ticker,
            "signal":    signal,
            "rsi":       round(rsi_value, 4),
            "macd":      round(macd_value, 6),
            "timestamp": timestamp.isoformat(),
        }

    except Exception as exc:
        logger.error(
            f"[{ticker}] Task failed (attempt {retry_count + 1}): {exc}"
        )
        raise self.retry(exc=exc, countdown=retry_delay)