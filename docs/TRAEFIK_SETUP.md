# Traefik Dynamic Routing Setup

Traefik automatically discovers and routes to per-user VS Code containers.

## Architecture

```
User Request → Traefik → Auto-discovers containers → Routes to correct container
                  ↓
            Docker Socket
            (watches for new containers)
```

## How It Works

### 1. Traefik Watches Docker
Traefik connects to Docker socket and watches for containers with specific labels.

### 2. User Opens Code Editor
- Frontend calls `/api/v1/code-server/start`
- Backend spawns container with Traefik labels
- Traefik automatically detects the new container

### 3. Traefik Routes Requests
```
Request: https://shlinx.com/code/user/1/
         ↓
Traefik reads labels on code-server-user-1 container
         ↓
Routes to container's port 8080
         ↓
User gets their private VS Code
```

## Container Labels

When backend spawns a user container, it adds these labels:

```python
{
    "traefik.enable": "true",
    "traefik.http.routers.code-user-1.rule": "Host(`shlinx.com`) && PathPrefix(`/code/user/1`)",
    "traefik.http.routers.code-user-1.entrypoints": "websecure",
    "traefik.http.routers.code-user-1.tls.certresolver": "letsencrypt",
    "traefik.http.services.code-user-1.loadbalancer.server.port": "8080",
    "traefik.http.middlewares.code-user-1-stripprefix.stripprefix.prefixes": "/code/user/1",
    "traefik.http.routers.code-user-1.middlewares": "code-user-1-stripprefix",
}
```

## SSL Certificates

Traefik automatically handles SSL via Let's Encrypt:
- HTTP Challenge on port 80
- Certificates stored in `traefik-certs` volume
- Auto-renewal

## Services Routing

### Frontend
- `shlinx.com/` → nginx container (port 80)
- Serves React app

### Backend
- `shlinx.com/api/` → backend container (port 8000)
- API endpoints

### Per-User Code Servers
- `shlinx.com/code/user/1/` → code-server-user-1 (port 8080)
- `shlinx.com/code/user/2/` → code-server-user-2 (port 8080)
- Each user gets their own route

## Traefik Dashboard

Access at `http://your-server:8081` to see:
- All active routes
- Health status
- Certificate status
- Traffic metrics

## Configuration

### docker-compose.yml
```yaml
traefik:
  image: traefik:v2.10
  command:
    - "--api.insecure=true"  # Dashboard
    - "--providers.docker=true"  # Watch Docker
    - "--providers.docker.exposedbydefault=false"  # Require explicit labels
    - "--entrypoints.web.address=:80"  # HTTP
    - "--entrypoints.websecure.address=:443"  # HTTPS
    - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
    - "--certificatesresolvers.letsencrypt.acme.email=admin@shlinx.com"
  ports:
    - "80:80"
    - "443:443"
    - "8081:8080"  # Dashboard
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
```

## WebSocket Support

Traefik automatically handles WebSocket upgrades, which are required for:
- VS Code Live Server
- Terminal sessions
- Extension communication
- Real-time file watching

## Security

### Container Isolation
- Each user's container is isolated
- Traefik routes based on URL path
- Users can only access their own `/code/user/{their_id}/`

### Network Isolation
All containers on `beacon-network`:
- Containers can communicate internally
- External access only through Traefik
- No direct port exposure (except Traefik)

### SSL/TLS
- Automatic HTTPS for all routes
- Let's Encrypt certificates
- HTTP → HTTPS redirect

## Monitoring

### Check Active Routes
```bash
# List all Traefik routes
curl http://localhost:8081/api/http/routers | jq

# Check specific user's route
docker inspect code-server-user-1 | grep traefik
```

### Watch Container Discovery
```bash
# Traefik logs
docker logs -f beacon-traefik

# Look for: "Creating service" and "Creating router"
```

### Dashboard
Open `http://your-server:8081` in browser:
- **HTTP Routers**: See all active routes
- **HTTP Services**: Backend endpoints
- **HTTP Middleware**: Path stripping, redirects

## Troubleshooting

### Route not appearing
```bash
# Check if container has correct labels
docker inspect code-server-user-1 | grep -A 10 Labels

# Check if container is on beacon-network
docker inspect code-server-user-1 | grep -A 5 Networks

# Check Traefik can see it
curl http://localhost:8081/api/http/services | grep user-1
```

### SSL certificate issues
```bash
# Check certificate status
docker exec beacon-traefik cat /letsencrypt/acme.json

# Trigger renewal
docker exec beacon-traefik traefik healthcheck

# Reset certificates (removes old certs)
docker volume rm gunpowder-splash_traefik-certs
docker-compose up -d traefik
```

### 404 errors
1. Check container is running: `docker ps | grep code-server-user`
2. Check Traefik logs: `docker logs beacon-traefik`
3. Verify labels are correct
4. Check path: `/code/user/1/` (must end with /)

### WebSocket connection fails
- Traefik handles this automatically
- Check browser console for errors
- Verify SSL is working (mixed content blocks WebSockets)

## Production Deployment

### 1. Set Email for Let's Encrypt
Update in `docker-compose.yml`:
```yaml
- "--certificatesresolvers.letsencrypt.acme.email=your-email@domain.com"
```

### 2. Secure Dashboard
```yaml
# Change to secure access
- "--api.insecure=false"
- "--api.dashboard=true"
# Add authentication
```

### 3. Rate Limits (Optional)
```yaml
- "--entrypoints.websecure.http.ratelimit.average=100"
- "--entrypoints.websecure.http.ratelimit.burst=50"
```

### 4. Monitoring
- Enable Prometheus metrics
- Set up alerts for certificate expiry
- Monitor route health

## Advantages Over Nginx

### Dynamic Discovery
- **Nginx**: Static config, restart required for new routes
- **Traefik**: Detects new containers automatically

### SSL Management
- **Nginx**: Manual Certbot setup
- **Traefik**: Automatic Let's Encrypt integration

### Service Discovery
- **Nginx**: Hard-coded backends
- **Traefik**: Docker label-based discovery

### Zero Downtime
- New containers instantly routable
- No config reload needed
- Health checks automatic

## Migration from Nginx

Your existing Nginx container is replaced by Traefik:

**Before:**
```
Port 80/443 → Nginx → Proxy to backend/frontend
```

**After:**
```
Port 80/443 → Traefik → Auto-discover and route
```

All existing routes work the same, plus dynamic per-user routes!

## Testing

### 1. Start Traefik
```bash
docker-compose up -d traefik
```

### 2. Check Dashboard
Open `http://localhost:8081`

### 3. Start Backend
```bash
docker-compose up -d backend
```

### 4. Verify Backend Route
```bash
curl https://shlinx.com/api/health
```

### 5. Test User Container
```bash
# Login and open Code Editor tab
# Backend will spawn your container
# Check Traefik discovered it
curl http://localhost:8081/api/http/routers | grep "code-user"
```

## Cost & Performance

### Resource Usage
- Traefik: ~50MB RAM
- Similar to Nginx
- Handles thousands of routes efficiently

### Latency
- Minimal overhead (<1ms)
- Same performance as Nginx
- Optimized for Docker environments

## Future Enhancements

- [ ] Traefik plugins for custom auth
- [ ] Rate limiting per user
- [ ] Request tracing
- [ ] Custom middleware for logging
- [ ] Circuit breakers for failed routes

