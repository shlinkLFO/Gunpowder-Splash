# Production Deployment Checklist

## Pre-Deployment

### Critical Fixes Required
- [ ] Fix `backend/Dockerfile.beacon` line 16: Change `requirements_beacon.txt` to `requirements.txt`
- [ ] Add `Depends(verify_admin_secret)` to all `/admin/*` endpoints
- [ ] Update `storage.py` to fallback to default GCS credentials
- [ ] Configure Cloud SQL Connector (remove password from DATABASE_URL)

### Configuration
- [ ] Set `ENVIRONMENT=production` in Cloud Run
- [ ] Configure production CORS: `["https://glowstone.red"]`
- [ ] Set Cloud Run limits: max-instances=10, concurrency=80
- [ ] Generate and store `ADMIN_SECRET_KEY`

### Security
- [ ] All secrets in Google Secret Manager (not environment variables)
- [ ] Admin endpoints protected
- [ ] Stripe webhook signature verification enabled
- [ ] Rate limiting configured (Cloud Armor)
- [ ] HTTPS only (no HTTP)

### Monitoring
- [ ] Cloud Monitoring alerts configured
- [ ] Error rate alert (>1% errors)
- [ ] High latency alert (>3s p95)
- [ ] Uptime check configured
- [ ] Log-based metrics for critical operations

### Database
- [ ] Schema applied to production database
- [ ] Backup enabled (point-in-time recovery)
- [ ] Backup restore tested successfully
- [ ] Connection pool sized appropriately
- [ ] Weekly export to Cloud Storage configured

### Testing
- [ ] Local docker-compose works
- [ ] Health endpoint returns 200
- [ ] OAuth login flow works (Google + GitHub)
- [ ] Stripe checkout creates subscription
- [ ] Stripe webhooks process correctly
- [ ] File upload/download works
- [ ] Admin endpoints require authentication
- [ ] Load test completed (50+ concurrent users)

## Deployment

### Infrastructure
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Secrets
```bash
./scripts/setup-secrets.sh
# Or manually create each secret in Secret Manager
```

### Application
```bash
gcloud builds submit --config cloudbuild.beacon.yaml
```

### Database
```bash
gcloud sql connect beacon-db-prod --user=postgres < backend/schema.sql
```

## Post-Deployment

### Verification
- [ ] `curl https://YOUR-URL/health` returns healthy
- [ ] API docs accessible: `https://YOUR-URL/api/v1/docs`
- [ ] OAuth login redirects correctly
- [ ] Logs appearing in Cloud Logging
- [ ] Metrics appearing in Cloud Monitoring
- [ ] No errors in logs for 30 minutes

### Monitoring (First 24 Hours)
- [ ] Check error rate every hour
- [ ] Monitor database connection pool
- [ ] Verify Stripe webhooks delivering
- [ ] Check storage operations
- [ ] Review Cloud Run scaling behavior

### Documentation
- [ ] Update production URL in OAuth providers
- [ ] Update Stripe webhook URL
- [ ] Document rollback procedure
- [ ] Record deployment timestamp and version

## Rollback Plan

If issues occur:

```bash
# 1. Identify previous working revision
gcloud run revisions list --service=beacon-backend

# 2. Route 100% traffic to previous revision
gcloud run services update-traffic beacon-backend \
  --to-revisions=REVISION_NAME=100

# 3. Investigate issues
gcloud logging read "resource.type=cloud_run_revision" --limit=100

# 4. Fix and redeploy when ready
```

## Emergency Contacts

- **Cloud Console:** https://console.cloud.google.com
- **Status Page:** Add status page URL
- **On-Call:** Add contact info

