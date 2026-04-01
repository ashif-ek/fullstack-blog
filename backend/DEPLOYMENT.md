# Production Deployment Flow

## Target Topology

- Frontend deploys independently on Vercel and reads `VITE_API_URL`.
- Single EC2 host runs Docker Compose with 4 services:
  - `api` (Gunicorn + Django)
  - `worker` (Celery worker)
  - `beat` (Celery scheduler)
- `redis` (local Redis container)
- PostgreSQL is externalized through Neon (`DATABASE_URL`).
- Redis broker/cache URL is `redis://redis:6379/0`.

## Runtime Steps

1. Build backend image:
   - `docker compose build`
2. Start backend stack:
   - `docker compose up -d`
3. API container runs:
   - Django migrations
   - `collectstatic`
   - Gunicorn server on port `8000`
4. Worker/beat containers start from same image with role-specific Celery commands.
5. AWS ingress (ALB/Nginx) terminates TLS and forwards HTTPS traffic to `api`.
6. Health endpoints:
   - Liveness: `/health/`
   - Readiness: `/ready/`

## Required Environment Variables

- `DATABASE_URL` (Neon Postgres URL with `sslmode=require`)
- `REDIS_URL` (default: `redis://redis:6379/0`)
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

## Notes

- Frontend is no longer part of Docker orchestration.
- Redis is containerized locally; PostgreSQL remains externalized on Neon.
- Logging is JSON to stdout and includes request/user correlation fields.
