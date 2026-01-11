"""
Unit tests for middleware.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from team_alchemy.api.middleware.validation import ValidationMiddleware, validate_request_data
from fastapi import HTTPException


def test_validation_middleware_initialization():
    """Test that ValidationMiddleware can be initialized correctly."""
    app = FastAPI()
    app.add_middleware(ValidationMiddleware, max_request_size=1024)
    
    # If this doesn't raise an error, the middleware is initialized correctly
    client = TestClient(app)
    
    @app.get("/")
    def root():
        return {"message": "Hello"}
    
    response = client.get("/")
    assert response.status_code == 200


def test_validation_middleware_normal_request():
    """Test that normal requests pass through the middleware."""
    app = FastAPI()
    app.add_middleware(ValidationMiddleware, max_request_size=10 * 1024 * 1024)
    
    @app.get("/")
    def root():
        return {"message": "Hello"}
    
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello"}


def test_validation_middleware_request_too_large():
    """Test that requests exceeding max size are rejected."""
    app = FastAPI()
    app.add_middleware(ValidationMiddleware, max_request_size=100)  # 100 bytes
    
    @app.post("/")
    def root(data: dict):
        return {"message": "Hello"}
    
    client = TestClient(app)
    
    # Create a request that will trigger the validation
    # The middleware checks the Content-Length header before processing the body
    import json
    large_data = {"data": "x" * 1000}
    json_data = json.dumps(large_data)
    actual_length = len(json_data)
    
    # Send request with actual content length that exceeds the limit
    response = client.post("/", json=large_data, headers={"content-length": str(actual_length)})
    
    assert response.status_code == 413
    assert response.json() == {"detail": "Request too large"}


def test_validate_request_data_valid():
    """Test validate_request_data with valid data."""
    data = {"name": "John", "email": "john@example.com"}
    required_fields = ["name", "email"]
    
    result = validate_request_data(data, required_fields)
    assert result is True


def test_validate_request_data_missing_fields():
    """Test validate_request_data with missing fields."""
    data = {"name": "John"}
    required_fields = ["name", "email"]
    
    with pytest.raises(HTTPException) as exc_info:
        validate_request_data(data, required_fields)
    
    assert exc_info.value.status_code == 422
    assert "Missing required fields: email" in str(exc_info.value.detail)


def test_validate_request_data_multiple_missing_fields():
    """Test validate_request_data with multiple missing fields."""
    data = {"name": "John"}
    required_fields = ["name", "email", "age"]
    
    with pytest.raises(HTTPException) as exc_info:
        validate_request_data(data, required_fields)
    
    assert exc_info.value.status_code == 422
    assert "email" in str(exc_info.value.detail)
    assert "age" in str(exc_info.value.detail)
