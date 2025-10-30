# Gunpowder Splash - Backend

FastAPI-based backend for the Gunpowder Splash collaborative IDE.

## Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI application entry
│   ├── routers/         # API route handlers
│   │   ├── files.py     # File operations
│   │   ├── data.py      # Data processing
│   │   ├── history.py   # Code history
│   │   ├── notebooks.py # Jupyter notebooks
│   │   ├── system.py    # System operations
│   │   └── templates.py # Code templates
│   └── services/        # Business logic
│       ├── data_service.py
│       ├── execution_service.py
│       ├── file_service.py
│       ├── history_service.py
│       ├── notebook_service.py
│       └── query_service.py
├── workspace/           # User workspace directory
├── requirements.txt     # Python dependencies
└── Dockerfile          # Docker configuration
```

## Running

### Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

- `WORKSPACE_DIR`: Directory for user files (default: workspace)
- `PORT`: Server port (default: 8000)
- `HOST`: Server host (default: 0.0.0.0)

## Testing

```bash
pytest
```

