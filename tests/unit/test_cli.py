"""
Unit tests for CLI commands.
"""

import pytest
import tempfile
import os
from pathlib import Path
from typer.testing import CliRunner
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from team_alchemy.cli.main import app
from team_alchemy.data.models import Base, User, UserProfile, Team


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create temporary database file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db_path = tmp.name
    
    # Set up database
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_db_path}"
    
    # Re-import to pick up new DATABASE_URL
    import importlib
    import team_alchemy.data.repository as repo_module
    importlib.reload(repo_module)
    
    # Initialize database
    repo_module.init_db()
    
    # Create session for setup
    engine = create_engine(f"sqlite:///{tmp_db_path}")
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Add test data
    user1 = User(id=1, email="test1@example.com", name="Test User 1")
    user2 = User(id=2, email="test2@example.com", name="Test User 2")
    user3 = User(id=3, email="test3@example.com", name="Test User 3")
    
    db.add(user1)
    db.add(user2)
    db.add(user3)
    db.commit()
    
    # Add profile for user1
    profile1 = UserProfile(
        user_id=1,
        jungian_type="INTJ",
        archetype="Analyst",
        trait_scores={"mbti_type": "INTJ"}
    )
    db.add(profile1)
    
    # Add profile for user2
    profile2 = UserProfile(
        user_id=2,
        jungian_type="ENFP",
        archetype="Innovator",
        trait_scores={"mbti_type": "ENFP"}
    )
    db.add(profile2)
    
    db.commit()
    
    # Create test team
    team = Team(id=1, name="Test Team", description="A test team")
    team.members.extend([user1, user2, user3])
    db.add(team)
    db.commit()
    
    db.close()
    
    yield tmp_db_path
    
    # Cleanup
    if Path(tmp_db_path).exists():
        Path(tmp_db_path).unlink()


def test_cli_version():
    """Test version command."""
    runner = CliRunner()
    result = runner.invoke(app, ["version"])
    
    assert result.exit_code == 0
    assert "Team Alchemy version" in result.stdout


def test_cli_assess_user_found(temp_db):
    """Test assess command with existing user."""
    runner = CliRunner()
    result = runner.invoke(app, ["assess", "1"])
    
    assert result.exit_code == 0
    assert "Test User 1" in result.stdout
    assert "INTJ" in result.stdout
    assert "Jungian Profile" in result.stdout
    assert "Assessment completed" in result.stdout


def test_cli_assess_user_not_found(temp_db):
    """Test assess command with non-existent user."""
    runner = CliRunner()
    result = runner.invoke(app, ["assess", "999"])
    
    assert result.exit_code == 1
    assert "not found" in result.stdout


def test_cli_assess_user_without_profile(temp_db):
    """Test assess command with user that has no profile."""
    runner = CliRunner()
    result = runner.invoke(app, ["assess", "3"])
    
    assert result.exit_code == 0
    assert "Test User 3" in result.stdout
    assert "Assessment completed" in result.stdout


def test_cli_analyze_team_found(temp_db):
    """Test analyze_team command with existing team."""
    runner = CliRunner()
    result = runner.invoke(app, ["analyze-team", "1"])
    
    assert result.exit_code == 0
    assert "Test Team" in result.stdout
    assert "3 members" in result.stdout
    assert "Team Dynamics" in result.stdout
    assert "Analysis completed" in result.stdout


def test_cli_analyze_team_not_found(temp_db):
    """Test analyze_team command with non-existent team."""
    runner = CliRunner()
    result = runner.invoke(app, ["analyze-team", "999"])
    
    assert result.exit_code == 1
    assert "not found" in result.stdout


def test_cli_recommend_team_found(temp_db):
    """Test recommend command with existing team."""
    runner = CliRunner()
    result = runner.invoke(app, ["recommend", "1"])
    
    assert result.exit_code == 0
    assert "Generating recommendations" in result.stdout
    assert "Team Recommendations" in result.stdout
    assert "recommendations generated" in result.stdout


def test_cli_recommend_with_max_limit(temp_db):
    """Test recommend command with max recommendations limit."""
    runner = CliRunner()
    result = runner.invoke(app, ["recommend", "1", "--max-recommendations", "3"])
    
    assert result.exit_code == 0
    assert "3 recommendations generated" in result.stdout or "recommendations generated" in result.stdout


def test_cli_recommend_team_not_found(temp_db):
    """Test recommend command with non-existent team."""
    runner = CliRunner()
    result = runner.invoke(app, ["recommend", "999"])
    
    assert result.exit_code == 1
    assert "not found" in result.stdout


def test_cli_init_db():
    """Test database initialization command."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db_path = tmp.name
    
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{tmp_db_path}"
        
        runner = CliRunner()
        result = runner.invoke(app, ["init"])
        
        assert result.exit_code == 0
        assert "initialized successfully" in result.stdout
        assert Path(tmp_db_path).exists()
    finally:
        if Path(tmp_db_path).exists():
            Path(tmp_db_path).unlink()
