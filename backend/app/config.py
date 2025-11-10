"""
Configuration management for Beacon Studio backend
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "Beacon Studio"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"
    
    # Security
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30
    
    # Database
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Google Cloud Storage
    gcs_bucket_name: str = "beacon-prod-files"
    gcs_project_id: str
    gcs_credentials_path: str | None = None
    
    # OAuth - Google
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    
    # OAuth - GitHub
    github_client_id: str
    github_client_secret: str
    github_redirect_uri: str
    
    # Stripe
    stripe_api_key: str
    stripe_webhook_secret: str
    stripe_price_id_haste_i: str
    stripe_price_id_haste_ii: str
    stripe_price_id_haste_iii: str
    
    # AI Providers
    gemini_api_key: str | None = None
    lm_studio_endpoint: str | None = None
    ollama_endpoint: str | None = None
    
    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://shlinx.com",
        "http://shlinx.com"
    ]
    
    # Admin
    admin_secret_key: str | None = None
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # Storage Defaults
    free_storage_bytes: int = 902299238  # 0.84 GB
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

