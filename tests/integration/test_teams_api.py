"""
Integration tests for team API endpoints.
"""

import pytest
import os
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from team_alchemy.data.models import Base, Team, User
from team_alchemy.data.repository import get_db


@pytest.fixture(scope="function")
def test_db():
    """Create a test database."""
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db_path = tmp.name
    
    # Create engine and session
    database_url = f"sqlite:///{tmp_db_path}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield TestingSessionLocal
    
    # Cleanup
    engine.dispose()
    if Path(tmp_db_path).exists():
        Path(tmp_db_path).unlink()


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with test database."""
    from main import app
    
    # Override get_db dependency
    def override_get_db():
        db = test_db()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_users(test_db):
    """Create sample users for testing."""
    db = test_db()
    
    users = [
        User(id=1, email="user1@example.com", name="User One"),
        User(id=2, email="user2@example.com", name="User Two"),
        User(id=3, email="user3@example.com", name="User Three"),
    ]
    
    for user in users:
        db.add(user)
    db.commit()
    
    for user in users:
        db.refresh(user)
    
    db.close()
    return users


class TestCreateTeam:
    """Tests for POST /teams/ endpoint."""

    def test_create_team_success(self, client):
        """Test successful team creation."""
        team_data = {
            "name": "Engineering Team",
            "description": "Core engineering team"
        }
        
        response = client.post("/api/v1/teams/", json=team_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == team_data["name"]
        assert data["description"] == team_data["description"]
        assert "id" in data
        assert data["id"] > 0
        assert "created_at" in data
        assert "updated_at" in data
        assert data["members"] == []

    def test_create_team_minimal(self, client):
        """Test team creation with minimal data (only name)."""
        team_data = {"name": "Minimal Team"}
        
        response = client.post("/api/v1/teams/", json=team_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == team_data["name"]
        assert data["description"] is None
        assert "id" in data

    def test_create_team_invalid_empty_name(self, client):
        """Test team creation with empty name fails."""
        team_data = {"name": ""}
        
        response = client.post("/api/v1/teams/", json=team_data)
        
        assert response.status_code == 422  # Validation error

    def test_create_team_missing_name(self, client):
        """Test team creation without name fails."""
        team_data = {"description": "Team without name"}
        
        response = client.post("/api/v1/teams/", json=team_data)
        
        assert response.status_code == 422  # Validation error


class TestGetTeam:
    """Tests for GET /teams/{team_id} endpoint."""

    def test_get_team_success(self, client):
        """Test successful team retrieval."""
        # First create a team
        team_data = {"name": "Test Team", "description": "Test Description"}
        create_response = client.post("/api/v1/teams/", json=team_data)
        created_team = create_response.json()
        team_id = created_team["id"]
        
        # Get the team
        response = client.get(f"/api/v1/teams/{team_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == team_id
        assert data["name"] == team_data["name"]
        assert data["description"] == team_data["description"]
        assert "members" in data

    def test_get_team_not_found(self, client):
        """Test getting non-existent team returns 404."""
        response = client.get("/api/v1/teams/999999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_get_team_with_members(self, client, sample_users):
        """Test getting team with members."""
        # Create a team
        team_data = {"name": "Team with Members"}
        create_response = client.post("/api/v1/teams/", json=team_data)
        team_id = create_response.json()["id"]
        
        # Add members
        client.post(f"/api/v1/teams/{team_id}/members/1")
        client.post(f"/api/v1/teams/{team_id}/members/2")
        
        # Get team
        response = client.get(f"/api/v1/teams/{team_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["members"]) == 2
        member_ids = [m["id"] for m in data["members"]]
        assert 1 in member_ids
        assert 2 in member_ids


class TestAddTeamMember:
    """Tests for POST /teams/{team_id}/members/{user_id} endpoint."""

    def test_add_member_success(self, client, sample_users):
        """Test successfully adding a member to a team."""
        # Create a team
        team_data = {"name": "Test Team"}
        create_response = client.post("/api/v1/teams/", json=team_data)
        team_id = create_response.json()["id"]
        
        # Add a member
        response = client.post(f"/api/v1/teams/{team_id}/members/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User added to team successfully"
        assert data["team_id"] == team_id
        assert data["user_id"] == 1

    def test_add_member_team_not_found(self, client, sample_users):
        """Test adding member to non-existent team."""
        response = client.post("/api/v1/teams/999999/members/1")
        
        assert response.status_code == 404
        data = response.json()
        assert "team" in data["detail"].lower()

    def test_add_member_user_not_found(self, client):
        """Test adding non-existent user to team."""
        # Create a team
        team_data = {"name": "Test Team"}
        create_response = client.post("/api/v1/teams/", json=team_data)
        team_id = create_response.json()["id"]
        
        # Try to add non-existent user
        response = client.post(f"/api/v1/teams/{team_id}/members/999999")
        
        assert response.status_code == 404
        data = response.json()
        assert "user" in data["detail"].lower()

    def test_add_member_duplicate(self, client, sample_users):
        """Test adding the same member twice fails."""
        # Create a team
        team_data = {"name": "Test Team"}
        create_response = client.post("/api/v1/teams/", json=team_data)
        team_id = create_response.json()["id"]
        
        # Add member first time
        response1 = client.post(f"/api/v1/teams/{team_id}/members/1")
        assert response1.status_code == 200
        
        # Try to add same member again
        response2 = client.post(f"/api/v1/teams/{team_id}/members/1")
        
        assert response2.status_code == 400
        data = response2.json()
        assert "already a member" in data["detail"].lower()

    def test_add_multiple_members(self, client, sample_users):
        """Test adding multiple members to a team."""
        # Create a team
        team_data = {"name": "Test Team"}
        create_response = client.post("/api/v1/teams/", json=team_data)
        team_id = create_response.json()["id"]
        
        # Add multiple members
        response1 = client.post(f"/api/v1/teams/{team_id}/members/1")
        response2 = client.post(f"/api/v1/teams/{team_id}/members/2")
        response3 = client.post(f"/api/v1/teams/{team_id}/members/3")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        
        # Verify all members are in team
        get_response = client.get(f"/api/v1/teams/{team_id}")
        team_data = get_response.json()
        assert len(team_data["members"]) == 3


class TestListTeams:
    """Tests for GET /teams/ endpoint."""

    def test_list_teams_empty(self, client):
        """Test listing teams when none exist."""
        response = client.get("/api/v1/teams/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_teams_multiple(self, client):
        """Test listing multiple teams."""
        # Create multiple teams
        teams_data = [
            {"name": "Team 1", "description": "First team"},
            {"name": "Team 2", "description": "Second team"},
            {"name": "Team 3"},
        ]
        
        for team_data in teams_data:
            client.post("/api/v1/teams/", json=team_data)
        
        # List all teams
        response = client.get("/api/v1/teams/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        
        # Verify team names
        team_names = [team["name"] for team in data]
        assert "Team 1" in team_names
        assert "Team 2" in team_names
        assert "Team 3" in team_names

    def test_list_teams_with_members(self, client, sample_users):
        """Test listing teams includes member information."""
        # Create a team
        team_data = {"name": "Team with Members"}
        create_response = client.post("/api/v1/teams/", json=team_data)
        team_id = create_response.json()["id"]
        
        # Add members
        client.post(f"/api/v1/teams/{team_id}/members/1")
        client.post(f"/api/v1/teams/{team_id}/members/2")
        
        # List teams
        response = client.get("/api/v1/teams/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert len(data[0]["members"]) == 2
