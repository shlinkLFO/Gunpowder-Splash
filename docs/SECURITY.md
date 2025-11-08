# Security & Production Readiness

## ⚠️ IMPORTANT: Current Limitations

This collaborative IDE implementation is designed for **trusted team environments** on a **private domain**. Before deploying to a public-facing domain, you MUST implement the security enhancements described below.

---

## Current State

### What Works
- ✅ Real-time code synchronization
- ✅ User presence indicators
- ✅ Automatic reconnection
- ✅ Bidirectional communication
- ✅ SSL/TLS support (when properly configured)

### What's Missing for Production
- ❌ **No Authentication**: Anyone who knows the URL can join
- ❌ **No Authorization**: All users can edit everything
- ❌ **No Conflict Resolution**: Concurrent edits may overwrite each other
- ❌ **No Rate Limiting**: Vulnerable to spam/abuse
- ❌ **No Origin Checking**: Susceptible to CSRF attacks

---

## Security Risks

### 1. Unauthenticated Access
**Risk**: Anyone can connect to `wss://glowstone.red/ws` and view/edit code

**Impact**: 
- Unauthorized users can see your code
- Malicious actors can modify or delete code
- No audit trail of who made changes

**Mitigation** (Required for public deployment):
```python
# In websocket_server.py
async def handler(self, websocket, path):
    # Verify authentication token
    auth_header = websocket.request_headers.get('Authorization')
    if not auth_header or not verify_token(auth_header):
        await websocket.close(1008, "Authentication required")
        return
    
    # Continue with normal flow...
```

### 2. Concurrent Edit Conflicts
**Risk**: When two users edit the same file simultaneously, last-write-wins

**Example**:
- User A types: "hello"
- User B types: "world"
- Result: Only "world" remains (User A's work lost)

**Mitigation Options**:

#### Option A: Operational Transformation (OT)
```python
# Install: pip install pyot
from pyot import OT

# Apply transformations to resolve conflicts
transformed = OT.transform(user_a_edit, user_b_edit)
```

#### Option B: CRDTs (Recommended)
```python
# Install: pip install ypy
import y_py as Y

doc = Y.YDoc()
text = doc.get_text("code")
# Automatically resolves conflicts
```

#### Option C: Locking (Simple but Limited)
```python
# In websocket_server.py
FILE_LOCKS = {}

async def acquire_lock(user_id, file):
    if file in FILE_LOCKS:
        return False  # File is locked
    FILE_LOCKS[file] = user_id
    return True
```

### 3. CSRF & Origin Validation
**Risk**: Malicious websites can connect to your WebSocket

**Mitigation**:
```python
# In websocket_server.py
async def handler(self, websocket, path):
    origin = websocket.request_headers.get('Origin')
    allowed_origins = ['https://glowstone.red', 'https://www.glowstone.red']
    
    if origin not in allowed_origins:
        await websocket.close(1008, "Invalid origin")
        return
```

---

## Deployment Scenarios

### Scenario 1: Private Team (glowstone.red - current use case)
**Setup**: Deployed on your own domain for your team only

**Required Security**:
1. **Firewall**: Restrict WebSocket port to known IPs
   ```bash
   sudo ufw allow from 192.168.1.0/24 to any port 8001
   ```

2. **Password Protection** (Nginx):
   ```nginx
   location /ws {
       auth_basic "Restricted";
       auth_basic_user_file /etc/nginx/.htpasswd;
       proxy_pass http://127.0.0.1:8001;
   }
   ```

3. **VPN**: Require VPN connection to access
   - Use WireGuard or OpenVPN
   - Only allow WebSocket access through VPN

**Risk Level**: Low (trusted team, private network)

### Scenario 2: Public Deployment
**Setup**: Open to internet users

**Required Security** (All of the above plus):
1. **User Authentication System**
   ```python
   # Example with JWT tokens
   import jwt
   
   def verify_token(token):
       try:
           payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
           return payload['user_id']
       except:
           return None
   ```

2. **Session Management**
   - Tie WebSocket connections to authenticated sessions
   - Use HTTP-only cookies for session tokens
   - Implement session timeout

3. **Rate Limiting**
   ```python
   from collections import defaultdict
   import time
   
   user_message_count = defaultdict(list)
   
   def rate_limit_check(user_id):
       now = time.time()
       messages = user_message_count[user_id]
       # Remove messages older than 1 minute
       messages[:] = [t for t in messages if now - t < 60]
       
       if len(messages) >= 100:  # Max 100 messages per minute
           return False
       
       messages.append(now)
       return True
   ```

4. **HTTPS Only**: Force all traffic through HTTPS
   ```nginx
   # Redirect HTTP to HTTPS
   server {
       listen 80;
       return 301 https://$host$request_uri;
   }
   ```

**Risk Level**: High (public access requires full security stack)

---

## Recommended Architecture for Production

```
[User Browser]
    ↓ HTTPS
[Cloudflare/CDN] ← DDoS protection, rate limiting
    ↓ HTTPS
[Nginx Reverse Proxy] ← SSL termination, origin check
    ↓ Local HTTP
[Auth Middleware] ← Verify JWT, check permissions
    ↓ WebSocket
[Collaboration Server] ← CRDT/OT, state management
    ↓
[PostgreSQL] ← Store document versions, audit log
```

---

## Implementation Timeline

### Phase 1: Current (Trusted Team Only)
- ✅ Basic WebSocket collaboration
- ✅ User presence
- ✅ Real-time sync
- ⚠️ **Use with IP whitelist only**

### Phase 2: Authentication (Required for Public)
- [ ] Add JWT authentication
- [ ] Session management
- [ ] Origin validation
- [ ] User roles (editor vs viewer)

### Phase 3: Conflict Resolution
- [ ] Implement CRDT (ypy)
- [ ] Add edit history
- [ ] Version control integration

### Phase 4: Production Hardening
- [ ] Rate limiting
- [ ] Audit logging
- [ ] Monitoring & alerts
- [ ] Backup & recovery

---

## Quick Security Checklist

Before going public, ensure:

- [ ] WebSocket requires authentication
- [ ] HTTPS/WSS enabled (no plain HTTP/WS)
- [ ] Origin validation implemented
- [ ] Rate limiting active
- [ ] Audit logging enabled
- [ ] Firewall configured
- [ ] Regular security updates
- [ ] Backup system in place
- [ ] Monitoring alerts configured
- [ ] Terms of Service published

---

## For Your Current Use Case (glowstone.red)

Since you're deploying for your own team on a private domain:

### Recommended Setup:
1. **IP Whitelist**: Only allow your team's IPs
2. **Strong SSL**: Use Let's Encrypt for HTTPS
3. **Private Network**: Consider VPN access
4. **Regular Backups**: Backup workspace directory daily

### Simple Auth (Optional):
```nginx
# Add basic auth to Nginx
location /ws {
    auth_basic "Team Only";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://127.0.0.1:8001;
}
```

Create password file:
```bash
sudo apt install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd teamuser
```

---

## Conflict Resolution Example

For now, the system uses "last-write-wins". To prevent data loss:

### Best Practices:
1. **Communicate**: Use chat before major edits
2. **Work on Different Files**: Avoid simultaneous edits
3. **Save Often**: Frequent saves to workspace
4. **Use Git**: Commit to version control regularly

### Future: Automatic Conflict Resolution
```python
# Example CRDT implementation (planned)
import y_py as Y

doc = Y.YDoc()
css_text = doc.get_text("css")

# User A types
css_text.insert(0, "body { ")

# User B types (concurrent)
css_text.insert(0, "html { ")

# Result: Automatically merged!
# "html { body { "
```

---

## Monitoring

### Key Metrics to Track:
- Active connections
- Messages per second
- Failed authentication attempts
- Connection errors
- Server resource usage

### Log Analysis:
```bash
# Watch WebSocket logs
sudo journalctl -u glowstone-websocket -f | grep -i "error\|warning"

# Count active users
sudo journalctl -u glowstone-websocket | grep "Client connected" | wc -l
```

---

## Emergency Response

### If Compromised:
1. **Immediately**: Stop WebSocket server
   ```bash
   sudo systemctl stop glowstone-websocket
   ```

2. **Block Access**: Update firewall
   ```bash
   sudo ufw deny 8001
   ```

3. **Review Logs**: Check for suspicious activity
   ```bash
   sudo journalctl -u glowstone-websocket --since "1 hour ago"
   ```

4. **Restore Backup**: If code was modified
   ```bash
   cp -r /backup/workspace/* /var/www/glowstone-ide/workspace/
   ```

5. **Update Security**: Add authentication before restarting

---

## Conclusion

**Current Implementation**: Suitable for **trusted team environments** with proper network security

**Public Deployment**: Requires authentication, authorization, and conflict resolution

**Your Use Case (glowstone.red)**: Safe with IP whitelisting and team-only access

For questions or security concerns, review the DEPLOYMENT.md guide for hardening instructions.
