# app/worker/__init__.py
# ─────────────────────────────────────────────────────────────────
# Celery Application Configuration
# ─────────────────────────────────────────────────────────────────
from celery import Celery
import os
 
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
 
celery_app = Celery(
    "trading_engine",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.worker.tasks"],
)
 
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,              # Results expire after 1 hour
    task_acks_late=True,              # Acknowledge task after execution (safer)
    worker_prefetch_multiplier=1,     # One task per worker at a time
    task_routes={
        "app.worker.tasks.run_analysis": {"queue": "analysis"},
    },
    broker_connection_retry_on_startup=True,
)
 