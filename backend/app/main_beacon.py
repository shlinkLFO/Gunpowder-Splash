"""
Beacon Studio FastAPI application
Main entry point for the backend API
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import logging

from .config import get_settings
from .database import engine, Base, get_db
from .routers import auth, workspaces, projects, billing, ai, diagnostics, code_server
from .auth import verify_admin_secret

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events
    """
    # Startup
    logger.info("Starting Beacon Studio backend...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"API Prefix: {settings.api_prefix}")
    
    # Create database tables if they don't exist
    # (In production, use Alembic migrations instead)
    if settings.environment == "development":
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Beacon Studio backend...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(diagnostics.router, prefix=settings.api_prefix)
app.include_router(workspaces.router, prefix=settings.api_prefix)
app.include_router(projects.router, prefix=settings.api_prefix)
app.include_router(billing.router, prefix=settings.api_prefix)
app.include_router(ai.router, prefix=settings.api_prefix)
app.include_router(code_server.router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "running"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for load balancers
    
    Returns:
        Health status
    """
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.environment
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )


# Admin endpoints (protected by admin secret)
@app.post("/admin/storage-reconciliation")
async def storage_reconciliation_job(
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_secret)
):
    """
    Admin endpoint: Reconcile storage usage for all workspaces
    
    This endpoint should be called by Cloud Scheduler daily.
    In production, verify the request comes from Cloud Scheduler service account.
    
    Returns:
        Reconciliation results
    """
    from .models import Workspace
    from .storage import storage_service
    
    logger.info("Starting storage reconciliation job")
    
    workspaces = db.query(Workspace).all()
    reconciled_count = 0
    errors = []
    
    for workspace in workspaces:
        try:
            # Calculate actual storage usage
            actual_bytes = storage_service.calculate_workspace_storage(workspace.id)
            
            # Update if different
            if workspace.storage_used_bytes != actual_bytes:
                old_value = workspace.storage_used_bytes
                workspace.storage_used_bytes = actual_bytes
                logger.info(
                    f"Workspace {workspace.id}: {old_value} -> {actual_bytes} bytes"
                )
            
            reconciled_count += 1
        except Exception as e:
            logger.error(f"Failed to reconcile workspace {workspace.id}: {e}")
            errors.append({"workspace_id": str(workspace.id), "error": str(e)})
    
    db.commit()
    
    logger.info(f"Storage reconciliation complete: {reconciled_count} workspaces")
    
    return {
        "status": "completed",
        "reconciled_count": reconciled_count,
        "total_workspaces": len(workspaces),
        "errors": errors
    }


@app.post("/admin/purge-deleted-workspaces")
async def purge_deleted_workspaces_job(
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_secret)
):
    """
    Admin endpoint: Purge workspaces past their deletion date
    
    This endpoint should be called by Cloud Scheduler daily.
    In production, verify the request comes from Cloud Scheduler service account.
    
    Returns:
        Purge results
    """
    from .models import Workspace, Membership, Project
    from .storage import storage_service
    from datetime import datetime
    
    logger.info("Starting purge deleted workspaces job")
    
    # Find workspaces to delete
    now = datetime.utcnow()
    workspaces_to_delete = db.query(Workspace).filter(
        Workspace.delete_after.isnot(None),
        Workspace.delete_after < now
    ).all()
    
    deleted_count = 0
    errors = []
    
    for workspace in workspaces_to_delete:
        try:
            logger.info(f"Purging workspace {workspace.id}")
            
            # Delete all files in storage
            storage_service.delete_workspace(workspace.id)
            
            # Delete database records (cascade will handle memberships and projects)
            db.delete(workspace)
            db.commit()
            
            deleted_count += 1
            logger.info(f"Workspace {workspace.id} purged successfully")
        except Exception as e:
            logger.error(f"Failed to purge workspace {workspace.id}: {e}")
            errors.append({"workspace_id": str(workspace.id), "error": str(e)})
            db.rollback()
    
    logger.info(f"Purge complete: {deleted_count} workspaces deleted")
    
    return {
        "status": "completed",
        "deleted_count": deleted_count,
        "total_candidates": len(workspaces_to_delete),
        "errors": errors
    }


@app.post("/admin/cleanup-expired-oauth-states")
async def cleanup_expired_oauth_states_job(
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_secret)
):
    """
    Admin endpoint: Clean up expired OAuth state tokens
    
    This endpoint should be called by Cloud Scheduler hourly.
    In production, verify the request comes from Cloud Scheduler service account.
    
    Returns:
        Cleanup results
    """
    from .models import OAuthState
    from datetime import datetime
    
    logger.info("Starting cleanup expired OAuth states job")
    
    # Find expired states
    now = datetime.utcnow()
    expired_states = db.query(OAuthState).filter(
        OAuthState.expires_at < now
    ).all()
    
    deleted_count = 0
    
    for oauth_state in expired_states:
        try:
            db.delete(oauth_state)
            deleted_count += 1
        except Exception as e:
            logger.error(f"Failed to delete OAuth state {oauth_state.state}: {e}")
            db.rollback()
    
    db.commit()
    
    logger.info(f"OAuth state cleanup complete: {deleted_count} expired tokens deleted")
    
    return {
        "status": "completed",
        "deleted_count": deleted_count,
        "total_candidates": len(expired_states)
    }


@app.get("/admin/stats")
async def get_admin_stats(
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_secret)
):
    """
    Admin endpoint: Get system statistics
    
    Returns:
        System statistics
    """
    from .models import User, Workspace, Project, Membership, Plan
    from sqlalchemy import func
    
    # Count statistics
    total_users = db.query(func.count(User.id)).scalar()
    total_workspaces = db.query(func.count(Workspace.id)).scalar()
    total_projects = db.query(func.count(Project.id)).scalar()
    
    # Plan distribution
    plan_stats = db.query(
        Plan.name,
        func.count(Workspace.id).label('count')
    ).join(Workspace).group_by(Plan.name).all()
    
    # Storage statistics
    total_storage = db.query(func.sum(Workspace.storage_used_bytes)).scalar() or 0
    
    # Cancelled workspaces
    cancelled_workspaces = db.query(func.count(Workspace.id)).filter(
        Workspace.cancelled_at.isnot(None)
    ).scalar()
    
    return {
        "users": {
            "total": total_users
        },
        "workspaces": {
            "total": total_workspaces,
            "cancelled": cancelled_workspaces,
            "by_plan": [{"plan": name, "count": count} for name, count in plan_stats]
        },
        "projects": {
            "total": total_projects
        },
        "storage": {
            "total_bytes": total_storage,
            "total_gb": round(total_storage / (1024**3), 2)
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main_beacon:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )

