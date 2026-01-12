"""
Unit tests for environment variable validation.
"""

import pytest
from config.settings import Settings


def test_validation_passes_in_development(monkeypatch):
    """Test that validation warnings are logged in development, not errors."""
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("SECRET_KEY", "your-secret-key-change-in-production")
    
    settings = Settings()
    
    # Should not raise an error in development
    settings.validate_critical_env_vars()
    
    # Verify settings are still accessible
    assert settings.environment == "development"


def test_validation_fails_in_production_with_default_secret(monkeypatch):
    """Test that validation fails in production with default SECRET_KEY."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "your-secret-key-change-in-production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")
    
    settings = Settings()
    
    with pytest.raises(ValueError, match="SECRET_KEY is set to default value"):
        settings.validate_critical_env_vars()


def test_validation_fails_with_short_secret_key(monkeypatch):
    """Test that validation fails with a short SECRET_KEY in production."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "short")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")
    
    settings = Settings()
    
    with pytest.raises(ValueError, match="SECRET_KEY is too short"):
        settings.validate_critical_env_vars()


def test_validation_passes_with_valid_production_config(monkeypatch):
    """Test that validation passes with valid production configuration."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)  # 32 character secret
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")
    monkeypatch.setenv("PORT", "8000")
    
    settings = Settings()
    
    # Should not raise an error
    settings.validate_critical_env_vars()


def test_validation_catches_invalid_database_url(monkeypatch):
    """Test that validation catches invalid DATABASE_URL format."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("DATABASE_URL", "invalid-url")
    
    settings = Settings()
    
    with pytest.raises(ValueError, match="DATABASE_URL appears to have an invalid format"):
        settings.validate_critical_env_vars()


def test_validation_accepts_valid_database_urls(monkeypatch):
    """Test that validation accepts various valid DATABASE_URL formats."""
    valid_urls = [
        "postgresql://user:pass@localhost:5432/db",
        "postgres://user:pass@localhost:5432/db",
        "sqlite:///./test.db",
        "mysql://user:pass@localhost:3306/db"
    ]
    
    for db_url in valid_urls:
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        monkeypatch.setenv("DATABASE_URL", db_url)
        
        settings = Settings()
        
        # Should not raise an error
        settings.validate_critical_env_vars()


def test_validation_catches_invalid_port(monkeypatch):
    """Test that validation catches invalid PORT values."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")
    monkeypatch.setenv("PORT", "99999")  # Out of valid range
    
    settings = Settings()
    
    # The port parser accepts 99999, but validation should catch it
    with pytest.raises(ValueError, match="API port is invalid"):
        settings.validate_critical_env_vars()
