"""
Diagnostic endpoints for troubleshooting OAuth and system configuration
"""
from fastapi import APIRouter, Depends
from ..config import get_settings
from ..auth import verify_admin_secret
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


@router.get("/oauth-config")
async def get_oauth_config(_=Depends(verify_admin_secret)):
    """
    Get OAuth configuration status (protected by admin secret)
    
    Requires X-Admin-Secret header with valid admin secret key
    
    Returns:
        OAuth configuration status without exposing secrets
    """
    settings = get_settings()
    
    return {
        "google": {
            "client_id_configured": bool(settings.google_client_id),
            "client_id_prefix": settings.google_client_id[:20] if settings.google_client_id else None,
            "client_secret_configured": bool(settings.google_client_secret),
            "client_secret_length": len(settings.google_client_secret) if settings.google_client_secret else 0,
            "redirect_uri": settings.google_redirect_uri,
        },
        "github": {
            "client_id_configured": bool(settings.github_client_id),
            "client_id_prefix": settings.github_client_id[:20] if settings.github_client_id else None,
            "client_secret_configured": bool(settings.github_client_secret),
            "client_secret_length": len(settings.github_client_secret) if settings.github_client_secret else 0,
            "redirect_uri": settings.github_redirect_uri,
        },
        "environment": settings.environment,
        "api_prefix": settings.api_prefix,
    }


@router.get("/health")
async def health_check():
    """
    Public health check endpoint
    
    Returns:
        Service status
    """
    return {
        "status": "healthy",
        "service": "Gunpowder Splash API",
    }

