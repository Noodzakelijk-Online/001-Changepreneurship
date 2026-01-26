# Backend Dockerfile - Optimized for Production
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps for psycopg (minimal layer caching)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python dependencies (layer cached separately)
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy source
COPY . .

# Expose port
EXPOSE 5000

# Environment defaults (override in compose)
ENV DATABASE_URL=sqlite:///./src/database/app.db \
    REDIS_URL=redis://redis:6379/0 \
    FLASK_ENV=production \
    PYTHONPATH=/app

# Add entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["/app/entrypoint.sh"]
# Use gunicorn for Linux/Docker, waitress can be used locally on Windows
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--keep-alive", "5", "--access-logfile", "-", "--error-logfile", "-"]
