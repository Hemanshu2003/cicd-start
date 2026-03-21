# app/main.py
# ─────────────────────────────────────────────────────────────────
# FastAPI API Gateway — Trading Engine
# ─────────────────────────────────────────────────────────────────
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from celery.result import AsyncResult
import uuid
import logging

from app.worker import celery_app
from app.models import AnalysisResponse, TaskStatusResponse
from app.database import engine, Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Trading Engine API",
    description="Distributed Quantitative Trading Signal Generator",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health Check ──────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}


# ── Submit Analysis Task ──────────────────────────────────────────
@app.post("/api/v1/analyze/{ticker}", response_model=TaskStatusResponse, tags=["Analysis"])
async def submit_analysis(ticker: str):
    """
    Submit a ticker symbol for quantitative analysis.
    Returns a task_id to poll for results.
    """
    ticker = ticker.upper().strip()
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker symbol cannot be empty")

    logger.info(f"Queuing analysis task for ticker: {ticker}")

    task = celery_app.send_task(
        "app.worker.tasks.run_analysis",
        args=[ticker],
        queue="analysis",
    )

    return TaskStatusResponse(
        task_id=task.id,
        status="PENDING",
        ticker=ticker,
        status_endpoint=f"/api/v1/task/{task.id}",
    )


# ── Poll Task Result ──────────────────────────────────────────────
@app.get("/api/v1/task/{task_id}", response_model=AnalysisResponse, tags=["Analysis"])
async def get_task_result(task_id: str):
    """
    Poll the result of a previously submitted analysis task.
    """
    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.state == "PENDING":
        return AnalysisResponse(task_id=task_id, status="PENDING")

    if task_result.state == "FAILURE":
        raise HTTPException(status_code=500, detail=str(task_result.info))

    if task_result.state == "SUCCESS":
        result = task_result.result
        return AnalysisResponse(
            task_id=task_id,
            status="SUCCESS",
            ticker=result.get("ticker"),
            signal=result.get("signal"),
            rsi=result.get("rsi"),
            macd=result.get("macd"),
            timestamp=result.get("timestamp"),
        )

    return AnalysisResponse(task_id=task_id, status=task_result.state)


# ── Recent Signals (from DB) ──────────────────────────────────────
@app.get("/api/v1/signals", tags=["Signals"])
async def get_recent_signals(limit: int = 20):
    """
    Retrieve the most recent trading signals stored in PostgreSQL.
    """
    from app.database import SessionLocal
    from app.models_db import TradingSignal

    db = SessionLocal()
    try:
        signals = (
            db.query(TradingSignal)
            .order_by(TradingSignal.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": s.id,
                "ticker": s.ticker,
                "signal": s.signal,
                "rsi": s.rsi,
                "macd": s.macd,
                "created_at": s.created_at.isoformat(),
            }
            for s in signals
        ]
    finally:
        db.close()
