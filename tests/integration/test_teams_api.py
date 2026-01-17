"""
Integration tests for team management API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from team_alchemy.data.models import Base, Team, User
from team_alchemy.data.repository import get_db


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_teams.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create test client with database override."""
    from main import app

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_users(db_session):
    """Create multiple sample users for testing."""
    users = [
        User(email=f"user{i}@example.com", name=f"User {i}")
        for i in range(1, 4)
    ]
    for user in users:
        db_session.add(user)
    db_session.commit()
    for user in users:
        db_session.refresh(user)
    return users


@pytest.fixture
def sample_team(db_session):
    """Create a sample team for testing."""
    team = Team(
        name="Test Team",
        description="A test team"
    )
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)
    return team


class TestCreateTeam:
    """Tests for POST /teams/ endpoint."""

    def test_create_team_success(self, client):
        """Test creating a new team successfully."""
        team_data = {
            "name": "Engineering Team",
            "description": "Software development team"
        }

        response = client.post("/api/v1/teams/", json=team_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == team_data["name"]
        assert data["description"] == team_data["description"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["members"] == []

    def test_create_team_minimal(self, client):
        """Test creating a team with only required fields."""
        team_data = {
            "name": "Minimal Team"
        }

        response = client.post("/api/v1/teams/", json=team_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == team_data["name"]
        assert data["description"] is None

    def test_create_team_duplicate_name(self, client, sample_team):
        """Test creating a team with duplicate name fails."""
        team_data = {
            "name": sample_team.name,
            "description": "Different description"
        }

        response = client.post("/api/v1/teams/", json=team_data)

        assert response.status_code == 400
        data = response.json()
        assert "already exists" in data["detail"].lower()

    def test_create_team_empty_name(self, client):
        """Test creating a team with empty name fails."""
        team_data = {
            "name": ""
        }

        response = client.post("/api/v1/teams/", json=team_data)

        assert response.status_code == 422  # Validation error

    def test_create_team_no_name(self, client):
        """Test creating a team without name fails."""
        team_data = {
            "description": "Team without name"
        }

        response = client.post("/api/v1/teams/", json=team_data)

        assert response.status_code == 422  # Validation error


class TestGetTeam:
    """Tests for GET /teams/{team_id} endpoint."""

    def test_get_team_success(self, client, sample_team):
        """Test retrieving a team by ID successfully."""
        response = client.get(f"/api/v1/teams/{sample_team.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_team.id
        assert data["name"] == sample_team.name
        assert data["description"] == sample_team.description
        assert "created_at" in data
        assert "updated_at" in data
        assert isinstance(data["members"], list)

    def test_get_team_with_members(self, client, sample_team, sample_users, db_session):
        """Test retrieving a team with members."""
        # Add members to team
        for user in sample_users:
            sample_team.members.append(user)
        db_session.commit()

        response = client.get(f"/api/v1/teams/{sample_team.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["members"]) == len(sample_users)
        member_emails = [m["email"] for m in data["members"]]
        for user in sample_users:
            assert user.email in member_emails

    def test_get_team_not_found(self, client):
        """Test retrieving a non-existent team returns 404."""
        response = client.get("/api/v1/teams/99999")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestListTeams:
    """Tests for GET /teams/ endpoint."""

    def test_list_teams_empty(self, client):
        """Test listing teams when none exist."""
        response = client.get("/api/v1/teams/")

        assert response.status_code == 200
        data = response.json()
        assert data["teams"] == []
        assert data["total"] == 0
        assert data["skip"] == 0
        assert data["limit"] == 100

    def test_list_teams_with_data(self, client, db_session):
        """Test listing teams with data."""
        # Create multiple teams
        teams = [
            Team(name=f"Team {i}", description=f"Description {i}")
            for i in range(1, 6)
        ]
        for team in teams:
            db_session.add(team)
        db_session.commit()

        response = client.get("/api/v1/teams/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["teams"]) == 5
        assert data["total"] == 5
        assert data["skip"] == 0
        assert data["limit"] == 100

    def test_list_teams_pagination(self, client, db_session):
        """Test pagination in team listing."""
        # Create 10 teams
        teams = [
            Team(name=f"Team {i}", description=f"Description {i}")
            for i in range(1, 11)
        ]
        for team in teams:
            db_session.add(team)
        db_session.commit()

        # Test skip and limit
        response = client.get("/api/v1/teams/?skip=2&limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data["teams"]) == 3
        assert data["total"] == 10
        assert data["skip"] == 2
        assert data["limit"] == 3

    def test_list_teams_invalid_skip(self, client):
        """Test listing teams with invalid skip parameter."""
        response = client.get("/api/v1/teams/?skip=-1")

        assert response.status_code == 400
        data = response.json()
        assert "non-negative" in data["detail"].lower()

    def test_list_teams_invalid_limit(self, client):
        """Test listing teams with invalid limit parameter."""
        response = client.get("/api/v1/teams/?limit=0")

        assert response.status_code == 400

        response = client.get("/api/v1/teams/?limit=101")

        assert response.status_code == 400


class TestAddTeamMember:
    """Tests for POST /teams/{team_id}/members/{user_id} endpoint."""

    def test_add_member_success(self, client, sample_team, sample_user):
        """Test adding a member to a team successfully."""
        response = client.post(
            f"/api/v1/teams/{sample_team.id}/members/{sample_user.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Member added successfully"
        assert data["team"]["id"] == sample_team.id
        assert len(data["team"]["members"]) == 1
        assert data["team"]["members"][0]["id"] == sample_user.id
        assert data["team"]["members"][0]["email"] == sample_user.email

    def test_add_member_duplicate(self, client, sample_team, sample_user, db_session):
        """Test adding a member who is already in the team fails."""
        # Add member first time
        sample_team.members.append(sample_user)
        db_session.commit()

        # Try to add again
        response = client.post(
            f"/api/v1/teams/{sample_team.id}/members/{sample_user.id}"
        )

        assert response.status_code == 400
        data = response.json()
        assert "already a member" in data["detail"].lower()

    def test_add_member_team_not_found(self, client, sample_user):
        """Test adding a member to non-existent team fails."""
        response = client.post(
            f"/api/v1/teams/99999/members/{sample_user.id}"
        )

        assert response.status_code == 404
        data = response.json()
        assert "team" in data["detail"].lower()
        assert "not found" in data["detail"].lower()

    def test_add_member_user_not_found(self, client, sample_team):
        """Test adding a non-existent user to team fails."""
        response = client.post(
            f"/api/v1/teams/{sample_team.id}/members/99999"
        )

        assert response.status_code == 404
        data = response.json()
        assert "user" in data["detail"].lower()
        assert "not found" in data["detail"].lower()

    def test_add_multiple_members(self, client, sample_team, sample_users):
        """Test adding multiple members to a team."""
        for user in sample_users:
            response = client.post(
                f"/api/v1/teams/{sample_team.id}/members/{user.id}"
            )
            assert response.status_code == 200

        # Verify all members are in the team
        response = client.get(f"/api/v1/teams/{sample_team.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["members"]) == len(sample_users)
