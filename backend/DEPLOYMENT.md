# Production Deployment Flow

## Target Topology

- Frontend deploys independently on Vercel and reads `VITE_API_URL`.
- Backend image deploys on AWS (EC2 or ECS) with 3 services:
  - `api` (Gunicorn + Django)
  - `worker` (Celery worker)
  - `beat` (Celery scheduler)
- PostgreSQL is externalized through Neon (`DATABASE_URL`).
- Redis is externalized through AWS ElastiCache (`REDIS_URL`).

## Runtime Steps

1. Build backend image:
   - `docker compose -f docker-compose.prod.yml build`
2. Start backend stack:
   - `docker compose -f docker-compose.prod.yml up -d`
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
- `REDIS_URL` (ElastiCache Redis endpoint)
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

## Notes

- Frontend is no longer part of Docker orchestration.
- Redis/Postgres are no longer containerized in compose.
- Logging is JSON to stdout and includes request/user correlation fields.
