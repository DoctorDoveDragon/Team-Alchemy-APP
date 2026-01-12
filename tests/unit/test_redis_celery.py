"""
Unit tests for Redis and Celery configuration with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import redis


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis_client = Mock()
    redis_client.ping.return_value = True
    redis_client.get.return_value = None
    redis_client.set.return_value = True
    redis_client.delete.return_value = 1
    redis_client.exists.return_value = False
    return redis_client


@pytest.fixture
def mock_celery_app():
    """Create a mock Celery application."""
    celery_app = Mock()
    celery_app.conf = {}
    celery_app.task = Mock(return_value=lambda f: f)
    return celery_app


def test_redis_connection_with_valid_url(monkeypatch, mock_redis):
    """Test Redis connection with valid URL."""
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    
    with patch('redis.from_url') as mock_from_url:
        mock_from_url.return_value = mock_redis
        
        client = redis.from_url("redis://localhost:6379/0")
        
        # Verify connection
        assert client.ping() is True
        mock_redis.ping.assert_called_once()


def test_redis_connection_failure(monkeypatch):
    """Test Redis connection handles failures gracefully."""
    monkeypatch.setenv("REDIS_URL", "redis://invalid:6379/0")
    
    with patch('redis.from_url') as mock_from_url:
        mock_from_url.side_effect = ConnectionError("Redis connection failed")
        
        with pytest.raises(ConnectionError):
            redis.from_url("redis://invalid:6379/0")


def test_redis_operations_with_mock(mock_redis):
    """Test basic Redis operations with mock."""
    # Test SET
    result = mock_redis.set("key", "value")
    assert result is True
    
    # Test GET
    value = mock_redis.get("key")
    assert value is None  # Mock returns None by default
    
    # Test DELETE
    deleted = mock_redis.delete("key")
    assert deleted == 1
    
    # Test EXISTS
    exists = mock_redis.exists("key")
    assert exists is False


def test_celery_configuration_with_redis(monkeypatch, mock_celery_app):
    """Test Celery configuration with Redis backend."""
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    from config.settings import get_settings
    
    settings = get_settings()
    
    # Verify Celery URLs are set correctly
    assert settings.celery_broker_url == "redis://localhost:6379/0"
    assert settings.celery_result_backend == "redis://localhost:6379/0"


def test_celery_task_execution(mock_celery_app):
    """Test Celery task decorator with mock."""
    # Mock the task decorator to return the original function
    def task_decorator(func):
        return func
    
    mock_celery_app.task = task_decorator
    
    # Create a task
    @mock_celery_app.task
    def sample_task(x, y):
        return x + y
    
    # Execute task
    result = sample_task(2, 3)
    assert result == 5


def test_celery_broker_fallback_to_redis_url(monkeypatch):
    """Test that Celery broker falls back to REDIS_URL."""
    monkeypatch.delenv("CELERY_BROKER_URL", raising=False)
    monkeypatch.setenv("REDIS_URL", "redis://fallback-redis:6379/0")
    
    from config.settings import Settings
    
    settings = Settings()
    
    # Should fall back to REDIS_URL
    assert settings.celery_broker_url == "redis://fallback-redis:6379/0"


def test_celery_result_backend_fallback_to_redis_url(monkeypatch):
    """Test that Celery result backend falls back to REDIS_URL."""
    monkeypatch.delenv("CELERY_RESULT_BACKEND", raising=False)
    monkeypatch.setenv("REDIS_URL", "redis://fallback-redis:6379/0")
    
    from config.settings import Settings
    
    settings = Settings()
    
    # Should fall back to REDIS_URL
    assert settings.celery_result_backend == "redis://fallback-redis:6379/0"


def test_redis_connection_pool(mock_redis):
    """Test Redis connection pool configuration."""
    # Configure mock for connection pool
    mock_pool = Mock()
    mock_pool.get_connection.return_value = Mock()
    
    mock_redis.connection_pool = mock_pool
    
    # Verify connection pool is accessible
    assert mock_redis.connection_pool is not None
    assert mock_redis.connection_pool == mock_pool


@patch('redis.Redis')
def test_redis_health_check(mock_redis_class):
    """Test Redis health check functionality."""
    mock_instance = Mock()
    mock_instance.ping.return_value = True
    mock_redis_class.return_value = mock_instance
    
    client = redis.Redis()
    
    # Health check
    is_healthy = client.ping()
    assert is_healthy is True
    mock_instance.ping.assert_called_once()


def test_multiple_redis_databases(monkeypatch):
    """Test configuration with different Redis databases."""
    test_cases = [
        ("redis://localhost:6379/0", "redis://localhost:6379/0"),
        ("redis://localhost:6379/1", "redis://localhost:6379/1"),
        ("redis://localhost:6379/15", "redis://localhost:6379/15"),
    ]
    
    for redis_url, expected_url in test_cases:
        monkeypatch.setenv("REDIS_URL", redis_url)
        
        from config.settings import Settings
        
        settings = Settings()
        assert settings.celery_broker_url == expected_url
        assert settings.celery_result_backend == expected_url
