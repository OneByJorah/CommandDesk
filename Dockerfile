FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ── Production stage ──────────────────────────────────
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_USER=appuser \
    APP_UID=1001

# Create non-root user
RUN groupadd -r ${APP_USER} && \
    useradd -r -g ${APP_USER} -u ${APP_UID} -d /app -s /sbin/nologin ${APP_USER}

# System deps (runtime only)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python deps from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# App code
COPY ticket_platforms /app/ticket_platforms
COPY scripts/*.py /app/scripts/
COPY config/ /app/config/

# Create data dirs with correct ownership
RUN mkdir -p /app/data/logs /app/data/kb && \
    chown -R ${APP_USER}:${APP_USER} /app

# Security: read-only root filesystem, non-root user
USER ${APP_USER}

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -sf http://127.0.0.1:8080/health || exit 1

CMD ["python", "-m", "uvicorn", "agent_server:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
