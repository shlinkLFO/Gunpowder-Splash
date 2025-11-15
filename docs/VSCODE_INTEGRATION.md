# VS Code OSS Integration

Gunpowder Splash integrates **code-server** (VS Code OSS) to provide a full VS Code experience in the browser.

## Architecture

### Current Setup (Phase 1)
- Single code-server instance running in Docker
- Shared workspace accessible to all users
- Password authentication via environment variable
- Accessible at `/code/` path via Nginx proxy

### Components

1. **code-server Service** (`docker-compose.yml`)
   - Runs on port 8080
   - Mounts `./backend/workspace` for file access
   - Uses persistent volumes for config and extensions

2. **Nginx Proxy** (`frontend/nginx.conf`)
   - Routes `/code/` requests to code-server
   - Handles WebSocket upgrades for real-time features
   - Long timeout (24 hours) for persistent connections

3. **CodeEditor Component** (`frontend/src/components/tabs/CodeEditor.tsx`)
   - Embeds code-server in an iframe
   - Full-screen VS Code experience
   - Clipboard access enabled

## Setup Instructions

### 1. Set Password
Add to your `.env` file:
```bash
CODE_SERVER_PASSWORD=your-secure-password
```

### 2. Start Services
```bash
docker-compose up -d
```

### 3. Access VS Code
Navigate to the "Code Editor" tab in the application. The first time you access it, you'll need to enter the password.

## Features

### Available Now
- Full VS Code editor with syntax highlighting
- File explorer and multi-file editing
- Integrated terminal
- Git integration
- Extension marketplace
- Search and replace
- IntelliSense and autocomplete
- Debugging support

### Coming Soon (Phase 2)
- Per-user workspace isolation
- User-specific code-server instances
- GCS-backed persistent workspaces
- Auto-scaling on GCP
- Session management (start/stop on demand)

### Future (Phase 3)
- Live Share for collaboration
- Workspace sharing and permissions
- Shared terminals
- Real-time collaborative editing

## Development

### Local Testing
```bash
# Access code-server directly
curl http://localhost:8080

# Access via Nginx proxy
curl http://localhost/code/
```

### Logs
```bash
docker logs beacon-code-server
```

### Configuration
code-server config is stored in the `code-server-config` volume. To reset:
```bash
docker-compose down
docker volume rm gunpowder-splash_code-server-config
docker-compose up -d
```

## Production Deployment

### GCP Configuration
1. Open port 8080 in GCP firewall (if testing direct access)
2. Ensure SSL certificates are configured in Nginx
3. Set strong CODE_SERVER_PASSWORD in production .env

### Nginx SSL
The code-server proxy inherits SSL configuration from the main Nginx config, ensuring encrypted connections in production.

## Architecture Roadmap

### Phase 2: Multi-User Isolation
```
User Request → Backend Auth → Spawn/Route to User's code-server
                               ↓
                          User-specific workspace (GCS)
```

Each user will get:
- Dedicated code-server container (on-demand)
- Private workspace directory
- Isolated environment variables
- Custom extensions and settings

### Phase 3: Scaling Strategy (GCP)
- **Compute**: GKE or Cloud Run for code-server instances
- **Storage**: GCS buckets for user workspaces
- **Networking**: Cloud Load Balancer for routing
- **Monitoring**: Cloud Logging and Monitoring
- **Cost Optimization**: Auto-shutdown idle instances

## Troubleshooting

### "Connection refused" error
- Check if code-server is running: `docker ps | grep code-server`
- Check logs: `docker logs beacon-code-server`
- Verify port 8080 is exposed

### Password issues
- Ensure CODE_SERVER_PASSWORD is set in .env
- Restart code-server: `docker-compose restart code-server`

### WebSocket connection fails
- Check Nginx proxy configuration
- Verify upgrade headers are set correctly
- Check browser console for errors

### Extensions not working
- Extensions are stored in `code-server-local` volume
- To reinstall, remove volume and restart

## Security Considerations

### Current
- Password authentication
- HTTPS in production
- Same-origin iframe restrictions

### Future Enhancements
- JWT-based authentication integration
- User workspace isolation
- Resource quotas per user
- Network policies
- Audit logging

## Resources

- [code-server GitHub](https://github.com/coder/code-server)
- [VS Code Documentation](https://code.visualstudio.com/docs)
- [Docker Deployment Guide](https://coder.com/docs/code-server/latest/install#docker)

