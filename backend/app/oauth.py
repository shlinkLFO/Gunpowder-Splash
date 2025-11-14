"""
OAuth2 integration for Google and GitHub authentication
"""
from typing import Optional
import httpx
import logging
from fastapi import HTTPException, status
from .config import get_settings

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

settings = get_settings()

# Log OAuth configuration status at startup
logger.info("=== OAuth Configuration Status ===")
logger.info(f"Google Client ID configured: {bool(settings.google_client_id)}")
logger.info(f"Google Client Secret configured: {bool(settings.google_client_secret)}")
logger.info(f"Google Redirect URI: {settings.google_redirect_uri}")
logger.info(f"GitHub Client ID configured: {bool(settings.github_client_id)}")
logger.info(f"GitHub Client Secret configured: {bool(settings.github_client_secret)}")
logger.info(f"GitHub Redirect URI: {settings.github_redirect_uri}")
logger.info("====================================")


class OAuthProvider:
    """Base class for OAuth providers"""
    
    async def get_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL"""
        raise NotImplementedError
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token"""
        raise NotImplementedError
    
    async def get_user_info(self, access_token: str) -> dict:
        """Get user information from provider"""
        raise NotImplementedError


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth2 provider"""
    
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    SCOPE = "openid email profile"
    
    async def get_authorization_url(self, state: str) -> str:
        """Generate Google OAuth authorization URL"""
        logger.info("=== Google OAuth: Generating Authorization URL ===")
        
        if not settings.google_client_id:
            logger.error("MISSING: Google Client ID is not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth is not configured - missing client_id"
            )
        
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": self.SCOPE,
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        
        auth_url = f"{self.AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        logger.info(f"Generated auth URL with redirect_uri: {settings.google_redirect_uri}")
        logger.info(f"State token: {state[:10]}...")
        
        return auth_url
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange Google authorization code for access token"""
        logger.info("=== Google OAuth: Exchanging Code for Token ===")
        logger.info(f"Authorization code: {code[:20]}...")
        
        if not settings.google_client_secret:
            logger.error("MISSING: Google Client Secret is not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth is not configured - missing client_secret"
            )
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        "client_id": settings.google_client_id,
                        "client_secret": settings.google_client_secret,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": settings.google_redirect_uri,
                    },
                    timeout=10.0
                )
                
                logger.info(f"Token exchange response status: {response.status_code}")
                
                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"Token exchange failed: {error_detail}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to exchange code for token: {error_detail}"
                    )
                
                token_data = response.json()
                logger.info(f"Successfully obtained access token (length: {len(token_data.get('access_token', ''))})")
                return token_data
                
            except httpx.TimeoutException:
                logger.error("Token exchange timed out after 10 seconds")
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Google OAuth token exchange timed out"
                )
            except Exception as e:
                logger.error(f"Unexpected error during token exchange: {str(e)}")
                raise
    
    async def get_user_info(self, access_token: str) -> dict:
        """Get user information from Google"""
        logger.info("=== Google OAuth: Fetching User Info ===")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.USER_INFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )
                
                logger.info(f"User info response status: {response.status_code}")
                
                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"Failed to get user info: {error_detail}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to get user info from Google: {error_detail}"
                    )
                
                data = response.json()
                logger.info(f"Successfully retrieved user info for: {data.get('email', 'unknown')}")
                
                return {
                    "provider_user_id": data["id"],
                    "email": data["email"],
                    "display_name": data.get("name"),
                    "avatar_url": data.get("picture")
                }
                
            except httpx.TimeoutException:
                logger.error("User info fetch timed out after 10 seconds")
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Google user info fetch timed out"
                )
            except Exception as e:
                logger.error(f"Unexpected error fetching user info: {str(e)}")
                raise


class GitHubOAuthProvider(OAuthProvider):
    """GitHub OAuth2 provider"""
    
    AUTH_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_INFO_URL = "https://api.github.com/user"
    USER_EMAIL_URL = "https://api.github.com/user/emails"
    SCOPE = "read:user user:email"
    
    async def get_authorization_url(self, state: str) -> str:
        """Generate GitHub OAuth authorization URL"""
        logger.info("=== GitHub OAuth: Generating Authorization URL ===")
        
        if not settings.github_client_id:
            logger.error("MISSING: GitHub Client ID is not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GitHub OAuth is not configured - missing client_id"
            )
        
        params = {
            "client_id": settings.github_client_id,
            "redirect_uri": settings.github_redirect_uri,
            "scope": self.SCOPE,
            "state": state,
        }
        
        auth_url = f"{self.AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        logger.info(f"Generated auth URL with redirect_uri: {settings.github_redirect_uri}")
        logger.info(f"State token: {state[:10]}...")
        
        return auth_url
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange GitHub authorization code for access token"""
        logger.info("=== GitHub OAuth: Exchanging Code for Token ===")
        logger.info(f"Authorization code: {code[:20]}...")
        
        if not settings.github_client_secret:
            logger.error("MISSING: GitHub Client Secret is not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GitHub OAuth is not configured - missing client_secret"
            )
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        "client_id": settings.github_client_id,
                        "client_secret": settings.github_client_secret,
                        "code": code,
                        "redirect_uri": settings.github_redirect_uri,
                    },
                    headers={"Accept": "application/json"},
                    timeout=10.0
                )
                
                logger.info(f"Token exchange response status: {response.status_code}")
                
                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"Token exchange failed: {error_detail}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to exchange code for token: {error_detail}"
                    )
                
                token_data = response.json()
                logger.info(f"Successfully obtained access token (length: {len(token_data.get('access_token', ''))})")
                return token_data
                
            except httpx.TimeoutException:
                logger.error("Token exchange timed out after 10 seconds")
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="GitHub OAuth token exchange timed out"
                )
            except Exception as e:
                logger.error(f"Unexpected error during token exchange: {str(e)}")
                raise
    
    async def get_user_info(self, access_token: str) -> dict:
        """Get user information from GitHub"""
        logger.info("=== GitHub OAuth: Fetching User Info ===")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Get user profile
                user_response = await client.get(self.USER_INFO_URL, headers=headers, timeout=10.0)
                
                logger.info(f"User info response status: {user_response.status_code}")
                
                if user_response.status_code != 200:
                    error_detail = user_response.text
                    logger.error(f"Failed to get user info: {error_detail}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to get user info from GitHub: {error_detail}"
                    )
                
                user_data = user_response.json()
                logger.info(f"Retrieved user profile for: {user_data.get('login', 'unknown')}")
                
                # Get primary email (GitHub may not include email in user profile)
                email = user_data.get("email")
                logger.info(f"Email from profile: {email if email else 'not found'}")
                
                if not email:
                    logger.info("Email not in profile, fetching from emails endpoint...")
                    email_response = await client.get(self.USER_EMAIL_URL, headers=headers, timeout=10.0)
                    logger.info(f"Email fetch response status: {email_response.status_code}")
                    
                    if email_response.status_code == 200:
                        emails = email_response.json()
                        logger.info(f"Found {len(emails)} email addresses")
                        
                        # Find primary verified email
                        for email_obj in emails:
                            if email_obj.get("primary") and email_obj.get("verified"):
                                email = email_obj["email"]
                                logger.info(f"Using primary verified email: {email}")
                                break
                        
                        # Fallback to first verified email
                        if not email:
                            for email_obj in emails:
                                if email_obj.get("verified"):
                                    email = email_obj["email"]
                                    logger.info(f"Using first verified email: {email}")
                                    break
                    else:
                        logger.warning(f"Failed to fetch emails: {email_response.text}")
                
                if not email:
                    logger.error("No verified email found in GitHub account")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No verified email found in GitHub account"
                    )
                
                logger.info(f"Successfully retrieved user info for: {email}")
                
                return {
                    "provider_user_id": str(user_data["id"]),
                    "email": email,
                    "display_name": user_data.get("name") or user_data.get("login"),
                    "avatar_url": user_data.get("avatar_url")
                }
                
            except httpx.TimeoutException:
                logger.error("User info fetch timed out after 10 seconds")
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="GitHub user info fetch timed out"
                )
            except Exception as e:
                logger.error(f"Unexpected error fetching user info: {str(e)}")
                raise


# Provider instances
google_oauth = GoogleOAuthProvider()
github_oauth = GitHubOAuthProvider()


def get_oauth_provider(provider_name: str) -> OAuthProvider:
    """Get OAuth provider instance by name"""
    providers = {
        "google": google_oauth,
        "github": github_oauth
    }
    
    provider = providers.get(provider_name.lower())
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown OAuth provider: {provider_name}"
        )
    
    return provider

