# Multi-stage build for Python Flask backend
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/logs/llm && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health', timeout=5)" || exit 1

# Run migrations and start server
CMD ["sh", "-c", "flask db upgrade && gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 wsgi:app"]

# ---------------------------------------------------------------------------
# Test stage — installs test deps, runs pytest, exits with test result code
# Build: docker build --target test -t changepreneurship-test .
# ---------------------------------------------------------------------------
FROM base AS test

# Switch back to root to install test deps
USER root

COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

# Re-own (base already copied code as root before useradd)
RUN chown -R appuser:appuser /app

USER appuser

ENV FLASK_ENV=testing \
    TESTING=true \
    PYTHONPATH=/app

# Default: run all tests with coverage
CMD ["python", "-m", "pytest", "tests/", "-v", "--tb=short", "--no-header"]
