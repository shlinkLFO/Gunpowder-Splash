"""
Authentication router: OAuth login and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import secrets
import logging
from typing import Optional
from datetime import datetime, timedelta, timezone
from ..database import get_db
from ..auth import create_access_token, create_refresh_token, get_or_create_user, get_current_user
from ..oauth import get_oauth_provider
from ..models import User, OAuthState

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


class TokenResponse(BaseModel):
    """Response model for token endpoints"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """User information response"""
    id: str
    email: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    provider: str
    linked_providers: list[str]  # List of linked providers ['google', 'github']


@router.get("/login/{provider}")
async def login(
    provider: str, 
    linking_email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Initiate OAuth login flow
    
    Args:
        provider: 'google' or 'github'
        linking_email: Email of current user (if linking accounts)
        db: Database session
        
    Returns:
        Redirect to OAuth provider
    """
    logger.info(f"=== Starting OAuth login flow for provider: {provider} ===")
    if linking_email:
        logger.info(f"Account linking request for email: {linking_email}")
    
    try:
        oauth = get_oauth_provider(provider)
        
        # Generate CSRF state token
        state = secrets.token_urlsafe(32)
        logger.info(f"Generated state token: {state[:10]}...")
        
        # Store state in database (persistent across instances)
        oauth_state = OAuthState(
            state=state,
            provider=provider,
            linking_user_email=linking_email  # Store email if linking
        )
        db.add(oauth_state)
        db.commit()
        logger.info("State token stored in database")
        
        # Get authorization URL and redirect
        auth_url = await oauth.get_authorization_url(state)
        logger.info(f"Redirecting to OAuth provider: {auth_url[:100]}...")
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        logger.error(f"Error initiating OAuth login: {str(e)}", exc_info=True)
        raise


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """
    OAuth callback endpoint
    
    Args:
        provider: 'google' or 'github'
        code: Authorization code from provider
        state: CSRF state token
        db: Database session
        
    Returns:
        JWT tokens and user info
    """
    logger.info(f"=== OAuth callback received from {provider} ===")
    logger.info(f"Code: {code[:20]}...")
    logger.info(f"State: {state[:10]}...")
    
    try:
        # Verify state token from database
        oauth_state = db.query(OAuthState).filter(OAuthState.state == state).first()
        
        if not oauth_state:
            logger.error("State token not found in database")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired state token"
            )
        
        logger.info(f"State token found, provider: {oauth_state.provider}")
        
        # Verify provider matches
        if oauth_state.provider != provider:
            logger.error(f"Provider mismatch: expected {oauth_state.provider}, got {provider}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State token provider mismatch"
            )
        
        # Check if token expired (10 minute TTL)
        if oauth_state.expires_at < datetime.now(timezone.utc):
            logger.error(f"State token expired at {oauth_state.expires_at}")
            db.delete(oauth_state)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State token expired"
            )
        
        # Remove used state (one-time use)
        db.delete(oauth_state)
        db.commit()
        logger.info("State token validated and removed")
        
        # Get OAuth provider
        oauth = get_oauth_provider(provider)
        
        # Exchange code for token
        logger.info("Exchanging code for access token...")
        token_data = await oauth.exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            logger.error("No access token in response")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token"
            )
        
        # Get user info from provider
        logger.info("Fetching user info from provider...")
        user_info = await oauth.get_user_info(access_token)
        logger.info(f"User info retrieved for: {user_info.get('email')}")
        
        # SECURITY: Verify email matches when linking accounts
        if oauth_state.linking_user_email:
            logger.info(f"Account linking requested - verifying emails match")
            logger.info(f"Expected email: {oauth_state.linking_user_email}")
            logger.info(f"Provider email: {user_info.get('email')}")
            
            if oauth_state.linking_user_email != user_info.get('email'):
                logger.error(f"Email mismatch during account linking!")
                logger.error(f"Current account: {oauth_state.linking_user_email}")
                logger.error(f"Provider account: {user_info.get('email')}")
                
                # Redirect to frontend with error message instead of throwing exception
                from ..config import get_settings
                settings = get_settings()
                frontend_url = "https://shlinx.com" if settings.environment == "production" else "http://localhost:5173"
                
                error_msg = f"Cannot link accounts with different emails. Your {provider.title()} account uses {user_info.get('email')}, but you're logged in with {oauth_state.linking_user_email}."
                return RedirectResponse(
                    url=f"{frontend_url}?error={error_msg}"
                )
            logger.info("Email verification passed - proceeding with account linking")
        
        # Get or create user in database
        logger.info("Creating or updating user in database...")
        user = get_or_create_user(
            db=db,
            provider=provider,
            provider_user_id=user_info["provider_user_id"],
            email=user_info["email"],
            display_name=user_info.get("display_name"),
            avatar_url=user_info.get("avatar_url")
        )
        logger.info(f"User created/updated: {user.id}")
        
        # Generate JWT tokens
        jwt_access_token = create_access_token(data={"sub": str(user.id)})
        jwt_refresh_token = create_refresh_token(user_id=str(user.id))
        logger.info("JWT tokens generated")
        
        # Redirect to frontend with token
        from ..config import get_settings
        settings = get_settings()
        
        # Determine frontend URL based on environment
        if settings.environment == "production":
            frontend_url = "https://shlinx.com"
        else:
            frontend_url = "http://localhost:5173"
        
        logger.info(f"Redirecting to frontend: {frontend_url}")
        
        # Redirect with token in URL parameter (frontend will extract and store it)
        return RedirectResponse(
            url=f"{frontend_url}?token={jwt_access_token}&refresh_token={jwt_refresh_token}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in OAuth callback: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback failed: {str(e)}"
        )


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user information
    
    Args:
        current_user: Injected current user from JWT
        
    Returns:
        User information
    """
    import json
    
    # Parse linked providers
    try:
        linked_providers = json.loads(current_user.linked_providers or '[]')
    except:
        linked_providers = [current_user.provider]
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.primary_email,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url,
        provider=current_user.provider,
        linked_providers=linked_providers
    )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Refresh access token using refresh token
    
    Args:
        refresh_token: Valid refresh token
        db: Database session
        
    Returns:
        New access and refresh tokens
    """
    from ..auth import decode_token
    import uuid
    
    # Decode refresh token
    payload = decode_token(refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user
    user_uuid = uuid.UUID(user_id_str)
    user = db.query(User).filter(User.id == user_uuid).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Generate new tokens
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(user_id=str(user.id))
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        user={
            "id": str(user.id),
            "email": user.primary_email,
            "display_name": user.display_name,
            "avatar_url": user.avatar_url,
            "provider": user.provider
        }
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client should discard tokens)
    
    Returns:
        Success message
    """
    return {"message": "Logged out successfully"}

