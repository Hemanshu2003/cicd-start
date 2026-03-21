# app/database.py
# ─────────────────────────────────────────────────────────────────
# SQLAlchemy — Database Engine & Session Factory
# ─────────────────────────────────────────────────────────────────
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://tradingadmin:changeme@localhost:5432/trading_signals",
)

# pool_pre_ping checks connection health before using it from the pool
# pool_size / max_overflow tuned low for db.t3.micro (max 50 connections)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,       # Recycle connections every hour
    connect_args={
        "connect_timeout": 10,
        "application_name": "trading-engine",
    },
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
