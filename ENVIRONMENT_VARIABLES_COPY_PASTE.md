# Copy-Paste Environment Variables for Deployment Dashboards

Use these exact values in your Render and Vercel dashboards.

---

## 🔴 RENDER DASHBOARD - Environment Variables

**Location:** Render Web Service → Settings → Environment Variables

### Copy These Exactly:

#### For Supabase PostgreSQL:
```
DATABASE_URL
postgresql://postgres:YOUR_PASSWORD@db.supabase.co:5432/postgres?sslmode=require

HOST
0.0.0.0

FRONTEND_URL
https://finances-tracker.vercel.app
```

#### For Render PostgreSQL:
```
DATABASE_URL
postgresql://your_username:your_password@dpg-xxxxx-a.render-postgres.com:5432/your_db_name

HOST
0.0.0.0

FRONTEND_URL
https://finances-tracker.vercel.app
```

### Step-by-Step Instructions:

1. Open Render Dashboard
2. Select your Web Service
3. Click "Settings" (gear icon)
4. Scroll to "Environment Variables"
5. For each variable:
   - Click "Add Environment Variable"
   - **Name** field: Copy the first line above (e.g., `DATABASE_URL`)
   - **Value** field: Copy the second line above (replace credentials with your actual values)
   - Click "Add"
6. After adding all 3 variables, scroll up and click "Deploy" or "Redeply"

### What to Replace:
- `YOUR_PASSWORD`: Your Supabase password
- `finances-tracker.vercel.app`: Your actual Vercel frontend URL (get from step 1 below)

---

## 🔵 VERCEL DASHBOARD - Environment Variables

**Location:** Vercel Project Settings → Environment Variables

### Copy This Exactly:

```
VITE_API_URL
https://finances-api.onrender.com
```

### Step-by-Step Instructions:

1. Open Vercel Dashboard
2. Select your Project
3. Go to "Settings" (in the top navigation)
4. Click "Environment Variables" (left sidebar)
5. Click "Add New"
6. **Name**: `VITE_API_URL`
7. **Value**: Copy the URL from your Render Web Service
   - Go to Render Dashboard → Web Service → Note the "Service URL" field
   - Paste that URL here (example: `https://finances-api.onrender.com`)
8. Click "Save"
9. Vercel will auto-redeploy (or manually redeploy from "Deployments" tab)

### What to Replace:
- `https://finances-api.onrender.com`: Your actual Render service URL

---

## 📋 FINDING YOUR ACTUAL URLs

### Finding Render Service URL:
1. Render Dashboard → Select Web Service → Top of page shows "Service URL"
2. Looks like: `https://finances-api-xxxx.onrender.com`
3. Copy entire URL (including `https://`)

### Finding Vercel Project URL:
1. Vercel Dashboard → Select Project → Top shows "Production" domain
2. Looks like: `https://finances-tracker-xxxx.vercel.app`
3. Copy entire URL (including `https://`)

### Finding Supabase Connection String:
1. Supabase Dashboard → Select Project
2. Settings → Database (left sidebar)
3. Connection String section → Select "URI"
4. Copy the full connection string
5. Make sure it says "Transaction Pool" mode at the top

---

## ⚠️ REMEMBER THIS ORDER

1. **First:** Deploy Render backend (with temporary `FRONTEND_URL` value)
2. **Get:** Note the Render Service URL
3. **Second:** Deploy Vercel frontend with that URL as `VITE_API_URL`
4. **Get:** Note the Vercel Project URL
5. **Final:** Update Render's `FRONTEND_URL` with the Vercel URL, then redeploy

This order matters because you need the Vercel URL before setting `FRONTEND_URL` in Render.

---

## ✅ VALIDATION

After setting all variables:

### Test Render Backend:
```
Visit: https://your-render-service-url.com/docs
```
You should see interactive API documentation (Swagger UI).
If you see a blank page or error, check Render logs: Web Service → Logs

### Test Vercel Frontend:
```
Visit: https://your-vercel-url.vercel.app
```
Open DevTools → Console tab
Try to make an API call (create a transaction, view dashboard)
✅ If it works: No errors in console, data appears
❌ If it fails: Check console for CORS or network errors

---

## 🔧 COMMON ISSUES & FIXES

| Issue | Check | Solution |
|-------|-------|----------|
| Blank page on Vercel | DevTools Console | Check if VITE_API_URL is set correctly |
| API 404 errors | Network tab → requests | Verify VITE_API_URL doesn't have trailing slash |
| CORS errors in console | Browser console | Verify FRONTEND_URL in Render exactly matches Vercel URL |
| Can't connect to database | Render Logs → error | Verify DATABASE_URL is correct |
| "Connection timeout" | Render Logs → error | Check DATABASE_URL has `?sslmode=require` |

---

## 🚀 QUICK CHECKLIST

- [ ] Supabase connection string copied
- [ ] Render backend deployed with DATABASE_URL, HOST, FRONTEND_URL
- [ ] Render service URL noted
- [ ] Vercel frontend deployed with VITE_API_URL
- [ ] Vercel project URL noted
- [ ] Render FRONTEND_URL updated with Vercel URL
- [ ] Render redeployed
- [ ] Test backend: `/docs` endpoint works
- [ ] Test frontend: Can access at Vercel URL
- [ ] Test API calls: Can create/view transactions
- [ ] Check logs: No errors in Render or Vercel logs

---

## 📞 NEED HELP?

### If deployment fails on Render:
→ Check Render Logs: Web Service → Logs tab
→ Look for errors about DATABASE_URL, imports, or settings
→ Common: Database URL formatting, psycopg import errors

### If frontend can't reach API:
→ Check browser DevTools → Network tab
→ Check if requests are going to correct backend URL
→ Check if CORS error (likely FRONTEND_URL mismatch)

### If API returns 500 errors:
→ Check Render Logs for stacktrace
→ Verify DATABASE_URL is working: Try `/docs` endpoint
→ Check if tables exist: Might need manual restart

---

## 📚 For More Information

- See `ENV_VARIABLES.md` for detailed documentation
- See `ENV_VARIABLES_QUICK.md` for step-by-step setup
- See `backend/DEPLOYMENT.md` for technical details
- See `SUPABASE_RENDER_VERCEL_SETUP.md` for complete overview
