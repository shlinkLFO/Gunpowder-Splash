# START HERE

Welcome to Gunpowder Splash - Your Cloud IDE Platform!

## What is Gunpowder Splash?

A modern, collaborative cloud IDE for data analysis and code execution, featuring:
- Real-time collaborative editing
- Jupyter notebook support
- Data visualization with Plotly
- Multi-file code editor
- CSV/Excel data exploration

## Quick Navigation

### First Time Setup
1. **[MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md)** - Overview of the transformation from Replit
2. **[QUICK_START.md](QUICK_START.md)** - Get running in 5 minutes
3. Run `./verify-setup.sh` - Check your environment

### For Developers
- **[README.md](README.md)** - Complete documentation
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Architecture details
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute
- **[backend/README.md](backend/README.md)** - Backend documentation
- **[frontend/README.md](frontend/README.md)** - Frontend documentation

### For Deployment
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[docker-compose.yml](docker-compose.yml)** - Docker configuration

### Other Resources
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[SECURITY.md](SECURITY.md)** - Security best practices
- **[COLLABORATION.md](COLLABORATION.md)** - Collaboration features
- **[LICENSE](LICENSE)** - License information

## Fastest Way to Get Started

### Option 1: Docker (Recommended)
```bash
docker-compose up --build
```
Then open http://localhost:5173

### Option 2: Local Development
```bash
# Check prerequisites
./verify-setup.sh

# Install dependencies
make install

# Start all services
./start-dev.sh
```
Then open http://localhost:5173

## Need Help?

1. Read [QUICK_START.md](QUICK_START.md) for detailed setup
2. Check [MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md) for troubleshooting
3. Review the API docs at http://localhost:8000/docs (after starting)
4. Contact the Glowstone team

## Project Status

This is the standalone version of Gunpowder Splash, transformed from the Replit deployment. All core features are functional and ready for development.

### What's Working
- Backend API (FastAPI)
- Frontend UI (React + TypeScript)
- WebSocket collaboration
- Code execution
- Data processing
- File management

### What to Set Up
- Python virtual environment
- Node.js dependencies
- Environment variables (see `.env.example`)

## Repository Structure

```
Gunpowder Splash/
├── backend/              # FastAPI backend
├── frontend/             # React frontend
├── websocket_server.py   # Real-time collaboration
├── start-dev.sh          # Start all services
├── verify-setup.sh       # Check prerequisites
├── cleanup-replit.sh     # Remove old Replit files
└── Documentation files   # You are here!
```

## Next Steps

1. Run `./verify-setup.sh` to check your environment
2. Follow [QUICK_START.md](QUICK_START.md) to get running
3. Read [README.md](README.md) for complete documentation
4. After verifying everything works, run `./cleanup-replit.sh` to remove old files

## Features Overview

### Code Editor
- Monaco editor with 25+ language support
- Multi-tab interface
- Syntax highlighting
- Code execution

### Data Tools
- CSV/Excel viewer with inline editing
- Plotly visualizations
- Data filtering and queries
- Export functionality

### Collaboration
- Real-time code synchronization
- User presence indicators
- Cursor tracking
- Shared workspaces

### Notebooks
- Jupyter-style notebooks
- Inline cell execution
- Markdown support
- Result caching

Ready to build? Start with [QUICK_START.md](QUICK_START.md)!

