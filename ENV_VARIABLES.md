# Environment Variables Setup Guide

Complete list of environment variables needed for production deployment on Render and Vercel.

## Backend Environment Variables (Render)

Add these to your **Render Web Service** → **Environment** tab:

### Required for Database Connection

| Variable | Value | Example |
|----------|-------|---------|
| `DATABASE_URL` | Your Supabase/PostgreSQL connection string | `postgresql://user:password@db.supabase.co:5432/postgres?sslmode=require` |

**Note**: Supabase provides this automatically. Copy from:
- Supabase Dashboard → Project Settings → Database → Connection String (URI)
- Select "Transaction Pool" mode for better compatibility with pgBouncer

### Required for Server Configuration

| Variable | Value | Default |
|----------|-------|---------|
| `HOST` | Server bind address for production | `0.0.0.0` |
| `PORT` | Server port (auto-set by Render) | `8000` |

### Required for CORS (Frontend Communication)

| Variable | Value | Example |
|----------|-------|---------|
| `FRONTEND_URL` | Your deployed frontend URL | `https://finances-tracker.vercel.app` |

### Optional (Development)

| Variable | Purpose | Example |
|----------|---------|---------|
| `LOG_LEVEL` | Python logging level | `INFO` |
| `WORKERS` | Number of Uvicorn workers | `4` |

### Example Render Configuration

```
DATABASE_URL=postgresql://user:password@db.supabase.co:5432/postgres?sslmode=require
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=https://finances-tracker.vercel.app
```

---

## Frontend Environment Variables (Vercel)

Add these to your **Vercel Project** → **Settings** → **Environment Variables**:

### Required for Backend API Communication

| Variable | Value | Example |
|----------|-------|---------|
| `VITE_API_URL` | Your deployed backend API URL | `https://finances-api.onrender.com` |

This variable is used in:
- `frontend/vite.config.ts` (dev proxy configuration)
- Frontend API calls during production builds

### Example Vercel Configuration

```
VITE_API_URL=https://finances-api.onrender.com
```

---

## Complete Deployment Checklist

### Render Backend Setup

- [ ] Create Render PostgreSQL Database (or link to Supabase)
- [ ] Create Render Web Service
  - [ ] Repository: Connect your GitHub repo
  - [ ] Build Command: `pip install -r requirements.txt`
  - [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Set Environment Variables:
  - [ ] `DATABASE_URL` (copy from Supabase or Render PostgreSQL)
  - [ ] `HOST=0.0.0.0`
  - [ ] `FRONTEND_URL=<your-vercel-frontend-url>`
- [ ] Deploy

### Vercel Frontend Setup

- [ ] Create Vercel Project
  - [ ] Repository: Connect your GitHub repo (frontend folder)
  - [ ] Build Command: `npm run build`
  - [ ] Start Command: `npm run dev` (for dev), or automatic for production
- [ ] Set Environment Variables:
  - [ ] `VITE_API_URL=<your-render-backend-url>`
- [ ] Deploy

---

## Local Development (No Environment Variables Needed)

For local development, defaults are used:

**Backend:**
- `DATABASE_URL` defaults to SQLite at `data/db/finance.db`
- `HOST` defaults to `127.0.0.1`
- `PORT` defaults to `8000`
- `FRONTEND_URL` defaults to localhost origins

**Frontend:**
- `VITE_API_URL` defaults to `http://127.0.0.1:8000`

Just run:
```bash
cd backend && python run.py
# In another terminal
cd frontend && npm run dev
```

---

## How the Environment Variables Are Used

### Backend (app/config.py)
```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/db/finance.db")
FRONTEND_URL = os.getenv("FRONTEND_URL")  # Dynamically added to CORS origins
```

### Backend (run.py)
```python
host = os.getenv("HOST", "127.0.0.1")
port = int(os.getenv("PORT", "8000"))
```

### Frontend (vite.config.ts)
```typescript
target: process.env.VITE_API_URL || 'http://127.0.0.1:8000'
```

### Frontend (API calls)
All API calls use `/api` prefix which is proxied to the backend in development.
In production, the Vite build includes the `VITE_API_URL` in bundle.

---

## Troubleshooting

### "CORS error: origin not allowed"
- Backend: Verify `FRONTEND_URL` includes the exact domain with protocol (`https://`, not just domain)
- Frontend: Check if `VITE_API_URL` is correctly set in Vercel environment

### "Connection refused" to database
- Backend: Verify `DATABASE_URL` is correct and includes `?sslmode=require` for remote PostgreSQL
- Render: Check database is in the same region as Web Service

### API calls from frontend getting 404
- Frontend: Verify `VITE_API_URL` matches your Render backend service URL (without trailing slash)
- Rebuild: After changing `VITE_API_URL`, rebuild frontend with `npm run build`

---

## Security Notes

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Always use HTTPS** in `FRONTEND_URL` for production
3. **Keep `DATABASE_URL` secret** - Use environment variables, never hardcode
4. **Rotate DATABASE credentials** periodically
5. **Use strong passwords** for Supabase/PostgreSQL

---

## Additional References

- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Supabase Connection Pooling](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)
