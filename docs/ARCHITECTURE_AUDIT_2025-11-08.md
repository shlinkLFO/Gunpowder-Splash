# Comprehensive Architecture Audit Report

**Date:** November 8, 2025  
**Auditor:** Gemini (System Architect)  
**Status:** COMPLETED  
**Scope:** Full codebase review for potential conflicts, race conditions, and architectural issues

---

## Executive Summary

This audit builds upon the recent security fixes and examines the entire Beacon Studio codebase for potential conflicts, race conditions, data integrity issues, and architectural inconsistencies. The audit identified **7 critical issues**, **3 high-priority issues**, and **5 medium-priority recommendations**.

### Recent Fixes Verified

The following issues have been successfully resolved:
- Dependency conflict between `requirements.txt` and `requirements_beacon.txt`
- Race condition in file deletion quota updates
- Stale storage quotas after project deletion
- Membership limit race condition in database trigger

---

## Critical Issues

### 1. Stripe Webhook Race Conditions

**Severity:** CRITICAL  
**Location:** `backend/app/routers/billing.py` lines 289-338  
**Impact:** Data corruption, billing inconsistencies

#### Problem

The Stripe webhook handler modifies workspace records without database locking. Multiple concurrent webhook events (e.g., `checkout.session.completed` and `customer.subscription.updated`) can race, leading to:
- Lost subscription IDs
- Incorrect plan assignments
- Read-only mode being incorrectly set/unset

```python
# Line 298-305: No locking
workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
if workspace:
    workspace.plan_id = plan_id
    workspace.stripe_subscription_id = subscription_id
    workspace.is_read_only = False
    workspace.cancelled_at = None
    workspace.delete_after = None
    db.commit()
```

#### Solution

Add row-level locking to all webhook handlers:

```python
workspace = (
    db.query(Workspace)
    .filter(Workspace.id == workspace_id)
    .with_for_update()
    .first()
)
```

Additionally, implement idempotency keys to handle duplicate webhook deliveries.

---

### 2. Checkout Session Customer Creation Race

**Severity:** CRITICAL  
**Location:** `backend/app/routers/billing.py` lines 111-123  
**Impact:** Duplicate Stripe customers, billing confusion

#### Problem

When creating a Stripe customer during checkout, the code checks if `workspace.stripe_customer_id` exists, then creates a customer if not. Without locking, concurrent checkout attempts can both see `None` and create duplicate customers.

```python
# Line 111-123: Race window
if workspace.stripe_customer_id:
    customer_id = workspace.stripe_customer_id
else:
    customer = stripe.Customer.create(...)  # Both requests reach here
    customer_id = customer.id
    workspace.stripe_customer_id = customer_id
    db.commit()
```

#### Solution

Lock the workspace row before checking for existing customer:

```python
workspace = (
    db.query(Workspace)
    .filter(Workspace.id == workspace_id)
    .with_for_update()
    .first()
)
```

---

### 3. OAuth User Creation Race Condition

**Severity:** CRITICAL  
**Location:** `backend/app/auth.py` lines 155-221  
**Impact:** Duplicate user accounts, broken foreign keys

#### Problem

The `get_or_create_user` function has multiple race windows:

1. **Check-then-create pattern** (lines 178-191): Two concurrent OAuth logins can both find no user and attempt to create one, violating the unique constraint.
2. **Email linking logic** (lines 193-205): Can race with concurrent logins from different providers using the same email.

```python
# Lines 178-181: Race window
user = db.query(User).filter(
    User.provider == provider,
    User.provider_user_id == provider_user_id
).first()

if user:
    # Update...
else:
    # Both concurrent requests reach here
```

#### Solution

Use database-level upsert (PostgreSQL `INSERT ... ON CONFLICT`) or implement pessimistic locking:

```python
# Option 1: Upsert with SQLAlchemy
from sqlalchemy.dialects.postgresql import insert

stmt = insert(User).values(
    provider=provider,
    provider_user_id=provider_user_id,
    primary_email=email,
    # ...
).on_conflict_do_update(
    index_elements=['provider', 'provider_user_id'],
    set_={'primary_email': email, 'last_login_at': datetime.utcnow()}
)

# Option 2: Advisory lock
db.execute("SELECT pg_advisory_xact_lock(hashtext(:email))", {"email": email})
```

---

### 4. Last Login Timestamp Race

**Severity:** HIGH  
**Location:** `backend/app/auth.py` line 130-131  
**Impact:** Lost writes, minor data inconsistency

#### Problem

The `get_current_user` dependency updates `last_login_at` on every authenticated request without locking. Concurrent requests from the same user will race, and some updates may be lost.

```python
# Line 130-131: No lock
user.last_login_at = datetime.utcnow()
db.commit()
```

#### Solution

This is a low-impact race (losing a timestamp update is acceptable). However, for consistency:

1. **Option A (Recommended):** Make this update asynchronous/background to avoid blocking requests.
2. **Option B:** Use a database trigger to update on any user activity.
3. **Option C:** Accept the race as benign and document it.

---

### 5. AI Usage Tracking Missing Transaction Management

**Severity:** HIGH  
**Location:** `backend/app/routers/ai.py` lines 69-77, 132-140  
**Impact:** Lost usage records, incorrect billing

#### Problem

The AI usage tracking calls `track_usage`, which commits to the database. If the outer request fails after this commit, usage is recorded but the AI response is never delivered to the user. This can lead to:
- Billing for failed requests
- Incorrect usage statistics

```python
# Line 69-77: Commits inside request handler
response = await ai_provider.chat(request)

ai_provider.track_usage(...)  # This commits to DB

return response  # If this fails, usage is already recorded
```

#### Solution

Defer the commit until the response is successfully returned:

```python
# In ai_providers.py, change track_usage to NOT commit
def track_usage(self, db, ...):
    usage = AIUsage(...)
    db.add(usage)
    # Remove db.commit() - let the caller commit

# In routers/ai.py, commit after successful response
try:
    response = await ai_provider.chat(request)
    ai_provider.track_usage(...)
    db.commit()  # Only commit if everything succeeded
    return response
except Exception:
    db.rollback()
    raise
```

---

### 6. Missing Rollback in Workspace Member Addition

**Severity:** HIGH  
**Location:** `backend/app/routers/workspaces.py` lines 311-328  
**Impact:** Inconsistent error handling

#### Problem

The `add_workspace_member` endpoint catches exceptions from the team size limit trigger but only rolls back in the exception handler. If other exceptions occur, the rollback may not happen consistently.

```python
# Line 311-328: Inconsistent rollback
try:
    membership = Membership(...)
    db.add(membership)
    db.commit()
    return {"message": ...}
except Exception as e:
    db.rollback()  # Only rolls back on exception
    if "Team size limit exceeded" in str(e):
        raise HTTPException(...)
    raise
```

#### Solution

This is actually correct, but should be more explicit:

```python
try:
    membership = Membership(...)
    db.add(membership)
    db.commit()
    return {"message": ...}
except Exception as e:
    db.rollback()
    # More specific exception handling
    if "Team size limit exceeded" in str(e):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Team size limit exceeded for this plan"
        )
    # Log unexpected errors
    logger.error(f"Failed to add member: {e}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to add member to workspace"
    )
```

---

### 7. Dockerfile References Non-Existent File

**Severity:** MEDIUM  
**Location:** `backend/Dockerfile` line 12  
**Impact:** Build failure

#### Problem

The Dockerfile was updated to copy `requirements_beacon.txt` and rename it to `requirements.txt`, but the source file `requirements_beacon.txt` no longer exists (it was renamed to `requirements.txt`).

```dockerfile
# Line 12: File doesn't exist
COPY requirements_beacon.txt ./requirements.txt
```

#### Solution

Update the Dockerfile to use the correct filename:

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

---

## Medium Priority Issues

### 8. No Audit Logging Implementation

**Severity:** MEDIUM  
**Location:** Entire codebase  
**Impact:** Compliance risk, no forensics capability

#### Problem

The database schema includes an `audit_log` table (lines 117-132 in `schema.sql`), but no code actually writes to it. Critical actions like:
- File uploads/deletions
- Member additions/removals
- Plan changes
- Project deletions

...are not being logged.

#### Solution

Implement audit logging middleware or decorators:

```python
# backend/app/audit.py
def log_audit(
    db: Session,
    user_id: uuid.UUID,
    workspace_id: uuid.UUID,
    action: str,
    resource_type: str,
    resource_id: str,
    details: dict = None,
    request: Request = None
):
    from .models import AuditLog
    
    log_entry = AuditLog(
        user_id=user_id,
        workspace_id=workspace_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    db.add(log_entry)
```

Then call this function in all sensitive operations.

---

### 9. Inconsistent Error Handling Patterns

**Severity:** MEDIUM  
**Location:** Multiple files  
**Impact:** Inconsistent user experience, debugging difficulty

#### Problem

Different routers use different error handling patterns:
- Some use try/except with rollback
- Some rely on FastAPI's automatic rollback
- Some don't handle database errors at all

#### Solution

Establish a consistent pattern and document it:

```python
# Recommended pattern for all database operations
try:
    # Database operations
    db.commit()
    return response
except IntegrityError as e:
    db.rollback()
    # Handle specific constraint violations
    raise HTTPException(status_code=400, detail="...")
except Exception as e:
    db.rollback()
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

---

### 10. Missing Database Connection Pool Monitoring

**Severity:** MEDIUM  
**Location:** `backend/app/database.py`  
**Impact:** Potential connection exhaustion

#### Problem

The database configuration sets `pool_size=10` and `max_overflow=20`, but there's no monitoring or alerting for pool exhaustion. Long-running requests (like large file uploads) could exhaust the pool.

#### Solution

Add connection pool monitoring to the health check endpoint:

```python
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        
        # Check pool status
        pool = engine.pool
        pool_status = {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "overflow": pool.overflow(),
            "checked_out": pool.checkedout()
        }
        
        # Alert if pool is near exhaustion
        if pool.checkedout() > pool.size() * 0.8:
            logger.warning(f"Database pool near exhaustion: {pool_status}")
        
        return {
            "status": "healthy",
            "database": "connected",
            "pool": pool_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")
```

---

### 11. No Rate Limiting Implementation

**Severity:** MEDIUM  
**Location:** Configuration exists but not implemented  
**Impact:** API abuse, DoS vulnerability

#### Problem

The config file defines `rate_limit_per_minute: int = 60` (line 63 in `config.py`), but no rate limiting middleware is actually implemented.

#### Solution

Implement rate limiting using a library like `slowapi`:

```python
# backend/app/main_beacon.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Then on sensitive endpoints:
@router.post("/files")
@limiter.limit("60/minute")
async def upload_file(...):
    ...
```

---

### 12. Workspace Export Not Transactional

**Severity:** MEDIUM  
**Location:** `backend/app/storage.py` lines 383-430  
**Impact:** Incomplete exports, wasted storage

#### Problem

The `export_workspace` method creates a ZIP archive by iterating through blobs. If a file is deleted mid-export, the export may be incomplete or fail. Additionally, there's no cleanup of old export archives.

#### Solution

1. Add a workspace snapshot mechanism or use GCS object versioning
2. Implement cleanup job for old exports:

```python
# In main_beacon.py admin jobs
@app.post("/admin/cleanup-old-exports")
async def cleanup_old_exports():
    """Delete export archives older than 48 hours"""
    from datetime import datetime, timedelta
    
    cutoff = datetime.utcnow() - timedelta(hours=48)
    blobs = storage_service.client.list_blobs(
        storage_service.bucket,
        prefix="exports/"
    )
    
    deleted_count = 0
    for blob in blobs:
        if blob.time_created < cutoff:
            blob.delete()
            deleted_count += 1
    
    return {"deleted_count": deleted_count}
```

---

## Low Priority Recommendations

### 13. Add Database Migration Tool

Currently, schema changes require manual SQL execution. Implement Alembic migrations for safer schema evolution.

### 14. Implement Request ID Tracing

Add request ID headers to all responses for easier debugging and log correlation.

### 15. Add Metrics Collection

Implement Prometheus metrics for monitoring:
- Request latency
- Database query times
- Storage operation times
- Error rates

### 16. Implement Circuit Breaker for External Services

Add circuit breakers for Stripe, Google OAuth, and GCS to prevent cascading failures.

### 17. Add Database Query Logging in Development

Enable SQLAlchemy query logging in development mode for performance analysis.

---

## Summary of Action Items

### Immediate (Critical)

1. Fix Stripe webhook race conditions with row locking
2. Fix checkout customer creation race with locking
3. Fix OAuth user creation race with upsert or advisory locks
4. Fix Dockerfile to reference correct requirements file
5. Fix AI usage tracking transaction management

### Short Term (High Priority)

6. Implement audit logging for compliance
7. Standardize error handling patterns across codebase
8. Add database connection pool monitoring
9. Implement rate limiting

### Medium Term (Medium Priority)

10. Add export archive cleanup job
11. Implement database migrations with Alembic
12. Add request tracing and metrics collection

---

## Testing Recommendations

Before deploying these fixes:

1. **Load Testing:** Simulate concurrent requests to verify race condition fixes
2. **Chaos Testing:** Test webhook delivery with duplicates and out-of-order events
3. **Integration Testing:** Test OAuth flows with concurrent logins
4. **Database Testing:** Verify all transactions commit/rollback correctly under failure conditions

---

## Conclusion

The codebase has a solid foundation with good security practices (OAuth, RBAC, quota enforcement). The recent fixes have addressed several critical race conditions. However, the issues identified in this audit—particularly around Stripe webhooks and OAuth user creation—require immediate attention to prevent data corruption and billing inconsistencies.

The recommended fixes follow established patterns already present in the codebase (e.g., `with_for_update()` locking) and should be straightforward to implement.

**Estimated Implementation Time:**
- Critical fixes: 2-3 days
- High priority: 3-5 days
- Medium priority: 5-7 days

**Total:** ~2 weeks for complete remediation

---

**Audit Completed By:** Gemini (System Architect)  
**Next Review:** After critical fixes are deployed  
**Sign-off Required:** Technical Lead, Security Team

