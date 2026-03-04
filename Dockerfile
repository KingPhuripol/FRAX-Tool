# ─────────────────────────────────────────────
# FRAX® Tool — Dockerfile
# ─────────────────────────────────────────────

# Stage 1: base image
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# System dependencies (for SQLite + locale Thai)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsqlite3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ─── Install Python dependencies ───
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── Copy application code ───
COPY backend/ ./backend/

# Create database directory
RUN mkdir -p /app/data

# ─── Set environment variables ───
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DATABASE_PATH=/app/data/frax_patients.db

WORKDIR /app/backend

# Expose port
EXPOSE 8000

# ─── Health check ───
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# ─── Start server ───
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
