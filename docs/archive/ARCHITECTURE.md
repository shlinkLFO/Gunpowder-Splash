# Gunpowder Splash - Architecture

## System Overview

Gunpowder Splash is a modern cloud IDE platform built on a three-tier architecture:

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│                    Port 5173 (Dev)                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Monaco Editor │ Data Viz │ Notebook │ CSV Viewer │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────┬────────────────┬───────────────────────┘
                 │                │
        REST API │                │ WebSocket
         (HTTP) │                │ (Real-time)
                 │                │
      ┌──────────▼────────┐  ┌───▼──────────────────┐
      │   Backend API     │  │  WebSocket Server    │
      │   (FastAPI)       │  │  (Collaboration)     │
      │   Port 8000       │  │  Port 8001           │
      └──────────┬────────┘  └──────────────────────┘
                 │
      ┌──────────▼────────┐
      │   Workspace       │
      │   (File System)   │
      └───────────────────┘
```

## Component Architecture

### 1. Frontend Layer

**Technology Stack:**
- React 19 (UI Framework)
- TypeScript (Type Safety)
- Vite (Build Tool)
- Chakra UI (Component Library)
- Monaco Editor (Code Editor)
- Socket.IO (WebSocket Client)
- Zustand (State Management)

**Key Components:**

```
Frontend/
├── Layout Components
│   ├── Sidebar.tsx          # Navigation
│   ├── MainContent.tsx      # Content area
│   └── FileTree.tsx         # File explorer
│
├── Tab Components
│   ├── CodeEditor.tsx       # Code editing
│   ├── Notebook.tsx         # Jupyter notebooks
│   ├── DataExplorer.tsx     # Data visualization
│   ├── RainbowCSV.tsx       # CSV editing
│   ├── WebEdit.tsx          # HTML/CSS/JS preview
│   ├── History.tsx          # Execution history
│   ├── Templates.tsx        # Code templates
│   └── System.tsx           # System info
│
└── Infrastructure
    ├── contexts/            # React contexts
    ├── hooks/              # Custom hooks
    ├── styles/             # Theme & styling
    └── utils/              # Helper functions
```

**State Management:**
- Local state: React useState/useReducer
- Global state: Zustand stores
- Server state: React Query (TanStack Query)
- Real-time state: WebSocket events

### 2. Backend Layer

**Technology Stack:**
- FastAPI (Web Framework)
- Python 3.11+ (Runtime)
- Uvicorn (ASGI Server)
- Pandas (Data Processing)
- Plotly (Visualization)
- Aiofiles (Async File I/O)

**Architecture Pattern:**
```
Backend/
├── Routers (API Endpoints)
│   ├── files.py             # CRUD operations
│   ├── data.py              # Data processing
│   ├── history.py           # History tracking
│   ├── notebooks.py         # Notebook execution
│   ├── system.py            # System operations
│   └── templates.py         # Template management
│
├── Services (Business Logic)
│   ├── file_service.py      # File operations
│   ├── data_service.py      # Data handling
│   ├── execution_service.py # Code execution
│   ├── notebook_service.py  # Notebook logic
│   ├── history_service.py   # History management
│   └── query_service.py     # Data queries
│
└── Infrastructure
    ├── main.py              # App initialization
    └── models/              # Data models
```

**API Design:**
- RESTful endpoints
- Async/await for I/O operations
- Dependency injection
- Automatic API documentation (Swagger/ReDoc)

### 3. WebSocket Layer

**Technology Stack:**
- WebSockets (Protocol)
- Python asyncio (Event Loop)
- JSON (Message Format)

**Features:**
- Real-time code synchronization
- User presence tracking
- Cursor position sharing
- File state management
- Broadcast messaging

**Message Types:**
```python
{
    'code_update': 'Update code in editor',
    'file_open': 'User opened a file',
    'file_close': 'User closed a file',
    'file_update': 'File content changed',
    'cursor_update': 'Cursor position moved',
    'chat_message': 'Chat communication',
    'ping/pong': 'Connection health check'
}
```

## Data Flow

### 1. File Operations

```
User Action → Frontend → HTTP Request → Backend Router
                                           ↓
                                     File Service
                                           ↓
                                    Filesystem I/O
                                           ↓
                                   WebSocket Broadcast
                                           ↓
                              All Connected Clients ← Update UI
```

### 2. Code Execution

```
User Runs Code → Frontend → POST /execute
                                ↓
                         Execution Service
                                ↓
                    Python exec() in isolated context
                                ↓
                     Capture stdout/stderr
                                ↓
                    Save to history (optional)
                                ↓
                    Return results to frontend
                                ↓
                         Display output
```

### 3. Real-time Collaboration

```
User Types → Frontend detects change
                    ↓
            Debounced WebSocket send
                    ↓
            WebSocket Server receives
                    ↓
        Update server file state
                    ↓
    Broadcast to other users
                    ↓
    Other clients receive update
                    ↓
    Update their editor (if not editing)
```

## Security Architecture

### Authentication & Authorization
- Session-based authentication (to be implemented)
- CORS configuration for API access
- Path traversal protection
- File system sandboxing

### Code Execution Safety
- Isolated execution contexts per session
- Resource limits (to be implemented)
- Stdout/stderr capture and sanitization
- No shell command execution by default

### Data Protection
- Environment variable secrets
- Workspace isolation
- File access validation
- HTTPS in production

## Scalability Considerations

### Horizontal Scaling
```
              Load Balancer
                   ↓
    ┌──────────────┼──────────────┐
    ↓              ↓              ↓
Backend 1     Backend 2     Backend 3
    ↓              ↓              ↓
           Shared Workspace
          (NFS / S3 / GCS)
```

### Current Limitations
- Single WebSocket server (not horizontally scalable)
- File system workspace (not distributed)
- In-memory session state

### Future Improvements
- Redis for shared state
- S3/GCS for workspace storage
- WebSocket server clustering
- Database for metadata
- Caching layer (Redis/Memcached)

## Development Workflow

```
Developer → Edit Code → Git Commit
                ↓
        Push to Repository
                ↓
        CI/CD Pipeline
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
  Test      Build      Deploy
    ↓           ↓           ↓
  Pass    Docker Images  Production
```

## Deployment Architecture

### Development
```
Local Machine
├── Terminal 1: WebSocket Server (8001)
├── Terminal 2: Backend API (8000)
└── Terminal 3: Frontend Dev Server (5173)
```

### Docker Compose
```
Docker Network
├── Backend Container (8000)
├── WebSocket Container (8001)
└── Frontend Container (80)
```

### Production (Cloud)
```
                Internet
                   ↓
            Load Balancer / CDN
                   ↓
        ┌──────────┼──────────┐
        ↓          ↓          ↓
    Nginx    API Server  WebSocket
    (Static)  (Backend)   (Real-time)
        ↓          ↓          ↓
    Frontend    Database  Cache
    Build       (Future)  (Future)
```

## Technology Decisions

### Why FastAPI?
- High performance (async support)
- Automatic API documentation
- Type checking with Pydantic
- Modern Python features

### Why React?
- Component reusability
- Large ecosystem
- Performance optimizations
- Developer experience

### Why WebSocket?
- Real-time bidirectional communication
- Lower latency than polling
- Native browser support
- Event-driven architecture

### Why Monaco Editor?
- VS Code editor engine
- Excellent language support
- Customizable
- TypeScript support

### Why Chakra UI?
- Accessible by default
- Composable components
- Theming support
- TypeScript support

## Performance Considerations

### Frontend Optimization
- Code splitting
- Lazy loading components
- Memoization (React.memo, useMemo)
- Virtualization for large lists
- Debouncing user input

### Backend Optimization
- Async I/O operations
- Connection pooling (future)
- Response caching (future)
- Pagination for large datasets
- Streaming large files

### Network Optimization
- Compression (gzip)
- HTTP/2
- WebSocket compression
- CDN for static assets (production)
- API response caching

## Monitoring & Observability

### To Be Implemented
- Application logging
- Error tracking (Sentry)
- Performance monitoring
- User analytics
- Health check endpoints

### Current Health Checks
- Backend: `GET /health`
- Frontend: Nginx health endpoint
- WebSocket: Ping/pong messages

## Future Architecture Enhancements

1. **Authentication System**
   - User registration/login
   - JWT tokens
   - OAuth integration

2. **Database Layer**
   - PostgreSQL for metadata
   - User profiles
   - Project management
   - Permissions system

3. **Storage Layer**
   - S3-compatible object storage
   - Version control integration
   - Backup automation

4. **Compute Layer**
   - Containerized code execution
   - Resource limits
   - Queue system for long-running tasks

5. **Collaboration Enhancements**
   - Video chat integration
   - Real-time chat
   - Comments and annotations
   - Conflict resolution

## Conclusion

Gunpowder Splash follows modern web application architecture patterns with a clear separation of concerns, enabling independent scaling and development of each component. The system is designed for extensibility and can evolve to support enterprise-scale deployments.

