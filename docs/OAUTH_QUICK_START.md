# OAuth Quick Start Guide

Get OAuth authentication working in 5 minutes.

## Prerequisites

- Backend running on port 8000
- Frontend running on port 5173 (or your configured port)
- Database connected and migrations applied

## Step 1: Configure OAuth Providers

### Google OAuth

1. Visit [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create project or select existing
3. Create OAuth 2.0 Client ID (Web application)
4. Add authorized redirect URIs:
   - **Development:** `http://localhost:8000/api/v1/auth/callback/google`
   - **Production:** `https://shlinx.com/api/v1/auth/callback/google`
5. Copy Client ID and Client Secret

### GitHub OAuth

1. Visit [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in:
   - **Development:**
     - Application name: `Gunpowder Splash (Dev)`
     - Homepage URL: `http://localhost:5173`
     - Authorization callback URL: `http://localhost:8000/api/v1/auth/callback/github`
   - **Production:**
     - Application name: `Gunpowder Splash`
     - Homepage URL: `https://shlinx.com`
     - Authorization callback URL: `https://shlinx.com/api/v1/auth/callback/github`
4. Copy Client ID and Client Secret

**Note:** You can add multiple redirect URIs to Google OAuth, but GitHub requires separate OAuth apps for dev and production.

## Step 2: Update Environment Variables

Edit your `.env` file in the backend directory:

**For Development:**
```bash
# Google OAuth
GOOGLE_CLIENT_ID=123456789-abc123.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdef123456
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback/google

# GitHub OAuth (use dev app credentials)
GITHUB_CLIENT_ID=Iv1.1234567890abcdef
GITHUB_CLIENT_SECRET=1234567890abcdef1234567890abcdef12345678
GITHUB_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback/github

# Admin Secret (generate with: openssl rand -hex 32)
ADMIN_SECRET_KEY=your_random_secret_here
```

**For Production (shlinx.com):**
```bash
# Google OAuth (same client ID, different redirect URI)
GOOGLE_CLIENT_ID=123456789-abc123.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdef123456
GOOGLE_REDIRECT_URI=https://shlinx.com/api/v1/auth/callback/google

# GitHub OAuth (use production app credentials)
GITHUB_CLIENT_ID=Iv1.production-client-id
GITHUB_CLIENT_SECRET=production-secret-here
GITHUB_REDIRECT_URI=https://shlinx.com/api/v1/auth/callback/github

# Admin Secret (use different secret for production)
ADMIN_SECRET_KEY=production_random_secret_here

# Environment
ENVIRONMENT=production
```

## Step 3: Restart Backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Watch for configuration logs:
```
=== OAuth Configuration Status ===
Google Client ID configured: True
GitHub Client ID configured: True
```

## Step 4: Test Login

1. Open frontend: `http://localhost:5173`
2. Click the "Log In" button in the top right
3. Choose Google or GitHub
4. Watch the backend console for detailed logs
5. After authentication, you should see your profile picture

## Verify Setup

Check configuration without secrets:

```bash
curl -H "X-Admin-Secret: your_random_secret_here" \
  http://localhost:8000/api/v1/diagnostics/oauth-config
```

Expected response:
```json
{
  "google": {
    "client_id_configured": true,
    "client_secret_configured": true,
    "redirect_uri": "http://localhost:8000/api/v1/auth/callback/google"
  },
  "github": {
    "client_id_configured": true,
    "client_secret_configured": true,
    "redirect_uri": "http://localhost:8000/api/v1/auth/callback/github"
  }
}
```

## New UI Features

### Login Button
- Located in top-right corner
- Click to open login modal
- Choose Google or GitHub

### User Profile Menu
After login, click your profile picture to:
- View account information
- Access account settings
- Log out

### Guest Mode
- Original "Continue as Guest" still available
- Guest users see option to log in from profile menu
- Logging in preserves guest work

## Viewing Detailed Logs

The system now provides comprehensive logging:

### Backend Console
Watch for:
- `=== Starting OAuth login flow ===`
- `=== Exchanging Code for Token ===`
- `=== Fetching User Info ===`
- All HTTP status codes
- Error messages with details

### Browser DevTools
Open Console (F12) to see:
- Token handling
- API responses
- Authentication status
- JavaScript errors

## Common Issues

### "Invalid redirect_uri"
- Verify `.env` redirect URIs match OAuth provider settings exactly
- Include `http://` or `https://`
- Include port number if not standard

### "Client ID not configured"
- Check `.env` file exists in backend directory
- Verify variable names are correct (case-sensitive)
- Restart backend after changes

### "No verified email" (GitHub)
- GitHub account must have at least one verified email
- Check GitHub Settings > Emails

### Login button doesn't appear
- Check frontend console for errors
- Verify UserMenu component is imported in App.tsx
- Ensure Chakra UI is properly configured

## Production Setup (shlinx.com)

For production deployment to shlinx.com:

1. **Google OAuth:**
   - Use same OAuth client
   - Add production redirect URI: `https://shlinx.com/api/v1/auth/callback/google`
   - Update `.env`: `GOOGLE_REDIRECT_URI=https://shlinx.com/api/v1/auth/callback/google`

2. **GitHub OAuth:**
   - Create NEW OAuth app for production
   - Homepage: `https://shlinx.com`
   - Callback: `https://shlinx.com/api/v1/auth/callback/github`
   - Use production app credentials in `.env`

3. **Environment Settings:**
   ```bash
   ENVIRONMENT=production
   ADMIN_SECRET_KEY=$(openssl rand -hex 32)
   ```

4. **Requirements:**
   - HTTPS enabled (required for OAuth)
   - SSL certificate valid
   - API accessible at `/api/v1/*` path

5. **Verify:**
   - Test OAuth flow on production
   - Check backend logs for any redirect URI mismatches
   - Run diagnostics endpoint to confirm configuration

## Need Help?

- Full troubleshooting guide: [OAUTH_TROUBLESHOOTING.md](./OAUTH_TROUBLESHOOTING.md)
- Check backend logs for detailed error messages
- Verify all environment variables are set
- Ensure database is accessible
- Test with diagnostics endpoint

