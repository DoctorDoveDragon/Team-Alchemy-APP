"""
Unit tests for team schemas.
"""

import pytest
from pydantic import ValidationError
from team_alchemy.api.schemas.teams import TeamCreate, TeamResponse, UserInTeam, TeamListResponse
from datetime import datetime


def test_team_create_valid():
    """Test TeamCreate schema with valid data."""
    team_data = {
        "name": "Engineering Team",
        "description": "Core engineering team"
    }
    team = TeamCreate(**team_data)
    assert team.name == "Engineering Team"
    assert team.description == "Core engineering team"


def test_team_create_without_description():
    """Test TeamCreate schema without description."""
    team_data = {"name": "Minimal Team"}
    team = TeamCreate(**team_data)
    assert team.name == "Minimal Team"
    assert team.description is None


def test_team_create_empty_name():
    """Test TeamCreate schema with empty name."""
    with pytest.raises(ValidationError) as exc_info:
        TeamCreate(name="")
    
    errors = exc_info.value.errors()
    assert any("name" in str(error) for error in errors)


def test_team_create_name_too_long():
    """Test TeamCreate schema with name exceeding max length."""
    long_name = "a" * 256
    with pytest.raises(ValidationError) as exc_info:
        TeamCreate(name=long_name)
    
    errors = exc_info.value.errors()
    assert any("name" in str(error) for error in errors)


def test_team_create_description_too_long():
    """Test TeamCreate schema with description exceeding max length."""
    long_description = "a" * 1001
    with pytest.raises(ValidationError) as exc_info:
        TeamCreate(name="Team", description=long_description)
    
    errors = exc_info.value.errors()
    assert any("description" in str(error) for error in errors)


def test_user_in_team_schema():
    """Test UserInTeam schema."""
    user_data = {
        "id": 1,
        "email": "user@example.com",
        "name": "Test User"
    }
    user = UserInTeam(**user_data)
    assert user.id == 1
    assert user.email == "user@example.com"
    assert user.name == "Test User"


def test_team_response_schema():
    """Test TeamResponse schema."""
    team_data = {
        "id": 1,
        "name": "Engineering Team",
        "description": "Core team",
        "created_at": datetime(2024, 1, 1),
        "updated_at": datetime(2024, 1, 1),
        "members": [
            {
                "id": 1,
                "email": "user@example.com",
                "name": "Test User"
            }
        ]
    }
    team = TeamResponse(**team_data)
    assert team.id == 1
    assert team.name == "Engineering Team"
    assert team.description == "Core team"
    assert len(team.members) == 1
    assert team.members[0].email == "user@example.com"


def test_team_response_without_members():
    """Test TeamResponse schema without members."""
    team_data = {
        "id": 1,
        "name": "Empty Team",
        "description": None,
        "created_at": datetime(2024, 1, 1),
        "updated_at": datetime(2024, 1, 1)
    }
    team = TeamResponse(**team_data)
    assert team.id == 1
    assert team.name == "Empty Team"
    assert team.description is None
    assert team.members == []


def test_team_list_response_schema():
    """Test TeamListResponse schema."""
    list_data = {
        "teams": [
            {
                "id": 1,
                "name": "Team 1",
                "description": "First team",
                "created_at": datetime(2024, 1, 1),
                "updated_at": datetime(2024, 1, 1),
                "members": []
            },
            {
                "id": 2,
                "name": "Team 2",
                "description": "Second team",
                "created_at": datetime(2024, 1, 2),
                "updated_at": datetime(2024, 1, 2),
                "members": []
            }
        ],
        "total": 2
    }
    team_list = TeamListResponse(**list_data)
    assert team_list.total == 2
    assert len(team_list.teams) == 2
    assert team_list.teams[0].name == "Team 1"
    assert team_list.teams[1].name == "Team 2"


def test_team_list_response_empty():
    """Test TeamListResponse schema with empty list."""
    list_data = {
        "teams": [],
        "total": 0
    }
    team_list = TeamListResponse(**list_data)
    assert team_list.total == 0
    assert team_list.teams == []
