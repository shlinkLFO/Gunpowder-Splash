# Welcome to Gunpowder Splash! 

Thank you for your interest in Gunpowder Splash - a free, open-source collaborative IDE for teams.

## What You'll Find Here

Gunpowder Splash is a complete cloud IDE platform that includes:

- **Browser-based code editor** with Monaco (the engine behind VS Code)
- **Data science tools** including Jupyter notebooks and CSV viewers
- **Team collaboration** with shared workspaces
- **Cloud storage** with 0.84 GB free for all users
- **OAuth authentication** via Google and GitHub
- **RESTful API** built with FastAPI
- **Modern frontend** using React and TypeScript

## Quick Links

### For Users
- **Try it now**: [shlinx.com](https://shlinx.com)
- **FAQ**: [docs/FAQ.md](docs/FAQ.md)
- **User Guide**: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)

### For Developers
- **Setup Guide**: [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **API Docs**: [api.shlinx.com/api/v1/docs](https://api.shlinx.com/api/v1/docs)

### For DevOps
- **Deployment**: [docs/DEPLOY.md](docs/DEPLOY.md)
- **Configuration**: [docs/CONFIGURATION_GUIDE.md](docs/CONFIGURATION_GUIDE.md)
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## Getting Started

### Option 1: Try the Live Demo

Visit [shlinx.com](https://shlinx.com) and click "Continue as Guest" to start coding immediately - no signup required!

### Option 2: Run Locally with Docker

```bash
# Clone the repository
git clone https://github.com/shlinkLFO/Gunpowder-Splash.git
cd Gunpowder-Splash

# Start all services
docker-compose up -d

# Access the IDE
open http://localhost:80
```

### Option 3: Development Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main_beacon

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed setup instructions.

## Project Structure

```
Gunpowder-Splash/
├── README.md                  # Project overview
├── CONTRIBUTING.md            # How to contribute
├── LICENSE                    # MIT License
├── SETUP_INSTRUCTIONS.md      # Detailed setup guide
│
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── main_beacon.py    # Main application
│   │   ├── models.py         # Database models
│   │   ├── routers/          # API endpoints
│   │   └── services/         # Business logic
│   ├── tests/                # Backend tests
│   └── requirements.txt
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   └── lib/              # Utilities
│   └── package.json
│
├── docs/                      # Documentation
│   ├── FAQ.md
│   ├── DEPLOY.md
│   ├── CONFIGURATION_GUIDE.md
│   └── ...
│
├── terraform/                 # Infrastructure as code
└── docker-compose.yml         # Local development
```

## Key Features

### Code Editor
- **Monaco Editor** - Industry-standard code editor
- **50+ Languages** - Syntax highlighting for all major languages
- **IntelliSense** - Smart code completion
- **Multi-file Editing** - Tabs and split views

### Data Science
- **Jupyter Notebooks** - Execute Python cells inline
- **CSV Viewer** - Rainbow CSV with sorting and filtering
- **SQL Query Tool** - Run SQL queries on your data
- **Data Explorer** - Upload and analyze datasets

### Collaboration
- **Shared Workspaces** - Work together in real-time
- **Role-based Access** - Admin, Moderator, and User roles
- **Team Management** - Invite up to 1 member (free tier)
- **Cloud Storage** - 0.84 GB free for all users

## Technology Stack

**Backend**
- Python 3.11+ with FastAPI
- PostgreSQL 15 database
- SQLAlchemy ORM
- Google Cloud Storage
- OAuth 2.0 authentication

**Frontend**
- React 19 with TypeScript
- Chakra UI components
- Monaco Editor
- Vite build tool
- Axios for API calls

**Infrastructure**
- Google Cloud Platform
- Cloud Run (serverless)
- Cloud SQL (managed PostgreSQL)
- Cloud Build (CI/CD)
- Terraform (IaC)

## Next Steps

### For Users
1. Visit [shlinx.com](https://shlinx.com)
2. Try Guest mode or sign in
3. Create your first project
4. Invite a team member

### For Contributors
1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Set up your development environment
3. Pick an issue or feature to work on
4. Submit a pull request

### For Self-Hosting
1. Review [docs/DEPLOY.md](docs/DEPLOY.md)
2. Set up your infrastructure
3. Configure environment variables
4. Deploy the application

## Resources

### Documentation
- [README.md](README.md) - Project overview
- [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) - Detailed setup
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [docs/FAQ.md](docs/FAQ.md) - Frequently asked questions
- [docs/DEPLOY.md](docs/DEPLOY.md) - Deployment guide

### Community
- **GitHub**: [github.com/shlinkLFO/Gunpowder-Splash](https://github.com/shlinkLFO/Gunpowder-Splash)
- **Issues**: [Report bugs](https://github.com/shlinkLFO/Gunpowder-Splash/issues)
- **Discussions**: [Ask questions](https://github.com/shlinkLFO/Gunpowder-Splash/discussions)
- **Email**: support@shlinx.com

### Live Services
- **Production**: [shlinx.com](https://shlinx.com)
- **API**: [api.shlinx.com](https://api.shlinx.com)
- **API Docs**: [api.shlinx.com/api/v1/docs](https://api.shlinx.com/api/v1/docs)

## Support

Need help? We're here for you:

- **Documentation**: Check [docs/](docs/) for guides
- **FAQ**: See [docs/FAQ.md](docs/FAQ.md) for common questions
- **Issues**: Report bugs on [GitHub](https://github.com/shlinkLFO/Gunpowder-Splash/issues)
- **Discussions**: Ask questions on [GitHub Discussions](https://github.com/shlinkLFO/Gunpowder-Splash/discussions)
- **Email**: support@shlinx.com

## License

Gunpowder Splash is open source software licensed under the [MIT License](LICENSE).

---

**Ready to start coding?** Visit [shlinx.com](https://shlinx.com) or follow the setup guide above!

*Gunpowder Splash - Code together, anywhere.*
