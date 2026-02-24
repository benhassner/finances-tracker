# Production Deployment & Environment Variables - Complete Guide

Choose your path below based on your needs:

---

## 🚀 I want to deploy NOW (Quick Start)

**→ Open: [`ENVIRONMENT_VARIABLES_COPY_PASTE.md`](ENVIRONMENT_VARIABLES_COPY_PASTE.md)**

This gives you exact step-by-step instructions with copy-paste values for:
- Render dashboard
- Vercel dashboard
- What to replace

**Time to read:** 5 minutes
**Time to deploy:** 15 minutes

---

## 📚 I want to understand what was changed

**→ Open: [`SUPABASE_RENDER_VERCEL_SETUP.md`](SUPABASE_RENDER_VERCEL_SETUP.md)**

Complete summary of all changes including:
- What was configured and why
- How the pieces fit together
- Backward compatibility
- Security considerations

**Time to read:** 15 minutes

---

## 📋 I need a detailed checklist

**→ Open: [`ENV_VARIABLES_QUICK.md`](ENV_VARIABLES_QUICK.md)**

Quick reference with:
- Copy-paste templates
- Step-by-step checklists
- Common mistakes & fixes
- Troubleshooting guide

**Time to read:** 10 minutes

---

## 🔧 I need detailed technical documentation

**→ Open: [`ENV_VARIABLES.md`](ENV_VARIABLES.md)**

Complete technical reference with:
- Every environment variable explained
- Render setup walkthrough
- Vercel setup walkthrough
- Local testing with PostgreSQL
- Troubleshooting deep-dives

**Time to read:** 20 minutes

---

## 📖 I need backend-specific deployment info

**→ Open: [`backend/DEPLOYMENT.md`](backend/DEPLOYMENT.md)**

Backend deployment guide including:
- Render deployment steps
- Supabase configuration
- Database initialization
- Connection pooling details
- Production best practices

**Time to read:** 15 minutes

---

## 🎯 Which path for me?

| Scenario | Read First | Then |
|----------|-----------|------|
| Just deploy & get it working | COPY_PASTE | QUICK |
| Learning how this works | SUPABASE_SETUP | ENV_VARIABLES |
| Troubleshooting an error | COPY_PASTE → QUICK | ENV_VARIABLES |
| Setting up from scratch | COPY_PASTE | DEPLOYMENT |
| Migrating from localhost | ENV_VARIABLES | DEPLOYMENT |

---

## ✨ What Was Configured

### Backend Changes
- ✅ SQLAlchemy NullPool for serverless environments
- ✅ connect_args optimization for Supabase pgBouncer
- ✅ CORS configured via `FRONTEND_URL` environment variable
- ✅ DATABASE_URL support for PostgreSQL + Supabase
- ✅ Backward compatible with local SQLite

### Frontend Changes
- ✅ `VITE_API_URL` environment variable support
- ✅ Dynamic backend URL configuration
- ✅ Vite dev proxy respects environment variables
- ✅ Works with Vercel environment setup

### Deployment Ready
- ✅ Render.com compatible (NullPool + connect_args)
- ✅ Supabase PostgreSQL compatible
- ✅ Vercel frontend deployment ready
- ✅ Environment variable driven configuration
- ✅ Production security best practices

---

## 📍 Environment Variables at a Glance

### Render Backend (3 variables)
```
DATABASE_URL = postgresql://...supabase...
HOST = 0.0.0.0
FRONTEND_URL = https://your-vercel-url.vercel.app
```

### Vercel Frontend (1 variable)
```
VITE_API_URL = https://your-render-url.onrender.com
```

**👉 See `ENVIRONMENT_VARIABLES_COPY_PASTE.md` for exact values to use**

---

## 🗺️ Architecture

```
┌─────────────────────────────────────────────────────┐
│  Browser                                            │
│  ↓ Visits https://your-frontend.vercel.app          │
├─────────────────────────────────────────────────────┤
│  Vercel (Frontend)                                  │
│  VITE_API_URL tells it where backend is             │
│  ↓ API calls to /api/...                            │
├─────────────────────────────────────────────────────┤
│  Render (Backend - FastAPI)                         │
│  DATABASE_URL connects to Supabase                  │
│  FRONTEND_URL validates CORS                        │
│  HOST=0.0.0.0 for production                        │
│  ↓ Database queries                                 │
├─────────────────────────────────────────────────────┤
│  Supabase PostgreSQL                                │
│  pgBouncer handles connection pooling               │
│  (NullPool + connect_args optimized)               │
└─────────────────────────────────────────────────────┘
```

---

## ✅ Local Development (Still Works!)

No environment variables needed:
```bash
cd backend && python run.py
# Uses SQLite at data/db/finance.db automatically
```

```bash
cd frontend && npm run dev
# Proxies to http://127.0.0.1:8000 automatically
```

---

## 📞 Quick Links

| Need | Link |
|------|------|
| Copy-paste values for dashboards | [ENVIRONMENT_VARIABLES_COPY_PASTE.md](ENVIRONMENT_VARIABLES_COPY_PASTE.md) |
| Quick reference checklist | [ENV_VARIABLES_QUICK.md](ENV_VARIABLES_QUICK.md) |
| Complete documentation | [ENV_VARIABLES.md](ENV_VARIABLES.md) |
| Backend deployment guide | [backend/DEPLOYMENT.md](backend/DEPLOYMENT.md) |
| What was changed summary | [SUPABASE_RENDER_VERCEL_SETUP.md](SUPABASE_RENDER_VERCEL_SETUP.md) |
| First steps guide | [PRODUCTION_REFACTOR.md](PRODUCTION_REFACTOR.md) |
| Quick start | [QUICKSTART_PRODUCTION.md](QUICKSTART_PRODUCTION.md) |

---

## 🚢 Ready to Deploy?

1. **5 min setup:** Open `ENVIRONMENT_VARIABLES_COPY_PASTE.md`
2. **15 min deployment:** Follow the copy-paste guide
3. **2 min verification:** Test your frontend URL

**That's it! You're live! 🎉**

---

*For questions, see the relevant documentation file above or check backend/DEPLOYMENT.md for technical details.*
