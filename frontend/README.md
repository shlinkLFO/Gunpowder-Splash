# Gunpowder Splash - Frontend

React + TypeScript frontend for the Gunpowder Splash collaborative IDE.

## Structure

```
frontend/
├── src/
│   ├── App.tsx              # Main application component
│   ├── main.tsx             # Entry point
│   ├── components/          # React components
│   │   ├── FileTree.tsx     # File explorer
│   │   ├── MainContent.tsx  # Main content area
│   │   ├── Sidebar.tsx      # Navigation sidebar
│   │   └── tabs/            # Tab components
│   │       ├── CodeEditor.tsx    # Monaco code editor
│   │       ├── DataExplorer.tsx  # Data visualization
│   │       ├── History.tsx       # Code history
│   │       ├── Notebook.tsx      # Jupyter notebooks
│   │       ├── RainbowCSV.tsx    # CSV editor
│   │       ├── WebEdit.tsx       # HTML/CSS/JS editor
│   │       └── Templates.tsx     # Code templates
│   ├── contexts/            # React contexts
│   ├── hooks/               # Custom hooks
│   ├── styles/              # Global styles & theme
│   └── utils/               # Utility functions
├── index.html               # HTML template
├── vite.config.ts          # Vite configuration
├── package.json            # Dependencies
└── tsconfig.json           # TypeScript config
```

## Running

### Development
```bash
cd frontend
npm install
npm run dev
```

Access at http://localhost:5173

### Build
```bash
npm run build
```

Output in `dist/` directory.

### Preview Production Build
```bash
npm run preview
```

## Technologies

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Chakra UI** - Component library
- **Monaco Editor** - Code editor
- **Socket.IO** - Real-time communication
- **Axios** - HTTP client
- **Zustand** - State management

## Configuration

Edit `vite.config.ts` to configure:
- Server port
- Proxy settings
- Build options

## Environment Variables

Create `.env.local`:
```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8001
```

## Code Style

- Use TypeScript for all new code
- Follow React best practices
- Use functional components with hooks
- Use ESLint and Prettier

## Testing

```bash
npm test
```

