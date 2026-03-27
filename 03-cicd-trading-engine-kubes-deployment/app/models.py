# app/models.py
# ─────────────────────────────────────────────────────────────────
# Pydantic Models — API Request / Response Schemas
# ─────────────────────────────────────────────────────────────────
from typing import Optional
from pydantic import BaseModel


class TaskStatusResponse(BaseModel):
    task_id:         str
    status:          str
    ticker:          Optional[str] = None
    status_endpoint: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "task_id":         "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "status":          "PENDING",
                "ticker":          "RELIANCE.NS",
                "status_endpoint": "/api/v1/task/a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            }
        }


class AnalysisResponse(BaseModel):
    task_id:   str
    status:    str
    ticker:    Optional[str]  = None
    signal:    Optional[str]  = None    # STRONG_BUY | BUY | HOLD | SELL | STRONG_SELL
    rsi:       Optional[float] = None
    macd:      Optional[float] = None
    timestamp: Optional[str]  = None

    class Config:
        json_schema_extra = {
            "example": {
                "task_id":   "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "status":    "SUCCESS",
                "ticker":    "RELIANCE.NS",
                "signal":    "STRONG_BUY",
                "rsi":       28.74,
                "macd":      0.0321,
                "timestamp": "2024-11-15T10:30:00+00:00",
            }
        }
