# tests/conftest.py
# ─────────────────────────────────────────────────────────────────
# Shared pytest fixtures
# ─────────────────────────────────────────────────────────────────
import pytest
import os

# Set env vars before any app imports so the app doesn't
# try to connect to a real database or Redis during tests
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("REDIS_URL",    "redis://localhost:6379/0")
os.environ.setdefault("ENVIRONMENT",  "test")


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create in-memory SQLite tables for tests that need the DB."""
    from app.database import engine, Base
    from app.models_db import TradingSignal  # noqa: F401 — registers the model

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
