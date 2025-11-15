# Multi-User VS Code Architecture

## Overview

To provide **secure, isolated VS Code workspaces** for each user, Gunpowder Splash uses a per-user container architecture.

## Security & Privacy

✅ **Each user gets:**
- Their own Docker container running code-server
- Private workspace directory (`/app/workspace/user_{id}`)
- Isolated file system (cannot see other users' files)
- Dedicated port assignment
- Separate processes and resources

## How It Works

### 1. User Opens Code Editor Tab
Frontend calls `/api/v1/code-server/start`

### 2. Backend Spawns Container
```python
# backend/app/services/code_server_manager.py
- Checks if user's container exists
- Creates new container if needed
- Assigns unique port (9000 + user_id)
- Mounts user-specific workspace
```

### 3. Frontend Connects
User's browser connects to `/code/user/{user_id}/`

### 4. Nginx Routes Request
Nginx proxies to the correct port for that user's container

## Port Assignment

- Base port: 9000
- User 1: port 9001
- User 2: port 9002
- User N: port 9000 + N

## Container Lifecycle

### On First Access
1. Container is created
2. Workspace directory initialized with README
3. User can start coding

### On Subsequent Access
- Existing container is started if stopped
- Or connected to if already running

### Auto-Shutdown (Future)
- Stop containers after 30 minutes of inactivity
- Save resources
- Containers restart on next access

## Docker Socket Access

The backend container needs access to the Docker socket to manage per-user containers:

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

**Security Note:** This gives the backend significant permissions. In production:
- Use Docker-in-Docker or
- Use Kubernetes with proper RBAC or
- Use a dedicated container orchestration service

## Nginx Configuration Challenge

**Current Limitation:** Nginx static configuration can't dynamically route to different ports based on user ID.

**Solutions:**

### Option A: Port Range Proxy (Current)
Map a port range in Nginx:
```nginx
# Proxy ports 9000-9100 for up to 100 users
location ~* ^/code/user/(\d+)/(.*)$ {
    set $user_port 900$1;  # Simplified - needs proper calculation
    proxy_pass http://localhost:$user_port/$2;
}
```

### Option B: Dynamic Proxy Service
Create a dedicated reverse proxy that:
1. Reads JWT token
2. Looks up user's container port
3. Proxies request to correct port

### Option C: Use Traefik or Kong
Use a dynamic reverse proxy that auto-discovers containers via Docker labels.

## Production Scaling (GCP)

### Phase 2: GKE (Google Kubernetes Engine)
```
User Request → Ingress → Service → Pod (code-server)
                                    ↓
                               GCS Persistent Volume
                               (User workspace)
```

**Benefits:**
- Auto-scaling based on demand
- Health checks and automatic restarts
- Resource quotas per user
- Native load balancing

### Cost Optimization
- Use preemptible nodes for dev workspaces
- Auto-shutdown after inactivity
- Shared node pools
- GCS for persistent storage (cheaper than persistent disks)

## Testing Locally

### 1. Ensure Docker socket is accessible
```bash
ls -l /var/run/docker.sock
```

### 2. Start services
```bash
docker-compose up -d
```

### 3. Test container management
```bash
# Backend logs
docker logs -f beacon-backend

# List user containers
docker ps | grep code-server-user
```

### 4. Access Code Editor
Navigate to Code Editor tab in the app. Your personal container will start automatically.

## Monitoring

### Check user containers
```bash
# List all user code-server containers
docker ps -a | grep code-server-user

# Check specific user
docker ps -a | grep code-server-user-1

# View logs
docker logs code-server-user-1
```

### Resource usage
```bash
# See memory/CPU usage
docker stats $(docker ps -q --filter name=code-server-user)
```

## Troubleshooting

### Container won't start
```bash
# Check Docker socket permissions
ls -l /var/run/docker.sock

# Check backend logs
docker logs beacon-backend | grep code-server

# Try manual container creation
docker run -d --name test-code-server \
  -p 9999:8080 \
  -v $(pwd)/test-workspace:/home/coder/workspace \
  codercom/code-server:latest \
  --bind-addr 0.0.0.0:8080 --auth none /home/coder/workspace
```

### Can't connect to code-server
1. Check if container is running: `docker ps | grep code-server-user`
2. Check port assignment in backend logs
3. Test direct access: `curl http://localhost:9001` (replace with user's port)
4. Check Nginx proxy configuration

### Workspace files not persisting
- Check volume mount in code_server_manager.py
- Verify workspace directory exists: `ls -la backend/workspace/`
- Check permissions: containers run as user 1000:1000

## Security Considerations

### Current
✅ Per-user containers (process isolation)
✅ Per-user workspaces (file isolation)
✅ JWT authentication required
✅ No container-to-container networking

### Future Enhancements
- [ ] Resource quotas (CPU/memory limits)
- [ ] Network policies
- [ ] Audit logging
- [ ] Workspace encryption at rest
- [ ] Container image scanning

## Known Limitations

1. **Port exhaustion**: Max ~65,000 users per host
2. **Resource overhead**: Each container uses ~200MB RAM minimum
3. **No live collaboration**: Users work in isolated environments
4. **Single host**: Not yet distributed across multiple servers

## Roadmap

### Phase 1 (Current)
- ✅ Per-user containers
- ✅ Per-user workspaces
- ⏳ Nginx dynamic routing
- ⏳ Auto-shutdown idle containers

### Phase 2
- GKE deployment
- GCS-backed workspaces
- Resource quotas
- Horizontal scaling

### Phase 3
- Live Share / collaboration
- Workspace sharing
- Shared terminals

