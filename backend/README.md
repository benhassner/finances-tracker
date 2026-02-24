# Finance Tracker Backend

Personal finance tracking API built with FastAPI. Supports both local development (SQLite) and production deployment (PostgreSQL).

## Features

- **Privacy-first**: All data stored locally or on your own database
- **Flexible database**: SQLite for development, PostgreSQL for production
- **CSV Import**: Supports Chase, Bank of America, Wells Fargo, and generic CSV formats
- **Rule-based categorization**: Automatic categorization with customizable rules
- **ML fallback**: Scikit-learn classifier for uncategorized transactions
- **Analytics**: Dashboard metrics, projections, and subscription detection
- **Production-ready**: Configured for deployment on Render, Heroku, or similar platforms

## Setup

1. Install Python dependencies:
```bash
cd ./backend
pip install -r requirements.txt
```

2. Run the server (recommended):
- From the repository root:
```bash
python backend/run.py
```
- Or set HOST/PORT if needed:
```bash
set HOST=127.0.0.1
set PORT=8000
python backend/run.py
```
- Or from the ./backend folder:
```bash
python ./run.py
```

Advanced (alternative):
- From the repository root (ensures correct module path):
```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
- Or from the backend folder:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`

Tip: If port 8000 is blocked, pick a different port (e.g. 8010) and update the frontend proxy target in `frontend/vite.config.ts` accordingly.

## Production Deployment

The backend is configured for production deployment on Render, Heroku, or similar platforms.

### Environment Variables

Create a `.env` file (or set environment variables) with the following:

```bash
# PostgreSQL database URL (required for production)
DATABASE_URL=postgresql://user:password@hostname:5432/database_name

# Server configuration
HOST=0.0.0.0                  # Bind to all interfaces for production
PORT=8000                      # Render/Heroku sets this automatically

# Frontend URL for CORS (required for production)
FRONTEND_URL=https://yourdomain.com
```

See [.env.example](.env.example) for complete documentation.

### Deploying to Render

1. **Create PostgreSQL database** on Render
2. **Create Web Service** on Render:
   - Connect your GitHub repository
   - Set **Build Command**: `pip install -r requirements.txt`
   - Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Set environment variables (DATABASE_URL, FRONTEND_URL, etc.)
3. **Deploy** — Render automatically creates tables on first run

### Database Migrations

The app automatically creates tables on startup using SQLAlchemy's `create_all()`. No additional migration steps are required.

To use PostgreSQL locally for testing:

```bash
# Install postgres locally or use Docker
export DATABASE_URL=postgresql://user:password@localhost:5432/finances
python -m uvicorn app.main:app --reload
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Data Storage

- **Local Development**: SQLite database at `backend/data/db/finance.db`
- **Production**: PostgreSQL database (configured via `DATABASE_URL`)
- **ML Models**: `backend/data/models/`

## Security

- **CORS**: Restricted to localhost origins (development) and configured frontend URL (production)
- **No external API calls**: App runs completely offline or with your own database
- **No telemetry**: No data collection or tracking

## 🚨 ERROR NOTES

### ❌ `[WinError 10048] Only one usage of each socket address is normally permitted`

**Cause:**
Port `8000` is already in use by another process. Only one application can bind to a port at a time.

### 🔎 Step 1 — Check What’s Using Port 8000

Open **Command Prompt (Run as Administrator)** and run:

```bash
netstat -ano | findstr :8000
```

You should see something like:

```bash
TCP    127.0.0.1:8000    0.0.0.0:0    LISTENING    12345
```

The last number (`12345`) is the **PID (Process ID)**.

---

### 🔎 Step 2 — Identify the Process

Replace `12345` with your PID:

```bash
tasklist /FI "PID eq 12345"
```

This will show which application is using the port.

Common causes:

* Previously running FastAPI / Django server
* Uvicorn still running
* VSCode Live Server
* Docker container
* Stuck Python process

---

### 💀 Step 3 — Kill the Process (If Safe)

If it’s safe to terminate:

```bash
taskkill /PID 12345 /F
```

---

### ⚡ Alternative: Use a Different Port

Instead of killing the process, you can run your server on a different port:

**FastAPI / Uvicorn:**

```bash
uvicorn main:app --port 8001
```

**Django:**

```bash
python manage.py runserver 8001
```

---

### 🧠 If Port Still Seems Stuck

Sometimes a process lingers after closing a terminal.

Try:

* Restarting VSCode
* Restarting your terminal
* Restarting your computer (guaranteed reset)

---

### ✅ Quick One-Liner (PowerShell)

To find and kill whatever is using port 8000:

```powershell
for /f "tokens=5" %a in ('netstat -ano ^| findstr :8000') do taskkill /PID %a /F
```
