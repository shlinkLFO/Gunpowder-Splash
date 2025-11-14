# Setup Next Steps

## What Was Completed

All code changes for OAuth logging and UI improvements are complete:

- Backend has comprehensive logging throughout OAuth flow
- New diagnostics endpoint to check OAuth configuration
- Frontend has login button that becomes profile picture after login
- Account settings accessible via profile menu
- Complete documentation for troubleshooting

## What You Need to Do

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

This installs `react-icons` which is needed for the new UserMenu component.

### 2. Configure OAuth Applications

#### Google OAuth
1. Go to https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID (Web application type)
3. Add authorized redirect URI:
   - Dev: `http://localhost:8000/api/v1/auth/callback/google`
   - Prod: `https://your-domain.com/api/v1/auth/callback/google`
4. Copy the Client ID and Client Secret

#### GitHub OAuth
1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in:
   - Application name: `Gunpowder Splash (Dev)`
   - Homepage URL: `http://localhost:5173`
   - Authorization callback URL: `http://localhost:8000/api/v1/auth/callback/github`
4. Copy the Client ID and Client Secret

### 3. Update Your .env File

Add these to your `backend/.env` file:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback/google

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id-here
GITHUB_CLIENT_SECRET=your-github-secret-here
GITHUB_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback/github

# Admin Secret (for diagnostics - generate with: openssl rand -hex 32)
ADMIN_SECRET_KEY=generate_a_random_string_here
```

### 4. Restart Backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Watch for these logs on startup:
```
=== OAuth Configuration Status ===
Google Client ID configured: True
Google Client Secret configured: True
Google Redirect URI: http://localhost:8000/api/v1/auth/callback/google
GitHub Client ID configured: True
GitHub Client Secret configured: True
GitHub Redirect URI: http://localhost:8000/api/v1/auth/callback/github
```

### 5. Start Frontend

```bash
cd frontend
npm run dev
```

### 6. Test OAuth Login

1. Open http://localhost:5173
2. Click "Log In" button in top-right corner
3. Choose Google or GitHub
4. Watch backend console for detailed logs:
   - Starting OAuth login flow
   - Redirecting to OAuth provider
   - Callback received
   - Token exchange status
   - User info retrieval
   - JWT tokens generated
5. After successful login, you should see your profile picture in top-right
6. Click profile picture to access account settings

### 7. Verify Configuration (Optional)

Check your OAuth configuration without exposing secrets:

```bash
curl -H "X-Admin-Secret: your-admin-secret-key" \
  http://localhost:8000/api/v1/diagnostics/oauth-config | jq
```

Expected output:
```json
{
  "google": {
    "client_id_configured": true,
    "client_id_prefix": "123456789-abc123",
    "client_secret_configured": true,
    "client_secret_length": 24,
    "redirect_uri": "http://localhost:8000/api/v1/auth/callback/google"
  },
  "github": {
    "client_id_configured": true,
    "client_id_prefix": "Iv1.1234567890abcd",
    "client_secret_configured": true,
    "client_secret_length": 40,
    "redirect_uri": "http://localhost:8000/api/v1/auth/callback/github"
  },
  "environment": "development"
}
```

## Troubleshooting

If OAuth login fails:

1. **Check Backend Logs** - Look for detailed error messages
2. **Review Redirect URIs** - Must match exactly in .env and OAuth provider
3. **Verify Credentials** - Run diagnostics endpoint
4. **Check Browser Console** - Look for JavaScript errors
5. **Read Full Guide** - See `docs/OAUTH_TROUBLESHOOTING.md`

### Common Issues

**"Invalid redirect_uri"**
- Redirect URI in .env must exactly match OAuth provider settings
- Include http:// or https://
- Include port number if not standard

**"MISSING: Client ID is not configured"**
- Check .env file is in backend directory
- Verify variable names are correct (case-sensitive)
- Restart backend after updating .env

**Login button doesn't appear**
- Run `npm install` in frontend directory
- Check browser console for errors
- Clear browser cache

## Documentation

- **Quick Start:** `docs/OAUTH_QUICK_START.md`
- **Full Troubleshooting:** `docs/OAUTH_TROUBLESHOOTING.md`
- **All Changes:** `OAUTH_IMPROVEMENTS_SUMMARY.md`

## Summary of New Features

### For Debugging
- Detailed logs at every OAuth step
- HTTP status codes visible
- Error messages with context
- Configuration validation on startup
- Diagnostics endpoint

### For Users
- Login button in top-right corner
- Profile picture after authentication
- Account settings modal
- Clean OAuth provider selection
- Guest mode integration

## Need Help?

1. Check the troubleshooting guide: `docs/OAUTH_TROUBLESHOOTING.md`
2. Review backend logs for specific errors
3. Use diagnostics endpoint to verify configuration
4. Ensure all environment variables are set correctly

## Production Deployment

When deploying to production:

1. Update redirect URIs in .env to use production domain
2. Update OAuth apps with production URLs
3. Set `ENVIRONMENT=production`
4. Use HTTPS (required for OAuth)
5. Generate strong random secrets
6. Test thoroughly before going live

---

**Ready to test?** Follow steps 1-6 above and watch the detailed logs to see exactly what's happening at each step of the OAuth flow!

