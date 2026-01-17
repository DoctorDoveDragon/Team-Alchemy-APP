"""
Command-line interface for Team Alchemy.
"""

import typer
from typing import Optional
import json
import logging
from enum import Enum
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError

# Initialize logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_MBTI_TYPE = "INTJ"
DEFAULT_ARCHETYPE = "Analyst"

JUNGIAN_FUNCTION_NAMES = {
    "Ti": "Introverted Thinking",
    "Te": "Extraverted Thinking",
    "Fi": "Introverted Feeling",
    "Fe": "Extraverted Feeling",
    "Si": "Introverted Sensing",
    "Se": "Extraverted Sensing",
    "Ni": "Introverted Intuition",
    "Ne": "Extraverted Intuition",
}

JUNGIAN_POSITIONS = ["Dominant", "Auxiliary", "Tertiary", "Inferior"]


class AssessmentType(str, Enum):
    """Assessment type options."""

    FULL = "full"
    MBTI = "mbti"
    ARCHETYPE = "archetype"
    JUNGIAN = "jungian"


@contextmanager
def get_db_session():
    """Context manager for database sessions with automatic cleanup."""
    from team_alchemy.data.repository import SessionLocal

    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        typer.echo(f"✗ Database error: {e}", err=True)
        raise typer.Exit(1)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_user_mbti_type(profile: Optional["UserProfile"], warn_if_default: bool = True) -> str:
    """Extract MBTI type from profile with fallback to default."""
    if profile and profile.jungian_type:
        return profile.jungian_type

    if profile and profile.trait_scores:
        if isinstance(profile.trait_scores, dict) and "mbti_type" in profile.trait_scores:
            return profile.trait_scores["mbti_type"]

    if warn_if_default:
        typer.echo("⚠  Warning: User has no MBTI assessment on file.")
        typer.echo(f"   Using {DEFAULT_MBTI_TYPE} as example for demonstration purposes.")
        typer.echo("   Results may not reflect actual personality type.\n")

    return DEFAULT_MBTI_TYPE


def display_user_info(user: "User") -> None:
    """Display formatted user information."""
    typer.echo("User Information:")
    typer.echo(f"  ID: {user.id}")
    typer.echo(f"  Name: {user.name}")
    typer.echo(f"  Email: {user.email}\n")


def display_jungian_profile(mbti_type: str, jungian_profile, mapping: dict) -> None:
    """Display formatted Jungian profile information."""
    typer.echo("Jungian Profile:")
    typer.echo(f"  MBTI Type: {mbti_type}")
    typer.echo("  Function Stack:")

    if jungian_profile:
        functions = jungian_profile.get_function_stack()
        for i, func in enumerate(functions):
            full_name = JUNGIAN_FUNCTION_NAMES.get(func.value, func.value)
            typer.echo(f"    • {JUNGIAN_POSITIONS[i]}: {full_name} ({func.value})")
    typer.echo()


def display_archetypes(archetype_patterns: list, mapping: dict) -> None:
    """Display formatted archetype information."""
    typer.echo("Dominant Archetypes:")
    if archetype_patterns:
        for pattern in archetype_patterns[:3]:
            dominant_text = " - Dominant" if pattern.is_dominant() else ""
            typer.echo(
                f"  • {pattern.archetype.value.replace('_', ' ').title()} "
                f"(strength: {pattern.strength:.2f}){dominant_text}"
            )
    else:
        if mapping.get("archetype_affinity"):
            for arch in mapping["archetype_affinity"][:2]:
                typer.echo(f"  • {arch.title()} (strength: 0.85)")
    typer.echo()


def display_defense_mechanisms(defense_profiles: list) -> None:
    """Display formatted defense mechanism information."""
    typer.echo("Defense Mechanisms:")
    if defense_profiles:
        for defense in defense_profiles[:3]:
            typer.echo(
                f"  • {defense.mechanism.value.replace('_', ' ').title()} "
                f"(frequency: {defense.frequency:.2f}, "
                f"adaptiveness: {defense.adaptiveness:.2f})"
            )
    else:
        typer.echo("  • No behavioral data available for defense mechanism analysis")
        typer.echo("    (Provide behavioral observations for detailed results)")
    typer.echo()


def display_recommendations(mbti_type: str, mapping: dict) -> None:
    """Display formatted recommendations."""
    typer.echo("Recommendations:")

    # MBTI-based recommendations
    if mbti_type in ["INTJ", "INTP"]:
        typer.echo("  • Consider balancing analytical thinking with emotional awareness")
    elif mbti_type in ["ENFP", "ENFJ"]:
        typer.echo("  • Practice structured planning to complement your creativity")
    elif mbti_type in ["ISTJ", "ESTJ"]:
        typer.echo("  • Embrace flexibility and openness to new approaches")
    elif mbti_type in ["INFJ", "INFP"]:
        typer.echo("  • Balance idealism with practical considerations")

    # Archetype-based recommendations
    if mapping.get("archetype_affinity"):
        primary_archetype = mapping["archetype_affinity"][0]
        typer.echo(
            f"  • Work on integrating {primary_archetype.title()} archetype more consciously"
        )

    # Shadow work recommendation
    if mapping.get("shadow"):
        typer.echo(f"  • Shadow work: {mapping['shadow']}")

    typer.echo()


app = typer.Typer(
    name="team-alchemy", help="Team Alchemy - Team dynamics and psychology assessment platform"
)


@app.command()
def init(db_url: Optional[str] = typer.Option(None, help="Database URL")):
    """Initialize the Team Alchemy database."""
    typer.echo("Initializing Team Alchemy database...")

    from team_alchemy.data.repository import init_db

    try:
        init_db()
        typer.echo("✓ Database initialized successfully!")
    except Exception as e:
        typer.echo(f"✗ Error initializing database: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def assess(
    user_id: int = typer.Argument(..., help="User ID to assess"),
    assessment_type: AssessmentType = typer.Option(AssessmentType.FULL, help="Assessment type"),
):
    """Run an assessment for a user."""
    from team_alchemy.data.repository import SessionLocal
    from team_alchemy.data.models import User, UserProfile
    from team_alchemy.core.archetypes.jungian_mapper import JungianMapper, MBTIType
    from team_alchemy.core.psychology.jungian import JungianAnalyzer
    from team_alchemy.core.psychology.freudian import FreudianAnalyzer

    logger.info(f"Starting {assessment_type.value} assessment for user {user_id}")
    typer.echo(f"\n✓ Running {assessment_type.value} assessment for User {user_id}...\n")

    with get_db_session() as db:
        # Query user from database
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            logger.warning(f"User {user_id} not found")
            typer.echo(f"✗ Error: User {user_id} not found", err=True)
            raise typer.Exit(1)

        logger.info(f"Found user: {user.name} ({user.email})")

        # Always display user information
        display_user_info(user)

        # Get or create user profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

        # Default behaviors if no profile data exists
        behaviors = []
        mbti_type_str = get_user_mbti_type(profile, warn_if_default=True)

        # Initialize analyzers
        jungian_mapper = JungianMapper()
        jungian_analyzer = JungianAnalyzer()
        freudian_analyzer = FreudianAnalyzer()

        # Get Jungian profile
        try:
            mbti_enum = MBTIType(mbti_type_str.upper())
        except ValueError:
            logger.error(f"Invalid MBTI type: {mbti_type_str}")
            typer.echo(f"✗ Error: Invalid MBTI type: {mbti_type_str}", err=True)
            raise typer.Exit(1)

        jungian_profile = jungian_mapper.get_jungian_profile(mbti_enum)
        mapping = jungian_mapper.type_mappings.get(mbti_enum, {})

        # Conditional display based on assessment type
        if assessment_type in [AssessmentType.FULL, AssessmentType.MBTI, AssessmentType.JUNGIAN]:
            display_jungian_profile(mbti_type_str, jungian_profile, mapping)

        if assessment_type in [AssessmentType.FULL, AssessmentType.ARCHETYPE]:
            # Identify archetypes
            archetype_patterns = jungian_analyzer.identify_active_archetypes(behaviors, {})
            display_archetypes(archetype_patterns, mapping)

        if assessment_type == AssessmentType.FULL:
            # Identify defense mechanisms
            defense_profiles = freudian_analyzer.identify_defenses(behaviors, {})
            display_defense_mechanisms(defense_profiles)

            # Generate recommendations
            display_recommendations(mbti_type_str, mapping)

        # Save/update profile in database
        if not profile:
            profile = UserProfile(
                user_id=user_id,
                jungian_type=mbti_type_str,
                archetype=(
                    mapping.get("archetype_affinity", [""])[0]
                    if mapping.get("archetype_affinity")
                    else ""
                ),
                trait_scores={
                    "mbti_type": mbti_type_str,
                    "strengths": mapping.get("strengths", []),
                    "shadow": mapping.get("shadow", ""),
                },
            )
            db.add(profile)
            logger.info(f"Created new profile for user {user_id}")
        else:
            profile.jungian_type = mbti_type_str
            if not profile.trait_scores:
                profile.trait_scores = {}
            profile.trait_scores["mbti_type"] = mbti_type_str
            profile.trait_scores["strengths"] = mapping.get("strengths", [])
            logger.info(f"Updated profile for user {user_id}")

        typer.echo("✓ Assessment completed and saved to database\n")
        logger.info(f"Assessment completed successfully for user {user_id}")


@app.command()
def analyze_team(team_id: int = typer.Argument(..., help="Team ID to analyze")):
    """Analyze team dynamics and composition."""
    from team_alchemy.data.repository import SessionLocal
    from team_alchemy.data.models import Team, User, UserProfile, TeamAnalysis
    from team_alchemy.core.archetypes.jungian_mapper import JungianMapper, MBTIType
    from team_alchemy.core.psychology.jungian import (
        JungianAnalyzer,
        assess_collective_unconscious_patterns,
    )
    from team_alchemy.core.psychology.freudian import FreudianAnalyzer

    logger.info(f"Starting team analysis for team {team_id}")
    typer.echo(f"\n✓ Analyzing Team {team_id}...\n")

    with get_db_session() as db:
        # Query team from database
        team = db.query(Team).filter(Team.id == team_id).first()

        if not team:
            logger.warning(f"Team {team_id} not found")
            typer.echo(f"✗ Error: Team {team_id} not found", err=True)
            raise typer.Exit(1)

        if not team.members:
            logger.warning(f"Team {team_id} has no members")
            typer.echo(f"✗ Error: Team {team_id} has no members", err=True)
            raise typer.Exit(1)

        logger.info(f"Found team: {team.name} with {len(team.members)} members")

        # Display team information
        typer.echo("Team Information:")
        typer.echo(f"  Name: {team.name}")
        typer.echo(f"  Size: {len(team.members)} members")
        if team.description:
            typer.echo(f"  Description: {team.description}")
        typer.echo()

        # Initialize analyzers
        jungian_mapper = JungianMapper()
        jungian_analyzer = JungianAnalyzer()

        # Collect member data
        member_data = []
        all_archetypes = []
        mbti_distribution = {}

        typer.echo("Members:")
        for member in team.members:
            # Get member profile
            profile = db.query(UserProfile).filter(UserProfile.user_id == member.id).first()

            # Determine MBTI type
            mbti_type_str = get_user_mbti_type(profile, warn_if_default=False)

            # Get archetype
            archetype_name = DEFAULT_ARCHETYPE
            if profile and profile.archetype:
                archetype_name = profile.archetype
            else:
                # Get from mapping
                try:
                    mbti_enum = MBTIType(mbti_type_str.upper())
                    mapping = jungian_mapper.type_mappings.get(mbti_enum, {})
                    if mapping.get("archetype_affinity"):
                        archetype_name = mapping["archetype_affinity"][0]
                except ValueError:
                    pass

            # Display member
            typer.echo(f"  • {member.name} ({mbti_type_str}) - {archetype_name.title()}")

            # Track distribution
            mbti_distribution[mbti_type_str] = mbti_distribution.get(mbti_type_str, 0) + 1

            # Analyze archetypes
            archetype_patterns = jungian_analyzer.identify_active_archetypes([], {})
            all_archetypes.append(archetype_patterns)

            member_data.append(
                {
                    "user_id": member.id,
                    "name": member.name,
                    "mbti_type": mbti_type_str,
                    "archetype": archetype_name,
                }
            )

        typer.echo()

        # Analyze team dynamics
        typer.echo("Team Dynamics:")

        # MBTI Distribution
        typer.echo("  MBTI Distribution:")
        for mbti_type, count in sorted(mbti_distribution.items()):
            typer.echo(f"    {mbti_type}: {count}")

        # Calculate diversity score
        diversity_score = len(mbti_distribution) / len(team.members) if team.members else 0
        typer.echo(f"  Diversity Score: {diversity_score * 100:.1f}%")

        # Balance assessment
        if diversity_score > 0.8:
            balance = "Highly Balanced"
        elif diversity_score > 0.6:
            balance = "Balanced"
        elif diversity_score > 0.4:
            balance = "Moderately Balanced"
        else:
            balance = "Homogeneous"
        typer.echo(f"  Balance: {balance}")
        typer.echo()

        # Collective patterns
        if all_archetypes:
            collective = assess_collective_unconscious_patterns(all_archetypes)

            typer.echo("Collective Patterns:")
            typer.echo(
                f"  • Archetype Diversity: {collective.get('archetype_diversity', 0)} unique archetypes"
            )

            if collective.get("dominant_pattern"):
                typer.echo(
                    f"  • Dominant Pattern: {collective['dominant_pattern'].replace('_', ' ').title()}"
                )

            # General patterns based on composition
            typer.echo("  • Strong analytical capability")

            # Check for intuition vs sensing balance
            intuitive_count = sum(1 for m in member_data if m["mbti_type"][1] == "N")
            sensing_count = len(member_data) - intuitive_count
            if abs(intuitive_count - sensing_count) <= 1:
                typer.echo("  • Good balance of intuition and sensing")

            # Check for thinking vs feeling balance
            thinking_count = sum(1 for m in member_data if m["mbti_type"][2] == "T")
            feeling_count = len(member_data) - thinking_count
            if abs(thinking_count - feeling_count) <= 1:
                typer.echo("  • Diverse thinking and feeling representation")

            typer.echo()

        # Save analysis to database
        analysis_results = {
            "mbti_distribution": mbti_distribution,
            "diversity_score": diversity_score,
            "balance": balance,
            "member_count": len(team.members),
            "members": member_data,
        }

        team_analysis = TeamAnalysis(
            team_id=team_id,
            analysis_type="comprehensive",
            results=analysis_results,
            score=diversity_score * 100,
        )
        db.add(team_analysis)

        logger.info(f"Team analysis completed for team {team_id}")
        typer.echo("✓ Analysis completed and saved to database\n")


@app.command()
def recommend(
    team_id: int = typer.Argument(..., help="Team ID"),
    max_recommendations: int = typer.Option(5, help="Maximum recommendations"),
):
    """Generate recommendations for a team."""
    from team_alchemy.data.repository import SessionLocal
    from team_alchemy.data.models import Team, User, UserProfile, TeamAnalysis
    from team_alchemy.core.archetypes.jungian_mapper import JungianMapper, MBTIType

    logger.info(f"Generating recommendations for team {team_id}")
    typer.echo(f"\n✓ Generating recommendations for Team {team_id}...\n")

    with get_db_session() as db:
        # Query team from database
        team = db.query(Team).filter(Team.id == team_id).first()

        if not team:
            logger.warning(f"Team {team_id} not found")
            typer.echo(f"✗ Error: Team {team_id} not found", err=True)
            raise typer.Exit(1)

        if not team.members:
            logger.warning(f"Team {team_id} has no members")
            typer.echo(f"✗ Error: Team {team_id} has no members", err=True)
            raise typer.Exit(1)

        logger.info(f"Found team: {team.name} with {len(team.members)} members")

        # Get or create team analysis
        latest_analysis = (
            db.query(TeamAnalysis)
            .filter(TeamAnalysis.team_id == team_id)
            .order_by(TeamAnalysis.created_at.desc())
            .first()
        )

        # Collect member data for analysis
        jungian_mapper = JungianMapper()
        member_data = []
        mbti_distribution = {}

        for member in team.members:
            profile = db.query(UserProfile).filter(UserProfile.user_id == member.id).first()

            mbti_type_str = get_user_mbti_type(profile, warn_if_default=False)

            mbti_distribution[mbti_type_str] = mbti_distribution.get(mbti_type_str, 0) + 1
            member_data.append(
                {
                    "user_id": member.id,
                    "name": member.name,
                    "mbti_type": mbti_type_str,
                }
            )

        # Calculate diversity
        diversity_score = len(mbti_distribution) / len(team.members) if team.members else 0

        # Generate recommendations
        typer.echo("Team Recommendations:\n")

        recommendations = []
        rec_count = 0

        # Diversity-based recommendations
        if diversity_score > 0.8:
            rec_count += 1
            rec = (
                f"{rec_count}. Leverage Diversity\n"
                f"   Your team has excellent MBTI diversity ({diversity_score*100:.1f}%). Ensure all perspectives\n"
                f"   are heard in decision-making processes."
            )
            recommendations.append(rec)
            typer.echo(rec + "\n")
        elif diversity_score < 0.4:
            rec_count += 1
            rec = (
                f"{rec_count}. Increase Diversity\n"
                f"   Your team has low MBTI diversity ({diversity_score*100:.1f}%). Consider adding members\n"
                f"   with different personality types for better perspective balance."
            )
            recommendations.append(rec)
            typer.echo(rec + "\n")

        if rec_count >= max_recommendations:
            logger.info(f"Generated {rec_count} recommendations for team {team_id}")
            typer.echo(f"\n✓ {rec_count} recommendations generated\n")
            return

        # Check for thinking vs feeling balance
        thinking_count = sum(1 for m in member_data if m["mbti_type"][2] == "T")
        feeling_count = len(member_data) - thinking_count

        if abs(thinking_count - feeling_count) <= 1 and rec_count < max_recommendations:
            rec_count += 1
            rec = (
                f"{rec_count}. Balance Logic and Empathy\n"
                f"   Your team has a good balance of Thinkers ({thinking_count}) and Feelers ({feeling_count}).\n"
                f"   Leverage both analytical and empathetic perspectives in problem-solving."
            )
            recommendations.append(rec)
            typer.echo(rec + "\n")
        elif thinking_count > feeling_count + 2 and rec_count < max_recommendations:
            rec_count += 1
            rec = (
                f"{rec_count}. Consider Emotional Perspectives\n"
                f"   Your team is heavily weighted toward Thinking types ({thinking_count} vs {feeling_count}).\n"
                f"   Make deliberate effort to consider emotional and interpersonal impacts."
            )
            recommendations.append(rec)
            typer.echo(rec + "\n")

        if rec_count >= max_recommendations:
            logger.info(f"Generated {rec_count} recommendations for team {team_id}")
            typer.echo(f"\n✓ {rec_count} recommendations generated\n")
            return

        # Check for intuition vs sensing balance
        intuitive_count = sum(1 for m in member_data if m["mbti_type"][1] == "N")
        sensing_count = len(member_data) - intuitive_count

        if intuitive_count > sensing_count + 2 and rec_count < max_recommendations:
            rec_count += 1
            rec = (
                f"{rec_count}. Ground Ideas in Reality\n"
                f"   Your team has more Intuitive types ({intuitive_count} vs {sensing_count}).\n"
                f"   Ensure innovative ideas are balanced with practical implementation considerations."
            )
            recommendations.append(rec)
            typer.echo(rec + "\n")
        elif sensing_count > intuitive_count + 2 and rec_count < max_recommendations:
            rec_count += 1
            rec = (
                f"{rec_count}. Encourage Innovation\n"
                f"   Your team has more Sensing types ({sensing_count} vs {intuitive_count}).\n"
                f"   Create space for brainstorming and exploring future possibilities."
            )
            recommendations.append(rec)
            typer.echo(rec + "\n")

        if rec_count >= max_recommendations:
            logger.info(f"Generated {rec_count} recommendations for team {team_id}")
            typer.echo(f"\n✓ {rec_count} recommendations generated\n")
            return

        # Specific type-based recommendations
        type_counts = sorted(mbti_distribution.items(), key=lambda x: x[1], reverse=True)

        if type_counts[0][1] > 1 and rec_count < max_recommendations:
            dominant_type = type_counts[0][0]
            rec_count += 1
            rec = (
                f"{rec_count}. Manage Type Clustering\n"
                f"   You have multiple {dominant_type} types on the team. Ensure they don't dominate\n"
                f"   discussions and actively seek input from other personality types."
            )
            recommendations.append(rec)
            typer.echo(rec + "\n")

        if rec_count >= max_recommendations:
            logger.info(f"Generated {rec_count} recommendations for team {team_id}")
            typer.echo(f"\n✓ {rec_count} recommendations generated\n")
            return

        # General teamwork recommendation
        if rec_count < max_recommendations:
            rec_count += 1
            rec = (
                f"{rec_count}. Foster Psychological Safety\n"
                f"   Create an environment where all personality types feel comfortable\n"
                f"   contributing their unique perspectives without judgment."
            )
            recommendations.append(rec)
            typer.echo(rec + "\n")

        logger.info(f"Generated {rec_count} recommendations for team {team_id}")
        typer.echo(f"✓ {rec_count} recommendations generated\n")


@app.command()
def version():
    """Show version information."""
    from team_alchemy import __version__

    typer.echo(f"Team Alchemy version {__version__}")


if __name__ == "__main__":
    app()
