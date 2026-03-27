# ─────────────────────────────────────────────────────────────────
# Dockerfile — Multi-Stage Build
# Stage 1: builder  — installs dependencies
# Stage 2: runtime  — lean final image
#
# Both the API Gateway and Celery Worker use the SAME image.
# The K8s deployment overrides CMD to pick the right role.
# ─────────────────────────────────────────────────────────────────

# ── Stage 1: Builder ─────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Build args (injected by CI/CD)
ARG BUILD_DATE
ARG GIT_SHA

WORKDIR /build

# Install build dependencies (gcc needed for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer cache
COPY requirements.txt .

# Install into a prefix directory so we can copy cleanly to runtime stage
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

RUN pip install --no-cache-dir --upgrade yfinance requests

# ── Stage 2: Runtime ─────────────────────────────────────────────
FROM python:3.11-slim AS runtime

ARG BUILD_DATE
ARG GIT_SHA

# OCI image labels
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${GIT_SHA}"
LABEL org.opencontainers.image.title="trading-engine"
LABEL org.opencontainers.image.description="Distributed Quantitative Trading Engine"

# Runtime OS dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --create-home appuser

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

WORKDIR /app

# Copy application source
COPY --chown=appuser:appgroup app/ ./app/

# Copy Alembic config and migrations
COPY --chown=appuser:appgroup alembic.ini .
COPY --chown=appuser:appgroup alembic/ ./alembic/

# Switch to non-root user
USER appuser

# Expose FastAPI port (only meaningful for the API Gateway role)
EXPOSE 8000

# Health check for the API Gateway role
# Celery Worker ignores this; liveness is checked via K8s exec probe
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command: run FastAPI API Gateway
# Overridden in celery-worker K8s deployment to run Celery instead
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--log-level", "info"]
