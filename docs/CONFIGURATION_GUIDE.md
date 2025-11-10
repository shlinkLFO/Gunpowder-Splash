# Configuration Guide

Step-by-step guide to configure Beacon Studio for Google Cloud Platform deployment.

---

## Prerequisites

- Google Cloud account with billing enabled
- GitHub account (for OAuth)
- Google account (for OAuth)
- Stripe account (for payments)

---

## Step 1: Google Cloud Platform Setup

### 1.1 Create GCP Project

```bash
# Set your project ID
PROJECT_ID="beacon-studio-prod"

# Create project
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID

# Link billing account
gcloud billing accounts list
gcloud billing projects link $PROJECT_ID \
  --billing-account=BILLING_ACCOUNT_ID
```

### 1.2 Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  storage-api.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  cloudscheduler.googleapis.com \
  compute.googleapis.com
```

### 1.3 Create Service Accounts

```bash
# Cloud Run service account
gcloud iam service-accounts create beacon-cloud-run \
  --display-name="Beacon Cloud Run Service Account"

# Cloud Scheduler service account
gcloud iam service-accounts create beacon-scheduler \
  --display-name="Beacon Cloud Scheduler Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:beacon-cloud-run@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:beacon-cloud-run@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

### 1.4 Create Cloud Storage Bucket

```bash
# Production bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://beacon-prod-files-${PROJECT_ID}

# Grant access to Cloud Run service account
gsutil iam ch \
  serviceAccount:beacon-cloud-run@${PROJECT_ID}.iam.gserviceaccount.com:roles/storage.objectAdmin \
  gs://beacon-prod-files-${PROJECT_ID}

# Enable versioning (optional but recommended)
gsutil versioning set on gs://beacon-prod-files-${PROJECT_ID}
```

---

## Step 2: Google OAuth Configuration

### 2.1 Create OAuth Credentials

1. Go to: https://console.cloud.google.com/apis/credentials
2. Select your project
3. Click "Create Credentials" → "OAuth client ID"
4. Choose "Web application"
5. Set name: "Beacon Studio"

### 2.2 Configure Authorized Redirect URIs

Add these URIs:

**For Development:**
```
http://localhost:8000/api/v1/auth/callback/google
```

**For Production:**
```
https://YOUR-CLOUD-RUN-URL/api/v1/auth/callback/google
https://glowstone.red/api/v1/auth/callback/google
```

### 2.3 Save Credentials

Copy the **Client ID** and **Client Secret**. You'll need these for `.env` file.

Example:
```
Client ID: 123456789-abc123.apps.googleusercontent.com
Client Secret: GOCSPX-abc123def456
```

---

## Step 3: GitHub OAuth Configuration

### 3.1 Create OAuth App

1. Go to: https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in details:
   - **Application name:** Beacon Studio
   - **Homepage URL:** https://glowstone.red
   - **Authorization callback URL:** 
     - Dev: `http://localhost:8000/api/v1/auth/callback/github`
     - Prod: `https://YOUR-CLOUD-RUN-URL/api/v1/auth/callback/github`

### 3.2 Save Credentials

Copy the **Client ID** and generate a **Client Secret**.

Example:
```
Client ID: Iv1.abc123def456
Client Secret: a1b2c3d4e5f6g7h8i9j0
```

---

## Step 4: Stripe Configuration

### 4.1 Get API Keys

1. Go to: https://dashboard.stripe.com/apikeys
2. Copy your **Secret Key** (starts with `sk_test_` or `sk_live_`)

### 4.2 Create Products & Prices

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Create products
stripe products create --name="Haste I" --description="20 GB storage, 5 users"
stripe products create --name="Haste II" --description="60 GB storage, 9 users"
stripe products create --name="Haste III" --description="240 GB storage, 17 users"

# Create prices (get product IDs from above)
stripe prices create --product=PRODUCT_ID_1 --unit-amount=1699 --currency=usd --recurring[interval]=month
stripe prices create --product=PRODUCT_ID_2 --unit-amount=2999 --currency=usd --recurring[interval]=month
stripe prices create --product=PRODUCT_ID_3 --unit-amount=4999 --currency=usd --recurring[interval]=month
```

Save the **Price IDs** (start with `price_`).

### 4.3 Create Webhook Endpoint

1. Go to: https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Set endpoint URL: `https://YOUR-CLOUD-RUN-URL/api/v1/billing/webhook`
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copy the **Webhook Secret** (starts with `whsec_`)

---

## Step 5: Configure Secrets in GCP

### 5.1 Generate Secure Keys

```bash
# Generate secret key
SECRET_KEY=$(openssl rand -hex 32)
echo $SECRET_KEY

# Generate admin secret
ADMIN_SECRET=$(openssl rand -hex 32)
echo $ADMIN_SECRET
```

### 5.2 Create Secrets in Secret Manager

```bash
# Application secrets
echo -n "$SECRET_KEY" | gcloud secrets create beacon-secret-key --data-file=-
echo -n "$ADMIN_SECRET" | gcloud secrets create beacon-admin-secret-key --data-file=-

# Database password
DB_PASSWORD="$(openssl rand -base64 32)"
echo -n "$DB_PASSWORD" | gcloud secrets create beacon-db-password --data-file=-

# OAuth - Google
echo -n "YOUR_GOOGLE_CLIENT_ID" | gcloud secrets create beacon-google-client-id --data-file=-
echo -n "YOUR_GOOGLE_CLIENT_SECRET" | gcloud secrets create beacon-google-client-secret --data-file=-

# OAuth - GitHub
echo -n "YOUR_GITHUB_CLIENT_ID" | gcloud secrets create beacon-github-client-id --data-file=-
echo -n "YOUR_GITHUB_CLIENT_SECRET" | gcloud secrets create beacon-github-client-secret --data-file=-

# Stripe
echo -n "YOUR_STRIPE_API_KEY" | gcloud secrets create beacon-stripe-api-key --data-file=-
echo -n "YOUR_STRIPE_WEBHOOK_SECRET" | gcloud secrets create beacon-stripe-webhook-secret --data-file=-

# Stripe Price IDs
echo -n "YOUR_HASTE_I_PRICE_ID" | gcloud secrets create beacon-stripe-price-haste-i --data-file=-
echo -n "YOUR_HASTE_II_PRICE_ID" | gcloud secrets create beacon-stripe-price-haste-ii --data-file=-
echo -n "YOUR_HASTE_III_PRICE_ID" | gcloud secrets create beacon-stripe-price-haste-iii --data-file=-

# Gemini API (optional)
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create beacon-gemini-api-key --data-file=-
```

### 5.3 Grant Access to Service Accounts

```bash
for secret in beacon-secret-key beacon-admin-secret-key beacon-db-password beacon-google-client-id beacon-google-client-secret beacon-github-client-id beacon-github-client-secret beacon-stripe-api-key beacon-stripe-webhook-secret beacon-stripe-price-haste-i beacon-stripe-price-haste-ii beacon-stripe-price-haste-iii beacon-gemini-api-key; do
  gcloud secrets add-iam-policy-binding $secret \
    --member="serviceAccount:beacon-cloud-run@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
done
```

---

## Step 6: Local Development Configuration

### 6.1 Create `.env` File

Copy `env.example` to `.env`:

```bash
cp env.example .env
```

### 6.2 Fill in Values

Edit `.env` with your credentials:

```bash
# Security
SECRET_KEY=<generated-key-from-step-5>
ADMIN_SECRET_KEY=<generated-admin-key-from-step-5>

# Database (local)
POSTGRES_PASSWORD=localpassword
DATABASE_URL=postgresql://postgres:localpassword@postgres:5432/beacon_studio

# Google Cloud Storage
GCS_BUCKET_NAME=beacon-prod-files-YOUR-PROJECT-ID
GCS_PROJECT_ID=YOUR-PROJECT-ID

# OAuth - Google
GOOGLE_CLIENT_ID=<from-step-2>
GOOGLE_CLIENT_SECRET=<from-step-2>
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback/google

# OAuth - GitHub
GITHUB_CLIENT_ID=<from-step-3>
GITHUB_CLIENT_SECRET=<from-step-3>
GITHUB_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback/github

# Stripe
STRIPE_API_KEY=<from-step-4>
STRIPE_WEBHOOK_SECRET=<from-step-4>
STRIPE_PRICE_ID_HASTE_I=<from-step-4>
STRIPE_PRICE_ID_HASTE_II=<from-step-4>
STRIPE_PRICE_ID_HASTE_III=<from-step-4>

# AI (optional)
GEMINI_API_KEY=<your-key>

# Environment
ENVIRONMENT=development
DEBUG=true
```

---

## Step 7: Verify Configuration

### 7.1 Test Local Setup

```bash
# Start services
docker-compose up -d

# Check health
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","database":"connected","environment":"development"}
```

### 7.2 Test OAuth

Open browser:
- Google: http://localhost:8000/api/v1/auth/login/google
- GitHub: http://localhost:8000/api/v1/auth/login/github

Should redirect to provider login page.

### 7.3 Test Admin Endpoints

```bash
# Should fail (401/403)
curl -X POST http://localhost:8000/admin/stats

# Should succeed
curl -X GET http://localhost:8000/admin/stats \
  -H "X-Admin-Secret: YOUR_ADMIN_SECRET"
```

---

## Step 8: Update Production URLs

After deploying to Cloud Run, you'll get a URL like:
```
https://beacon-backend-abc123-uc.a.run.app
```

Update these locations with your production URL:

### 8.1 Google OAuth Console
- Add: `https://YOUR-CLOUD-RUN-URL/api/v1/auth/callback/google`

### 8.2 GitHub OAuth App
- Update callback: `https://YOUR-CLOUD-RUN-URL/api/v1/auth/callback/github`

### 8.3 Stripe Webhook
- Update endpoint: `https://YOUR-CLOUD-RUN-URL/api/v1/billing/webhook`

### 8.4 Custom Domain (Optional)

If using custom domain (e.g., glowstone.red):

```bash
# Map domain to Cloud Run
gcloud run domain-mappings create \
  --service beacon-backend \
  --domain glowstone.red \
  --region us-central1
```

Then update all OAuth redirect URIs to use your custom domain.

---

## Checklist

Configuration complete when you can check all these:

- [ ] GCP project created and billing enabled
- [ ] Required APIs enabled
- [ ] Service accounts created
- [ ] Cloud Storage bucket created
- [ ] Google OAuth credentials created
- [ ] GitHub OAuth app created
- [ ] Stripe products and prices created
- [ ] All secrets stored in Secret Manager
- [ ] Service accounts granted access to secrets
- [ ] Local `.env` file configured
- [ ] Docker Compose starts successfully
- [ ] Health check returns healthy
- [ ] OAuth login redirects work
- [ ] Admin endpoints protected

---

## Next Steps

After configuration is complete:

1. **Test locally**: Run full test suite
2. **Deploy infrastructure**: `cd terraform && terraform apply`
3. **Deploy application**: `gcloud builds submit --config cloudbuild.beacon.yaml`
4. **Update production URLs**: In OAuth providers and Stripe
5. **Verify production**: Test OAuth and webhooks in production

See [DEPLOYMENT_ROADMAP.md](DEPLOYMENT_ROADMAP.md) for deployment instructions.

---

## Troubleshooting

### OAuth Redirect Mismatch

**Error:** `redirect_uri_mismatch`

**Fix:** Ensure the redirect URI in your OAuth provider exactly matches the one in your `.env`:
- Check for http vs https
- Check for trailing slashes
- Check domain spelling

### Stripe Webhook 401

**Error:** `Invalid signature`

**Fix:** 
1. Get fresh webhook secret from Stripe dashboard
2. Update in Secret Manager or `.env`
3. Restart backend

### GCS Permission Denied

**Error:** `403 Forbidden` on file upload

**Fix:**
```bash
# Grant storage permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:beacon-cloud-run@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

### Admin Endpoint 500 Error

**Error:** `Admin secret key is not configured`

**Fix:** Ensure `ADMIN_SECRET_KEY` is set in environment:
- Local: Add to `.env`
- Production: Create secret in Secret Manager

---

## Security Notes

1. **Never commit `.env`** - It's in `.gitignore`, keep it there
2. **Rotate secrets regularly** - At least every 90 days
3. **Use test keys in development** - Use Stripe test mode, not live keys
4. **Monitor Secret Manager access** - Check audit logs regularly
5. **Limit service account permissions** - Only grant what's needed

---

**Configuration Guide Version:** 1.0  
**Last Updated:** November 10, 2025

