# Frontend (Vercel Deployment)

This frontend is fully decoupled from backend Docker orchestration.

## Environment Variable

Create `.env` from `.env.example`:

```
VITE_API_URL=https://api.example.com
```

On Vercel, set the same `VITE_API_URL` value in project environment variables.
