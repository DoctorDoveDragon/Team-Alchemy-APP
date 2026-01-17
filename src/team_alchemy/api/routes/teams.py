"""
FastAPI routes for team management.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from team_alchemy.data.repository import get_db
from team_alchemy.data.models import Team, User
from team_alchemy.api.schemas.teams import (
    TeamCreate,
    TeamResponse,
    TeamListResponse,
    TeamMemberAddResponse,
)

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    """
    Create a new team.
    
    Args:
        team: Team creation data (name and optional description)
        db: Database session
        
    Returns:
        Created team with ID and timestamps
        
    Raises:
        HTTPException 400: If team name is invalid or already exists
    """
    # Check if team with same name already exists
    existing_team = db.query(Team).filter(Team.name == team.name).first()
    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team with name '{team.name}' already exists"
        )
    
    # Create new team
    db_team = Team(
        name=team.name,
        description=team.description
    )
    
    try:
        db.add(db_team)
        db.commit()
        db.refresh(db_team)
        return db_team
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create team due to database constraint"
        )


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    """
    Get team by ID.
    
    Args:
        team_id: ID of the team to retrieve
        db: Database session
        
    Returns:
        Team with members
        
    Raises:
        HTTPException 404: If team not found
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found"
        )
    
    return team


@router.post("/{team_id}/members/{user_id}", response_model=TeamMemberAddResponse)
async def add_team_member(team_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Add a member to a team.
    
    Args:
        team_id: ID of the team
        user_id: ID of the user to add
        db: Database session
        
    Returns:
        Success message and updated team
        
    Raises:
        HTTPException 404: If team or user not found
        HTTPException 400: If user is already a member
    """
    # Check if team exists
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found"
        )
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Check if user is already a member
    if user in team.members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_id} is already a member of team {team_id}"
        )
    
    # Add user to team
    team.members.append(user)
    
    try:
        db.commit()
        db.refresh(team)
        return {
            "message": "Member added successfully",
            "team": team
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add member due to database constraint"
        )


@router.get("/", response_model=TeamListResponse)
async def list_teams(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all teams with pagination.
    
    Args:
        skip: Number of teams to skip (for pagination)
        limit: Maximum number of teams to return (default 100, max 100)
        db: Database session
        
    Returns:
        List of teams with pagination metadata
    """
    # Validate pagination parameters
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip parameter must be non-negative"
        )
    
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit parameter must be between 1 and 100"
        )
    
    # Get total count
    total = db.query(Team).count()
    
    # Get paginated teams
    teams = db.query(Team).offset(skip).limit(limit).all()
    
    return {
        "teams": teams,
        "total": total,
        "skip": skip,
        "limit": limit
    }
