# Gunpowder Splash - Cloud IDE Platform

A modern, collaborative cloud IDE for data analysis and code execution. Built by Glowstone (glowstone.red).

## Features

- Real-time collaborative code editing with WebSocket synchronization
- Multi-file tabbed code editor with syntax highlighting (Monaco Editor)
- Jupyter notebook integration with inline cell execution
- Interactive data exploration and visualization (Plotly)
- Rainbow CSV viewer with inline editing
- Web-Edit mode (HTML/CSS/JS live preview)
- Code history tracking
- Template library for quick starts
- Multi-sheet Excel file support

## Architecture

### Backend
- **FastAPI** - High-performance async API
- **Python 3.11+** - Core runtime
- **Pandas** - Data processing
- **WebSocket** - Real-time collaboration

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Chakra UI** - Component library
- **Monaco Editor** - Code editor

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd "Gunpowder Splash"
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

3. Set up the frontend:
```bash
cd frontend
npm install
cd ..
```

### Running the Application

#### Development Mode

Run all services with the startup script:
```bash
chmod +x start-dev.sh
./start-dev.sh
```

Or manually start each service:

1. Start the WebSocket server (Terminal 1):
```bash
python websocket_server.py
```

2. Start the backend API (Terminal 2):
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

3. Start the frontend (Terminal 3):
```bash
cd frontend
npm run dev
```

#### Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- WebSocket: ws://localhost:8001
- API Docs: http://localhost:8000/docs

### Using Docker

Build and run with Docker Compose:
```bash
docker-compose up --build
```

## Project Structure

```
Gunpowder Splash/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # Application entry point
│   │   ├── routers/     # API endpoints
│   │   └── services/    # Business logic
│   ├── requirements.txt
│   └── workspace/       # User file workspace
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── hooks/       # Custom hooks
│   │   └── styles/      # Theme and styles
│   ├── package.json
│   └── vite.config.ts
├── websocket_server.py  # Collaboration server
├── docker-compose.yml   # Docker orchestration
└── README.md
```

## Development

### Backend Development
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Code Style
- Backend: Follow PEP 8
- Frontend: Use ESLint and Prettier

## Configuration

### Backend Environment Variables
Create a `.env` file in the `backend` directory:
```
WORKSPACE_DIR=workspace
PORT=8000
```

### Frontend Configuration
Update `frontend/vite.config.ts` for custom proxy settings.

## Deployment

### Production Build

1. Build the frontend:
```bash
cd frontend
npm run build
```

2. Run the backend with production settings:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Security

- Always use HTTPS in production
- Set proper CORS origins in `backend/app/main.py`
- Use environment variables for secrets
- Review `SECURITY.md` for detailed guidelines

## Contributing

See `COLLABORATION.md` for contribution guidelines.

## License

Proprietary - Glowstone (glowstone.red)

## Support

For issues and questions, contact the Glowstone team.

