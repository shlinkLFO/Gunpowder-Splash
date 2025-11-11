# Contributing to Gunpowder Splash

Thank you for your interest in contributing to Gunpowder Splash! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/shlinkLFO/Gunpowder-Splash/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Environment details (OS, browser, etc.)

### Suggesting Features

1. Check [Discussions](https://github.com/shlinkLFO/Gunpowder-Splash/discussions) for similar ideas
2. Create a new discussion with:
   - Clear description of the feature
   - Use case and benefits
   - Potential implementation approach

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Gunpowder-Splash.git
   cd Gunpowder-Splash
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the code style guidelines below
   - Write tests for new features
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Backend tests
   cd backend
   pytest tests/
   
   # Frontend tests
   cd frontend
   npm test
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes (formatting, etc.)
   - `refactor:` Code refactoring
   - `test:` Adding or updating tests
   - `chore:` Maintenance tasks

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**
   - Provide a clear description
   - Reference related issues
   - Include screenshots for UI changes

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Docker (optional)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment
cp ../.env.example .env
# Edit .env with your configuration

# Run database migrations
python -m alembic upgrade head

# Start development server
python -m app.main_beacon
```

### Frontend Setup

```bash
cd frontend
npm install

# Start development server
npm run dev
```

### Docker Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Code Style Guidelines

### Python (Backend)

- Follow [PEP 8](https://pep8.org/)
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for functions and classes

```python
def create_workspace(
    db: Session,
    user_id: str,
    name: str
) -> Workspace:
    """
    Create a new workspace for a user.
    
    Args:
        db: Database session
        user_id: UUID of the user
        name: Workspace name
        
    Returns:
        Created workspace object
    """
    workspace = Workspace(
        user_id=user_id,
        name=name
    )
    db.add(workspace)
    db.commit()
    return workspace
```

### TypeScript (Frontend)

- Use TypeScript strict mode
- Prefer functional components with hooks
- Use meaningful variable names
- Maximum line length: 100 characters

```typescript
interface WorkspaceProps {
  workspaceId: string
  onUpdate: (workspace: Workspace) => void
}

export function WorkspaceCard({ workspaceId, onUpdate }: WorkspaceProps) {
  const [workspace, setWorkspace] = useState<Workspace | null>(null)
  
  useEffect(() => {
    fetchWorkspace(workspaceId).then(setWorkspace)
  }, [workspaceId])
  
  return (
    <Box>
      {workspace && <Text>{workspace.name}</Text>}
    </Box>
  )
}
```

### Git Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- First line should be 50 characters or less
- Reference issues and pull requests

```
feat: add real-time collaboration

- Implement WebSocket connection
- Add cursor tracking
- Update UI for multiple users

Closes #123
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

## Documentation

- Update README.md for user-facing changes
- Update API documentation for endpoint changes
- Add inline comments for complex logic
- Update CHANGELOG.md for notable changes

## Project Structure

```
Gunpowder-Splash/
├── backend/
│   ├── app/
│   │   ├── main_beacon.py      # Main application
│   │   ├── models.py           # Database models
│   │   ├── auth.py             # Authentication
│   │   ├── routers/            # API endpoints
│   │   └── services/           # Business logic
│   ├── tests/                  # Backend tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── lib/                # Utilities
│   │   └── styles/             # Styling
│   └── package.json
├── docs/                       # Documentation
├── terraform/                  # Infrastructure
└── docker-compose.yml
```

## Review Process

1. **Automated Checks**
   - Linting (Python: flake8, TypeScript: ESLint)
   - Type checking (mypy, TypeScript)
   - Tests must pass
   - Code coverage should not decrease

2. **Code Review**
   - At least one maintainer approval required
   - Address all review comments
   - Keep PR scope focused

3. **Merge**
   - Squash and merge for feature branches
   - Maintain clean commit history

## Release Process

1. Version bump in `package.json` and `__version__.py`
2. Update CHANGELOG.md
3. Create release tag
4. Deploy to production

## Getting Help

- **Questions**: Open a [Discussion](https://github.com/shlinkLFO/Gunpowder-Splash/discussions)
- **Bugs**: Open an [Issue](https://github.com/shlinkLFO/Gunpowder-Splash/issues)
- **Chat**: Join our community (coming soon)
- **Email**: dev@shlinx.com

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in the application (for significant contributions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Gunpowder Splash!

