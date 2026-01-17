"""
Unit tests for team management.
"""

import pytest
from datetime import datetime
from team_alchemy.data.models import Team, User
from team_alchemy.api.schemas.teams import TeamCreate, TeamResponse, UserResponse


class TestTeamSchemas:
    """Test Pydantic schemas for team management."""

    def test_team_create_valid(self):
        """Test valid TeamCreate schema."""
        team_data = TeamCreate(name="Test Team", description="Test Description")
        assert team_data.name == "Test Team"
        assert team_data.description == "Test Description"

    def test_team_create_minimal(self):
        """Test TeamCreate with minimal data."""
        team_data = TeamCreate(name="Test Team")
        assert team_data.name == "Test Team"
        assert team_data.description is None

    def test_team_create_invalid_empty_name(self):
        """Test TeamCreate with empty name fails validation."""
        with pytest.raises(ValueError):
            TeamCreate(name="")

    def test_team_response_from_model(self):
        """Test TeamResponse can be created from Team model."""
        team = Team(
            id=1,
            name="Test Team",
            description="Test Description",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        team.members = []
        
        # Test that model can be converted to schema
        response = TeamResponse.model_validate(team)
        assert response.id == 1
        assert response.name == "Test Team"
        assert response.description == "Test Description"
        assert isinstance(response.members, list)

    def test_user_response_from_model(self):
        """Test UserResponse can be created from User model."""
        user = User(
            id=1,
            email="test@example.com",
            name="Test User"
        )
        
        response = UserResponse.model_validate(user)
        assert response.id == 1
        assert response.email == "test@example.com"
        assert response.name == "Test User"


class TestTeamModel:
    """Test Team model."""

    def test_team_creation(self):
        """Test creating a Team instance."""
        team = Team(name="Test Team", description="Test Description")
        assert team.name == "Test Team"
        assert team.description == "Test Description"

    def test_team_members_relationship(self):
        """Test team-member relationship."""
        team = Team(name="Test Team")
        user = User(email="test@example.com", name="Test User")
        
        # Initialize members list
        team.members = []
        team.members.append(user)
        
        assert len(team.members) == 1
        assert team.members[0] == user


class TestUserModel:
    """Test User model."""

    def test_user_creation(self):
        """Test creating a User instance."""
        user = User(email="test@example.com", name="Test User")
        assert user.email == "test@example.com"
        assert user.name == "Test User"

    def test_user_teams_relationship(self):
        """Test user-team relationship."""
        user = User(email="test@example.com", name="Test User")
        team = Team(name="Test Team")
        
        # Initialize teams list
        user.teams = []
        user.teams.append(team)
        
        assert len(user.teams) == 1
        assert user.teams[0] == team
