# Supabase + Render + Vercel Production Setup - Complete Summary

This document summarizes all changes made to support production deployment with Supabase PostgreSQL, Render backend, and Vercel frontend.

## What Was Configured

### ✅ SQLAlchemy Engine Optimization

**File:** `backend/app/database.py`

- **NullPool configuration**: Eliminates application-level connection pooling, letting Supabase's pgBouncer handle it
- **connect_args optimization** for Supabase Connection Pooler:
  - `connect_timeout=10` - Robust timeout handling
  - `application_name=finances-tracker` - Identifies connections in database logs

```python
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={
        "connect_timeout": 10,
        "application_name": "finances-tracker",
    },
)
```

### ✅ CORS Configuration with Environment Variable

**File:** `backend/app/config.py` and `backend/app/main.py`

- Reads `FRONTEND_URL` environment variable
- Dynamically adds frontend domain to CORS allowed origins
- Maintains localhost origins for local development
- Flask/FastAPI automatically applies configuration via `CORSMiddleware`

```python
_frontend_url = os.getenv("FRONTEND_URL")
if _frontend_url:
    ALLOWED_ORIGINS.append(_frontend_url)
```

### ✅ Frontend API URL Configuration

**Files:** `frontend/vite.config.ts` and API service

- Frontend dev server proxies `/api` to `VITE_API_URL` environment variable
- Defaults to `http://127.0.0.1:8000` for local development
- Production: Set `VITE_API_URL` in Vercel environment to your Render backend URL

```typescript
target: process.env.VITE_API_URL || 'http://127.0.0.1:8000'
```

### ✅ Environment Variable Support

**Files:** 
- `backend/.env.example` - Backend configuration template
- `frontend/.env.example` - Frontend configuration template
- `.gitignore` - Ensures .env files are never committed

---

## Environment Variables Quick Reference

### Backend (Set in Render Dashboard)

| Variable | Required | Value |
|----------|----------|-------|
| `DATABASE_URL` | ✅ Yes | `postgresql://user:pass@db.supabase.co:5432/postgres?sslmode=require` |
| `HOST` | ✅ Yes | `0.0.0.0` (production) |
| `FRONTEND_URL` | ✅ Yes | `https://finances-tracker.vercel.app` |

### Frontend (Set in Vercel Dashboard)

| Variable | Required | Value |
|----------|----------|-------|
| `VITE_API_URL` | ✅ Yes | `https://finances-api.onrender.com` |

---

## Complete Deployment Checklist

### Database Setup
- [ ] Create Supabase project (or Render PostgreSQL)
- [ ] Get connection string from Supabase Dashboard → Settings → Database
- [ ] Copy "Transaction Pool" mode connection URI

### Render Backend Deployment
- [ ] Create Render Web Service
- [ ] Connect GitHub repository
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Add environment variables:
  - [ ] `DATABASE_URL` = Supabase connection string
  - [ ] `HOST` = `0.0.0.0`
  - [ ] `FRONTEND_URL` = (leave blank initially, update after Vercel deploys)
- [ ] Deploy and note service URL (e.g., `https://finances-api-xxxx.onrender.com`)

### Vercel Frontend Deployment
- [ ] Create Vercel project
- [ ] Connect GitHub repository (frontend folder)
- [ ] Add environment variable:
  - [ ] `VITE_API_URL` = Render service URL from previous step
- [ ] Deploy and note project URL (e.g., `https://finances-tracker-xxxx.vercel.app`)

### Final Configuration
- [ ] Go back to Render
- [ ] Update `FRONTEND_URL` to your Vercel URL
- [ ] Redeploy Render backend
- [ ] Test: Visit Vercel URL and verify API calls work

---

## File-by-File Changes

### Backend Changes

#### `requirements.txt`
- Added: `psycopg[binary]==3.3.3` (modern PostgreSQL driver)
- Added: `python-dotenv==1.0.1` (environment variable management)

#### `app/config.py`
- `DATABASE_URL` reads from environment with SQLite fallback
- `FRONTEND_URL` reads from environment and dynamically adds to CORS
- Maintains backward compatibility with local development

#### `app/database.py`
- **NEW:** NullPool configuration for PostgreSQL
- **NEW:** connect_args with timeout and application_name
- Auto-detects database type and configures accordingly
- Preserves SQLite WAL mode for local development

#### `app/main.py`
- CORS configuration reads from environment
- No code changes needed (uses `config.ALLOWED_ORIGINS`)

#### `run.py`
- Existing `HOST` and `PORT` environment variable support maintained
- Updated docstring

#### `backend/.env.example`
- NEW: Comprehensive template with Supabase examples
- Shows local dev, Render, and Supabase configurations

#### `backend/DEPLOYMENT.md`
- NEW: Supabase setup instructions
- NEW: Technical details on NullPool and connect_args
- Render and Supabase deployment guides

### Frontend Changes

#### `vite.config.ts`
- Uses `VITE_API_URL` environment variable
- Defaults to `http://127.0.0.1:8000` for local dev
- Works with Vercel environment variables in production

#### `frontend/.env.example`
- NEW: Configuration template
- Shows local dev and production examples

### Project Root Changes

#### `.env.example` files
- `backend/.env.example` - Backend configuration
- `frontend/.env.example` - Frontend configuration

#### `.gitignore`
- NEW: Root .gitignore prevents .env files from being committed
- NEW: `backend/.gitignore` - Python-specific patterns
- Existing: `frontend/.gitignore` - Node-specific patterns

#### Documentation Files
- **NEW:** `ENV_VARIABLES.md` - Complete environment variables guide
- **NEW:** `ENV_VARIABLES_QUICK.md` - Quick reference checklist
- **UPDATED:** `backend/DEPLOYMENT.md` - Supabase and production guides
- **EXISTING:** `PRODUCTION_REFACTOR.md` - Original refactoring summary
- **EXISTING:** `QUICKSTART_PRODUCTION.md` - Quick start guide

---

## How It Works in Production

```
┌─────────────────────────────────────────────────────────────┐
│                         USER BROWSER                         │
├─────────────────────────────────────────────────────────────┤
│                   Vercel Frontend (React)                    │
│ VITE_API_URL=https://finances-api.onrender.com              │
│  ↓ API calls to /api/...                                     │
├─────────────────────────────────────────────────────────────┤
│                   Render Backend (FastAPI)                   │
│ DATABASE_URL=postgresql://...supabase.co...                 │
│ FRONTEND_URL=https://finances-tracker.vercel.app            │
│ (CORS checks against FRONTEND_URL)                          │
│  ↓ Database connections                                      │
├─────────────────────────────────────────────────────────────┤
│            Supabase PostgreSQL + pgBouncer                   │
│ (Connection pooling handled by pgBouncer)                   │
└─────────────────────────────────────────────────────────────┘
```

### Connection Flow

1. **Frontend (Vercel):** Makes API request to `https://finances-api.onrender.com/api/...`
2. **Backend (Render):** 
   - Receives request with `Origin: https://finances-tracker.vercel.app`
   - Checks against `ALLOWED_ORIGINS` (which includes `FRONTEND_URL`)
   - Allows or denies based on CORS policy
3. **Database (Supabase):**
   - Backend uses `DATABASE_URL` to connect
   - NullPool means no connection pooling at app level
   - pgBouncer (Supabase's connection pooler) handles pooling
   - Returns data to backend
4. **Response:** Backend returns JSON to frontend

---

## Backward Compatibility

✅ **All existing functionality preserved:**
- Local development with SQLite still works unchanged
- All API routes work with both SQLite and PostgreSQL
- ML classifier functionality intact
- CSV import functionality intact
- Analytics and categorization unchanged
- No database migrations needed (tables auto-created)

**To use in local development:**
- Just run `python run.py` (no environment variables needed)
- Uses SQLite automatically
- CORS restricted to localhost automatically

---

## Security Considerations

1. ✅ Environment variables never hardcoded
2. ✅ `.env` files in `.gitignore`
3. ✅ Supabase uses TLS for database connections (`sslmode=require`)
4. ✅ CSRF protection via CORS on FRONTEND_URL
5. ✅ No secrets exposed in browser (API calls server-side proxied)
6. ✅ Database credentials in environment only, not in code

---

## Troubleshooting Guide

See `ENV_VARIABLES_QUICK.md` for common issues and solutions.

### Most Common Issues

1. **CORS Error** → Check `FRONTEND_URL` in Render matches exact Vercel URL
2. **API 404** → Check `VITE_API_URL` in Vercel matches exact Render URL (no trailing slash)
3. **Database Connection** → Verify `DATABASE_URL` is correct and includes `?sslmode=require`
4. **Changes not applied** → Redeploy in Render and Vercel after updating environment variables

---

## Testing the Setup

### Test Backend → Database Connection
```bash
curl https://your-render-url.com/docs
```
Should show API documentation (proves backend running and database ok)

### Test Frontend → Backend Connection
1. Open your Vercel URL
2. Open DevTools → Network tab
3. Try creating a transaction
4. Check that requests go to your Render backend URL
5. Check that CORS headers are correct

### Test Database Data Persistence
1. Add a transaction via frontend
2. Refresh page
3. Transaction should still be there
4. Check Supabase dashboard to verify data exists

---

## Next Steps (Optional)

1. Monitor logs: Render → Logs and Vercel → Logs
2. Set up error tracking (Sentry, LogRocket, etc.)
3. Monitor database usage: Supabase → Logs
4. Set up backups: Supabase handles automatically
5. Scale if needed: Both Render and Supabase auto-scale

---

## Documentation Files

| File | Purpose |
|------|---------|
| `ENV_VARIABLES.md` | Detailed environment variable documentation |
| `ENV_VARIABLES_QUICK.md` | Quick reference and step-by-step setup |
| `backend/DEPLOYMENT.md` | Backend deployment guide |
| `backend/README.md` | Backend setup and usage |
| `PRODUCTION_REFACTOR.md` | Original refactoring summary |
| `QUICKSTART_PRODUCTION.md` | Quick start overview |

Start with `ENV_VARIABLES_QUICK.md` for immediate setup, then refer to `ENV_VARIABLES.md` for detailed information.
