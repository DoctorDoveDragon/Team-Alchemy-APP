"""
Application settings and configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional, List, Union, ClassVar
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Constants
    DEFAULT_REDIS_URL: ClassVar[str] = "redis://localhost:6379/0"
    
    # Application
    app_name: str = Field(default="Team Alchemy", validation_alias="APP_NAME")
    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    debug: bool = Field(default=False, validation_alias="DEBUG")
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    
    # API
    api_host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    api_port: int = Field(default=8000)
    api_prefix: str = Field(default="/api/v1", validation_alias="API_PREFIX")
    cors_origins: Union[List[str], str] = Field(default=["*"])
    
    # Database
    database_url: str = Field(default="sqlite:///./team_alchemy.db", validation_alias="DATABASE_URL")
    database_echo: bool = Field(default=False, validation_alias="DATABASE_ECHO")
    
    # Redis/Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/0")
    celery_result_backend: str = Field(default="redis://localhost:6379/0")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", validation_alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", validation_alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Logging
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    log_format: str = Field(default="json", validation_alias="LOG_FORMAT")
    
    # ML Models
    model_path: str = Field(default="./models", validation_alias="MODEL_PATH")
    enable_ml: bool = Field(default=True, validation_alias="ENABLE_ML")
    
    # Features
    enable_shadow_work: bool = Field(default=True, validation_alias="ENABLE_SHADOW_WORK")
    enable_recommendations: bool = Field(default=True, validation_alias="ENABLE_RECOMMENDATIONS")
    max_recommendations: int = Field(default=10, validation_alias="MAX_RECOMMENDATIONS")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator('api_port', mode='before')
    @classmethod
    def parse_port(cls, v):
        """Parse port from environment, prioritizing PORT over API_PORT."""
        # Check PORT environment variable (Railway)
        port = os.getenv("PORT")
        if port:
            try:
                return int(port)
            except (ValueError, TypeError):
                pass  # Fall through to use provided value or API_PORT
        
        # Otherwise use the provided value or API_PORT
        if v is not None:
            try:
                return int(v) if not isinstance(v, int) else v
            except (ValueError, TypeError):
                pass
        
        api_port = os.getenv("API_PORT")
        if api_port:
            try:
                return int(api_port)
            except (ValueError, TypeError):
                pass
        
        return 8000
    
    @classmethod
    def _get_redis_based_url(cls, env_var_name: str, default_value: str) -> str:
        """Helper method to get Redis-based URL with fallback to REDIS_URL."""
        # Check specific environment variable first
        specific_url = os.getenv(env_var_name)
        if specific_url:
            return specific_url
        
        # Fall back to REDIS_URL if available
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            return redis_url
        
        return default_value
    
    @field_validator('celery_broker_url', mode='before')
    @classmethod
    def parse_celery_broker(cls, v):
        """Parse Celery broker URL, using REDIS_URL if available."""
        if v is not None and v != cls.DEFAULT_REDIS_URL:
            return v
        return cls._get_redis_based_url("CELERY_BROKER_URL", cls.DEFAULT_REDIS_URL)
    
    @field_validator('celery_result_backend', mode='before')
    @classmethod
    def parse_celery_result(cls, v):
        """Parse Celery result backend, using REDIS_URL if available."""
        if v is not None and v != cls.DEFAULT_REDIS_URL:
            return v
        return cls._get_redis_based_url("CELERY_RESULT_BACKEND", cls.DEFAULT_REDIS_URL)


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
