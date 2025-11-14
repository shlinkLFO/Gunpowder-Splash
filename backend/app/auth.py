"""
Authentication utilities: JWT, OAuth, and session management
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .config import get_settings
from .database import get_db
from .models import User
import uuid

settings = get_settings()
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Payload data to encode (should include 'sub' with user_id)
        expires_delta: Optional expiration time override
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """Create long-lived refresh token"""
    expires_delta = timedelta(days=settings.refresh_token_expire_days)
    return create_access_token(
        data={"sub": user_id, "type": "refresh"},
        expires_delta=expires_delta
    )


def decode_token(token: str) -> dict:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dictionary
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to get current authenticated user from JWT
    
    Args:
        credentials: HTTP Bearer token from request
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Convert string UUID to UUID object
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format",
        )
    
    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    # Update last login timestamp
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    return user


async def verify_admin_secret(
    x_admin_secret: str = Header(None, description="Admin secret key for protected endpoints")
):
    """
    Dependency to verify the admin secret key
    """
    if not settings.admin_secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin secret key is not configured"
        )
        
    if x_admin_secret != settings.admin_secret_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin secret key"
        )


def get_or_create_user(
    db: Session,
    provider: str,
    provider_user_id: str,
    email: str,
    display_name: Optional[str] = None,
    avatar_url: Optional[str] = None
) -> User:
    """
    Get existing user or create new one from OAuth data
    
    Supports account linking by email - users can log in with either Google or GitHub
    if they use the same email address. Tracks which providers are linked.
    
    Args:
        db: Database session
        provider: OAuth provider ('google' or 'github')
        provider_user_id: User ID from OAuth provider
        email: User's email
        display_name: Display name (optional)
        avatar_url: Avatar URL (optional)
        
    Returns:
        User object (existing or newly created)
    """
    from datetime import datetime, timezone
    import json
    
    # First, check if a user exists with this email (account linking by email)
    existing_user = db.query(User).filter(User.primary_email == email).first()
    
    if existing_user:
        # User exists with this email - link the provider if not already linked
        existing_user.last_login_at = datetime.now(timezone.utc)
        
        # Parse linked providers
        try:
            linked_providers = json.loads(existing_user.linked_providers or '[]')
        except:
            linked_providers = [existing_user.provider]
        
        # Add this provider to linked providers if not already there
        if provider not in linked_providers:
            linked_providers.append(provider)
            existing_user.linked_providers = json.dumps(linked_providers)
        
        # Update provider-specific avatar
        if provider == 'google' and avatar_url:
            existing_user.google_avatar_url = avatar_url
            # If primary provider is Google, update main avatar too
            if existing_user.provider == 'google':
                existing_user.avatar_url = avatar_url
        elif provider == 'github' and avatar_url:
            existing_user.github_avatar_url = avatar_url
            # If primary provider is GitHub, update main avatar too
            if existing_user.provider == 'github':
                existing_user.avatar_url = avatar_url
        
        # Update display name if not set
        if not existing_user.display_name and display_name:
            existing_user.display_name = display_name
        
        # Prefer Google avatar for main avatar_url if both are linked
        if 'google' in linked_providers and existing_user.google_avatar_url:
            existing_user.avatar_url = existing_user.google_avatar_url
        
        db.commit()
        db.refresh(existing_user)
        return existing_user
    
    # No user with this email - create new user
    linked_providers = json.dumps([provider])
    
    new_user = User(
        provider=provider,
        provider_user_id=provider_user_id,
        primary_email=email,
        display_name=display_name,
        avatar_url=avatar_url,
        linked_providers=linked_providers,
        google_avatar_url=avatar_url if provider == 'google' else None,
        github_avatar_url=avatar_url if provider == 'github' else None,
        last_login_at=datetime.now(timezone.utc)
    )
    
    db.add(new_user)
    
    try:
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        # Handle race condition - another request may have created the user
        existing_user = db.query(User).filter(User.primary_email == email).first()
        if existing_user:
            existing_user.last_login_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing_user)
            return existing_user
        raise

