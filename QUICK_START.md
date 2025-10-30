# Quick Start Guide

Get Gunpowder Splash running in under 5 minutes.

## Option 1: Docker (Fastest)

```bash
# Clone the repository
git clone <repository-url>
cd "Gunpowder Splash"

# Start all services
docker-compose up --build
```

Access the application at http://localhost:5173

## Option 2: Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+
- npm

### Setup

1. Install backend dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

3. Start all services:
```bash
./start-dev.sh
```

Or start manually:

```bash
# Terminal 1: WebSocket Server
python3 websocket_server.py

# Terminal 2: Backend API
cd backend
python -m uvicorn app.main:app --reload

# Terminal 3: Frontend
cd frontend
npm run dev
```

### Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8001

## First Steps

1. **Code Editor Tab**: Write and execute Python code
2. **Data Explorer**: Load and analyze datasets
3. **Notebook Tab**: Run Jupyter-style notebooks
4. **Rainbow CSV**: View and edit CSV files
5. **Web-Edit**: Create HTML/CSS/JS projects with live preview

## Features to Try

### Execute Python Code
1. Go to Code Editor tab
2. Write Python code
3. Click "Run" or press Ctrl+Enter
4. See output in the console

### Load Data
1. Go to Data Explorer tab
2. Upload a CSV or Excel file
3. Explore the data with built-in visualizations

### Collaborative Editing
1. Open the same file in multiple browsers
2. See real-time cursor positions
3. Changes sync automatically

## Troubleshooting

### Port Already in Use
```bash
# Kill processes on ports
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
lsof -i :8001 | grep LISTEN | awk '{print $2}' | xargs kill -9
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Dependencies Issues
```bash
# Backend: Update pip
pip install --upgrade pip
pip install -r backend/requirements.txt

# Frontend: Clear cache
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### WebSocket Connection Failed
- Ensure websocket_server.py is running
- Check browser console for errors
- Verify port 8001 is not blocked

## Next Steps

- Read the full [README.md](README.md)
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- Review [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## Getting Help

- Open an issue on GitHub
- Contact the Glowstone team
- Check the documentation at http://localhost:8000/docs

