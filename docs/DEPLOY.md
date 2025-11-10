# Deployment Guide

Quick deployment guide for Beacon Studio on Google Cloud Platform.

---

## Critical Fixes Applied ✅

The following issues have been resolved:

1. ✅ **Dockerfile.beacon** - Fixed requirements file reference
2. ✅ **Admin endpoints** - Protected with admin secret authentication
3. ✅ **GCS credentials** - Configured fallback to Cloud Run service account

---

## Prerequisites

Before deploying, complete:
- [ ] **Configuration**: Follow [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)
- [ ] **Secrets**: All secrets stored in GCP Secret Manager
- [ ] **Local testing**: Docker Compose runs successfully

---

## Deploy to Production

### Step 1: Deploy Infrastructure

```bash
cd terraform

# Initialize (first time only)
terraform init

# Review changes
terraform plan -var="project_id=YOUR_PROJECT_ID"

# Apply
terraform apply -var="project_id=YOUR_PROJECT_ID"

# Save outputs
terraform output > ../terraform-outputs.txt
```

**Outputs you'll need:**
- `backend_url` - Cloud Run service URL
- `database_connection_name` - Cloud SQL instance name
- `storage_bucket_name` - GCS bucket name

### Step 2: Apply Database Schema

```bash
# Connect to Cloud SQL
gcloud sql connect beacon-db-prod --user=postgres

# In the PostgreSQL prompt:
\i backend/schema.sql
\q
```

Or use Cloud SQL Proxy:

```bash
# Start proxy
cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE=tcp:5432 &

# Apply schema
psql "host=127.0.0.1 port=5432 dbname=beacon_studio user=postgres" \
  -f backend/schema.sql
```

### Step 3: Build and Deploy Application

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Submit build
gcloud builds submit \
  --config cloudbuild.beacon.yaml \
  --substitutions=COMMIT_SHA=$(git rev-parse --short HEAD)

# Wait for deployment (5-10 minutes)
```

### Step 4: Update OAuth Redirect URIs

After deployment, get your Cloud Run URL:

```bash
gcloud run services describe beacon-backend \
  --region us-central1 \
  --format="value(status.url)"
```

Update redirect URIs in:

**Google OAuth Console:**
```
https://YOUR-CLOUD-RUN-URL/api/v1/auth/callback/google
```

**GitHub OAuth App:**
```
https://YOUR-CLOUD-RUN-URL/api/v1/auth/callback/github
```

**Stripe Webhook:**
```
https://YOUR-CLOUD-RUN-URL/api/v1/billing/webhook
```

### Step 5: Verify Deployment

```bash
# Check health
curl https://YOUR-CLOUD-RUN-URL/health

# Expected response:
# {"status":"healthy","database":"connected","environment":"production"}

# Check API docs
open https://YOUR-CLOUD-RUN-URL/api/v1/docs

# Test OAuth (should redirect to Google)
open https://YOUR-CLOUD-RUN-URL/api/v1/auth/login/google
```

### Step 6: Test Critical Paths

```bash
# Get admin secret from Secret Manager
ADMIN_SECRET=$(gcloud secrets versions access latest --secret=beacon-admin-secret-key)

# Test admin endpoint
curl https://YOUR-CLOUD-RUN-URL/admin/stats \
  -H "X-Admin-Secret: $ADMIN_SECRET"

# Should return system stats, not 401/403
```

---

## Post-Deployment Setup

### Configure Monitoring

```bash
# Create uptime check
gcloud monitoring uptime-checks create https beacon-health \
  --resource-type=uptime-url \
  --host=YOUR-CLOUD-RUN-URL \
  --path=/health \
  --check-interval=60s
```

### Set Up Alerts

1. Go to Cloud Console → Monitoring → Alerting
2. Create alerts for:
   - Error rate > 1%
   - Latency p95 > 3s
   - Uptime check failures

### Configure Budget Alerts

1. Go to Cloud Console → Billing → Budgets
2. Create budget: $500/month
3. Set alerts at 50%, 90%, 100%

### Schedule Admin Jobs

Update Cloud Scheduler jobs with your Cloud Run URL:

```bash
# Storage reconciliation (daily at 3 AM)
gcloud scheduler jobs create http beacon-storage-reconciliation \
  --schedule="0 3 * * *" \
  --uri="https://YOUR-CLOUD-RUN-URL/admin/storage-reconciliation" \
  --http-method=POST \
  --headers="X-Admin-Secret=$ADMIN_SECRET" \
  --location=us-central1

# Purge deleted workspaces (daily at 4 AM)
gcloud scheduler jobs create http beacon-purge-deleted \
  --schedule="0 4 * * *" \
  --uri="https://YOUR-CLOUD-RUN-URL/admin/purge-deleted-workspaces" \
  --http-method=POST \
  --headers="X-Admin-Secret=$ADMIN_SECRET" \
  --location=us-central1

# OAuth cleanup (hourly)
gcloud scheduler jobs create http beacon-oauth-cleanup \
  --schedule="0 * * * *" \
  --uri="https://YOUR-CLOUD-RUN-URL/admin/cleanup-expired-oauth-states" \
  --http-method=POST \
  --headers="X-Admin-Secret=$ADMIN_SECRET" \
  --location=us-central1
```

---

## Updates & Rollbacks

### Deploy Updates

```bash
# Pull latest code
git pull origin blazerod

# Deploy
gcloud builds submit --config cloudbuild.beacon.yaml
```

### Rollback to Previous Version

```bash
# List revisions
gcloud run revisions list \
  --service=beacon-backend \
  --region=us-central1

# Route traffic to previous revision
gcloud run services update-traffic beacon-backend \
  --region=us-central1 \
  --to-revisions=REVISION_NAME=100
```

### View Logs

```bash
# Tail logs
gcloud logging tail "resource.type=cloud_run_revision" \
  --format="table(timestamp,severity,textPayload)"

# Search for errors
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit=50 \
  --format=json
```

---

## Custom Domain Setup (Optional)

### Map Domain

```bash
# Add domain mapping
gcloud run domain-mappings create \
  --service=beacon-backend \
  --domain=shlinx.com \
  --region=us-central1

# Get DNS records to configure
gcloud run domain-mappings describe \
  --domain=shlinx.com \
  --region=us-central1
```

### Update DNS

Add the provided DNS records to your domain registrar:
- A record: points to Cloud Run IP
- AAAA record: points to Cloud Run IPv6

### Update OAuth Providers

After DNS propagates, update redirect URIs to use custom domain:
```
https://shlinx.com/api/v1/auth/callback/google
https://shlinx.com/api/v1/auth/callback/github
https://shlinx.com/api/v1/billing/webhook
```

---

## Monitoring Checklist

First 24 hours after deployment:

- [ ] Health check returns 200
- [ ] No errors in logs
- [ ] OAuth login works (Google + GitHub)
- [ ] Stripe checkout creates subscription
- [ ] Stripe webhooks process successfully
- [ ] File upload/download works
- [ ] Admin scheduled jobs run successfully
- [ ] Database backup created
- [ ] Monitoring alerts configured
- [ ] Budget alerts configured

---

## Performance Tuning

### If experiencing high latency:

```bash
# Increase memory
gcloud run services update beacon-backend \
  --region=us-central1 \
  --memory=4Gi

# Increase CPU
gcloud run services update beacon-backend \
  --region=us-central1 \
  --cpu=4
```

### If costs are too high:

```bash
# Reduce max instances
gcloud run services update beacon-backend \
  --region=us-central1 \
  --max-instances=5

# Set min instances to 0 (cold starts)
gcloud run services update beacon-backend \
  --region=us-central1 \
  --min-instances=0
```

---

## Cost Monitoring

Check current costs:

```bash
# This month's costs
gcloud billing accounts list
gcloud billing projects list --billing-account=BILLING_ACCOUNT_ID

# Detailed breakdown
# Go to: https://console.cloud.google.com/billing
```

**Expected monthly costs:**
- Cloud Run: $50-200
- Cloud SQL: $180
- Cloud Storage: $30
- Networking: $20
- **Total: $280-430/month**

---

## Emergency Procedures

### Service Down

```bash
# Check service status
gcloud run services describe beacon-backend \
  --region=us-central1 \
  --format="value(status.conditions)"

# Check recent logs
gcloud logging tail "resource.type=cloud_run_revision" --limit=100

# Restart by deploying same revision
gcloud run services update backend-backend \
  --region=us-central1 \
  --no-traffic
```

### Database Issues

```bash
# Check database status
gcloud sql instances describe beacon-db-prod

# Check connections
gcloud sql operations list --instance=beacon-db-prod

# If needed, restart
gcloud sql instances restart beacon-db-prod
```

### Storage Issues

```bash
# Check bucket
gsutil ls -L gs://beacon-prod-files-PROJECT_ID

# Check permissions
gsutil iam get gs://beacon-prod-files-PROJECT_ID
```

---

## Security Maintenance

### Rotate Secrets (Every 90 Days)

```bash
# Generate new secret
NEW_SECRET=$(openssl rand -hex 32)

# Update in Secret Manager
echo -n "$NEW_SECRET" | gcloud secrets versions add beacon-secret-key --data-file=-

# Redeploy to pick up new secret
gcloud run services update beacon-backend \
  --region=us-central1 \
  --update-secrets=SECRET_KEY=beacon-secret-key:latest
```

### Review Access Logs

```bash
# Check who accessed admin endpoints
gcloud logging read 'resource.type="cloud_run_revision" AND httpRequest.path=~"/admin/"' \
  --limit=100 \
  --format="table(timestamp,httpRequest.remoteIp,httpRequest.path,httpRequest.status)"
```

---

## Next Steps

After successful deployment:

1. **Load testing**: Test with 50+ concurrent users
2. **Backup verification**: Restore database from backup
3. **Disaster recovery drill**: Practice failover procedure
4. **Documentation**: Update runbook with production URLs
5. **Team access**: Grant necessary team members access to GCP project

See [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) for complete verification steps.

---

**Deployment Guide Version:** 1.0  
**Last Updated:** November 10, 2025

