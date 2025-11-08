"""
OAuth2 integration for Google and GitHub authentication
"""
from typing import Optional
import httpx
from fastapi import HTTPException, status
from .config import get_settings

settings = get_settings()


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
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": self.SCOPE,
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTH_URL}?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange Google authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.google_redirect_uri,
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            return response.json()
    
    async def get_user_info(self, access_token: str) -> dict:
        """Get user information from Google"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.USER_INFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info from Google"
                )
            
            data = response.json()
            
            return {
                "provider_user_id": data["id"],
                "email": data["email"],
                "display_name": data.get("name"),
                "avatar_url": data.get("picture")
            }


class GitHubOAuthProvider(OAuthProvider):
    """GitHub OAuth2 provider"""
    
    AUTH_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_INFO_URL = "https://api.github.com/user"
    USER_EMAIL_URL = "https://api.github.com/user/emails"
    SCOPE = "read:user user:email"
    
    async def get_authorization_url(self, state: str) -> str:
        """Generate GitHub OAuth authorization URL"""
        params = {
            "client_id": settings.github_client_id,
            "redirect_uri": settings.github_redirect_uri,
            "scope": self.SCOPE,
            "state": state,
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTH_URL}?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange GitHub authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": settings.github_client_id,
                    "client_secret": settings.github_client_secret,
                    "code": code,
                    "redirect_uri": settings.github_redirect_uri,
                },
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            return response.json()
    
    async def get_user_info(self, access_token: str) -> dict:
        """Get user information from GitHub"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            # Get user profile
            user_response = await client.get(self.USER_INFO_URL, headers=headers)
            
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info from GitHub"
                )
            
            user_data = user_response.json()
            
            # Get primary email (GitHub may not include email in user profile)
            email = user_data.get("email")
            
            if not email:
                email_response = await client.get(self.USER_EMAIL_URL, headers=headers)
                if email_response.status_code == 200:
                    emails = email_response.json()
                    # Find primary verified email
                    for email_obj in emails:
                        if email_obj.get("primary") and email_obj.get("verified"):
                            email = email_obj["email"]
                            break
                    
                    # Fallback to first verified email
                    if not email:
                        for email_obj in emails:
                            if email_obj.get("verified"):
                                email = email_obj["email"]
                                break
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No verified email found in GitHub account"
                )
            
            return {
                "provider_user_id": str(user_data["id"]),
                "email": email,
                "display_name": user_data.get("name") or user_data.get("login"),
                "avatar_url": user_data.get("avatar_url")
            }


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

