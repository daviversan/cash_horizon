"""Application configuration using Pydantic Settings."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Settings
    app_name: str = "Cash Horizon"
    app_version: str = "1.0.0"
    environment: str = "development"
    
    # Database
    database_url: str = "sqlite:///./cash_horizon.db"
    
    # Google Gemini API
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash-exp"
    
    # Google Custom Search API
    google_search_api_key: str = ""
    google_search_engine_id: str = ""
    google_search_enabled: bool = False  # Set to True when API keys are configured
    search_max_results: int = 10
    search_safe_mode: str = "active"
    
    # Google Cloud (for deployment)
    google_cloud_project: str = ""
    google_application_credentials: str = ""
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Session Configuration
    session_timeout: int = 3600
    
    # Logging
    log_level: str = "INFO"
    enable_cloud_logging: bool = False
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()

