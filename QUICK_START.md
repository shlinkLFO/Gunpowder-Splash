# Quick Start

## Local Development

```bash
# Clone and navigate
cd "Gunpowder Splash"

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

**Access:**
- Frontend: http://localhost:80
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs

## Environment Setup

Copy `.env.example` to `.env` and configure:

```bash
# Required
SECRET_KEY=<generate with: openssl rand -hex 32>
POSTGRES_PASSWORD=<secure password>
GCS_BUCKET_NAME=<your-bucket>
GCS_PROJECT_ID=<your-project>

# OAuth
GOOGLE_CLIENT_ID=<from console.cloud.google.com>
GOOGLE_CLIENT_SECRET=<from console.cloud.google.com>
GITHUB_CLIENT_ID=<from github.com/settings/developers>
GITHUB_CLIENT_SECRET=<from github.com/settings/developers>

# Stripe
STRIPE_API_KEY=<from dashboard.stripe.com>
STRIPE_WEBHOOK_SECRET=<from stripe webhooks>
STRIPE_PRICE_ID_HASTE_I=<price id>
STRIPE_PRICE_ID_HASTE_II=<price id>
STRIPE_PRICE_ID_HASTE_III=<price id>
```

## Deploy to Google Cloud

```bash
# 1. Set project
gcloud config set project YOUR_PROJECT_ID

# 2. Deploy infrastructure
cd terraform
terraform init
terraform apply

# 3. Setup secrets
./scripts/setup-secrets.sh

# 4. Deploy application
gcloud builds submit --config cloudbuild.beacon.yaml

# 5. Apply database schema
gcloud sql connect beacon-db-prod --user=postgres < backend/schema.sql
```

## Common Commands

```bash
# Rebuild containers
docker-compose build --no-cache

# Reset database
docker-compose down -v
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Check backend health
curl http://localhost:8000/health
```

## Documentation

- **Deployment:** docs/DEPLOYMENT_ROADMAP.md
- **Architecture:** docs/ARCHITECTURE_AUDIT_2025-11-08.md
- **Troubleshooting:** docs/TROUBLESHOOTING_GCP_DEPLOYMENT.md
- **Security Fixes:** docs/FIXES_IMPLEMENTED_2025-11-08.md

## Critical Pre-Production Tasks

1. Fix `backend/Dockerfile.beacon` (requirements.txt not requirements_beacon.txt)
2. Protect admin endpoints with `verify_admin_secret`
3. Configure GCS workload identity
4. Set production CORS origins
5. Enable monitoring alerts

See docs/DEPLOYMENT_ROADMAP.md for complete checklist.

