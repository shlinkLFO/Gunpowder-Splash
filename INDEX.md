# Gunpowder Splash - Complete File Index

## Documentation Files

### Getting Started
- **[START_HERE.md](START_HERE.md)** - Your starting point, read this first
- **[QUICK_START.md](QUICK_START.md)** - Get up and running in 5 minutes
- **[README.md](README.md)** - Complete project documentation
- **[MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md)** - Details about the Replit → Standalone transformation

### Architecture & Technical
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design decisions
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Detailed project structure breakdown
- **[backend/README.md](backend/README.md)** - Backend-specific documentation
- **[frontend/README.md](frontend/README.md)** - Frontend-specific documentation

### Development & Deployment
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute to the project
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes

### Policies & Guidelines
- **[SECURITY.md](SECURITY.md)** - Security policies and best practices
- **[COLLABORATION.md](COLLABORATION.md)** - Collaboration features documentation
- **[LICENSE](LICENSE)** - Proprietary license information

## Configuration Files

### Root Level
- **[.gitignore](.gitignore)** - Git ignore patterns
- **[.dockerignore](.dockerignore)** - Docker build ignore patterns
- **[docker-compose.yml](docker-compose.yml)** - Docker orchestration
- **[Makefile](Makefile)** - Build automation commands

### Backend
- **[backend/requirements.txt](backend/requirements.txt)** - Python dependencies
- **[backend/Dockerfile](backend/Dockerfile)** - Backend container image

### Frontend
- **[frontend/package.json](frontend/package.json)** - Node.js dependencies
- **[frontend/vite.config.ts](frontend/vite.config.ts)** - Vite build configuration
- **[frontend/tsconfig.json](frontend/tsconfig.json)** - TypeScript configuration
- **[frontend/tsconfig.node.json](frontend/tsconfig.node.json)** - TypeScript build configuration
- **[frontend/nginx.conf](frontend/nginx.conf)** - Production nginx configuration
- **[frontend/Dockerfile](frontend/Dockerfile)** - Frontend container image

### WebSocket
- **[Dockerfile.websocket](Dockerfile.websocket)** - WebSocket server container
- **[websocket_server.py](websocket_server.py)** - Real-time collaboration server

## Scripts

### Setup & Verification
- **[verify-setup.sh](verify-setup.sh)** - Check prerequisites and environment
- **[cleanup-replit.sh](cleanup-replit.sh)** - Remove Replit artifacts

### Development
- **[start-dev.sh](start-dev.sh)** - Start all development services

## Application Code

### Backend Structure
```
backend/
├── app/
│   ├── main.py                    # FastAPI application entry
│   ├── routers/                   # API endpoints
│   │   ├── files.py              # File operations
│   │   ├── data.py               # Data processing
│   │   ├── history.py            # Code history
│   │   ├── notebooks.py          # Jupyter notebooks
│   │   ├── system.py             # System info
│   │   └── templates.py          # Code templates
│   └── services/                  # Business logic
│       ├── data_service.py       # Data handling
│       ├── execution_service.py  # Code execution
│       ├── file_service.py       # File operations
│       ├── history_service.py    # History management
│       ├── notebook_service.py   # Notebook logic
│       └── query_service.py      # Data queries
└── workspace/                     # User workspace
```

### Frontend Structure
```
frontend/
├── src/
│   ├── App.tsx                   # Main app component
│   ├── main.tsx                  # Entry point
│   ├── components/               # React components
│   │   ├── FileTree.tsx         # File explorer
│   │   ├── MainContent.tsx      # Content area
│   │   ├── Sidebar.tsx          # Navigation
│   │   └── tabs/                # Tab components
│   │       ├── CodeEditor.tsx   # Monaco editor
│   │       ├── DataExplorer.tsx # Data visualization
│   │       ├── History.tsx      # Execution history
│   │       ├── InlineNotebook.tsx # Notebook cells
│   │       ├── Notebook.tsx     # Jupyter notebooks
│   │       ├── QueryFilter.tsx  # SQL queries
│   │       ├── RainbowCSV.tsx   # CSV editor
│   │       ├── System.tsx       # System info
│   │       ├── Templates.tsx    # Code templates
│   │       └── WebEdit.tsx      # HTML/CSS/JS editor
│   ├── contexts/                # React contexts
│   ├── hooks/                   # Custom hooks
│   ├── pages/                   # Page components
│   ├── styles/                  # Styling
│   └── utils/                   # Utilities
└── index.html                   # HTML entry
```

## Quick Access by Purpose

### I want to...

**Get Started**
1. [START_HERE.md](START_HERE.md)
2. [QUICK_START.md](QUICK_START.md)
3. Run `./verify-setup.sh`

**Understand the System**
1. [ARCHITECTURE.md](ARCHITECTURE.md)
2. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
3. [README.md](README.md)

**Deploy to Production**
1. [DEPLOYMENT.md](DEPLOYMENT.md)
2. [docker-compose.yml](docker-compose.yml)
3. [frontend/nginx.conf](frontend/nginx.conf)

**Contribute Code**
1. [CONTRIBUTING.md](CONTRIBUTING.md)
2. [backend/README.md](backend/README.md)
3. [frontend/README.md](frontend/README.md)

**Understand Security**
1. [SECURITY.md](SECURITY.md)
2. [LICENSE](LICENSE)

**Set Up Development Environment**
1. Run `./verify-setup.sh`
2. Run `make install` or follow [QUICK_START.md](QUICK_START.md)
3. Run `./start-dev.sh`

**Clean Up Replit Files**
1. Verify standalone setup works
2. Run `./cleanup-replit.sh`

## File Statistics

- **Documentation**: 14 markdown files
- **Configuration**: 10 config files
- **Scripts**: 3 shell scripts
- **Dockerfiles**: 3 container definitions
- **Application Code**: Backend + Frontend (see structure above)

## What Each File Does

### Core Application Files

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI application initialization |
| `frontend/src/App.tsx` | React application root |
| `websocket_server.py` | Real-time collaboration server |

### Configuration Priority

1. **Must configure**: 
   - `backend/requirements.txt` (Python deps)
   - `frontend/package.json` (Node deps)
   
2. **Should configure**:
   - `.env` file (create from template)
   - `vite.config.ts` (if ports need changing)
   
3. **Optional**:
   - `docker-compose.yml` (for Docker deployment)
   - `nginx.conf` (for production)

### Script Execution Order

1. First: `./verify-setup.sh` - Check environment
2. Then: `make install` or manual install
3. Finally: `./start-dev.sh` - Start application
4. Cleanup (optional): `./cleanup-replit.sh` - Remove old files

## Documentation Reading Order

### For New Users
1. [START_HERE.md](START_HERE.md)
2. [QUICK_START.md](QUICK_START.md)
3. [README.md](README.md)

### For Developers
1. [ARCHITECTURE.md](ARCHITECTURE.md)
2. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
3. [CONTRIBUTING.md](CONTRIBUTING.md)
4. Component-specific READMEs

### For DevOps
1. [DEPLOYMENT.md](DEPLOYMENT.md)
2. [SECURITY.md](SECURITY.md)
3. Docker configurations

## Additional Resources

### Generated During Development
- `backend/workspace/` - User files (not tracked)
- `frontend/dist/` - Production build (generated)
- `frontend/node_modules/` - Dependencies (generated)
- `backend/venv/` - Python virtual env (generated)

### Legacy (Can Be Removed)
- `ReplitCore/` - Original Replit structure
- `GunPowder-Splash.zip` - Archive
- `.replit` - Replit config
- `pyproject.toml` - Replit package file

## Summary

This repository contains everything needed to:
- Develop Gunpowder Splash locally
- Deploy to production
- Understand the architecture
- Contribute to the project
- Maintain security standards

Start with [START_HERE.md](START_HERE.md) and follow the guides!

