# OAuth Troubleshooting Guide

This guide helps you diagnose and fix OAuth authentication issues with Google and GitHub.

## Quick Setup Checklist

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID (Web application)
3. Add authorized redirect URIs (you can add both to the same OAuth client):
   - Development: `http://localhost:8000/api/v1/auth/callback/google`
   - Production: `https://shlinx.com/api/v1/auth/callback/google`
4. Copy Client ID and Client Secret to your `.env` file

### GitHub OAuth Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Create separate OAuth Apps for dev and production (GitHub only allows one callback URL per app)
3. Set Authorization callback URLs:
   - Development app: `http://localhost:8000/api/v1/auth/callback/github`
   - Production app: `https://shlinx.com/api/v1/auth/callback/github`
4. Copy Client ID and Client Secret to your `.env` file (use appropriate app for each environment)

## Environment Variables

Ensure these are set in your `.env` file:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback/google

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback/github

# Admin Secret (for diagnostics endpoint)
ADMIN_SECRET_KEY=your-secure-random-string
```

## Viewing Detailed Logs

The application now includes comprehensive logging for OAuth flows. To view logs:

### Backend Logs

When running the backend, you'll see detailed logs like:

```
=== OAuth Configuration Status ===
Google Client ID configured: True
Google Redirect URI: http://localhost:8000/api/v1/auth/callback/google
GitHub Client ID configured: True
...

=== Starting OAuth login flow for provider: google ===
Generated state token: Ab3D5fG7...
State token stored in database
Redirecting to OAuth provider: https://accounts.google.com...

=== Google OAuth: Exchanging Code for Token ===
Authorization code: 4/0AY0e-g5...
Token exchange response status: 200
Successfully obtained access token (length: 139)

=== Google OAuth: Fetching User Info ===
User info response status: 200
Successfully retrieved user info for: user@example.com
```

### Frontend Logs

Open browser DevTools Console to see:
- OAuth callback handling
- Token storage
- User authentication status
- API errors

## Diagnostic Endpoints

### 1. OAuth Configuration Check

Protected endpoint to verify OAuth settings without exposing secrets:

```bash
curl -H "X-Admin-Secret: your-admin-secret-key" \
  http://localhost:8000/api/v1/diagnostics/oauth-config
```

Response shows:
- Which credentials are configured
- Redirect URIs being used
- Environment settings
- Configuration prefix (first 20 chars of client ID)

### 2. Health Check

Public endpoint to verify service is running:

```bash
curl http://localhost:8000/api/v1/diagnostics/health
```

## Common Issues and Solutions

### Issue 1: "Invalid redirect_uri"

**Symptoms:**
- OAuth provider returns error about redirect URI mismatch
- Log shows: `Token exchange failed: redirect_uri_mismatch`

**Solution:**
- Check `GOOGLE_REDIRECT_URI` or `GITHUB_REDIRECT_URI` in `.env`
- Ensure it EXACTLY matches what's configured in OAuth provider console
- Include protocol (`http://` or `https://`)
- Include port if not standard (`:8000`, `:3000`)
- No trailing slash

### Issue 2: "Missing: Client ID is not configured"

**Symptoms:**
- Backend logs show: `MISSING: Google Client ID is not configured`
- 500 error when trying to log in

**Solution:**
- Verify `.env` file exists and is in the correct location
- Check variable names match exactly (case-sensitive)
- Restart backend after updating `.env`
- Run diagnostics endpoint to verify configuration

### Issue 3: "Token exchange timed out"

**Symptoms:**
- Log shows: `Token exchange timed out after 10 seconds`
- 504 Gateway Timeout error

**Solution:**
- Check internet connectivity
- Verify OAuth provider services are online
- Check firewall/proxy settings
- Verify client secret is correct

### Issue 4: "No verified email found in GitHub account"

**Symptoms:**
- GitHub login fails at user info stage
- Log shows: `No verified email found in GitHub account`

**Solution:**
- User must have at least one verified email in GitHub settings
- Go to GitHub Settings > Emails
- Add email and verify it
- Ensure "Keep my email addresses private" doesn't hide all emails

### Issue 5: "Invalid or expired state token"

**Symptoms:**
- OAuth callback fails with state token error
- Log shows: `State token not found in database`

**Solution:**
- Database connection issue - check `DATABASE_URL`
- State tokens expire after 10 minutes - restart flow
- Check system time is synchronized
- Verify database migrations are up to date

### Issue 6: Frontend doesn't redirect after login

**Symptoms:**
- OAuth completes but user stays on callback URL
- Tokens visible in URL but not stored

**Solution:**
- Check `VITE_API_BASE_URL` in frontend `.env`
- Verify frontend is correctly handling URL parameters
- Check browser console for JavaScript errors
- Ensure localStorage is not blocked/disabled

## Testing OAuth Flow

### Step-by-Step Testing

1. **Start Backend with Logging**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```
   Watch console for OAuth configuration logs

2. **Check Configuration**
   ```bash
   curl -H "X-Admin-Secret: your-secret" \
     http://localhost:8000/api/v1/diagnostics/oauth-config | jq
   ```

3. **Test Login Flow**
   - Open browser to frontend
   - Click "Log in with Google" or "Log in with GitHub"
   - Watch backend logs for each step
   - Watch browser DevTools Network tab
   - Watch browser DevTools Console

4. **Verify Callback**
   - After OAuth provider approval, check backend logs
   - Should see: code exchange, token retrieval, user creation
   - Frontend should redirect with tokens in URL
   - Tokens should be stored in localStorage

### Manual API Testing

Test the OAuth endpoints directly:

```bash
# 1. Initiate login (will redirect to provider)
curl -v http://localhost:8000/api/v1/auth/login/google

# 2. After provider approval, you'll be redirected to:
# http://localhost:8000/api/v1/auth/callback/google?code=...&state=...

# 3. Test the /me endpoint with obtained token
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/v1/auth/me
```

## Log Analysis Tips

### What to Look For

**Successful Flow:**
```
Starting OAuth login flow -> 
Generated state token -> 
Redirecting to OAuth provider -> 
OAuth callback received -> 
State token found -> 
Exchanging code for access token -> 
Token exchange response status: 200 -> 
Fetching user info from provider -> 
User info response status: 200 -> 
User created/updated -> 
JWT tokens generated -> 
Redirecting to frontend
```

**Failed Flow - Look For:**
- HTTP status codes other than 200
- "MISSING:" in configuration logs
- Timeout errors
- State token issues
- Empty response fields

### Enable Detailed HTTP Logging

Add to your backend main.py for even more detail:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Getting Help

When reporting OAuth issues, include:

1. **Logs**: Copy relevant backend logs
2. **Configuration**: Run diagnostics endpoint (redact secrets)
3. **Environment**: Development or production, OS, Python version
4. **Browser**: Which browser, DevTools console errors
5. **Provider**: Google or GitHub
6. **Error Message**: Exact error from UI and logs

## Security Notes

- Never commit `.env` files to version control
- Rotate secrets if accidentally exposed
- Use HTTPS in production
- Different OAuth apps for dev/staging/prod
- Keep client secrets secure
- Admin secret should be strong and random
- Regularly review authorized OAuth applications

