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
    
    Uses PostgreSQL upsert to prevent race conditions during concurrent logins.
    
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
    from sqlalchemy.dialects.postgresql import insert
    
    # Use PostgreSQL upsert to atomically create or update user
    # This prevents race conditions when multiple OAuth callbacks occur simultaneously
    stmt = insert(User).values(
        provider=provider,
        provider_user_id=provider_user_id,
        primary_email=email,
        display_name=display_name,
        avatar_url=avatar_url,
        last_login_at=datetime.utcnow()
    ).on_conflict_do_update(
        # Conflict on unique constraint (provider, provider_user_id)
        index_elements=['provider', 'provider_user_id'],
        set_={
            'primary_email': email,
            'display_name': display_name,
            'avatar_url': avatar_url,
            'last_login_at': datetime.utcnow()
        }
    ).returning(User)
    
    try:
        result = db.execute(stmt)
        user = result.scalar_one()
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        # If upsert fails, fall back to query (should be rare)
        user = db.query(User).filter(
            User.provider == provider,
            User.provider_user_id == provider_user_id
        ).first()
        
        if user:
            # Update and return existing user
            user.primary_email = email
            user.display_name = display_name
            user.avatar_url = avatar_url
            user.last_login_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            return user
        
        # If still no user, re-raise the original error
        raise

