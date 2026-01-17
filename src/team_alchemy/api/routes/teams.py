"""
FastAPI routes for team management.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List
from sqlalchemy.orm import Session

from team_alchemy.data.repository import get_db
from team_alchemy.data.models import Team, User
from team_alchemy.api.schemas.teams import TeamCreate, TeamResponse, TeamMemberResponse

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamResponse, status_code=201)
async def create_team(team: TeamCreate = Body(...), db: Session = Depends(get_db)):
    """Create a new team."""
    # Create new team instance
    db_team = Team(name=team.name, description=team.description)

    # Add to database
    db.add(db_team)
    db.commit()
    db.refresh(db_team)

    return db_team


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    """Get team by ID."""
    # Query team from database
    team = db.query(Team).filter(Team.id == team_id).first()

    # Return 404 if team not found
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team with id {team_id} not found")

    return team


@router.post("/{team_id}/members/{user_id}", response_model=TeamMemberResponse)
async def add_team_member(team_id: int, user_id: int, db: Session = Depends(get_db)):
    """Add member to team."""
    # Validate team exists
    team = db.query(Team).filter(Team.id == team_id).first()
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team with id {team_id} not found")

    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    # Check if user is already a member
    if user in team.members:
        raise HTTPException(
            status_code=400,
            detail=f"User {user_id} is already a member of team {team_id}"
        )

    # Add user to team
    team.members.append(user)
    db.commit()

    return TeamMemberResponse(
        message="User added to team successfully",
        team_id=team_id,
        user_id=user_id
    )


@router.get("/", response_model=List[TeamResponse])
async def list_teams(db: Session = Depends(get_db)):
    """List all teams."""
    teams = db.query(Team).all()
    return teams
