"""
Integration tests for API endpoints.
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

# Note: These are placeholder tests that will need a proper test setup
# with database fixtures and app initialization


def test_placeholder():
    """Placeholder test to ensure test suite runs."""
    assert True


@pytest.fixture
def client():
    """Create test client."""
    from main import app

    return TestClient(app)


def test_healthz_endpoint(client):
    """Test Railway health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "name" in data
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data
    # Verify timestamp is in ISO format
    timestamp = datetime.fromisoformat(data["timestamp"])
    assert timestamp is not None


def test_health_endpoint(client):
    """Test legacy health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "name" in data
    assert "version" in data
    assert data["docs"] == "/docs"


def test_healthz_detailed_endpoint_development(client, monkeypatch):
    """Test detailed health check endpoint in development environment."""
    # Set environment to development
    from config.settings import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "environment", "development")

    response = client.get("/healthz/detailed")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "degraded"]
    assert "name" in data
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data
    assert "components" in data
    assert "database" in data["components"]
    # Verify timestamp is in ISO format
    timestamp = datetime.fromisoformat(data["timestamp"])
    assert timestamp is not None


def test_healthz_detailed_endpoint_production(client, monkeypatch):
    """Test detailed health check endpoint returns 404 in production."""
    # Set environment to production
    from config.settings import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "environment", "production")

    response = client.get("/healthz/detailed")
    assert response.status_code == 404


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    # Could be either static files or JSON response
    # Just verify we get a response


def test_get_all_archetypes(client):
    """Test GET /api/v1/archetypes/ endpoint."""
    response = client.get("/api/v1/archetypes/")
    assert response.status_code == 200
    data = response.json()
    assert "archetypes" in data
    assert isinstance(data["archetypes"], dict)
    # Verify at least one archetype is returned
    assert len(data["archetypes"]) > 0
    # Verify the leader archetype exists
    assert "leader" in data["archetypes"]
    leader = data["archetypes"]["leader"]
    assert leader["archetype_type"] == "leader"
    assert leader["name"] == "The Leader"
    assert "description" in leader
    assert "core_traits" in leader
    assert "strengths" in leader
    assert "challenges" in leader
    assert "jungian_mapping" in leader


def test_get_specific_archetype(client):
    """Test GET /api/v1/archetypes/{archetype_type} endpoint."""
    response = client.get("/api/v1/archetypes/leader")
    assert response.status_code == 200
    data = response.json()
    assert data["archetype_type"] == "leader"
    assert data["name"] == "The Leader"
    assert "description" in data
    assert isinstance(data["core_traits"], list)
    assert isinstance(data["strengths"], list)
    assert isinstance(data["challenges"], list)
    assert isinstance(data["jungian_mapping"], dict)


def test_get_nonexistent_archetype(client):
    """Test GET /api/v1/archetypes/{archetype_type} with invalid type."""
    response = client.get("/api/v1/archetypes/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_archetype_case_insensitive(client):
    """Test that archetype lookup is case-insensitive."""
    # Test with uppercase
    response = client.get("/api/v1/archetypes/LEADER")
    assert response.status_code == 200
    data = response.json()
    assert data["archetype_type"] == "leader"


# def test_create_assessment(client):
#     """Test creating an assessment."""
#     assessment_data = {
#         "title": "Test Assessment",
#         "description": "A test assessment",
#         "questions": []
#     }
#
#     response = client.post("/assessments/", json=assessment_data)
#     # Placeholder - would check response
#     assert True


# def test_get_assessment(client):
#     """Test retrieving an assessment."""
#     response = client.get("/assessments/1")
#     # Placeholder - would check response
#     assert True
