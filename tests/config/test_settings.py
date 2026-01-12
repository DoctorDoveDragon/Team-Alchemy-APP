"""
Unit tests for settings configuration.
"""

import pytest
from config.settings import Settings, get_settings


def test_settings_default_values(monkeypatch):
    """Test that settings have correct default values."""
    # Clear any environment variables that might affect defaults
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    
    settings = Settings()
    
    assert settings.app_name == "Team Alchemy"
    assert settings.app_version == "0.1.0"
    assert settings.debug is False
    assert settings.environment == "development"
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000
    assert settings.api_prefix == "/api/v1"
    assert settings.cors_origins == ["*"]
    assert settings.database_url == "sqlite:///./team_alchemy.db"
    assert settings.secret_key == "your-secret-key-change-in-production"


def test_settings_with_environment_variables(monkeypatch):
    """Test that settings correctly read from environment variables."""
    # Set environment variables
    monkeypatch.setenv("PORT", "3000")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/testdb")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("CORS_ORIGINS", "https://example.com,https://www.example.com")
    monkeypatch.setenv("ENVIRONMENT", "production")
    
    # Create new settings instance
    settings = Settings()
    
    assert settings.api_port == 3000
    assert settings.database_url == "postgresql://test:test@localhost:5432/testdb"
    assert settings.secret_key == "test-secret-key"
    assert settings.cors_origins == ["https://example.com", "https://www.example.com"]
    assert settings.environment == "production"


def test_settings_redis_url_fallback(monkeypatch):
    """Test that Celery settings fall back to REDIS_URL."""
    monkeypatch.setenv("REDIS_URL", "redis://railway-redis:6379/0")
    
    settings = Settings()
    
    assert settings.celery_broker_url == "redis://railway-redis:6379/0"
    assert settings.celery_result_backend == "redis://railway-redis:6379/0"


def test_settings_cors_origins_single_value(monkeypatch):
    """Test that CORS origins work with single value."""
    monkeypatch.setenv("CORS_ORIGINS", "https://example.com")
    
    settings = Settings()
    
    assert settings.cors_origins == ["https://example.com"]


def test_settings_api_port_priority(monkeypatch):
    """Test that PORT environment variable takes priority over API_PORT."""
    monkeypatch.setenv("PORT", "8080")
    monkeypatch.setenv("API_PORT", "9000")
    
    settings = Settings()
    
    assert settings.api_port == 8080


def test_get_settings_function():
    """Test that get_settings() returns a Settings instance."""
    settings = get_settings()
    
    assert isinstance(settings, Settings)
    assert settings.app_name == "Team Alchemy"


def test_settings_boolean_parsing(monkeypatch):
    """Test that boolean values are correctly parsed."""
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("ENABLE_ML", "false")
    
    settings = Settings()
    
    assert settings.debug is True
    assert settings.enable_ml is False


def test_settings_invalid_port_fallback(monkeypatch):
    """Test that invalid PORT values fall back to default."""
    monkeypatch.setenv("PORT", "invalid-port")
    
    settings = Settings()
    
    # Should fall back to default port of 8000
    assert settings.api_port == 8000


def test_settings_jwt_secret_backward_compatibility(monkeypatch):
    """Test that JWT_SECRET is supported for backward compatibility."""
    # Clear SECRET_KEY to test JWT_SECRET fallback
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv("JWT_SECRET", "jwt-test-secret")
    
    settings = Settings()
    
    assert settings.secret_key == "jwt-test-secret"


def test_settings_secret_key_priority(monkeypatch):
    """Test that SECRET_KEY takes priority over JWT_SECRET."""
    monkeypatch.setenv("SECRET_KEY", "new-secret")
    monkeypatch.setenv("JWT_SECRET", "old-jwt-secret")
    
    settings = Settings()
    
    # SECRET_KEY should take priority
    assert settings.secret_key == "new-secret"
