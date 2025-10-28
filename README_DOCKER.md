# Dockerized Setup (Backend + Frontend + Postgres + Redis)

## Services
- Postgres 16 (port 5433 on host)
- Redis 7 (port 6380 on host)
- Backend (Flask + Gunicorn) on :5000
- Frontend (NGINX serving built Vite app) on :5173

## Quick Start
```bash
# From repo root
cp .env.example .env  # adjust if needed
docker compose build
docker compose up -d

# View logs
docker compose logs -f backend
```

Backend API: http://localhost:5000/api/health
Frontend UI: http://localhost:5173/

## Development Hints
- For active backend coding you can still run local virtualenv; compose is mainly for integration.
- DATABASE_URL uses SQLAlchemy psycopg driver.
- Redis is optional; if REDIS_URL missing, code gracefully skips caching.

## Running Alembic Migrations (inside container)
```bash
docker compose exec backend alembic upgrade head
```

## Rebuilding Frontend Only
```bash
docker compose build frontend --no-cache
```

## Cleanup
```bash
docker compose down -v
```

## Next Ideas
- Add healthcheck blocks in compose for dependency ordering.
- Add separate worker for async tasks (e.g., Celery + Redis) if AI features expand.
- Switch to Traefik / Caddy for SSL termination.
