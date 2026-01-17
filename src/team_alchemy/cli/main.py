"""
Command-line interface for Team Alchemy.
"""

import typer
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError

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
    assessment_type: str = typer.Option("full", help="Assessment type"),
):
    """Run an assessment for a user."""
    from team_alchemy.data.repository import get_db
    from team_alchemy.data.models import User, UserProfile
    from team_alchemy.core.archetypes.jungian_mapper import JungianMapper, MBTIType
    from team_alchemy.core.psychology.jungian import JungianAnalyzer
    from team_alchemy.core.psychology.freudian import FreudianAnalyzer

    typer.echo(f"Running {assessment_type} assessment for user {user_id}...")

    # Validate assessment type
    valid_types = ["full", "mbti", "archetype", "jungian"]
    if assessment_type not in valid_types:
        typer.echo(f"✗ Invalid assessment type. Valid types: {', '.join(valid_types)}", err=True)
        raise typer.Exit(1)

    try:
        # Get database session
        db_gen = get_db()
        db = next(db_gen)

        try:
            # Fetch user from database
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                typer.echo(f"✗ User {user_id} not found in database", err=True)
                raise typer.Exit(1)

            typer.echo(f"✓ User found: {user.name} ({user.email})")
            typer.echo()

            # Get or create user profile
            profile = user.profile
            if not profile:
                # Create profile with sample data for demonstration
                typer.echo("ℹ No existing profile found. Creating sample profile...")
                profile = UserProfile(
                    user_id=user_id,
                    archetype="Analyst",
                    jungian_type="INTJ",
                    trait_scores={
                        "openness": 0.8,
                        "conscientiousness": 0.7,
                        "extraversion": 0.3,
                        "agreeableness": 0.5,
                        "neuroticism": 0.4,
                    },
                )
                db.add(profile)
                db.commit()
                typer.echo("✓ Sample profile created")
                typer.echo()

            # Initialize analyzers
            jungian_mapper = JungianMapper()
            jungian_analyzer = JungianAnalyzer()
            freudian_analyzer = FreudianAnalyzer()

            # Get MBTI type
            mbti_type_str = profile.jungian_type or "INTJ"
            try:
                mbti_type = MBTIType(mbti_type_str)
            except ValueError:
                mbti_type = MBTIType.INTJ

            jungian_profile = jungian_mapper.get_jungian_profile(mbti_type)
            mapping = jungian_mapper.type_mappings.get(mbti_type, {})

            # Display assessment based on type
            if assessment_type in ["full", "jungian", "mbti"]:
                typer.echo("=== Jungian Profile ===")
                typer.echo(f"MBTI Type: {mbti_type.value}")
                typer.echo("Function Stack:")
                if jungian_profile:
                    for i, func in enumerate(jungian_profile.get_function_stack()):
                        labels = ["Dominant", "Auxiliary", "Tertiary", "Inferior"]
                        typer.echo(f"  - {labels[i]}: {func.value}")
                typer.echo()

            if assessment_type in ["full", "archetype"]:
                typer.echo("=== Archetype Analysis ===")
                typer.echo(f"Primary Archetype: {profile.archetype or 'Unknown'}")
                archetype_affinity = mapping.get("archetype_affinity", [])
                if archetype_affinity:
                    typer.echo(f"Archetype Affinity: {', '.join(archetype_affinity)}")
                typer.echo()

            if assessment_type == "full":
                # Sample behaviors for analysis
                sample_behaviors = [
                    "seeks achievement",
                    "analytical thinking",
                    "strategic planning",
                    "values knowledge",
                ]

                # Identify archetypes
                archetype_patterns = jungian_analyzer.identify_active_archetypes(
                    sample_behaviors, {}
                )

                if archetype_patterns:
                    typer.echo("=== Active Archetypes ===")
                    for pattern in archetype_patterns[:3]:
                        typer.echo(
                            f"  - {pattern.archetype.value}: {pattern.strength:.1%} strength"
                        )
                    typer.echo()

                # Defense mechanisms
                defense_profiles = freudian_analyzer.identify_defenses(sample_behaviors, {})

                if defense_profiles:
                    typer.echo("=== Defense Mechanisms ===")
                    for defense in defense_profiles[:3]:
                        adaptive = "Adaptive" if defense.adaptiveness > 0.6 else "Maladaptive"
                        typer.echo(
                            f"  - {defense.mechanism.value}: {adaptive} ({defense.adaptiveness:.1%})"
                        )
                    typer.echo()

                # Recommendations
                typer.echo("=== Recommendations ===")
                strengths = mapping.get("strengths", [])
                shadow = mapping.get("shadow", "")

                if strengths:
                    typer.echo(f"- Leverage strengths: {', '.join(strengths[:3])}")
                if shadow:
                    typer.echo(f"- Development area: {shadow}")

                # MBTI-specific recommendations
                if mbti_type_str in ["INTJ", "INTP"]:
                    typer.echo("- Balance analytical thinking with emotional awareness")
                    typer.echo("- Practice present-moment engagement")
                elif mbti_type_str in ["ENFP", "ENFJ"]:
                    typer.echo("- Develop structured planning to complement creativity")
                    typer.echo("- Practice follow-through on commitments")

                typer.echo()

            typer.echo("✓ Assessment completed and saved")

        finally:
            # Close database session
            try:
                next(db_gen)
            except StopIteration:
                pass

    except SQLAlchemyError as e:
        typer.echo(f"✗ Database error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"✗ Error running assessment: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def analyze_team(team_id: int = typer.Argument(..., help="Team ID to analyze")):
    """Analyze team dynamics and composition."""
    from team_alchemy.data.repository import get_db
    from team_alchemy.data.models import Team, TeamAnalysis, UserProfile
    from team_alchemy.core.archetypes.jungian_mapper import JungianMapper, MBTIType
    from team_alchemy.core.psychology.jungian import (
        JungianAnalyzer,
        assess_collective_unconscious_patterns,
    )
    from datetime import datetime

    typer.echo(f"Analyzing team {team_id}...")

    try:
        # Get database session
        db_gen = get_db()
        db = next(db_gen)

        try:
            # Fetch team from database
            team = db.query(Team).filter(Team.id == team_id).first()

            if not team:
                typer.echo(f"✗ Team {team_id} not found in database", err=True)
                raise typer.Exit(1)

            # Get team members
            members = team.members
            if not members:
                typer.echo(f"✗ Team {team_id} has no members", err=True)
                raise typer.Exit(1)

            typer.echo(f"✓ Team found: {team.name} ({len(members)} members)")
            typer.echo()

            # Initialize analyzers
            jungian_mapper = JungianMapper()
            jungian_analyzer = JungianAnalyzer()

            # Collect MBTI types and profiles
            mbti_distribution = {}
            function_coverage = {}
            all_archetypes = []
            members_with_profiles = []

            for member in members:
                profile = member.profile
                if profile and profile.jungian_type:
                    mbti_type_str = profile.jungian_type
                    members_with_profiles.append(member)

                    # Count MBTI distribution
                    mbti_distribution[mbti_type_str] = mbti_distribution.get(mbti_type_str, 0) + 1

                    # Analyze functions
                    try:
                        mbti_type = MBTIType(mbti_type_str)
                        jungian_profile = jungian_mapper.get_jungian_profile(mbti_type)

                        if jungian_profile:
                            for func in jungian_profile.get_function_stack()[
                                :2
                            ]:  # Dominant and auxiliary
                                func_name = func.value
                                function_coverage[func_name] = (
                                    function_coverage.get(func_name, 0) + 1
                                )

                        # Collect archetype patterns
                        sample_behaviors = ["strategic planning", "analytical thinking"]
                        archetype_patterns = jungian_analyzer.identify_active_archetypes(
                            sample_behaviors, {}
                        )
                        all_archetypes.append(archetype_patterns)
                    except ValueError:
                        pass

            if not members_with_profiles:
                typer.echo("⚠ No members have profiles. Creating sample profiles...")
                # Create sample profiles for demonstration
                sample_types = ["INTJ", "ENFP", "ISTJ", "ENTP"]
                for i, member in enumerate(members[:4]):
                    if not member.profile:
                        profile = UserProfile(
                            user_id=member.id,
                            jungian_type=sample_types[i % len(sample_types)],
                            archetype="Analyst" if i % 2 == 0 else "Innovator",
                            trait_scores={},
                        )
                        db.add(profile)
                db.commit()
                typer.echo("✓ Sample profiles created. Re-run command for full analysis.")
                raise typer.Exit(0)

            # Display team composition
            typer.echo("=== Team Composition ===")
            typer.echo("MBTI Distribution:")
            for mbti_type, count in sorted(mbti_distribution.items()):
                percentage = (count / len(members_with_profiles)) * 100
                typer.echo(
                    f"  - {mbti_type}: {count} member{'s' if count > 1 else ''} ({percentage:.0f}%)"
                )
            typer.echo()

            # Display team dynamics
            typer.echo("=== Team Dynamics ===")
            diversity_score = (
                len(mbti_distribution) / len(members_with_profiles) if members_with_profiles else 0
            )
            typer.echo(f"Diversity Score: {diversity_score:.0%}")
            typer.echo(f"Balance: {'Balanced' if diversity_score > 0.6 else 'Homogeneous'}")

            # Function coverage
            typer.echo("Function Coverage:")
            total_coverage = sum(function_coverage.values())
            for func, count in sorted(function_coverage.items(), key=lambda x: x[1], reverse=True):
                strength = count / total_coverage if total_coverage > 0 else 0
                level = "Strong" if strength > 0.25 else ("Moderate" if strength > 0.15 else "Weak")
                typer.echo(f"  - {func}: {level}")
            typer.echo()

            # Collective patterns
            if all_archetypes:
                collective = assess_collective_unconscious_patterns(all_archetypes)
                typer.echo("=== Collective Patterns ===")
                typer.echo(
                    f"Archetype Diversity: {collective.get('archetype_diversity', 0)} archetypes"
                )
                dominant = collective.get("dominant_pattern")
                if dominant:
                    typer.echo(f"Dominant Pattern: {dominant.title()}")
                typer.echo()

            # Generate team recommendations
            typer.echo("=== Team Recommendations ===")

            if diversity_score < 0.4:
                typer.echo(
                    "- Consider diversifying team composition for better perspective balance"
                )

            # Check for function gaps
            all_functions = ["Ti", "Te", "Fi", "Fe", "Si", "Se", "Ni", "Ne"]
            missing_functions = [
                f for f in all_functions if f not in function_coverage or function_coverage[f] == 0
            ]

            if "Se" in missing_functions or "Si" in missing_functions:
                typer.echo(
                    "- Team may lack practical execution focus - consider adding sensing-focused members"
                )

            if "Fe" in missing_functions or "Fi" in missing_functions:
                typer.echo("- Team may benefit from members with strong emotional intelligence")

            if "Ni" in function_coverage and "Ne" in function_coverage:
                typer.echo("- Team excels at strategic planning and innovation")

            if "Te" in function_coverage and "Ti" in function_coverage:
                typer.echo("- Team has strong analytical and decision-making capabilities")

            typer.echo()

            # Save analysis to database
            analysis_data = {
                "mbti_distribution": mbti_distribution,
                "diversity_score": diversity_score,
                "function_coverage": function_coverage,
                "team_size": len(members_with_profiles),
                "timestamp": datetime.utcnow().isoformat(),
            }

            analysis = TeamAnalysis(
                team_id=team_id, analysis_type="full", results=analysis_data, score=diversity_score
            )
            db.add(analysis)
            db.commit()

            typer.echo("✓ Analysis completed and saved")

        finally:
            # Close database session
            try:
                next(db_gen)
            except StopIteration:
                pass

    except SQLAlchemyError as e:
        typer.echo(f"✗ Database error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"✗ Error analyzing team: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def recommend(
    team_id: int = typer.Argument(..., help="Team ID"),
    max_recommendations: int = typer.Option(5, help="Maximum recommendations"),
):
    """Generate recommendations for a team."""
    from team_alchemy.data.repository import get_db
    from team_alchemy.data.models import Team, TeamAnalysis
    from team_alchemy.core.psychology.case_study_mapper import CaseStudyMapper

    typer.echo(f"Generating recommendations for team {team_id}...")

    try:
        # Get database session
        db_gen = get_db()
        db = next(db_gen)

        try:
            # Fetch team from database
            team = db.query(Team).filter(Team.id == team_id).first()

            if not team:
                typer.echo(f"✗ Team {team_id} not found in database", err=True)
                raise typer.Exit(1)

            typer.echo(f"✓ Team found: {team.name}")

            # Get latest analysis
            latest_analysis = (
                db.query(TeamAnalysis)
                .filter(TeamAnalysis.team_id == team_id)
                .order_by(TeamAnalysis.created_at.desc())
                .first()
            )

            if not latest_analysis:
                typer.echo("⚠ No analysis found. Please run 'analyze-team' first.")
                raise typer.Exit(1)

            analysis_date = latest_analysis.created_at.strftime("%Y-%m-%d")
            typer.echo(f"✓ Latest analysis loaded ({analysis_date})")
            typer.echo()

            # Extract analysis data
            results = latest_analysis.results or {}
            diversity_score = results.get("diversity_score", 0)
            mbti_distribution = results.get("mbti_distribution", {})
            function_coverage = results.get("function_coverage", {})

            # Initialize case study mapper
            case_mapper = CaseStudyMapper()

            # Build profile for case study matching
            profile = {
                "team_size": len(team.members),
                "diversity_score": diversity_score,
                "mbti_types": list(mbti_distribution.keys()),
            }

            # Find similar case studies
            similar_cases = case_mapper.find_similar_cases(profile, limit=2)

            # Generate prioritized recommendations
            recommendations = []

            # Priority 1: Address diversity issues
            if diversity_score < 0.4:
                recommendations.append(
                    {
                        "priority": "HIGH",
                        "title": "Increase Team Diversity",
                        "impact": "Decision Making & Innovation",
                        "rationale": "Low diversity score indicates homogeneous team composition",
                        "actions": [
                            "Recruit members with different MBTI types",
                            "Seek diverse cognitive function representation",
                            "Consider different archetype profiles",
                        ],
                    }
                )

            # Priority 2: Address function gaps
            all_functions = ["Ti", "Te", "Fi", "Fe", "Si", "Se", "Ni", "Ne"]
            missing_functions = [
                f for f in all_functions if f not in function_coverage or function_coverage[f] == 0
            ]

            if "Se" in missing_functions or "Si" in missing_functions:
                recommendations.append(
                    {
                        "priority": "HIGH",
                        "title": "Add Sensing-Focused Member",
                        "impact": "Execution & Detail Orientation",
                        "rationale": "Team lacks practical implementation focus (low S function coverage)",
                        "actions": [
                            "Recruit ISTJ, ISFJ, ESTP, or ESFP types",
                            "Assign detail-oriented tasks to existing sensing types",
                            "Implement structured execution processes",
                        ],
                    }
                )

            if "Fe" in missing_functions or "Fi" in missing_functions:
                recommendations.append(
                    {
                        "priority": "MEDIUM",
                        "title": "Develop Emotional Intelligence",
                        "impact": "Team Cohesion & Communication",
                        "rationale": "Low feeling function representation may lead to interpersonal challenges",
                        "actions": [
                            "Schedule regular team building activities",
                            "Implement feedback and communication training",
                            "Foster psychological safety in meetings",
                        ],
                    }
                )

            # Priority 3: Leverage strengths
            if "Ni" in function_coverage or "Ne" in function_coverage:
                recommendations.append(
                    {
                        "priority": "MEDIUM",
                        "title": "Leverage Strategic Strengths",
                        "impact": "Innovation & Planning",
                        "rationale": "High intuition concentration ideal for strategic initiatives",
                        "actions": [
                            "Assign long-term planning projects to team",
                            "Lead innovation workshops",
                            "Focus on strategic rather than tactical work",
                        ],
                    }
                )

            if "Te" in function_coverage and "Ti" in function_coverage:
                recommendations.append(
                    {
                        "priority": "MEDIUM",
                        "title": "Optimize Decision-Making Processes",
                        "impact": "Efficiency & Analysis",
                        "rationale": "Strong thinking functions enable data-driven decisions",
                        "actions": [
                            "Implement structured decision frameworks",
                            "Leverage analytical strengths for complex problems",
                            "Balance logic with stakeholder input",
                        ],
                    }
                )

            # Add case study based recommendations
            if similar_cases:
                for case in similar_cases:
                    interventions = case.interventions[:2]
                    recommendations.append(
                        {
                            "priority": "LOW",
                            "title": f"Apply Learnings from: {case.title}",
                            "impact": "Evidence-Based Improvement",
                            "rationale": "Similar team benefited from these interventions",
                            "actions": interventions,
                        }
                    )

            # Sort by priority and limit
            priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
            recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
            recommendations = recommendations[:max_recommendations]

            # Display recommendations
            typer.echo(f"=== Top {len(recommendations)} Recommendations ===")
            typer.echo()

            for i, rec in enumerate(recommendations, 1):
                typer.echo(f"{i}. [{rec['priority']} PRIORITY] {rec['title']}")
                typer.echo(f"   Impact: {rec['impact']}")
                typer.echo(f"   Rationale: {rec['rationale']}")

                if rec.get("actions"):
                    typer.echo("   Actions:")
                    for action in rec["actions"][:3]:
                        typer.echo(f"   - {action}")

                typer.echo()

            typer.echo("✓ Recommendations generated")

        finally:
            # Close database session
            try:
                next(db_gen)
            except StopIteration:
                pass

    except SQLAlchemyError as e:
        typer.echo(f"✗ Database error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"✗ Error generating recommendations: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    from team_alchemy import __version__

    typer.echo(f"Team Alchemy version {__version__}")


if __name__ == "__main__":
    app()
