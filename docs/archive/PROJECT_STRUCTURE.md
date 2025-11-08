# Project Structure

Gunpowder Splash follows a clean separation between frontend and backend.

## Root Directory

```
Gunpowder Splash/
├── backend/                 # FastAPI backend application
├── frontend/                # React frontend application
├── websocket_server.py      # Real-time collaboration server
├── docker-compose.yml       # Docker orchestration
├── Dockerfile.websocket     # WebSocket server Docker image
├── start-dev.sh            # Development startup script
├── README.md               # Main documentation
├── QUICK_START.md          # Quick start guide
├── DEPLOYMENT.md           # Deployment instructions
├── CONTRIBUTING.md         # Contribution guidelines
├── SECURITY.md             # Security policies
├── COLLABORATION.md        # Collaboration features
├── Makefile                # Build automation
└── .gitignore              # Git ignore rules
```

## Backend Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application entry point
│   ├── routers/            # API endpoints (grouped by feature)
│   │   ├── __init__.py
│   │   ├── files.py        # File CRUD operations
│   │   ├── data.py         # Data loading and processing
│   │   ├── history.py      # Code execution history
│   │   ├── notebooks.py    # Jupyter notebook support
│   │   ├── system.py       # System information
│   │   └── templates.py    # Code templates
│   ├── services/           # Business logic layer
│   │   ├── __init__.py
│   │   ├── data_service.py       # Data processing
│   │   ├── execution_service.py  # Code execution
│   │   ├── file_service.py       # File operations
│   │   ├── history_service.py    # History management
│   │   ├── notebook_service.py   # Notebook execution
│   │   └── query_service.py      # Data queries
│   └── models/             # Data models (if needed)
│       └── __init__.py
├── workspace/              # User workspace directory
│   ├── data/              # Sample data files
│   └── ...                # User-created files
├── requirements.txt        # Python dependencies
├── Dockerfile             # Backend Docker image
└── README.md              # Backend documentation
```

## Frontend Structure

```
frontend/
├── src/
│   ├── App.tsx                   # Root application component
│   ├── main.tsx                  # Application entry point
│   ├── vite-env.d.ts            # Vite type definitions
│   ├── components/               # React components
│   │   ├── FileTree.tsx         # File explorer tree
│   │   ├── MainContent.tsx      # Main content area
│   │   ├── Sidebar.tsx          # Left navigation sidebar
│   │   └── tabs/                # Tab content components
│   │       ├── CodeEditor.tsx        # Monaco editor integration
│   │       ├── DataExplorer.tsx      # Data visualization
│   │       ├── History.tsx           # Execution history
│   │       ├── InlineNotebook.tsx    # Inline notebook cells
│   │       ├── Notebook.tsx          # Jupyter notebook
│   │       ├── QueryFilter.tsx       # SQL query interface
│   │       ├── RainbowCSV.tsx        # CSV viewer/editor
│   │       ├── System.tsx            # System information
│   │       ├── Templates.tsx         # Code templates
│   │       └── WebEdit.tsx           # HTML/CSS/JS editor
│   ├── contexts/                # React context providers
│   ├── hooks/                   # Custom React hooks
│   ├── pages/                   # Page components
│   ├── styles/                  # Styling and theming
│   │   ├── global.css          # Global styles
│   │   └── theme.ts            # Chakra UI theme
│   └── utils/                   # Utility functions
├── index.html                   # HTML entry point
├── package.json                 # Node dependencies
├── tsconfig.json               # TypeScript configuration
├── tsconfig.node.json          # TypeScript config for build
├── vite.config.ts              # Vite configuration
├── Dockerfile                  # Frontend Docker image
├── nginx.conf                  # Nginx configuration for production
└── README.md                   # Frontend documentation
```

## WebSocket Server

```
websocket_server.py             # Standalone collaboration server
├── CollaborationServer class   # Main server logic
├── User management            # Track connected users
├── File state management      # Sync file changes
└── Cursor tracking            # Real-time cursor positions
```

## Key Design Patterns

### Backend
- **Routers**: Group related endpoints
- **Services**: Business logic separation
- **Async/Await**: Non-blocking operations
- **Dependency Injection**: FastAPI dependencies

### Frontend
- **Component Composition**: Reusable UI components
- **Hooks**: Functional component logic
- **Context**: Global state management
- **Tab-based Navigation**: Multi-view interface

### Real-time Communication
- **WebSocket**: Bidirectional real-time sync
- **Message Types**: Structured event protocol
- **State Synchronization**: Optimistic updates

## Data Flow

1. **User Action** (Frontend)
   - User interacts with UI
   - Action triggers React state update

2. **API Request** (Frontend → Backend)
   - Axios makes HTTP request
   - FastAPI router receives request
   - Service layer processes logic
   - Response sent back to frontend

3. **WebSocket Updates** (Real-time)
   - Changes broadcast to all clients
   - Frontend receives update
   - UI updates automatically

4. **File Operations** (Backend)
   - Files stored in workspace/
   - Read/write through file service
   - Changes tracked in history

## Configuration Files

- `vite.config.ts` - Frontend build configuration
- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies
- `docker-compose.yml` - Container orchestration
- `.gitignore` - Git ignore patterns
- `tsconfig.json` - TypeScript compiler options

## Workspace Directory

The `workspace/` directory contains:
- User-created files
- Uploaded datasets
- Analysis scripts
- Jupyter notebooks
- History snapshots

This directory is excluded from git and should be backed up separately.

## Port Allocation

- **5173**: Frontend development server (Vite)
- **8000**: Backend API (FastAPI/Uvicorn)
- **8001**: WebSocket server (Collaboration)

## Environment Variables

See `.env.example` for configuration options.

