# Personal Finance Tracker

A privacy-first, local-only personal finance tracking application. All data stays on your machine — no cloud storage, no external APIs, no telemetry.

## Features

- **Local-Only**: SQLite database stored locally, no data leaves your machine
- **CSV Import**: Support for Chase, Bank of America, Wells Fargo, and generic CSV formats
- **Smart Categorization**: Rule-based classification with ML fallback
- **Analytics Dashboard**: Spending breakdown, trends, and projections
- **Subscription Detection**: Automatically identifies recurring charges
- **Budget Alerts**: Set spending limits and get notified when exceeded
- **Modern UI**: Clean React interface with dark mode support

## Architecture

### Backend (Python/FastAPI)
- **Framework**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite with WAL mode for performance
- **ML**: Scikit-learn Logistic Regression for transaction categorization
- **Security**: CORS restricted to localhost, no external calls

### Frontend (React/TypeScript)
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS with dark mode
- **Charts**: Recharts for data visualization
- **Routing**: React Router for navigation

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the server:
```bash
python ./run.py
```

The backend will be available at `http://127.0.0.1:8000`

### Frontend Setup

1. Open a new terminal and navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

4. Open your browser to `http://localhost:5173` (or the port shown by Vite)

### Running Both Simultaneously

You'll want to run both the backend and frontend in separate terminal windows:

**Terminal 1 (Backend):**
```bash
cd backend
python ./run.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Then open `http://localhost:5173` in your browser to access the application.

## Usage

### First Time Setup
1. The application will automatically create default categories and rules
2. Import your first CSV file using the Import page
3. Transactions will be automatically categorized using rules
4. Review and manually categorize any uncategorized transactions

### Importing Transactions
- Go to the Import page
- Select a CSV file from your bank/credit card
- Choose an account name (optional)
- Click Import
- Review the results and any error messages

### Managing Categories
- Use the Categories page to add, edit, or remove spending categories
- Set budget limits for each category
- Categories are used for organization and reporting

### Creating Rules
- Rules automatically categorize transactions based on keywords
- Higher priority rules are applied first
- Example: keyword "starbucks" → category "Dining Out"

### Setting Alerts
- Create budget alerts for specific categories
- Get visual warnings when spending exceeds limits
- Alerts appear on the dashboard

### ML Training
- The system automatically trains on categorized transactions
- Retrain manually from the dashboard if needed
- Minimum 30 transactions required for training

## Data Storage

All data is stored locally in:
- `backend/data/db/finance.db` - SQLite database
- `backend/data/models/` - Trained ML models

## Security & Privacy

- **No External Calls**: Completely offline operation
- **Local Storage**: All data stays on your machine
- **No Telemetry**: No tracking or analytics collection
- **CORS Restricted**: Only accepts requests from localhost
- **No Credentials**: No API keys or external service authentication

## Backup & Restore

### Database Backup
```bash
# From backend directory
cp data/db/finance.db data/db/finance_backup.db
```

### Full Backup
```bash
# Backup entire data directory
cp -r backend/data backend/data_backup
```

### Restore
```bash
# Stop the backend server first
cp data_backup/db/finance.db data/db/finance.db
```

## Troubleshooting

### Backend Issues
- Ensure Python 3.11+ is installed
- Check that all dependencies are installed
- Verify the database file has proper permissions

### Frontend Issues
- Ensure Node.js 18+ is installed
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall

### Import Issues
- Check CSV format matches supported formats
- Ensure date columns are properly formatted
- Verify file encoding (UTF-8 preferred)

## Development

### Running Tests
```bash
# Backend tests (when implemented)
cd backend
python -m pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

### API Documentation
When the backend is running, visit `http://127.0.0.1:8000/docs` for interactive API documentation.

## License

This project is provided as-is for educational and personal use.