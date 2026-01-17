"""
Integration tests for team management API endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from team_alchemy.data.repository import get_db, init_db, SessionLocal
from team_alchemy.data.models import Team, User, Base
import os
import tempfile


@pytest.fixture(scope="function")
def test_db():
    """Create a test database."""
    # Use a temporary database file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db_path = tmp.name
    
    # Store original DATABASE_URL
    original_db_url = os.environ.get("DATABASE_URL")
    
    try:
        # Set DATABASE_URL to use temp file
        os.environ["DATABASE_URL"] = f"sqlite:///{tmp_db_path}"
        
        # Re-initialize the database with the test URL
        import team_alchemy.data.repository as repo_module
        repo_module.engine, repo_module.SessionLocal = repo_module._create_engine_and_session()
        
        # Initialize database tables
        init_db()
        
        yield
        
    finally:
        # Restore original DATABASE_URL
        if original_db_url:
            os.environ["DATABASE_URL"] = original_db_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        
        # Cleanup
        import team_alchemy.data.repository as repo_module
        if hasattr(repo_module, 'engine') and repo_module.engine is not None:
            repo_module.engine.dispose()
        
        # Re-initialize with original settings
        repo_module.engine, repo_module.SessionLocal = repo_module._create_engine_and_session()
        
        # Remove temp database file
        if os.path.exists(tmp_db_path):
            os.unlink(tmp_db_path)


@pytest.mark.asyncio
async def test_create_team(test_db):
    """Test creating a new team."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        team_data = {
            "name": "Engineering Team",
            "description": "Core engineering team for backend development"
        }
        
        response = await client.post("/api/v1/teams/", json=team_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == "Engineering Team"
        assert data["description"] == "Core engineering team for backend development"
        assert "id" in data
        assert data["id"] > 0
        assert "created_at" in data
        assert "updated_at" in data
        assert "members" in data
        assert data["members"] == []


@pytest.mark.asyncio
async def test_create_team_duplicate_name(test_db):
    """Test creating a team with duplicate name."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        team_data = {
            "name": "Duplicate Team",
            "description": "First team"
        }
        
        # Create first team
        response1 = await client.post("/api/v1/teams/", json=team_data)
        assert response1.status_code == 201
        
        # Try to create second team with same name
        response2 = await client.post("/api/v1/teams/", json=team_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_team_without_description(test_db):
    """Test creating a team without description."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        team_data = {
            "name": "Minimal Team"
        }
        
        response = await client.post("/api/v1/teams/", json=team_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Team"
        assert data["description"] is None


@pytest.mark.asyncio
async def test_get_team(test_db):
    """Test getting a team by ID."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First create a team
        team_data = {
            "name": "Test Team",
            "description": "A test team"
        }
        create_response = await client.post("/api/v1/teams/", json=team_data)
        assert create_response.status_code == 201
        team_id = create_response.json()["id"]
        
        # Get the team
        response = await client.get(f"/api/v1/teams/{team_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == team_id
        assert data["name"] == "Test Team"
        assert data["description"] == "A test team"
        assert "members" in data


@pytest.mark.asyncio
async def test_get_team_not_found(test_db):
    """Test getting a non-existent team."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/teams/99999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_teams_empty(test_db):
    """Test listing teams when none exist."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/teams/")
        
        assert response.status_code == 200
        data = response.json()
        assert "teams" in data
        assert "total" in data
        assert data["teams"] == []
        assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_teams(test_db):
    """Test listing multiple teams."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create multiple teams
        teams_to_create = [
            {"name": "Team 1", "description": "First team"},
            {"name": "Team 2", "description": "Second team"},
            {"name": "Team 3", "description": "Third team"}
        ]
        
        for team_data in teams_to_create:
            response = await client.post("/api/v1/teams/", json=team_data)
            assert response.status_code == 201
        
        # List all teams
        response = await client.get("/api/v1/teams/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["teams"]) == 3
        
        # Verify team names
        team_names = [team["name"] for team in data["teams"]]
        assert "Team 1" in team_names
        assert "Team 2" in team_names
        assert "Team 3" in team_names


@pytest.mark.asyncio
async def test_add_team_member(test_db):
    """Test adding a member to a team."""
    # Create user  directly in test database BEFORE starting client
    from team_alchemy.data.repository import SessionLocal
    db = SessionLocal()
    try:
        user = User(email="user@example.com", name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id
    finally:
        db.close()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a team
        team_data = {"name": "Test Team"}
        team_response = await client.post("/api/v1/teams/", json=team_data)
        assert team_response.status_code == 201
        team_id = team_response.json()["id"]
        
        # Add member to team
        response = await client.post(f"/api/v1/teams/{team_id}/members/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == team_id
        assert "members" in data
        assert len(data["members"]) == 1
        assert data["members"][0]["id"] == user_id
        assert data["members"][0]["email"] == "user@example.com"
        assert data["members"][0]["name"] == "Test User"


@pytest.mark.asyncio
async def test_add_team_member_team_not_found(test_db):
    """Test adding a member to a non-existent team."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/teams/99999/members/1")
        
        assert response.status_code == 404
        assert "team not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_add_team_member_user_not_found(test_db):
    """Test adding a non-existent user to a team."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a team
        team_data = {"name": "Test Team"}
        team_response = await client.post("/api/v1/teams/", json=team_data)
        assert team_response.status_code == 201
        team_id = team_response.json()["id"]
        
        # Try to add non-existent user
        response = await client.post(f"/api/v1/teams/{team_id}/members/99999")
        
        assert response.status_code == 404
        assert "user not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_add_team_member_duplicate(test_db):
    """Test adding the same member twice to a team."""
    # Create user directly in test database BEFORE starting client
    from team_alchemy.data.repository import SessionLocal
    db = SessionLocal()
    try:
        user = User(email="user@example.com", name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id
    finally:
        db.close()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a team
        team_data = {"name": "Test Team"}
        team_response = await client.post("/api/v1/teams/", json=team_data)
        assert team_response.status_code == 201
        team_id = team_response.json()["id"]
        
        # Add member first time
        response1 = await client.post(f"/api/v1/teams/{team_id}/members/{user_id}")
        assert response1.status_code == 200
        
        # Try to add same member again
        response2 = await client.post(f"/api/v1/teams/{team_id}/members/{user_id}")
        assert response2.status_code == 400
        assert "already a member" in response2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_add_multiple_members(test_db):
    """Test adding multiple members to a team."""
    # Create multiple users directly in test database BEFORE starting client
    from team_alchemy.data.repository import SessionLocal
    db = SessionLocal()
    try:
        user1 = User(email="user1@example.com", name="User One")
        user2 = User(email="user2@example.com", name="User Two")
        user3 = User(email="user3@example.com", name="User Three")
        db.add_all([user1, user2, user3])
        db.commit()
        db.refresh(user1)
        db.refresh(user2)
        db.refresh(user3)
        user_ids = [user1.id, user2.id, user3.id]
    finally:
        db.close()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create a team
        team_data = {"name": "Test Team"}
        team_response = await client.post("/api/v1/teams/", json=team_data)
        assert team_response.status_code == 201
        team_id = team_response.json()["id"]
        
        # Add all members
        for user_id in user_ids:
            response = await client.post(f"/api/v1/teams/{team_id}/members/{user_id}")
            assert response.status_code == 200
        
        # Get team and verify all members
        response = await client.get(f"/api/v1/teams/{team_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["members"]) == 3
        member_emails = [m["email"] for m in data["members"]]
        assert "user1@example.com" in member_emails
        assert "user2@example.com" in member_emails
        assert "user3@example.com" in member_emails
