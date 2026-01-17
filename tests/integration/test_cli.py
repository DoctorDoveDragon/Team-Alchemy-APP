"""
Integration tests for CLI commands.
"""

import pytest
import os
from typer.testing import CliRunner
from team_alchemy.cli.main import app
from team_alchemy.data.repository import get_db, init_db
from team_alchemy.data.models import User, Team, UserProfile, TeamAnalysis


runner = CliRunner()


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Set up database URL in environment
    original_db_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    
    # Re-import to pick up new DATABASE_URL
    import importlib
    import team_alchemy.data.repository as repo_module
    importlib.reload(repo_module)
    
    # Initialize database
    repo_module.init_db()
    
    yield repo_module
    
    # Cleanup
    if original_db_url:
        os.environ["DATABASE_URL"] = original_db_url
    elif "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]


@pytest.fixture
def sample_data(temp_db):
    """Create sample data for testing."""
    db_gen = temp_db.get_db()
    db = next(db_gen)
    
    try:
        # Create users
        users = []
        for i in range(1, 6):
            user = User(
                id=i,
                name=f"Test User {i}",
                email=f"user{i}@test.com"
            )
            db.add(user)
            users.append(user)
        
        # Create team
        team = Team(
            id=1,
            name="Test Team",
            description="A test team"
        )
        db.add(team)
        
        # Add members to team
        for user in users:
            team.members.append(user)
        
        # Create profiles
        profiles_data = [
            (1, "INTJ", "Analyst"),
            (2, "ENFP", "Innovator"),
            (3, "ISTJ", "Guardian"),
            (4, "ENTP", "Challenger"),
        ]
        
        for user_id, mbti, archetype in profiles_data:
            profile = UserProfile(
                user_id=user_id,
                jungian_type=mbti,
                archetype=archetype,
                trait_scores={}
            )
            db.add(profile)
        
        db.commit()
        
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass


def test_init_command():
    """Test database initialization command."""
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "✓ Database initialized successfully!" in result.stdout


def test_assess_command_user_found(temp_db, sample_data):
    """Test assess command with existing user."""
    result = runner.invoke(app, ["assess", "1"])
    assert result.exit_code == 0
    assert "✓ User found:" in result.stdout
    assert "=== Jungian Profile ===" in result.stdout
    assert "MBTI Type: INTJ" in result.stdout
    assert "✓ Assessment completed and saved" in result.stdout


def test_assess_command_mbti_type(temp_db, sample_data):
    """Test assess command with MBTI type filter."""
    result = runner.invoke(app, ["assess", "2", "--assessment-type=mbti"])
    assert result.exit_code == 0
    assert "✓ User found:" in result.stdout
    assert "=== Jungian Profile ===" in result.stdout
    assert "MBTI Type: ENFP" in result.stdout


def test_assess_command_archetype_type(temp_db, sample_data):
    """Test assess command with archetype type filter."""
    result = runner.invoke(app, ["assess", "3", "--assessment-type=archetype"])
    assert result.exit_code == 0
    assert "✓ User found:" in result.stdout
    assert "=== Archetype Analysis ===" in result.stdout
    assert "Primary Archetype: Guardian" in result.stdout


def test_assess_command_user_not_found(temp_db, sample_data):
    """Test assess command with non-existent user."""
    result = runner.invoke(app, ["assess", "999"])
    assert result.exit_code == 1
    assert "✗ User 999 not found in database" in result.stdout


def test_assess_command_invalid_type(temp_db, sample_data):
    """Test assess command with invalid assessment type."""
    result = runner.invoke(app, ["assess", "1", "--assessment-type=invalid"])
    assert result.exit_code == 1
    assert "✗ Invalid assessment type" in result.stdout


def test_assess_command_creates_profile(temp_db, sample_data):
    """Test assess command creates profile for user without one."""
    result = runner.invoke(app, ["assess", "5"])
    assert result.exit_code == 0
    assert "ℹ No existing profile found. Creating sample profile..." in result.stdout
    assert "✓ Sample profile created" in result.stdout


def test_analyze_team_command_found(temp_db, sample_data):
    """Test analyze_team command with existing team."""
    result = runner.invoke(app, ["analyze-team", "1"])
    assert result.exit_code == 0
    assert "✓ Team found:" in result.stdout
    assert "=== Team Composition ===" in result.stdout
    assert "MBTI Distribution:" in result.stdout
    assert "=== Team Dynamics ===" in result.stdout
    assert "Diversity Score:" in result.stdout
    assert "✓ Analysis completed and saved" in result.stdout


def test_analyze_team_command_not_found(temp_db, sample_data):
    """Test analyze_team command with non-existent team."""
    result = runner.invoke(app, ["analyze-team", "999"])
    assert result.exit_code == 1
    assert "✗ Team 999 not found in database" in result.stdout


def test_recommend_command_with_analysis(temp_db, sample_data):
    """Test recommend command with existing analysis."""
    # First run analysis
    runner.invoke(app, ["analyze-team", "1"])
    
    # Then get recommendations
    result = runner.invoke(app, ["recommend", "1"])
    assert result.exit_code == 0
    assert "✓ Team found:" in result.stdout
    assert "✓ Latest analysis loaded" in result.stdout
    assert "=== Top" in result.stdout
    assert "Recommendations ===" in result.stdout
    assert "✓ Recommendations generated" in result.stdout


def test_recommend_command_without_analysis(temp_db, sample_data):
    """Test recommend command without existing analysis."""
    result = runner.invoke(app, ["recommend", "1"])
    assert result.exit_code == 1
    assert "⚠ No analysis found. Please run 'analyze-team' first." in result.stdout


def test_recommend_command_team_not_found(temp_db, sample_data):
    """Test recommend command with non-existent team."""
    result = runner.invoke(app, ["recommend", "999"])
    assert result.exit_code == 1
    assert "✗ Team 999 not found in database" in result.stdout


def test_recommend_command_max_recommendations(temp_db, sample_data):
    """Test recommend command with custom max recommendations."""
    # First run analysis
    runner.invoke(app, ["analyze-team", "1"])
    
    # Then get limited recommendations
    result = runner.invoke(app, ["recommend", "1", "--max-recommendations=3"])
    assert result.exit_code == 0
    assert "=== Top 3 Recommendations ===" in result.stdout or "=== Top" in result.stdout


def test_version_command():
    """Test version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Team Alchemy version" in result.stdout
