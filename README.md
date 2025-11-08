# Beacon Studio

**Multi-tenant, browser-based IDE platform built on Code OSS**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GCP](https://img.shields.io/badge/Cloud-GCP-4285F4?logo=google-cloud)](https://cloud.google.com)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393.svg)](https://fastapi.tiangolo.com)

> **Codename**: Gunpowder Splash  
> **Production URL**: `https://glowstone.red/beacon-studio`

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

### For Developers

Get the backend running locally in 30 minutes:

```bash
# Set up database
createdb beacon_studio
psql beacon_studio < backend/schema.sql

# Set up backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements_beacon.txt
cp .env.example .env  # Edit with your values
python -m app.main_beacon
```

**Backend runs at**: http://localhost:8000  
**API docs at**: http://localhost:8000/api/v1/docs

📖 **Full guide**: [docs/QUICK_START_BEACON.md](docs/QUICK_START_BEACON.md)

### For DevOps

Deploy to GCP with Terraform:

```bash
cd terraform
terraform init
terraform apply -var="project_id=beacon-studio-prod"
```

📖 **Full guide**: [docs/SETUP_GUIDE_BEACON.md](docs/SETUP_GUIDE_BEACON.md)

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

### Essential Guides

| Document | Description |
|----------|-------------|
| [WORK_COMPLETED](docs/WORK_COMPLETED.md) | Complete summary of implementation work |
| [IMPLEMENTATION_SUMMARY](docs/IMPLEMENTATION_SUMMARY.md) | What's done, what's next |
| [QUICK_START_BEACON](docs/QUICK_START_BEACON.md) | Get running in 30 minutes |
| [SETUP_GUIDE_BEACON](docs/SETUP_GUIDE_BEACON.md) | Production deployment guide |

### Technical Documentation

| Document | Description |
|----------|-------------|
| [beacon-studio-spec](docs/beacon-studio-spec.md) | Complete product specification |
| [CODE_OSS_INTEGRATION](docs/CODE_OSS_INTEGRATION.md) | Frontend integration guide |
| [BEACON_MIGRATION_PLAN](docs/BEACON_MIGRATION_PLAN.md) | 18-phase roadmap |
| [LICENSES_BEACON](docs/LICENSES_BEACON.md) | Legal compliance & attributions |

### Project Documentation

| Document | Description |
|----------|-------------|
| [CONTRIBUTING](docs/CONTRIBUTING.md) | Contribution guidelines |
| [SECURITY](docs/SECURITY.md) | Security policies |
| [COLLABORATION](docs/COLLABORATION.md) | Team collaboration guide |

📁 **All documentation**: [docs/](docs/)

---

## Project Status

### ✅ Complete (Backend)

- [x] PostgreSQL database schema with triggers
- [x] FastAPI backend with all endpoints
- [x] OAuth authentication (Google, GitHub)
- [x] Storage management with quota enforcement
- [x] Stripe billing integration
- [x] AI provider integration (Gemini, LM Studio, Ollama)
- [x] GCP infrastructure as code (Terraform)
- [x] Admin endpoints (reconciliation, purge, stats)
- [x] Comprehensive documentation

### 🚧 In Progress (Frontend)

- [ ] Build Code OSS from source
- [ ] Apply Beacon Studio branding
- [ ] Implement custom file system provider
- [ ] Create Beacon UI components
- [ ] Deploy frontend to production

### 📋 Planned

- [ ] End-to-end testing
- [ ] Security audit
- [ ] Beta testing
- [ ] Production launch

📖 **Detailed status**: [docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)

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

### Staging/Production

```bash
# Deploy infrastructure
cd terraform
terraform apply -var="project_id=beacon-studio-prod"

# Deploy backend
cd backend
gcloud builds submit --config=../cloudbuild.beacon.yaml
```

📖 **Complete guide**: [docs/SETUP_GUIDE_BEACON.md](docs/SETUP_GUIDE_BEACON.md)

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
- **Email**: support@glowstone.red
- **Website**: https://glowstone.red/beacon-studio

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
