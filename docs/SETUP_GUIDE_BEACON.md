# Beacon Studio Setup Guide

Complete guide for deploying Beacon Studio from Gunpowder Splash codebase.

---

## Prerequisites

### Required Accounts & Services

1. **Google Cloud Platform (GCP)**
   - Create project: `beacon-studio-prod`
   - Enable billing
   - Enable APIs:
     - Cloud Run API
     - Cloud SQL Admin API
     - Cloud Storage API
     - Cloud Scheduler API
     - Secret Manager API
     - Container Registry API

2. **Stripe**
   - Create account: https://stripe.com
   - Get API keys (test and production)
   - Create products and prices for Haste I/II/III plans

3. **OAuth Providers**
   - **Google Cloud Console**: Create OAuth 2.0 Client
   - **GitHub**: Create OAuth App

4. **AI Providers (Optional)**
   - **Gemini**: Get API key from Google AI Studio
   - **LM Studio/Ollama**: Install locally for development

### Required Software

- Docker Desktop (for local development)
- Google Cloud SDK (gcloud CLI)
- Terraform 1.5+
- Node.js 18+ and Yarn (for Code OSS build)
- Python 3.11+
- PostgreSQL 15+ (for local development)
- Git

---

## Phase 1: Infrastructure Setup

### Step 1: Configure GCP Project

```bash
# Set project
gcloud config set project beacon-studio-prod

# Set default region
gcloud config set compute/region us-central1

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  storage.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com \
  containerregistry.googleapis.com
```

### Step 2: Deploy Infrastructure with Terraform

```bash
cd terraform/

# Initialize Terraform
terraform init

# Review planned changes
terraform plan -var="project_id=beacon-studio-prod"

# Apply infrastructure
terraform apply -var="project_id=beacon-studio-prod"

# Note the outputs:
# - backend_url
# - database_connection_name
# - storage_bucket_name
```

### Step 3: Configure Secrets

```bash
# Create secrets in Secret Manager
gcloud secrets create beacon-secret-key \
  --data-file=<(openssl rand -hex 32)

gcloud secrets create beacon-db-url \
  --data-file=<(echo "postgresql://beacon_app:PASSWORD@/beacon_studio?host=/cloudsql/CONNECTION_NAME")

gcloud secrets create beacon-google-client-id \
  --data-file=<(echo "YOUR_GOOGLE_CLIENT_ID")

gcloud secrets create beacon-google-client-secret \
  --data-file=<(echo "YOUR_GOOGLE_CLIENT_SECRET")

gcloud secrets create beacon-github-client-id \
  --data-file=<(echo "YOUR_GITHUB_CLIENT_ID")

gcloud secrets create beacon-github-client-secret \
  --data-file=<(echo "YOUR_GITHUB_CLIENT_SECRET")

gcloud secrets create beacon-stripe-api-key \
  --data-file=<(echo "sk_live_YOUR_STRIPE_KEY")

gcloud secrets create beacon-stripe-webhook-secret \
  --data-file=<(echo "whsec_YOUR_WEBHOOK_SECRET")

gcloud secrets create beacon-gemini-api-key \
  --data-file=<(echo "YOUR_GEMINI_API_KEY")
```

### Step 4: Initialize Database

```bash
# Connect to Cloud SQL
gcloud sql connect beacon-db-prod --user=beacon_app --database=beacon_studio

# Run schema creation
\i backend/schema.sql

# Verify tables
\dt

# Exit
\q
```

---

## Phase 2: OAuth Configuration

### Google OAuth

1. Go to: https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID
3. Application type: Web application
4. Authorized JavaScript origins:
   - `https://glowstone.red`
5. Authorized redirect URIs:
   - `https://glowstone.red/beacon-studio/auth/callback/google`
6. Copy Client ID and Client Secret to secrets

### GitHub OAuth

1. Go to: https://github.com/settings/developers
2. Create new OAuth App
3. Application name: Beacon Studio
4. Homepage URL: `https://glowstone.red/beacon-studio`
5. Authorization callback URL:
   - `https://glowstone.red/beacon-studio/auth/callback/github`
6. Copy Client ID and Client Secret to secrets

---

## Phase 3: Stripe Configuration

### Create Products and Prices

```bash
# Create Haste I product
stripe products create \
  --name="Haste I" \
  --description="20 GB storage, 5 team members" \
  --metadata[plan_id]=haste_i

# Create price for Haste I
stripe prices create \
  --product=prod_XXXXX \
  --unit-amount=1699 \
  --currency=usd \
  --recurring[interval]=month

# Repeat for Haste II and Haste III
# Note the price IDs for environment configuration
```

### Configure Webhook

1. Go to: https://dashboard.stripe.com/webhooks
2. Add endpoint: `https://glowstone.red/beacon-studio/api/v1/billing/webhook`
3. Listen to events:
   - `checkout.session.completed`
   - `customer.subscription.deleted`
   - `customer.subscription.updated`
4. Copy webhook signing secret to secrets

---

## Phase 4: Backend Deployment

### Build and Deploy Backend

```bash
cd backend/

# Build Docker image
docker build -f Dockerfile.beacon -t gcr.io/beacon-studio-prod/beacon-backend:v1.0.0 .

# Push to Container Registry
docker push gcr.io/beacon-studio-prod/beacon-backend:v1.0.0

# Deploy to Cloud Run (or use Cloud Build)
gcloud run deploy beacon-backend \
  --image gcr.io/beacon-studio-prod/beacon-backend:v1.0.0 \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --service-account beacon-cloud-run@beacon-studio-prod.iam.gserviceaccount.com \
  --set-secrets=SECRET_KEY=beacon-secret-key:latest,DATABASE_URL=beacon-db-url:latest \
  --add-cloudsql-instances INSTANCE_CONNECTION_NAME \
  --vpc-connector beacon-vpc-connector \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 100
```

### Configure Cloud Build (Automated Deployment)

```bash
# Create Cloud Build trigger
gcloud builds triggers create github \
  --repo-name=beacon-studio \
  --repo-owner=YOUR_ORG \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.beacon.yaml
```

### Test Backend

```bash
# Get backend URL
BACKEND_URL=$(gcloud run services describe beacon-backend --region us-central1 --format='value(status.url)')

# Test health endpoint
curl $BACKEND_URL/health

# Test API
curl $BACKEND_URL/api/v1/
```

---

## Phase 5: Code OSS Frontend

### Build Code OSS

```bash
# Clone Code OSS
git clone https://github.com/microsoft/vscode.git beacon-editor
cd beacon-editor

# Checkout stable release
git checkout 1.85.0

# Install dependencies
yarn install

# Apply Beacon Studio branding modifications
# (See CODE_OSS_INTEGRATION.md for detailed instructions)

# Build for web
yarn gulp vscode-web-min
```

### Customize Branding

1. Edit `product.json` with Beacon Studio configuration
2. Replace logos and icons in `resources/web/`
3. Modify telemetry to disable data collection
4. Update welcome page with Beacon branding
5. Add custom file system provider for backend integration

### Deploy Frontend

```bash
# Build production bundle
cd ../vscode-web
npm run build

# Deploy to Cloud Run (static site)
gcloud run deploy beacon-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## Phase 6: Domain Configuration

### Configure DNS

Add DNS records for `glowstone.red`:

```
A     glowstone.red           -> CLOUD_RUN_IP
CNAME beacon-studio           -> BACKEND_SERVICE_URL
```

### Configure SSL

```bash
# Create managed SSL certificate
gcloud compute ssl-certificates create beacon-ssl \
  --domains=glowstone.red,beacon-studio.glowstone.red \
  --global
```

### Configure Load Balancer

1. Create backend services for frontend and backend
2. Configure URL map:
   - `/beacon-studio/api/*` → Backend service
   - `/beacon-studio/editor/*` → Frontend service
3. Attach SSL certificate
4. Configure health checks

---

## Phase 7: Cloud Scheduler Jobs

```bash
# Storage reconciliation job (daily at 3 AM)
gcloud scheduler jobs create http beacon-storage-reconciliation \
  --location=us-central1 \
  --schedule="0 3 * * *" \
  --uri="${BACKEND_URL}/admin/storage-reconciliation" \
  --http-method=POST \
  --oidc-service-account-email=beacon-scheduler@beacon-studio-prod.iam.gserviceaccount.com

# Purge deleted workspaces job (daily at 4 AM)
gcloud scheduler jobs create http beacon-purge-deleted \
  --location=us-central1 \
  --schedule="0 4 * * *" \
  --uri="${BACKEND_URL}/admin/purge-deleted-workspaces" \
  --http-method=POST \
  --oidc-service-account-email=beacon-scheduler@beacon-studio-prod.iam.gserviceaccount.com
```

---

## Phase 8: Monitoring & Logging

### Set Up Cloud Monitoring

```bash
# Create uptime check
gcloud monitoring uptime create beacon-health-check \
  --resource-type=uptime-url \
  --host=glowstone.red \
  --path=/beacon-studio/health

# Create alerting policy
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Beacon Backend Down" \
  --condition-display-name="Health Check Failing" \
  --condition-threshold-value=1 \
  --condition-threshold-duration=300s
```

### Configure Log Sinks

```bash
# Export logs to BigQuery for analysis
gcloud logging sinks create beacon-logs-sink \
  bigquery.googleapis.com/projects/beacon-studio-prod/datasets/beacon_logs \
  --log-filter='resource.type="cloud_run_revision"'
```

---

## Phase 9: Testing

### Functional Testing

1. **User Registration**
   - Sign in with Google
   - Sign in with GitHub
   - Verify default workspace creation

2. **Project Management**
   - Create new project
   - Switch between projects
   - Upload files
   - Edit files in Code OSS

3. **Storage Quotas**
   - Upload files up to limit
   - Verify quota enforcement
   - Check storage reconciliation

4. **Billing**
   - Subscribe to Haste I plan
   - Verify team size increase
   - Verify storage limit increase
   - Test cancellation flow
   - Test 30-day grace period
   - Test workspace export

5. **AI Integration**
   - Test Gemini chat
   - Test code completion
   - Verify usage tracking

### Performance Testing

```bash
# Load test with Artillery
artillery quick --count 100 --num 10 ${BACKEND_URL}/health

# Monitor response times in Cloud Console
```

---

## Phase 10: Go Live

### Pre-Launch Checklist

- [ ] All secrets configured in Secret Manager
- [ ] Database schema deployed and seeded
- [ ] OAuth providers configured and tested
- [ ] Stripe products/prices created and tested
- [ ] Backend deployed and health checks passing
- [ ] Frontend deployed with proper branding
- [ ] DNS and SSL configured
- [ ] Cloud Scheduler jobs created and tested
- [ ] Monitoring and alerting configured
- [ ] Legal pages created (Terms, Privacy Policy)
- [ ] License attributions displayed
- [ ] Documentation complete

### Launch

1. Enable production mode in backend
2. Switch Stripe to live mode
3. Update OAuth redirect URIs to production
4. Announce launch
5. Monitor closely for first 48 hours

---

## Maintenance

### Daily

- Monitor error rates in Cloud Logging
- Check Cloud Scheduler job execution
- Review Stripe webhook logs

### Weekly

- Review storage usage trends
- Check AI usage costs
- Review user feedback

### Monthly

- Database backup verification
- Security updates
- Cost optimization review
- Compliance audit

---

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
gcloud run services logs read beacon-backend --region us-central1

# Common issues:
# - Secret not accessible
# - Database connection failed
# - Invalid environment variable
```

### OAuth Callback Fails

- Verify redirect URI matches exactly (including trailing slash)
- Check OAuth client ID and secret
- Ensure state parameter is being validated

### Storage Quota Not Enforcing

- Check Cloud Storage bucket permissions
- Verify reconciliation job is running
- Check workspace.storage_used_bytes in database

### Stripe Webhook Not Working

- Verify webhook secret matches
- Check webhook endpoint is publicly accessible
- Review webhook event logs in Stripe dashboard

---

## Support

For implementation support:

- **Documentation**: https://glowstone.red/beacon-studio/docs
- **Email**: support@glowstone.red
- **GitHub Issues**: [Your repository]

---

**Good luck with your Beacon Studio deployment!**

