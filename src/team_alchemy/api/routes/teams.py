"""
FastAPI routes for team management.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from team_alchemy.data.repository import get_db
from team_alchemy.data.models import Team, User
from team_alchemy.api.schemas.teams import (
    TeamCreate,
    TeamResponse,
    TeamListResponse,
)

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamResponse, status_code=201)
async def create_team(team_data: TeamCreate, db: Session = Depends(get_db)):
    """Create a new team."""
    # Check if team with same name already exists
    existing_team = db.query(Team).filter(Team.name == team_data.name).first()
    if existing_team:
        raise HTTPException(status_code=400, detail="Team with this name already exists")
    
    # Create new team
    new_team = Team(
        name=team_data.name,
        description=team_data.description
    )
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    
    return new_team


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    """Get team by ID."""
    team = db.query(Team).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return team


@router.post("/{team_id}/members/{user_id}", response_model=TeamResponse)
async def add_team_member(team_id: int, user_id: int, db: Session = Depends(get_db)):
    """Add member to team."""
    # Check if team exists
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is already a member
    if user in team.members:
        raise HTTPException(status_code=400, detail="User is already a member of this team")
    
    # Add user to team
    team.members.append(user)
    db.commit()
    db.refresh(team)
    
    return team


@router.get("/", response_model=TeamListResponse)
async def list_teams(db: Session = Depends(get_db)):
    """List all teams."""
    teams = db.query(Team).all()
    
    return TeamListResponse(
        teams=teams,
        total=len(teams)
    )
