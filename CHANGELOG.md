# Changelog

All notable changes to Gunpowder Splash will be documented in this file.

## [1.0.0] - 2024-10-29

### Added (Transformation from Replit to Standalone)

#### Infrastructure
- Standalone repository structure independent of Replit
- Docker Compose configuration for easy deployment
- Development startup script (`start-dev.sh`)
- Makefile for common development tasks
- Comprehensive .gitignore for clean version control

#### Documentation
- Enhanced README.md with detailed setup instructions
- QUICK_START.md for rapid onboarding
- DEPLOYMENT.md with production deployment guides
- CONTRIBUTING.md for contributor guidelines
- PROJECT_STRUCTURE.md detailing architecture
- Separate README files for backend and frontend
- SECURITY.md with security best practices

#### Configuration
- Cleaned vite.config.ts (removed Replit-specific settings)
- Updated package.json with proper project metadata
- Consolidated requirements.txt for backend
- Environment variable template (.env.example)
- Production-ready nginx configuration

#### Docker Support
- Backend Dockerfile
- Frontend Dockerfile with nginx
- WebSocket server Dockerfile
- Multi-stage builds for optimized images
- Docker Compose orchestration

### Changed
- Project structure reorganized from ReplitCore to root level
- Frontend port changed from 5000 to 5173 (Vite default)
- Removed Replit-specific proxy configurations
- Updated CORS settings for flexible deployment

### Removed
- .replit configuration file
- replit.nix and Nix-specific settings
- Replit deployment configurations
- Replit-specific allowed hosts

## Features (Existing from Replit Version)

### Core Functionality
- Real-time collaborative code editing
- Multi-file tabbed code editor with Monaco
- Jupyter notebook integration
- Data exploration and visualization
- Rainbow CSV viewer with inline editing
- Web-Edit mode (HTML/CSS/JS live preview)
- Code execution history
- Template library
- Multi-sheet Excel file support

### Technical Features
- FastAPI backend with async support
- React 18 + TypeScript frontend
- WebSocket-based real-time collaboration
- Pandas for data processing
- Plotly for visualizations
- Chakra UI component library
- Session-based notebook execution
- File system workspace management

## Migration Notes

### Breaking Changes from Replit Version
- Frontend now runs on port 5173 (was 5000)
- Environment variables now use .env files
- No automatic Replit deployment support

### Compatibility
- Python 3.11+ required
- Node.js 20+ required
- Works on macOS, Linux, and Windows (with WSL)

## Future Roadmap

### Planned Features
- User authentication system
- Persistent database integration
- Cloud storage integration (S3, Google Cloud)
- Enhanced collaboration features (chat, video)
- Plugin system for extensibility
- API rate limiting
- Advanced data visualization options
- Git integration
- Terminal emulator
- AI-powered code suggestions

### Infrastructure Improvements
- Kubernetes deployment manifests
- CI/CD pipeline setup
- Automated testing suite
- Performance monitoring
- Error tracking integration
- Backup automation
- Load balancing configuration

## Support

For issues, suggestions, or contributions, please contact the Glowstone team.

