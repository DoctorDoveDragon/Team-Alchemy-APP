"""
Unit tests for CLI commands.
"""

import os
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from team_alchemy.cli.main import app
from team_alchemy.data.models import Base, Team, User, UserProfile


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create temporary database file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db_path = tmp.name

    # Set up database URL in environment
    original_db_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_db_path}"

    # Import repository module after setting environment variable
    from team_alchemy.data import repository

    # Initialize database
    repository.init_db()

    # Create session for setup
    SessionLocal = repository.SessionLocal
    db = SessionLocal()

    # Use unique timestamp-based emails to avoid conflicts
    import time

    ts = str(time.time()).replace(".", "")

    # Add test data
    user1 = User(email=f"test1_{ts}@example.com", name="Test User 1")
    user2 = User(email=f"test2_{ts}@example.com", name="Test User 2")
    user3 = User(email=f"test3_{ts}@example.com", name="Test User 3")

    db.add(user1)
    db.add(user2)
    db.add(user3)
    db.commit()

    # Add profile for user1
    profile1 = UserProfile(
        user_id=user1.id,
        jungian_type="INTJ",
        archetype="Analyst",
        trait_scores={"mbti_type": "INTJ"},
    )
    db.add(profile1)

    # Add profile for user2
    profile2 = UserProfile(
        user_id=user2.id,
        jungian_type="ENFP",
        archetype="Innovator",
        trait_scores={"mbti_type": "ENFP"},
    )
    db.add(profile2)

    db.commit()

    # Create test team
    team = Team(name="Test Team", description="A test team")
    team.members.extend([user1, user2, user3])
    db.add(team)
    db.commit()

    # Get IDs for test assertions
    test_user_id = user1.id
    test_team_id = team.id

    db.close()

    yield (tmp_db_path, test_user_id, test_team_id)

    # Cleanup
    if original_db_url:
        os.environ["DATABASE_URL"] = original_db_url
    elif "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]

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
    tmp_db_path, test_user_id, test_team_id = temp_db
    runner = CliRunner()
    result = runner.invoke(app, ["assess", str(test_user_id)])

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
    tmp_db_path, test_user_id, test_team_id = temp_db
    # User 3 has no profile, but we need to find its actual ID
    # Since it's the 3rd user created, let's use test_user_id + 2
    user_without_profile_id = test_user_id + 2

    runner = CliRunner()
    result = runner.invoke(app, ["assess", str(user_without_profile_id)])

    assert result.exit_code == 0
    assert "Test User 3" in result.stdout
    assert "Assessment completed" in result.stdout


def test_cli_analyze_team_found(temp_db):
    """Test analyze_team command with existing team."""
    tmp_db_path, test_user_id, test_team_id = temp_db
    runner = CliRunner()
    result = runner.invoke(app, ["analyze-team", str(test_team_id)])

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
    tmp_db_path, test_user_id, test_team_id = temp_db
    runner = CliRunner()
    result = runner.invoke(app, ["recommend", str(test_team_id)])

    assert result.exit_code == 0
    assert "Generating recommendations" in result.stdout
    assert "Team Recommendations" in result.stdout
    assert "recommendations generated" in result.stdout


def test_cli_recommend_with_max_limit(temp_db):
    """Test recommend command with max recommendations limit."""
    tmp_db_path, test_user_id, test_team_id = temp_db
    runner = CliRunner()
    result = runner.invoke(app, ["recommend", str(test_team_id), "--max-recommendations", "3"])

    assert result.exit_code == 0
    assert (
        "3 recommendations generated" in result.stdout
        or "recommendations generated" in result.stdout
    )


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


def test_cli_assess_mbti_only(temp_db):
    """Test assess command with --assessment-type mbti."""
    tmp_db_path, test_user_id, test_team_id = temp_db
    runner = CliRunner()
    result = runner.invoke(app, ["assess", str(test_user_id), "--assessment-type", "mbti"])

    assert result.exit_code == 0
    assert "Running mbti assessment" in result.stdout
    assert "Jungian Profile" in result.stdout
    assert "INTJ" in result.stdout
    # Should NOT show recommendations when only mbti is requested
    assert "Recommendations:" not in result.stdout


def test_cli_assess_archetype_only(temp_db):
    """Test assess command with --assessment-type archetype."""
    tmp_db_path, test_user_id, test_team_id = temp_db
    runner = CliRunner()
    result = runner.invoke(app, ["assess", str(test_user_id), "--assessment-type", "archetype"])

    assert result.exit_code == 0
    assert "Running archetype assessment" in result.stdout
    assert "Dominant Archetypes:" in result.stdout
    # Should NOT show Jungian Profile when only archetype is requested
    assert "Function Stack:" not in result.stdout
    # Should NOT show recommendations when only archetype is requested
    assert "Recommendations:" not in result.stdout


def test_cli_assess_defense_only(temp_db):
    """Test assess command with --assessment-type defense."""
    tmp_db_path, test_user_id, test_team_id = temp_db
    runner = CliRunner()
    result = runner.invoke(app, ["assess", str(test_user_id), "--assessment-type", "defense"])

    assert result.exit_code == 0
    assert "Running defense assessment" in result.stdout
    assert "Defense Mechanisms:" in result.stdout
    # Should show warning about no behavioral data
    assert "No behavioral data available" in result.stdout
    # Should NOT show Jungian Profile when only defense is requested
    assert "Function Stack:" not in result.stdout
    # Should NOT show recommendations when only defense is requested
    assert "Recommendations:" not in result.stdout


def test_cli_assess_full_type(temp_db):
    """Test assess command with --assessment-type full (explicit)."""
    tmp_db_path, test_user_id, test_team_id = temp_db
    runner = CliRunner()
    result = runner.invoke(app, ["assess", str(test_user_id), "--assessment-type", "full"])

    assert result.exit_code == 0
    assert "Running full assessment" in result.stdout
    assert "Jungian Profile" in result.stdout
    assert "Dominant Archetypes:" in result.stdout
    assert "Defense Mechanisms:" in result.stdout
    assert "Recommendations:" in result.stdout


def test_cli_assess_invalid_type(temp_db):
    """Test assess command with invalid assessment type."""
    tmp_db_path, test_user_id, test_team_id = temp_db
    runner = CliRunner()
    result = runner.invoke(app, ["assess", str(test_user_id), "--assessment-type", "invalid"])

    assert result.exit_code == 1
    assert "Invalid assessment type" in result.stdout
    assert "full, mbti, archetype, defense" in result.stdout


def test_cli_assess_default_warning(temp_db):
    """Test that warning is shown when using default MBTI type."""
    tmp_db_path, test_user_id, test_team_id = temp_db
    # User 3 has no profile, so it should use default and show warning
    user_without_profile_id = test_user_id + 2

    runner = CliRunner()
    result = runner.invoke(app, ["assess", str(user_without_profile_id)])

    assert result.exit_code == 0
    assert "Warning: User has no MBTI profile" in result.stdout
    assert "Using INTJ as example" in result.stdout
    assert "Run an actual assessment to get accurate results" in result.stdout
