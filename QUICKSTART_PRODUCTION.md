# Quick Deployment Reference

## Local Development (SQLite)

```bash
cd backend
pip install -r requirements.txt
python run.py
# API: http://127.0.0.1:8000
```

No configuration needed. Automatically uses SQLite and localhost CORS.

## Production (PostgreSQL on Render)

### 1. Create PostgreSQL Database
- Render dashboard → PostgreSQL → Create
- Copy the external connection string

### 2. Create Web Service
- Render dashboard → Web Service → Connect GitHub repo
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. Set Environment Variables
```
DATABASE_URL=postgresql://...copy-from-postgres-service...
FRONTEND_URL=https://your-frontend-domain.com
```

### 4. Deploy
Click "Create Web Service" - done!

## Environment Variables

| Variable | Local Dev | Production |
|----------|-----------|------------|
| `DATABASE_URL` | (omit - uses SQLite) | Your PostgreSQL URL |
| `HOST` | 127.0.0.1 | 0.0.0.0 |
| `PORT` | (omit - uses 8000) | Auto-set by Render |
| `FRONTEND_URL` | (omit) | https://your-domain.com |

## Frontend Configuration

Local dev: No changes needed (proxy to localhost:8000)

Production: Set environment variable in `.env.local` or deployment platform:
```
VITE_API_URL=https://your-backend-api-domain.com
```

## Important

- ✅ Backward compatible with existing SQLite setup
- ✅ All features preserved
- ✅ Automatic table creation
- ✅ No manual migrations needed
- ✅ CORS automatically configured

See [DEPLOYMENT.md](backend/DEPLOYMENT.md) for detailed guide.
