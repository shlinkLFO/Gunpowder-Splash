# Documentation

Essential documentation for Beacon Studio deployment to Google Cloud Platform.

## Quick Start

**New to the project?** → Read root `/QUICK_START.md` first

## Documentation Files

1. **[CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)** - Set up GCP, OAuth (Google/GitHub), and Stripe
2. **[DEPLOY.md](DEPLOY.md)** - Deploy infrastructure and application to GCP
3. **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)** - Pre-deployment verification steps
4. **[TROUBLESHOOTING_GCP_DEPLOYMENT.md](TROUBLESHOOTING_GCP_DEPLOYMENT.md)** - Common issues and solutions

## Recommended Reading Order

### First Time Setup
1. `/QUICK_START.md` - Get local environment running
2. `CONFIGURATION_GUIDE.md` - Configure all external services
3. Test locally with `docker-compose up`
4. `DEPLOY.md` - Deploy to production
5. `PRODUCTION_CHECKLIST.md` - Verify deployment

### Troubleshooting
- Having issues? → `TROUBLESHOOTING_GCP_DEPLOYMENT.md`
- Need to rollback? → See "Updates & Rollbacks" in `DEPLOY.md`

## What's Been Fixed

All critical issues have been resolved:
- ✅ Dockerfile requirements file reference
- ✅ Admin endpoints now protected
- ✅ GCS credentials configured for Cloud Run
- ✅ Storage service has fallback to default credentials

## Archived Documentation

Historical docs moved to `archive/` directory.

