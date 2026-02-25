"""
Application configuration settings.
Supports both local development (SQLite) and production deployment (PostgreSQL).
No external services, no telemetry.
"""
import os
from pathlib import Path

# Base directory for all local data
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = DATA_DIR / "models"
DB_DIR = DATA_DIR / "db"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

# Database configuration
# Use DATABASE_URL environment variable for PostgreSQL in production
# Falls back to SQLite for local development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DB_DIR / 'finance.db'}"
)

# ML model paths
TFIDF_VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.joblib"
CLASSIFIER_PATH = MODEL_DIR / "classifier.joblib"

# Minimum labeled transactions needed to train/retrain the ML model
MIN_TRAINING_SAMPLES = 30

# CORS configuration
# Allow localhost in development
# Allow deployed frontend URL in production via FRONTEND_URL env var
_default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Vercel production frontend
    "https://finances-tracker-20d3dww45-benhassners-projects.vercel.app",
]

# Add FRONTEND_URL from environment variable if set
_frontend_url = os.getenv("FRONTEND_URL")
if _frontend_url and _frontend_url not in _default_origins:
    _default_origins.append(_frontend_url)

ALLOWED_ORIGINS = _default_origins

# Subscription detection thresholds
SUBSCRIPTION_MIN_OCCURRENCES = 2          # minimum repeats to flag
SUBSCRIPTION_AMOUNT_TOLERANCE = 0.05      # 5% variance allowed

# Default categories seeded into the database
DEFAULT_CATEGORIES = [
    "Groceries",
    "Dining Out",
    "Gas & Fuel",
    "Subscriptions",
    "Rent & Housing",
    "Income",
    "Utilities",
    "Healthcare",
    "Entertainment",
    "Shopping",
    "Travel",
    "Insurance",
    "Education",
    "Personal Care",
    "Transfers",
    "Other",
]

# Default categorisation rules  (keyword → category)
DEFAULT_RULES = [
    # Groceries
    ("walmart", "Groceries", 10),
    ("kroger", "Groceries", 10),
    ("whole foods", "Groceries", 10),
    ("trader joe", "Groceries", 10),
    ("safeway", "Groceries", 10),
    ("costco", "Groceries", 10),
    ("aldi", "Groceries", 10),
    ("publix", "Groceries", 10),
    ("target", "Groceries", 5),
    # Dining Out
    ("mcdonald", "Dining Out", 10),
    ("starbucks", "Dining Out", 10),
    ("chipotle", "Dining Out", 10),
    ("doordash", "Dining Out", 10),
    ("ubereats", "Dining Out", 10),
    ("grubhub", "Dining Out", 10),
    ("subway", "Dining Out", 10),
    ("chick-fil-a", "Dining Out", 10),
    ("taco bell", "Dining Out", 10),
    ("pizza", "Dining Out", 8),
    ("restaurant", "Dining Out", 7),
    # Gas & Fuel
    ("shell", "Gas & Fuel", 10),
    ("chevron", "Gas & Fuel", 10),
    ("exxon", "Gas & Fuel", 10),
    ("bp ", "Gas & Fuel", 10),
    ("mobil", "Gas & Fuel", 10),
    ("sunoco", "Gas & Fuel", 10),
    ("speedway", "Gas & Fuel", 10),
    ("gas station", "Gas & Fuel", 10),
    # Subscriptions
    ("netflix", "Subscriptions", 10),
    ("spotify", "Subscriptions", 10),
    ("hulu", "Subscriptions", 10),
    ("disney+", "Subscriptions", 10),
    ("apple.com/bill", "Subscriptions", 10),
    ("amazon prime", "Subscriptions", 10),
    ("youtube premium", "Subscriptions", 10),
    ("hbo", "Subscriptions", 10),
    ("paramount", "Subscriptions", 10),
    ("adobe", "Subscriptions", 10),
    ("microsoft 365", "Subscriptions", 10),
    ("dropbox", "Subscriptions", 10),
    ("github", "Subscriptions", 8),
    # Rent & Housing
    ("rent", "Rent & Housing", 10),
    ("mortgage", "Rent & Housing", 10),
    ("hoa", "Rent & Housing", 10),
    ("apartment", "Rent & Housing", 8),
    # Income
    ("direct deposit", "Income", 10),
    ("payroll", "Income", 10),
    ("salary", "Income", 10),
    ("transfer from", "Transfers", 8),
    # Utilities
    ("electric", "Utilities", 10),
    ("water bill", "Utilities", 10),
    ("gas bill", "Utilities", 10),
    ("internet", "Utilities", 10),
    ("at&t", "Utilities", 9),
    ("verizon", "Utilities", 9),
    ("t-mobile", "Utilities", 9),
    ("comcast", "Utilities", 9),
    ("xfinity", "Utilities", 9),
    # Healthcare
    ("pharmacy", "Healthcare", 10),
    ("cvs", "Healthcare", 9),
    ("walgreens", "Healthcare", 9),
    ("dr ", "Healthcare", 8),
    ("medical", "Healthcare", 8),
    ("hospital", "Healthcare", 10),
    ("dental", "Healthcare", 10),
    ("vision", "Healthcare", 9),
    # Entertainment
    ("amc", "Entertainment", 9),
    ("regal", "Entertainment", 9),
    ("cinema", "Entertainment", 9),
    ("movie", "Entertainment", 8),
    ("steam", "Entertainment", 9),
    ("playstation", "Entertainment", 9),
    ("xbox", "Entertainment", 9),
    # Travel
    ("airline", "Travel", 10),
    ("delta", "Travel", 9),
    ("united air", "Travel", 9),
    ("american air", "Travel", 9),
    ("southwest", "Travel", 9),
    ("hotel", "Travel", 10),
    ("airbnb", "Travel", 10),
    ("uber", "Travel", 8),
    ("lyft", "Travel", 8),
    # Shopping
    ("amazon", "Shopping", 8),
    ("ebay", "Shopping", 9),
    ("etsy", "Shopping", 9),
    ("best buy", "Shopping", 9),
    ("home depot", "Shopping", 9),
    ("lowes", "Shopping", 9),
    # Insurance
    ("insurance", "Insurance", 10),
    ("geico", "Insurance", 10),
    ("state farm", "Insurance", 10),
    ("progressive", "Insurance", 10),
    # Education
    ("tuition", "Education", 10),
    ("udemy", "Education", 10),
    ("coursera", "Education", 10),
    ("student loan", "Education", 10),
    ("bookstore", "Education", 9),
]
