# Deployment Guide

This guide covers deploying the Finance Tracker backend to production platforms like Render.

## Quick Start: Render Deployment

### 1. Create a PostgreSQL Database

1. Log in to [render.com](https://render.com)
2. Go to **PostgreSQL** → **Create New**
3. Fill in details:
   - **Name**: `finances-db` (or your choice)
   - **Region**: Choose closest to you
   - **PostgreSQL Version**: Latest (14+)
4. Click **Create Database**
5. Copy the **External Database URL** (looks like: `postgresql://user:password@host:5432/db`)

### 2. Create a Web Service

1. Click **New +** → **Web Service**
2. Select your GitHub repository
3. Configure:
   - **Name**: `finances-api` (or your choice)
   - **Environment**: Python 3.11+
   - **Region**: Same as database
   - **Build Command**: 
     ```
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

### 3. Add Environment Variables

In the Web Service settings, add these environment variables:

```
DATABASE_URL=postgresql://user:password@host:5432/db
HOST=0.0.0.0
FRONTEND_URL=https://your-frontend-domain.com
```

Replace:
- `postgresql://...` with your database URL from step 1
- `https://your-frontend-domain.com` with your frontend's deployed URL

### 4. Deploy

- Click **Create Web Service**
- Render will automatically build and deploy
- Click the service URL to verify it's running

## Quick Start: Supabase + Render Deployment

**Recommended:** Use Supabase for the database + Render for the backend service.

### 1. Create a Supabase PostgreSQL Database

1. Log in to [supabase.com](https://supabase.com)
2. Create a new project
3. Go to **Settings** → **Database**
4. Copy the **Connection String** (URI format)
   - Important: Use "Transaction Pool" for pgBouncer compatibility
   - URL should look like: `postgresql://postgres:password@db.supabase.co:5432/postgres?sslmode=require`

### 2. Create Render Web Service (same as above)

Follow the Render steps above, but use your Supabase connection string as `DATABASE_URL`.

### 3. Environment Variables on Render

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.supabase.co:5432/postgres?sslmode=require
HOST=0.0.0.0
FRONTEND_URL=https://your-frontend-domain.com
```

**Key differences from Render PostgreSQL:**
- Supabase connection string includes `?sslmode=require` for secure connections
- pgBouncer connection pooling is automatically handled
- No need to manage your own database backups (Supabase handles it)

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/dbname` |
| `HOST` | Server bind address | `0.0.0.0` (production) or `127.0.0.1` (local) |
| `PORT` | Server port | `8000` (auto-set by Render) |
| `FRONTEND_URL` | Frontend domain for CORS | `https://yourdomain.com` |

## Database Initialization

The app automatically:
1. Creates all required tables on startup
2. Seeds default categories and rules
3. No manual migrations needed

To verify database connection:
```bash
curl https://your-service.onrender.com/docs
```

You should see the Swagger UI.

## Local Testing with PostgreSQL

Before deploying, test locally with PostgreSQL:

### Install PostgreSQL (macOS with Homebrew)
```bash
brew install postgresql
brew services start postgresql
```

### Install PostgreSQL (Windows)
Download from [postgresql.org](https://www.postgresql.org/download/windows/) and install.

### Create Local Test Database
```bash
psql postgres
CREATE DATABASE finances_test;
\q
```

### Set Environment Variable and Test
```bash
# Linux/macOS
export DATABASE_URL=postgresql://postgres:@localhost/finances_test

# Windows (PowerShell)
$env:DATABASE_URL="postgresql://postgres:@localhost/finances_test"

# Run the app
python -m uvicorn app.main:app --reload
```

## Troubleshooting

### Database Connection Error
- Verify `DATABASE_URL` is correct and includes password
- Ensure database credentials are set in Render environment variables
- Check database is in the same region

### Port Already in Use
- The app automatically uses the `$PORT` environment variable on Render
- Locally, change with: `PORT=8001 python -m uvicorn app.main:app --reload`

### CORS Errors
- Confirm `FRONTEND_URL` is set correctly (include `https://`)
- Frontend URL must match exactly (including protocol and domain)

### Tables Not Created
- Restart the service (Render: click "Restart Latest Deployment")
- Check logs: `render.com` → Web Service → Logs tab

## Production Best Practices

1. **Use strong PostgreSQL password** (Render generates one; don't change it)
2. **Enable SSL for CORS** (use `https://` in `FRONTEND_URL`)
3. **Monitor logs regularly** (check Render's Logs tab)
4. **Backup database periodically** (Render includes backups)
5. **Keep dependencies updated** periodically

## Switching from SQLite to PostgreSQL

The code automatically detects the database type:
- If `DATABASE_URL` starts with `sqlite` → Uses SQLite
- If `DATABASE_URL` starts with `postgresql` → Uses PostgreSQL

**To migrate existing data:**
1. Export from SQLite: Use a database tool or script
2. Import to PostgreSQL: Use `pg_restore` or similar
3. Update `DATABASE_URL` to PostgreSQL
4. Test thoroughly before going live

## Support

For Render-specific help:
- [Render Docs](https://render.com/docs)
- [PostgreSQL on Render](https://render.com/docs/databases)

For Supabase-specific help:
- [Supabase Docs](https://supabase.com/docs)
- [Connection Pooling Guide](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)

## Technical Details: Connection Pooling and NullPool

The app uses **NullPool** for production PostgreSQL connections. This configuration:

1. **Eliminates connection pooling at the application level** - Better for serverless/ephemeral environments
2. **Works seamlessly with Supabase's pgBouncer** - Supabase uses pgBouncer for connection pooling, so the app doesn't duplicate this
3. **Includes connect_args optimization**:
   - `connect_timeout=10` - Better handling of temporary connection issues
   - `application_name=finances-tracker` - Helps identify connections in database logs

See `app/database.py` for implementation details.

For app-specific issues:
- Check `/docs` endpoint for API documentation
- Review `app/config.py` for configuration options
