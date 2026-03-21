# tests/test_api.py
# ─────────────────────────────────────────────────────────────────
# Unit Tests — FastAPI Endpoints
# Run: pytest tests/ -v --cov=app
# ─────────────────────────────────────────────────────────────────
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ── Health Check ──────────────────────────────────────────────────
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ── Submit Analysis ───────────────────────────────────────────────
@patch("app.main.celery_app.send_task")
def test_submit_analysis_success(mock_send_task):
    mock_task = MagicMock()
    mock_task.id = "test-task-id-1234"
    mock_send_task.return_value = mock_task

    response = client.post("/api/v1/analyze/RELIANCE.NS")
    assert response.status_code == 200

    data = response.json()
    assert data["task_id"] == "test-task-id-1234"
    assert data["status"] == "PENDING"
    assert data["ticker"] == "RELIANCE.NS"
    assert "status_endpoint" in data


@patch("app.main.celery_app.send_task")
def test_submit_analysis_ticker_uppercased(mock_send_task):
    mock_task = MagicMock()
    mock_task.id = "test-task-id-5678"
    mock_send_task.return_value = mock_task

    response = client.post("/api/v1/analyze/reliance.ns")
    assert response.status_code == 200
    assert response.json()["ticker"] == "RELIANCE.NS"


# ── Poll Task Result ──────────────────────────────────────────────
@patch("app.main.AsyncResult")
def test_get_task_result_pending(mock_async_result):
    mock_result = MagicMock()
    mock_result.state = "PENDING"
    mock_async_result.return_value = mock_result

    response = client.get("/api/v1/task/fake-task-id")
    assert response.status_code == 200
    assert response.json()["status"] == "PENDING"


@patch("app.main.AsyncResult")
def test_get_task_result_success(mock_async_result):
    mock_result = MagicMock()
    mock_result.state = "SUCCESS"
    mock_result.result = {
        "ticker":    "RELIANCE.NS",
        "signal":    "STRONG_BUY",
        "rsi":       27.5,
        "macd":      0.0312,
        "timestamp": "2024-11-15T10:00:00+00:00",
    }
    mock_async_result.return_value = mock_result

    response = client.get("/api/v1/task/fake-task-id")
    assert response.status_code == 200

    data = response.json()
    assert data["status"]  == "SUCCESS"
    assert data["signal"]  == "STRONG_BUY"
    assert data["ticker"]  == "RELIANCE.NS"
    assert data["rsi"]     == 27.5


@patch("app.main.AsyncResult")
def test_get_task_result_failure(mock_async_result):
    mock_result = MagicMock()
    mock_result.state = "FAILURE"
    mock_result.info = Exception("yfinance connection error")
    mock_async_result.return_value = mock_result

    response = client.get("/api/v1/task/fake-task-id")
    assert response.status_code == 500
