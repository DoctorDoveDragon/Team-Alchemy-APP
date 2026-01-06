"""
Command-line interface for Team Alchemy.
"""

import typer
from typing import Optional

app = typer.Typer(
    name="team-alchemy",
    help="Team Alchemy - Team dynamics and psychology assessment platform"
)


@app.command()
def init(
    db_url: Optional[str] = typer.Option(None, help="Database URL")
):
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
    assessment_type: str = typer.Option("full", help="Assessment type")
):
    """Run an assessment for a user."""
    typer.echo(f"Running {assessment_type} assessment for user {user_id}...")
    typer.echo("Not implemented yet")


@app.command()
def analyze_team(
    team_id: int = typer.Argument(..., help="Team ID to analyze")
):
    """Analyze team dynamics and composition."""
    typer.echo(f"Analyzing team {team_id}...")
    typer.echo("Not implemented yet")


@app.command()
def recommend(
    team_id: int = typer.Argument(..., help="Team ID"),
    max_recommendations: int = typer.Option(5, help="Maximum recommendations")
):
    """Generate recommendations for a team."""
    typer.echo(f"Generating up to {max_recommendations} recommendations for team {team_id}...")
    typer.echo("Not implemented yet")


@app.command()
def version():
    """Show version information."""
    from team_alchemy import __version__
    typer.echo(f"Team Alchemy version {__version__}")


if __name__ == "__main__":
    app()
