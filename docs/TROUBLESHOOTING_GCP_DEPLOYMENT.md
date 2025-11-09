# Troubleshooting GCP Deployment - Blazerod Branch

**Issue:** Changes not visible after deploying to GCP  
**Date:** November 8, 2025

---

## Understanding the Architecture

The blazerod branch contains **TWO DIFFERENT APPLICATIONS**:

### 1. Original Gunpowder Splash (Legacy)
- **Backend:** `backend/app/main.py`
- **Features:** File operations, notebooks, data analysis
- **No OAuth:** Uses simple authentication

### 2. Beacon Studio (New)
- **Backend:** `backend/app/main_beacon.py`
- **Features:** OAuth, workspaces, projects, billing, AI
- **Has OAuth:** Google & GitHub login

**The OAuth routes are ONLY in Beacon Studio (main_beacon.py)!**

---

## Step 1: Verify Which Backend Is Running

On your GCP instance:

```bash
# Check which containers are running
docker-compose ps

# Check backend logs to see which app started
docker-compose logs backend | grep -i "starting"

# You should see either:
# "Starting Beacon Studio backend..." (main_beacon.py - HAS OAuth)
# OR something else (main.py - NO OAuth)
```

---

## Step 2: Check docker-compose.yml

```bash
# On GCP instance
cat docker-compose.yml | grep -A 5 "backend:"
```

Look for the `command:` line under the backend service. It should be:

```yaml
backend:
  command: uvicorn app.main_beacon:app --host 0.0.0.0 --port 8000 --reload
  # NOT: uvicorn app.main:app
```

If it says `app.main:app`, you're running the wrong backend!

---

## Step 3: Fix docker-compose.yml (If Needed)

If you're running the wrong backend, update docker-compose.yml:

```yaml
services:
  backend:
    build: ./backend
    container_name: gunpowder-backend
    command: uvicorn app.main_beacon:app --host 0.0.0.0 --port 8000 --reload
    # ^^^^^^^^^^^^^^^^^ Make sure it says main_beacon
    ports:
      - "8000:8000"
    environment:
      # ... your environment variables
```

Then restart:

```bash
docker-compose down
docker-compose up -d
docker-compose logs -f backend
```

---

## Step 4: Verify Environment Variables

Beacon Studio requires these environment variables:

```bash
# On GCP, check if these are set
docker-compose exec backend env | grep -E "(GOOGLE|GITHUB|DATABASE|SECRET|STRIPE)"
```

Required variables:
```bash
# Security
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# OAuth - Google
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret
GOOGLE_REDIRECT_URI=https://your-domain.com/api/v1/auth/callback/google

# OAuth - GitHub  
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-secret
GITHUB_REDIRECT_URI=https://your-domain.com/api/v1/auth/callback/github

# Stripe
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_HASTE_I=price_...
STRIPE_PRICE_ID_HASTE_II=price_...
STRIPE_PRICE_ID_HASTE_III=price_...

# Google Cloud Storage
GCS_BUCKET_NAME=your-bucket
GCS_PROJECT_ID=your-project-id
GCS_CREDENTIALS_PATH=/path/to/credentials.json (optional)
```

If any are missing, add them to your `.env` file or docker-compose.yml.

---

## Step 5: Verify OAuth Routes Exist

Test the OAuth endpoints:

```bash
# From your local machine or GCP
curl http://your-gcp-ip:8000/api/v1/auth/login/google

# Should redirect to Google OAuth
# If you get 404, the routes aren't loaded
```

Check the API docs:

```bash
# Open in browser
http://your-gcp-ip:8000/api/v1/docs

# You should see these endpoints:
# /api/v1/auth/login/{provider}
# /api/v1/auth/callback/{provider}
# /api/v1/auth/me
# /api/v1/workspaces
# /api/v1/projects
# /api/v1/billing
```

If you don't see these, you're running the wrong backend.

---

## Step 6: Check Database Setup

Beacon Studio requires PostgreSQL with the schema applied:

```bash
# Check if database exists
docker-compose exec postgres psql -U postgres -l

# Should show a database (e.g., beacon_studio or gunpowder)

# Check if tables exist
docker-compose exec postgres psql -U postgres -d your_db_name -c "\dt"

# Should show tables: user, workspace, project, membership, plan, etc.
```

If tables don't exist, apply the schema:

```bash
# Copy schema to container
docker cp backend/schema.sql gunpowder-backend:/tmp/schema.sql

# Apply it
docker-compose exec postgres psql -U postgres -d your_db_name -f /tmp/schema.sql
```

---

## Step 7: Complete Deployment Checklist

Run through this checklist on your GCP instance:

```bash
# 1. Verify you're on blazerod branch
git branch
# Should show: * blazerod

# 2. Verify latest commit
git log --oneline -1
# Should show: 11b0c84 Fix TypeScript build error in ProjectSwitcher

# 3. Stop everything
docker-compose down

# 4. Clean rebuild
docker-compose build --no-cache

# 5. Start services
docker-compose up -d

# 6. Check backend is running main_beacon
docker-compose logs backend | head -20
# Should see: "Starting Beacon Studio backend..."

# 7. Test OAuth endpoint
curl http://localhost:8000/api/v1/auth/login/google
# Should get redirect or HTML response (not 404)

# 8. Check API docs
curl http://localhost:8000/api/v1/docs
# Should return HTML page

# 9. Monitor logs for errors
docker-compose logs -f backend
```

---

## Common Issues and Solutions

### Issue 1: "Module 'app.main_beacon' not found"

**Cause:** Backend container built with wrong files  
**Solution:**
```bash
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

### Issue 2: OAuth routes return 404

**Cause:** Running wrong backend (main.py instead of main_beacon.py)  
**Solution:** Update docker-compose.yml command to use `app.main_beacon:app`

### Issue 3: "Database connection failed"

**Cause:** DATABASE_URL not set or incorrect  
**Solution:**
```bash
# Check environment
docker-compose exec backend env | grep DATABASE_URL

# Should be: postgresql://user:pass@postgres:5432/dbname
# Note: Use 'postgres' as hostname (docker service name)
```

### Issue 4: "OAuth provider not configured"

**Cause:** Missing GOOGLE_CLIENT_ID or GITHUB_CLIENT_ID  
**Solution:** Add OAuth credentials to .env file

### Issue 5: Frontend shows old version

**Cause:** Frontend not rebuilt  
**Solution:**
```bash
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d
```

---

## Verification Commands

Run these to verify everything is working:

```bash
# 1. Check all services are running
docker-compose ps
# All should show "Up"

# 2. Test backend health
curl http://localhost:8000/health
# Should return: {"status":"healthy","database":"connected"}

# 3. Test OAuth redirect
curl -I http://localhost:8000/api/v1/auth/login/google
# Should return: HTTP/1.1 307 Temporary Redirect

# 4. Check frontend is serving
curl -I http://localhost:5173
# Should return: HTTP/1.1 200 OK

# 5. Check database tables
docker-compose exec postgres psql -U postgres -d your_db_name -c "SELECT COUNT(*) FROM plan;"
# Should return: 4 (the 4 plans: free, haste_i, haste_ii, haste_iii)
```

---

## Quick Reset (Nuclear Option)

If nothing works, start fresh:

```bash
# WARNING: This deletes all data!

# 1. Stop and remove everything
docker-compose down -v

# 2. Remove all containers and images
docker system prune -a -f

# 3. Pull latest code
git fetch origin
git checkout blazerod
git pull origin blazerod

# 4. Rebuild from scratch
docker-compose build --no-cache

# 5. Start services
docker-compose up -d

# 6. Apply database schema
docker cp backend/schema.sql gunpowder-backend:/tmp/schema.sql
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE beacon_studio;"
docker-compose exec postgres psql -U postgres -d beacon_studio -f /tmp/schema.sql

# 7. Verify
curl http://localhost:8000/api/v1/docs
```

---

## What You Should See

After successful deployment:

### Backend API Docs
Visit: `http://your-gcp-ip:8000/api/v1/docs`

You should see these endpoint groups:
- **authentication** - OAuth login, callback, me, refresh, logout
- **workspaces** - List, create, manage workspaces
- **projects** - List, create, manage projects
- **billing** - Stripe checkout, portal, webhooks
- **ai** - Chat, completion, usage

### OAuth Login Flow
1. Visit: `http://your-gcp-ip:8000/api/v1/auth/login/google`
2. Should redirect to Google login
3. After login, redirects back with tokens

### Database
```sql
-- Should have these tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Expected:
-- user, workspace, project, membership, plan
-- ai_usage, oauth_state, audit_log
```

---

## Still Not Working?

If you've tried everything above and it's still not working:

1. **Check the logs:**
   ```bash
   docker-compose logs backend > backend.log
   docker-compose logs frontend > frontend.log
   docker-compose logs postgres > postgres.log
   ```

2. **Verify git status:**
   ```bash
   git status
   git log --oneline -5
   git diff main..blazerod --stat
   ```

3. **Check file structure:**
   ```bash
   ls -la backend/app/
   # Should show: main_beacon.py, auth.py, oauth.py, etc.
   ```

4. **Test locally first:**
   - If it works locally but not on GCP, it's an environment issue
   - If it doesn't work locally, there's a code issue

---

## Contact Information

If you need help:
- Check: `docs/ARCHITECTURE_AUDIT_2025-11-08.md`
- Check: `docs/FIXES_IMPLEMENTED_2025-11-08.md`
- Review: `docs/DEPLOYMENT_INSTRUCTIONS_BLAZEROD.md`

---

**Last Updated:** November 8, 2025  
**Branch:** blazerod  
**Commit:** 11b0c84

