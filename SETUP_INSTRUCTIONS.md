# Setup Instructions

Read these files in order to configure and deploy Beacon Studio.

---

## 1. CONFIGURATION_GUIDE.md

**Purpose:** Configure all external services before deployment

**What you'll do:**
- Create Google Cloud Platform project
- Enable required APIs
- Create service accounts
- Set up Cloud Storage bucket
- Configure Google OAuth (for user login)
- Configure GitHub OAuth (for user login)
- Set up Stripe products and webhooks (for billing)
- Store all secrets in GCP Secret Manager
- Create local `.env` file for development

**Time Required:** 1-2 hours

**You'll need:**
- Google Cloud account (billing enabled)
- GitHub account
- Stripe account
- Access to DNS settings (if using custom domain)

**Key sections to focus on:**
- **Step 2:** Google OAuth (get Client ID and Secret)
- **Step 3:** GitHub OAuth (get Client ID and Secret)
- **Step 4:** Stripe (create products, get API keys, webhook secret)
- **Step 5:** Store secrets in GCP Secret Manager

---

## 2. QUICK_START.md (Project Root)

**Purpose:** Get local development environment running

**What you'll do:**
- Copy `.env.example` to `.env`
- Fill in secrets from Configuration Guide
- Start Docker Compose
- Test local backend
- Verify OAuth redirects work
- Test admin endpoints

**Time Required:** 30 minutes

**Success criteria:**
- `docker-compose up -d` runs without errors
- `curl http://localhost:8000/health` returns healthy
- OAuth login redirects to Google/GitHub
- Admin endpoints protected (return 401 without secret)

---

## 3. DEPLOY.md

**Purpose:** Deploy infrastructure and application to GCP

**What you'll do:**
- Deploy Terraform infrastructure (Cloud Run, Cloud SQL, etc.)
- Apply database schema
- Build and deploy Docker containers via Cloud Build
- Update OAuth redirect URIs with production URLs
- Configure monitoring and alerts
- Set up Cloud Scheduler for admin jobs
- (Optional) Configure custom domain

**Time Required:** 1-2 hours (including waiting for builds)

**Success criteria:**
- Terraform completes successfully
- Cloud Run service is running
- Health check returns 200
- OAuth login works in production
- Stripe webhooks receive events

---

## 4. PRODUCTION_CHECKLIST.md

**Purpose:** Verify deployment before going live

**What you'll do:**
- Test all critical paths
- Verify OAuth flows (Google + GitHub)
- Test Stripe checkout and webhooks
- Verify file upload/download
- Check admin endpoints
- Confirm monitoring alerts work
- Test rollback procedure

**Time Required:** 1 hour

**Success criteria:**
- All checklist items passing
- No errors in logs for 30 minutes
- Load test passes (optional)

---

## 5. TROUBLESHOOTING_GCP_DEPLOYMENT.md

**Purpose:** Fix common issues

**When to use:**
- OAuth redirect mismatch errors
- Stripe webhook signature failures
- GCS permission denied errors
- Database connection issues
- Admin endpoint errors

**Keep this open** while deploying in case issues arise.

---

## Quick Reference Card

### OAuth Configuration Locations

**Google OAuth Console:**
https://console.cloud.google.com/apis/credentials

**GitHub OAuth Apps:**
https://github.com/settings/developers

**Stripe Dashboard:**
https://dashboard.stripe.com/apikeys

### Common Environment Variables

```bash
# From Configuration Guide Step 2
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>

# From Configuration Guide Step 3
GITHUB_CLIENT_ID=<your-github-client-id>
GITHUB_CLIENT_SECRET=<your-github-client-secret>

# From Configuration Guide Step 4
STRIPE_API_KEY=sk_test_<your-stripe-key>
STRIPE_WEBHOOK_SECRET=whsec_<your-webhook-secret>
STRIPE_PRICE_ID_HASTE_I=price_<your-price-id>
STRIPE_PRICE_ID_HASTE_II=price_<your-price-id>
STRIPE_PRICE_ID_HASTE_III=price_<your-price-id>

# Generated in Configuration Guide Step 5
SECRET_KEY=<generated-hex-32>
ADMIN_SECRET_KEY=<generated-hex-32>

# From Configuration Guide Step 1
GCS_BUCKET_NAME=beacon-prod-files-<your-project-id>
GCS_PROJECT_ID=<your-project-id>
```

### Useful Commands

```bash
# Check local health
curl http://localhost:8000/health

# Check production health
curl https://YOUR-CLOUD-RUN-URL/health

# View logs
gcloud logging tail "resource.type=cloud_run_revision"

# Test OAuth
open http://localhost:8000/api/v1/auth/login/google

# Test admin endpoint
curl -H "X-Admin-Secret: YOUR_SECRET" \
  http://localhost:8000/admin/stats
```

---

## Estimated Timeline

| Phase | Time | Description |
|-------|------|-------------|
| **Configuration** | 1-2 hours | Set up GCP, OAuth, Stripe |
| **Local Setup** | 30 mins | Get Docker Compose running |
| **Infrastructure** | 30 mins | Deploy Terraform |
| **Application** | 1 hour | Build and deploy to Cloud Run |
| **Verification** | 1 hour | Test all functionality |
| **Total** | **4-5 hours** | Complete setup |

---

## Support

- **Documentation Issues:** Create GitHub issue
- **Deployment Help:** Check TROUBLESHOOTING_GCP_DEPLOYMENT.md
- **Configuration Questions:** Review CONFIGURATION_GUIDE.md

---

**Ready to start?**

👉 Open `docs/CONFIGURATION_GUIDE.md` and begin with Step 1!

