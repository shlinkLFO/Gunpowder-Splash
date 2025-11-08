# Beacon Studio - Quick Start for Developers

This guide gets you up and running with Beacon Studio development in under 30 minutes.

---

## Prerequisites

Install these tools:

```bash
# macOS
brew install python@3.11 postgresql docker node yarn gcloud
```

Clone the repository and navigate to the project:

```bash
cd "Gunpowder Splash"
```

---

## Local Development Setup

### 1. Database (2 minutes)

```bash
# Start PostgreSQL
brew services start postgresql

# Create database
createdb beacon_studio

# Apply schema
psql beacon_studio < backend/schema.sql
```

### 2. Backend (3 minutes)

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements_beacon.txt

# Create .env file
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://localhost:5432/beacon_studio

# Security (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-here

# Google OAuth (get from https://console.cloud.google.com/)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-secret

# GitHub OAuth (get from https://github.com/settings/developers)
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-secret

# Local development
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]

# GCS (optional for local dev - can use local filesystem)
GCS_BUCKET_NAME=beacon-local-files
GCS_PROJECT_ID=beacon-studio-dev
EOF

# Run backend
python -m app.main_beacon
```

Backend now running at: http://localhost:8000

Test it:
```bash
curl http://localhost:8000/health
```

### 3. Frontend Development (Later)

When ready to work on the Code OSS integration:

```bash
# Clone Code OSS
git clone https://github.com/microsoft/vscode.git beacon-editor
cd beacon-editor
git checkout 1.85.0

# Install dependencies
yarn install

# Build for web
yarn gulp vscode-web-min

# The built web app will be in ../vscode-web
```

---

## API Testing

### Get OAuth Login URL

```bash
# Google
curl http://localhost:8000/api/v1/auth/login/google

# GitHub
curl http://localhost:8000/api/v1/auth/login/github
```

### Manual Token Creation (for testing)

```python
# In Python shell
from app.auth import create_access_token
import uuid

# Create test token
user_id = "123e4567-e89b-12d3-a456-426614174000"
token = create_access_token(data={"sub": user_id})
print(token)
```

### Test Protected Endpoints

```bash
# Set token
TOKEN="your-jwt-token-here"

# List workspaces
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/workspaces

# Create project
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"workspace_id":"workspace-id","name":"Test Project"}' \
  http://localhost:8000/api/v1/projects
```

---

## Project Structure

```
backend/
├── app/
│   ├── main_beacon.py        # FastAPI app (START HERE)
│   ├── config.py             # Environment configuration
│   ├── database.py           # Database connection
│   ├── models.py             # ORM models
│   ├── auth.py               # JWT & auth
│   ├── oauth.py              # OAuth providers
│   ├── storage.py            # GCS integration
│   ├── ai_providers.py       # AI integration
│   └── routers/
│       ├── auth.py           # /auth/* endpoints
│       ├── workspaces.py     # /workspaces/* endpoints
│       ├── projects.py       # /projects/* endpoints
│       ├── billing.py        # /billing/* endpoints
│       └── ai.py             # /ai/* endpoints
└── schema.sql                # Database schema
```

---

## Common Tasks

### Add a New Endpoint

1. Create route in appropriate router file (e.g., `routers/projects.py`)
2. Use dependencies for auth: `Depends(get_current_user)`
3. Use database session: `Depends(get_db)`
4. Return Pydantic models for type safety

Example:

```python
@router.get("/projects/{project_id}/stats")
async def get_project_stats(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check access
    project, role = check_project_access(db, current_user.id, project_id)
    
    # Get stats
    file_count = db.query(File).filter(File.project_id == project_id).count()
    
    return {
        "project_id": str(project_id),
        "file_count": file_count
    }
```

### Add a Database Migration

```bash
# Install alembic
pip install alembic

# Initialize alembic
alembic init alembic

# Create migration
alembic revision -m "add new column"

# Edit the generated file in alembic/versions/
# Apply migration
alembic upgrade head
```

### Test Storage Operations

```python
from app.storage import storage_service
from app.database import get_db_context
import uuid

workspace_id = uuid.uuid4()
project_id = uuid.uuid4()

with get_db_context() as db:
    # Upload file
    storage_service.write_file(
        db=db,
        workspace_id=workspace_id,
        project_id=project_id,
        file_path="test.txt",
        content=b"Hello, Beacon!"
    )
    
    # Read file
    content = storage_service.read_file(
        workspace_id=workspace_id,
        project_id=project_id,
        file_path="test.txt"
    )
    print(content)
```

### Test AI Integration

```python
import asyncio
from app.ai_providers import get_ai_provider, ChatRequest, ChatMessage

async def test_ai():
    # Using Gemini
    provider = get_ai_provider("gemini")
    
    request = ChatRequest(
        messages=[
            ChatMessage(role="user", content="Explain Python decorators")
        ]
    )
    
    response = await provider.chat(request)
    print(response.message.content)

asyncio.run(test_ai())
```

---

## Documentation

- **Spec**: `beacon-studio-spec.md` - Product requirements
- **Migration Plan**: `BEACON_MIGRATION_PLAN.md` - Full roadmap
- **Setup Guide**: `SETUP_GUIDE_BEACON.md` - Production deployment
- **Code OSS Guide**: `CODE_OSS_INTEGRATION.md` - Frontend integration
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md` - What's done

---

## API Documentation

Once backend is running, view interactive API docs:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

---

## Development Workflow

### 1. Backend Feature Development

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# Test manually or write tests

# Run linting
black app/
flake8 app/

# Commit and push
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
```

### 2. Database Changes

```bash
# Make changes to models.py
# Create migration
alembic revision --autogenerate -m "describe change"

# Review generated migration file
# Apply to local database
alembic upgrade head

# Test thoroughly
# Commit migration file
```

### 3. Testing

```bash
# Install pytest
pip install pytest pytest-asyncio httpx

# Write tests in tests/
# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

---

## Troubleshooting

### Database Connection Failed

```bash
# Check PostgreSQL is running
brew services list | grep postgresql

# Check connection
psql beacon_studio -c "SELECT 1"

# Reset database
dropdb beacon_studio
createdb beacon_studio
psql beacon_studio < backend/schema.sql
```

### OAuth Not Working

- Verify redirect URIs match exactly in OAuth provider settings
- Check client ID and secret are correct
- Ensure state parameter is being generated and validated

### Storage Quota Not Enforcing

- Check workspace.storage_used_bytes in database
- Verify plan.storage_limit_bytes is set correctly
- Test with small quota to see enforcement

### Import Errors

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements_beacon.txt

# Check Python version
python --version  # Should be 3.11+
```

---

## Next Steps

1. **Get familiar with the codebase**
   - Read through `main_beacon.py`
   - Explore the routers
   - Review the data models

2. **Test the backend locally**
   - Create test user
   - Create workspace and project
   - Upload some files
   - Test quota enforcement

3. **Start on Code OSS integration**
   - Follow `CODE_OSS_INTEGRATION.md`
   - Build Code OSS for web
   - Implement file system provider
   - Add Beacon UI components

4. **Deploy to staging**
   - Follow `SETUP_GUIDE_BEACON.md`
   - Deploy infrastructure with Terraform
   - Deploy backend to Cloud Run
   - Test in cloud environment

---

## Getting Help

- **Spec Questions**: See `beacon-studio-spec.md`
- **Technical Issues**: See `IMPLEMENTATION_SUMMARY.md`
- **Deployment**: See `SETUP_GUIDE_BEACON.md`
- **Legal/Compliance**: See `LICENSES_BEACON.md`

---

## Key Commands Reference

```bash
# Backend
cd backend
source venv/bin/activate
python -m app.main_beacon

# Database
psql beacon_studio
\dt                          # List tables
\d+ workspace                # Describe table

# API Testing
curl http://localhost:8000/health
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/v1/workspaces

# Code Quality
black app/                   # Format code
flake8 app/                  # Lint
pytest tests/                # Run tests
```

---

**Happy coding! Build something amazing with Beacon Studio.**

