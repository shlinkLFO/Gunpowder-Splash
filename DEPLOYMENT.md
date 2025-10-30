# Deployment Guide

This guide covers deploying Gunpowder Splash to various environments.

## Prerequisites

- Docker and Docker Compose (recommended)
- Python 3.11+ (manual deployment)
- Node.js 20+ (manual deployment)
- Reverse proxy (nginx/Apache) for production

## Docker Deployment (Recommended)

### Development
```bash
docker-compose up --build
```

### Production
```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f
```

## Manual Deployment

### Backend

1. Install dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp ../.env.example .env
# Edit .env with production values
```

3. Run with production server:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### WebSocket Server

```bash
python3 websocket_server.py
```

### Frontend

1. Build the frontend:
```bash
cd frontend
npm install
npm run build
```

2. Serve with nginx:
```bash
# Copy dist/ to nginx web root
cp -r dist/* /var/www/html/
```

## Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Frontend
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
```

## Environment Variables

### Backend (.env)
```
WORKSPACE_DIR=/app/workspace
PORT=8000
HOST=0.0.0.0
SECRET_KEY=your-production-secret
CORS_ORIGINS=https://your-domain.com
DEBUG=false
```

## Cloud Platforms

### AWS

1. **EC2 Instance**
   - Launch Ubuntu 22.04 instance
   - Install Docker
   - Clone repository
   - Run with docker-compose

2. **Elastic Beanstalk**
   - Use docker-compose.yml
   - Configure environment variables
   - Deploy with EB CLI

### Google Cloud Platform

```bash
# Build and push images
gcloud builds submit --tag gcr.io/PROJECT_ID/gunpowder-splash

# Deploy to Cloud Run
gcloud run deploy gunpowder-splash \
  --image gcr.io/PROJECT_ID/gunpowder-splash \
  --platform managed
```

### DigitalOcean

1. Create Droplet (Ubuntu 22.04)
2. Install Docker
3. Clone repository
4. Run docker-compose

### Heroku

Not recommended due to WebSocket limitations. Consider using AWS or GCP instead.

## Monitoring

### Health Checks

- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:5173/health` (via nginx)

### Logs

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f websocket
docker-compose logs -f frontend

# System logs
tail -f /var/log/nginx/access.log
```

## Backup

Regular backups of the workspace directory:
```bash
tar -czf backup-$(date +%Y%m%d).tar.gz backend/workspace/
```

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Configure CORS origins properly
- [ ] Enable HTTPS with valid certificates
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Monitor application logs
- [ ] Implement rate limiting
- [ ] Use environment variables for secrets

## Scaling

### Horizontal Scaling

1. Use load balancer (nginx/HAProxy)
2. Run multiple backend instances
3. Share workspace via NFS or S3
4. Use Redis for session storage

### Vertical Scaling

- Increase server resources
- Optimize database queries
- Enable caching
- Use CDN for static assets

## Troubleshooting

### Port conflicts
```bash
# Check port usage
lsof -i :8000
lsof -i :8001
lsof -i :5173
```

### Permission issues
```bash
# Fix workspace permissions
chmod -R 755 backend/workspace
```

### WebSocket connection issues
- Check firewall rules
- Verify proxy configuration
- Ensure WebSocket protocol upgrade

## Support

For deployment issues, contact the Glowstone team.

