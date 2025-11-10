# Beacon Studio

**Multi-tenant, browser-based IDE platform built on Code OSS**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GCP](https://img.shields.io/badge/Cloud-GCP-4285F4?logo=google-cloud)](https://cloud.google.com)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393.svg)](https://fastapi.tiangolo.com)

> **Codename**: Gunpowder Splash  
> **Production URL**: `https://shlinx.com`

---

## Overview

Beacon Studio is a production-ready, cloud-hosted IDE platform that transforms Code OSS (open-source VS Code) into a multi-tenant SaaS application with:

- **Browser-based editor** - No installation required
- **Team collaboration** - Shared workspaces with role-based access
- **Cloud storage** - Up to 240 GB with automatic backup
- **AI integration** - Gemini, LM Studio, and Ollama support
- **Subscription billing** - Stripe-powered pricing tiers
- **OAuth authentication** - Google and GitHub sign-in

---

## Quick Start

```bash
# Clone and start with Docker Compose
docker-compose up -d

# Access
# Frontend: http://localhost:80
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/api/v1/docs
```

📖 **Full setup**: [QUICK_START.md](QUICK_START.md)  
📖 **Production deployment**: [docs/DEPLOYMENT_ROADMAP.md](docs/DEPLOYMENT_ROADMAP.md)

---

## Features

### Subscription Plans

| Plan | Price | Storage | Team Size | Best For |
|------|-------|---------|-----------|----------|
| **Free** | $0/mo | 0.84 GB | 1 user | Personal projects |
| **Haste I** | $16.99/mo | 20 GB | 5 users | Small teams |
| **Haste II** | $29.99/mo | 60 GB | 9 users | Growing teams |
| **Haste III** | $49.99/mo | 240 GB | 17 users | Large teams |

### Core Features

- **Code OSS Editor** - Full-featured IDE in your browser
- **Project Management** - Multiple projects per workspace
- **File Storage** - Cloud Storage with quota management
- **Team Collaboration** - ADMIN, MOD, and USER roles
- **AI Assistant** - Integrated code help and generation
- **Version Control** - Built-in Git support (via Code OSS)
- **Extensions** - Custom extension marketplace

---

## Architecture

### Technology Stack

**Backend**
- Python 3.11+ with FastAPI
- PostgreSQL 15 (Cloud SQL)
- Google Cloud Storage
- Google Cloud Run (serverless)

**Frontend**
- Code OSS (MIT-licensed VS Code)
- TypeScript + React
- Custom file system provider

**Infrastructure**
- Google Cloud Platform
- Terraform for IaC
- Cloud Scheduler for cron jobs

### API Endpoints

- `/api/v1/auth/*` - OAuth authentication
- `/api/v1/workspaces/*` - Workspace management
- `/api/v1/projects/*` - Project and file operations
- `/api/v1/billing/*` - Stripe integration
- `/api/v1/ai/*` - AI provider integration

📖 **Full API docs**: Available at `/api/v1/docs` when running

---

## Documentation

**Start Here:** [QUICK_START.md](QUICK_START.md)

**Setup & Deploy:**
1. [docs/CONFIGURATION_GUIDE.md](docs/CONFIGURATION_GUIDE.md) - Configure GCP, OAuth, Stripe
2. [docs/DEPLOY.md](docs/DEPLOY.md) - Deploy to Google Cloud
3. [docs/PRODUCTION_CHECKLIST.md](docs/PRODUCTION_CHECKLIST.md) - Verify deployment
4. [docs/TROUBLESHOOTING_GCP_DEPLOYMENT.md](docs/TROUBLESHOOTING_GCP_DEPLOYMENT.md) - Fix issues

---

## Project Status

**Current Branch:** `blazerod`  
**Status:** Ready for configuration and deployment

### Critical Issues Fixed ✅

- [x] Fix `Dockerfile.beacon` requirements file reference
- [x] Protect admin endpoints with authentication  
- [x] Configure GCS credentials fallback

### Next Steps

1. **Configure services** → [docs/CONFIGURATION_GUIDE.md](docs/CONFIGURATION_GUIDE.md)
2. **Deploy to GCP** → [docs/DEPLOY.md](docs/DEPLOY.md)
3. **Verify deployment** → [docs/PRODUCTION_CHECKLIST.md](docs/PRODUCTION_CHECKLIST.md)

---

## Development

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Node.js 18+ (for Code OSS)
- Docker (optional)
- Google Cloud SDK (for deployment)

### Project Structure

```
Beacon Studio/
├── README.md                   # This file
├── docs/                       # Documentation
│   ├── WORK_COMPLETED.md
│   ├── QUICK_START_BEACON.md
│   ├── SETUP_GUIDE_BEACON.md
│   ├── CODE_OSS_INTEGRATION.md
│   └── ...
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main_beacon.py     # Main application
│   │   ├── models.py          # ORM models
│   │   ├── auth.py            # Authentication
│   │   ├── storage.py         # Storage management
│   │   ├── ai_providers.py    # AI integration
│   │   └── routers/           # API endpoints
│   ├── schema.sql             # Database schema
│   ├── Dockerfile.beacon      # Production Docker
│   └── requirements_beacon.txt
├── frontend/                   # Code OSS integration
│   └── src/
│       └── beacon-components/ # Custom UI components
├── terraform/                  # Infrastructure as code
│   └── beacon-infrastructure.tf
└── cloudbuild.beacon.yaml     # CI/CD pipeline
```

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/

# With coverage
pytest --cov=app tests/
```

---

## Deployment

### Development

```bash
# Local backend
python -m app.main_beacon

# Access at http://localhost:8000
```

### Production

```bash
# 1. Configure services (GCP, OAuth, Stripe)
# See docs/CONFIGURATION_GUIDE.md

# 2. Deploy infrastructure
cd terraform
terraform apply -var="project_id=YOUR_PROJECT_ID"

# 3. Deploy application
gcloud builds submit --config cloudbuild.beacon.yaml

# 4. Verify deployment
# See docs/PRODUCTION_CHECKLIST.md
```

📖 **Complete guide**: [docs/DEPLOY.md](docs/DEPLOY.md)

---

## Security

- **Authentication**: OAuth 2.0 only (no passwords)
- **Authorization**: Role-based access control (RBAC)
- **Data**: Encrypted in transit and at rest
- **Secrets**: Google Secret Manager
- **Compliance**: GDPR/CCPA considerations, audit logging

📖 **Security policy**: [docs/SECURITY.md](docs/SECURITY.md)

---

## License

- **Beacon Studio Backend**: Proprietary (SaaS product)
- **Code OSS**: MIT License (see [docs/LICENSES_BEACON.md](docs/LICENSES_BEACON.md))
- **Third-party dependencies**: See [docs/LICENSES_BEACON.md](docs/LICENSES_BEACON.md)

**Important**: Beacon Studio is based on the MIT-licensed Code OSS project and is NOT affiliated with or endorsed by Microsoft Corporation. We do not use or redistribute the official Visual Studio Code product.

---

## Contributing

We welcome contributions! Please see:

- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) - Contribution guidelines
- [docs/COLLABORATION.md](docs/COLLABORATION.md) - Team collaboration
- [docs/QUICK_START_BEACON.md](docs/QUICK_START_BEACON.md) - Development setup

---

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: Create GitHub issues for bugs
- **Email**: support@shlinx.com
- **Website**: https://shlinx.com

---

## Roadmap

- [x] **Phase 1**: Backend infrastructure (Complete)
- [ ] **Phase 2**: Code OSS integration (In Progress)
- [ ] **Phase 3**: Testing & QA
- [ ] **Phase 4**: Beta launch
- [ ] **Phase 5**: Production launch

📖 **Detailed roadmap**: [docs/BEACON_MIGRATION_PLAN.md](docs/BEACON_MIGRATION_PLAN.md)

---

## Acknowledgments

Built with open-source software:

- [Code OSS](https://github.com/microsoft/vscode) - MIT License
- [FastAPI](https://fastapi.tiangolo.com/) - MIT License
- [SQLAlchemy](https://www.sqlalchemy.org/) - MIT License
- [Google Cloud Platform](https://cloud.google.com/) - Infrastructure

See [docs/LICENSES_BEACON.md](docs/LICENSES_BEACON.md) for complete attributions.

---

**Beacon Studio** - Illuminate your code, collaborate brilliantly.

*Version 1.0.0 | Last Updated: November 8, 2025*
