"""
Pydantic schemas for team API endpoints.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class UserBasic(BaseModel):
    """Basic user information for team member responses."""
    
    id: int
    email: str
    name: str
    
    class Config:
        from_attributes = True


class TeamBase(BaseModel):
    """Base team model."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Team name")
    description: Optional[str] = Field(None, max_length=1000, description="Team description")


class TeamCreate(TeamBase):
    """Model for creating a team."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Engineering Team",
                "description": "Software development team"
            }
        }


class TeamResponse(TeamBase):
    """Full team model for responses."""
    
    id: int
    created_at: datetime
    updated_at: datetime
    members: List[UserBasic] = []
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Engineering Team",
                "description": "Software development team",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "members": [
                    {
                        "id": 1,
                        "email": "user@example.com",
                        "name": "John Doe"
                    }
                ]
            }
        }


class TeamListResponse(BaseModel):
    """Response model for listing teams."""
    
    teams: List[TeamResponse]
    total: int
    skip: int
    limit: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "teams": [
                    {
                        "id": 1,
                        "name": "Engineering Team",
                        "description": "Software development team",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00",
                        "members": []
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 100
            }
        }


class TeamMemberAddResponse(BaseModel):
    """Response model for adding a team member."""
    
    message: str
    team: TeamResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Member added successfully",
                "team": {
                    "id": 1,
                    "name": "Engineering Team",
                    "description": "Software development team",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                    "members": [
                        {
                            "id": 1,
                            "email": "user@example.com",
                            "name": "John Doe"
                        }
                    ]
                }
            }
        }
