"""
Application settings and configuration.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = os.getenv("APP_NAME", "Team Alchemy")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # API
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")
    cors_origins: list[str] = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") else ["*"]
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./team_alchemy.db")
    database_echo: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"
    
    # Redis/Celery
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "json")
    
    # ML Models
    model_path: str = os.getenv("MODEL_PATH", "./models")
    enable_ml: bool = os.getenv("ENABLE_ML", "True").lower() == "true"
    
    # Features
    enable_shadow_work: bool = os.getenv("ENABLE_SHADOW_WORK", "True").lower() == "true"
    enable_recommendations: bool = os.getenv("ENABLE_RECOMMENDATIONS", "True").lower() == "true"
    max_recommendations: int = int(os.getenv("MAX_RECOMMENDATIONS", "10"))
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
