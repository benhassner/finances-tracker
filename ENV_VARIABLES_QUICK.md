# Quick Environment Variables Checklist

Copy and paste these exact environment variables into your deployment platforms.

## ✅ Render Dashboard Setup

**Location:** Render Web Service → Environment tab

```
DATABASE_URL=postgresql://user:password@db.supabase.co:5432/postgres?sslmode=require
HOST=0.0.0.0
FRONTEND_URL=https://finances-tracker.vercel.app
```

**Replace:**
- `postgresql://...` with your actual database connection string from Supabase
- `https://finances-tracker.vercel.app` with your actual Vercel frontend URL

---

## ✅ Vercel Dashboard Setup

**Location:** Vercel Project → Settings → Environment Variables

```
VITE_API_URL=https://finances-api.onrender.com
```

**Replace:**
- `https://finances-api.onrender.com` with your actual Render backend service URL

---

## ✅ Supabase Connection String

**Location:** Supabase Dashboard → Project Settings → Database → Connection String

1. Copy the **URI** (not password)
2. Change the pool mode parameter to `?sslmode=require` if not already present
3. Use this as your `DATABASE_URL` in Render

Example format:
```
postgresql://postgres:YOUR_PASSWORD@db.supabase.co:5432/postgres?sslmode=require
```

---

## ✅ Find Your URLs

### Render Backend URL
After deploying to Render, your URL will be something like:
```
https://finances-api-xxxx.onrender.com
```
(shown in Render dashboard as "Service URL")

### Vercel Frontend URL
After deploying to Vercel, your URL will be something like:
```
https://finances-tracker-xxxxx.vercel.app
```
(shown in Vercel dashboard)

---

## ✅ Step-by-Step for Render

1. Create/connect your PostgreSQL database (Render or Supabase)
2. Go to Render Web Service → Settings
3. Scroll to "Environment"
4. Click "Add Environment Variable" for each:
   - Name: `DATABASE_URL` → Value: (paste from Supabase)
   - Name: `HOST` → Value: `0.0.0.0`
   - Name: `FRONTEND_URL` → Value: (your Vercel URL with https://)
5. Save and redeploy

---

## ✅ Step-by-Step for Vercel

1. Go to Vercel Project → Settings
2. Click "Environment Variables" in left sidebar
3. Click "Add New"
4. Name: `VITE_API_URL`
5. Value: (your Render backend URL with https://)
6. Click "Add"
7. Redeploy (or push to main branch if auto-deploy enabled)

---

## ⚠️ Common Mistakes

| Mistake | Fix |
|---------|-----|
| Missing `https://` in `FRONTEND_URL` | Must include protocol: `https://yourdomain.com` |
| Using localhost URL in production vars | Use full deployed URLs only |
| `VITE_API_URL` has trailing slash | Remove it: `https://api.com` not `https://api.com/` |
| Database URL without `?sslmode=require` | Add it for Supabase remote connections |
| Forgot to redeploy after setting vars | Redeploy in both Render and Vercel after changes |

---

## 🔗 Where to Get the Values

| Variable | Where to Find |
|----------|---------------|
| `DATABASE_URL` | Supabase Dashboard → Settings → Database → Connection String (URI) |
| `FRONTEND_URL` | Vercel Dashboard → Domain (after first deploy) |
| `VITE_API_URL` | Render Dashboard → Web Service → Service URL |

---

## ✨ After Setting Variables

1. **Render:** Auto-redeploys when env vars change (check "Events" tab)
2. **Vercel:** Automatic redeploy on git push, or manual redeploy in dashboard
3. **Test:** Visit your frontend URL and try using the app
4. **Verify CORS:** Check browser console for CORS errors (if any)
5. **Check Logs:** 
   - Render: Web Service → Logs
   - Vercel: Deployments → select latest → Logs

---

## 📋 Full Production Checklist

- [ ] Database created (Supabase or Render PostgreSQL)
- [ ] Render Web Service created
- [ ] Render env vars set: `DATABASE_URL`, `HOST`, `FRONTEND_URL`
- [ ] Render deployed successfully (check logs)
- [ ] Note Render Service URL (`https://finances-api-xxxx.onrender.com`)
- [ ] Vercel project created
- [ ] Vercel env var set: `VITE_API_URL` (use Render URL)
- [ ] Vercel deployed successfully (check logs)
- [ ] Note Vercel URL (`https://finances-tracker-xxxxx.vercel.app`)
- [ ] Update Render `FRONTEND_URL` to Vercel URL, redeploy
- [ ] Test frontend → API communication
- [ ] Check browser console for errors
- [ ] Check Render/Vercel logs for backend errors

---

## 🆘 Troubleshooting

### Deployment fails on Render
```
Check: Render → Web Service → Logs
Look for: DATABASE_URL, build errors, psycopg import errors
```

### Frontend can't reach backend API
```
Check: Browser DevTools → Network tab
Error: CORS? → Verify FRONTEND_URL in Render
Error: 404? → Verify VITE_API_URL in Vercel doesn't have trailing slash
Error: Connection refused? → Ensure Render service is running
```

### CORS error in browser console
```
Backend: Render → Environment → Verify FRONTEND_URL matches exactly
Frontend: Vercel → Logs → Check if VITE_API_URL is set correctly
```

---

See `ENV_VARIABLES.md` for detailed documentation.
