# app/models_db.py
# ─────────────────────────────────────────────────────────────────
# SQLAlchemy ORM Models — PostgreSQL Table Definitions
# ─────────────────────────────────────────────────────────────────
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from app.database import Base


class TradingSignal(Base):
    __tablename__ = "trading_signals"

    id               = Column(Integer, primary_key=True, index=True)
    ticker           = Column(String(20),  nullable=False, index=True)
    signal           = Column(String(20),  nullable=False)   # STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
    rsi              = Column(Float,       nullable=True)
    macd             = Column(Float,       nullable=True)
    macd_signal_line = Column(Float,       nullable=True)
    created_at       = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Composite index for common query: latest signals per ticker
    __table_args__ = (
        Index("ix_trading_signals_ticker_created", "ticker", "created_at"),
    )

    def __repr__(self):
        return (
            f"<TradingSignal(id={self.id}, ticker={self.ticker}, "
            f"signal={self.signal}, rsi={self.rsi:.2f})>"
        )
