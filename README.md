# Gunpowder Splash

**Open-source collaborative cloud IDE platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Live Demo](https://img.shields.io/badge/Demo-shlinx.com-blue)](https://shlinx.com)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393.svg)](https://fastapi.tiangolo.com)

> **Live at**: [shlinx.com](https://shlinx.com)  
> **API**: [api.shlinx.com](https://api.shlinx.com)

---

## What is Gunpowder Splash?

Gunpowder Splash is a free, open-source collaborative IDE that runs entirely in your browser. Built with modern web technologies and designed for teams, it provides:

- **Browser-based coding** - No installation, just open and code
- **Real-time collaboration** - Share workspaces with up to 1 team member (free tier)
- **Cloud storage** - 0.84 GB free storage for all users
- **Multiple languages** - Python, JavaScript, TypeScript, and more
- **Data science tools** - Jupyter notebooks, CSV viewer, SQL queries
- **OAuth authentication** - Sign in with Google or GitHub
- **Guest mode** - Try it instantly without signing up

---

## Quick Start

### Try It Now

Visit [shlinx.com](https://shlinx.com) and click "Continue as Guest" to start coding immediately.

### Self-Hosted Deployment

```bash
# Clone the repository
git clone https://github.com/shlinkLFO/Gunpowder-Splash.git
cd Gunpowder-Splash

# Start with Docker Compose
docker-compose up -d

# Access
# Frontend: http://localhost:80
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/v1/docs
```

📖 **Full setup guide**: [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)  
📖 **Deployment guide**: [docs/DEPLOY.md](docs/DEPLOY.md)

---

## Features

### Code Editor
- **Monaco Editor** - The same editor that powers VS Code
- **Syntax highlighting** - 50+ languages supported
- **IntelliSense** - Code completion and suggestions
- **Multi-file editing** - Tabs and split views
- **File tree** - Navigate your project structure

### Data Science Tools
- **Jupyter Notebooks** - Execute Python cells inline
- **CSV/Excel Viewer** - Rainbow CSV with sorting and filtering
- **SQL Query Tool** - Run SQL queries on your data
- **Data Explorer** - Upload and analyze datasets

### Collaboration
- **Shared Workspaces** - Invite team members
- **Role-based Access** - Admin, Moderator, and User roles
- **Project Management** - Multiple projects per workspace
- **Cloud Storage** - Automatic file synchronization

### Free Tier
- **0.84 GB storage** - Generous free storage for all users
- **1 team member** - Share with one collaborator (requires login)
- **Unlimited projects** - Create as many projects as you need
- **No credit card** - Start for free, upgrade when ready

---

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM and database toolkit
- **Google Cloud Storage** - File storage
- **Cloud Run** - Serverless deployment

### Frontend
- **React** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Chakra UI** - Component library
- **Monaco Editor** - Code editor
- **Vite** - Build tool

### Infrastructure
- **Google Cloud Platform** - Cloud hosting
- **Cloud Build** - CI/CD pipeline
- **Cloud SQL** - Managed PostgreSQL
- **Secret Manager** - Secure credentials
- **Terraform** - Infrastructure as code

---

## Architecture

```
┌─────────────────┐
│   shlinx.com    │  Frontend (React + Monaco)
│   (Cloud Run)   │
└────────┬────────┘
         │
         │ HTTPS
         │
┌────────▼────────┐
│ api.shlinx.com  │  Backend API (FastAPI)
│  (Cloud Run)    │
└────────┬────────┘
         │
    ┌────┴────┬──────────┐
    │         │          │
┌───▼───┐ ┌──▼──┐  ┌────▼────┐
│Cloud  │ │Cloud│  │ Secret  │
│  SQL  │ │ GCS │  │ Manager │
└───────┘ └─────┘  └─────────┘
```

---

## API Documentation

### Authentication
- `GET /api/v1/auth/login/{provider}` - Initiate OAuth login
- `GET /api/v1/auth/callback/{provider}` - OAuth callback
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - Logout

### Workspaces
- `GET /api/v1/workspaces` - List workspaces
- `POST /api/v1/workspaces` - Create workspace
- `GET /api/v1/workspaces/{id}` - Get workspace details
- `POST /api/v1/workspaces/{id}/members` - Add team member

### Projects
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project details
- `GET /api/v1/projects/{id}/files` - List files
- `POST /api/v1/projects/{id}/files` - Upload file

### Files
- `GET /api/v1/files/{path}` - Read file
- `PUT /api/v1/files/{path}` - Update file
- `DELETE /api/v1/files/{path}` - Delete file

📖 **Interactive API docs**: [api.shlinx.com/api/v1/docs](https://api.shlinx.com/api/v1/docs)

---

## Self-Hosting

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Node.js 20+
- Docker (optional)
- Google Cloud account (for GCS)

### Environment Variables

Create a `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/gunpowder

# Security
SECRET_KEY=your-secret-key-here

# OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Storage
GCS_BUCKET_NAME=your-bucket-name
GCS_PROJECT_ID=your-project-id

# AI (optional)
GEMINI_API_KEY=your-gemini-key
```

### Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main_beacon

# Frontend
cd frontend
npm install
npm run dev
```

### Production Deployment

See [docs/DEPLOY.md](docs/DEPLOY.md) for complete deployment instructions for:
- Google Cloud Platform
- AWS
- Azure
- Self-hosted servers

---

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write tests for new features
- Update documentation

📖 **Contributing guide**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Roadmap

### Current (v1.0)
- [x] Core IDE functionality
- [x] OAuth authentication
- [x] Cloud storage integration
- [x] Jupyter notebook support
- [x] CSV/Excel viewer
- [x] Team collaboration

### Upcoming (v1.1)
- [ ] Real-time collaborative editing
- [ ] Terminal access
- [ ] Git integration UI
- [ ] Extension marketplace
- [ ] Mobile responsive design
- [ ] Dark/light theme toggle

### Future (v2.0)
- [ ] Video chat integration
- [ ] Code review tools
- [ ] CI/CD pipeline integration
- [ ] Container deployment
- [ ] VS Code extension compatibility

---

## Community

- **Website**: [shlinx.com](https://shlinx.com)
- **GitHub**: [github.com/shlinkLFO/Gunpowder-Splash](https://github.com/shlinkLFO/Gunpowder-Splash)
- **Issues**: [Report bugs](https://github.com/shlinkLFO/Gunpowder-Splash/issues)
- **Discussions**: [Join the conversation](https://github.com/shlinkLFO/Gunpowder-Splash/discussions)
- **Email**: support@shlinx.com

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- **Monaco Editor**: MIT License
- **FastAPI**: MIT License
- **React**: MIT License
- **Chakra UI**: MIT License

See [docs/LICENSES.md](docs/LICENSES.md) for complete attributions.

---

## Acknowledgments

Built with open-source software:

- [Monaco Editor](https://microsoft.github.io/monaco-editor/) - The code editor that powers VS Code
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library
- [Chakra UI](https://chakra-ui.com/) - Component library
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Google Cloud Platform](https://cloud.google.com/) - Infrastructure

---

## Security

Found a security vulnerability? Please email security@shlinx.com instead of opening a public issue.

---

## Support

- **Documentation**: [docs/](docs/)
- **FAQ**: [docs/FAQ.md](docs/FAQ.md)
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **Email**: support@shlinx.com

---

**Gunpowder Splash** - Code together, anywhere.

*Open Source • Free Forever • Built for Teams*

[![Deploy to GCP](https://img.shields.io/badge/Deploy-GCP-4285F4?logo=google-cloud)](docs/DEPLOY.md)
[![Star on GitHub](https://img.shields.io/github/stars/shlinkLFO/Gunpowder-Splash?style=social)](https://github.com/shlinkLFO/Gunpowder-Splash)
