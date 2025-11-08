# Gunpowder Splash - Backend

FastAPI-based backend for the Gunpowder Splash collaborative IDE.

## Structure

```
backend/
├── app/                   # Main FastAPI application
│   ├── __init__.py
│   ├── main_beacon.py     # Application entrypoint
│   ├── routers/           # API endpoint routers
│   ├── services/          # Business logic
│   ├── models.py          # SQLAlchemy models
│   └── ...
├── requirements_beacon.txt # Python dependencies
├── schema.sql             # Database schema for reference
└── ...
```

## Running

### Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements_beacon.txt
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

