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
    secret_key: str = Field(default="your-secret-key-change-in-production")
    algorithm: str = Field(default="HS256", validation_alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    @field_validator('secret_key', mode='before')
    @classmethod
    def parse_secret_key(cls, v):
        """Parse secret key, supporting both SECRET_KEY and JWT_SECRET for backward compatibility."""
        # Check SECRET_KEY first (new standard)
        secret = os.getenv("SECRET_KEY")
        if secret:
            return secret
        # Fall back to JWT_SECRET for backward compatibility
        jwt_secret = os.getenv("JWT_SECRET")
        if jwt_secret:
            return jwt_secret
        # Use provided value or default
        return v if v is not None else "your-secret-key-change-in-production"
    
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
        return cls._get_redis_based_url("CELERY_BROKER_URL", cls.DEFAULT_REDIS_URL)
    
    @field_validator('celery_result_backend', mode='before')
    @classmethod
    def parse_celery_result(cls, v):
        """Parse Celery result backend, using REDIS_URL if available."""
        return cls._get_redis_based_url("CELERY_RESULT_BACKEND", cls.DEFAULT_REDIS_URL)
    
    def validate_critical_env_vars(self) -> None:
        """
        Validate critical environment variables for production deployments.
        
        Raises:
            ValueError: If critical environment variables are missing or invalid in production.
        """
        issues = []
        
        # Check SECRET_KEY in production
        if self.environment.lower() == "production":
            if self.secret_key == "your-secret-key-change-in-production":
                issues.append(
                    "SECRET_KEY is set to default value. "
                    "Please set a secure random key in production environment."
                )
            elif len(self.secret_key) < 32:
                issues.append(
                    f"SECRET_KEY is too short ({len(self.secret_key)} characters). "
                    "Recommended minimum is 32 characters for security."
                )
        
        # Check DATABASE_URL
        if self.database_url:
            # Validate it's a proper database URL format
            if not any(self.database_url.startswith(prefix) for prefix in 
                      ['postgresql://', 'postgres://', 'sqlite://', 'mysql://']):
                issues.append(
                    "DATABASE_URL appears to have an invalid format. "
                    "Expected format: postgresql://user:pass@host:port/dbname"
                )
        else:
            issues.append("DATABASE_URL is empty or not set.")
        
        # Check PORT is valid
        if not isinstance(self.api_port, int) or self.api_port < 1 or self.api_port > 65535:
            issues.append(
                f"API port is invalid: {self.api_port}. Must be between 1 and 65535."
            )
        
        if issues:
            error_msg = "Environment variable validation failed:\n" + "\n".join(f"  - {issue}" for issue in issues)
            if self.environment.lower() == "production":
                raise ValueError(error_msg)
            else:
                # In development, just log warnings
                import logging
                logger = logging.getLogger("team_alchemy")
                logger.warning("Environment validation warnings:")
                for issue in issues:
                    logger.warning(f"  - {issue}")


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
