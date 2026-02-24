# Finance Tracker Frontend

React frontend for the personal finance tracker.

## Features

- **Modern UI**: Clean, responsive design with dark mode
- **Dashboard**: Financial overview with charts and analytics
- **Transaction Management**: View, edit, and categorize transactions
- **CSV Import**: Upload and import transaction files
- **Rule Management**: Create and manage categorization rules
- **Category Management**: Organize spending categories
- **Budget Alerts**: Set and monitor spending limits

## Setup

1. Install dependencies:
```bash
cd ./frontend
npm install
```

2. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

Proxy to backend API:
- The frontend proxies API calls from `/api/*` to `http://127.0.0.1:8000/*` (see `vite.config.ts`).
- If you run the backend on a different port, update `frontend/vite.config.ts` accordingly and restart the dev server.

Recommended backend start command (from repository root, ensures correct module path):
```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

## Build for Production

```bash
npm run build
```

## Tech Stack

- React 18 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Axios for API calls
- Recharts for data visualization
- React Router for navigation