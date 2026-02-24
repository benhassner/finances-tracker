# Finance Tracker Backend

Local-only personal finance tracking API built with FastAPI.

## Features

- **Privacy-first**: All data stored locally in SQLite
- **CSV Import**: Supports Chase, Bank of America, Wells Fargo, and generic CSV formats
- **Rule-based categorization**: Automatic categorization with customizable rules
- **ML fallback**: Scikit-learn classifier for uncategorized transactions
- **Analytics**: Dashboard metrics, projections, and subscription detection
- **No external dependencies**: Runs completely offline

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

## API Documentation

Once running, visit `http://127.0.0.1:8000/docs` for interactive API documentation.

## Data Storage

- Database: `backend/data/db/finance.db`
- ML Models: `backend/data/models/`

All data stays on your local machine.

## Security

- CORS restricted to localhost origins only
- No external API calls
- No telemetry or data collection

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
