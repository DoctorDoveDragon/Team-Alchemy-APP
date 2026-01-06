"""
FastAPI routes for team management.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from team_alchemy.data.repository import get_db

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/")
async def create_team(name: str, db: Session = Depends(get_db)):
    """Create a new team."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{team_id}")
async def get_team(team_id: int, db: Session = Depends(get_db)):
    """Get team by ID."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/{team_id}/members/{user_id}")
async def add_team_member(team_id: int, user_id: int, db: Session = Depends(get_db)):
    """Add member to team."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/")
async def list_teams(db: Session = Depends(get_db)):
    """List all teams."""
    return []
