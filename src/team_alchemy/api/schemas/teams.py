"""
Pydantic schemas for team API endpoints.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TeamCreate(BaseModel):
    """Schema for creating a new team."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Team name")
    description: Optional[str] = Field(None, max_length=1000, description="Team description")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Engineering Team",
                "description": "Core engineering team for backend development"
            }
        }


class UserInTeam(BaseModel):
    """Schema for user info within team context."""
    
    id: int
    email: str
    name: str

    class Config:
        from_attributes = True


class TeamResponse(BaseModel):
    """Schema for team response."""
    
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    members: List[UserInTeam] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Engineering Team",
                "description": "Core engineering team for backend development",
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
    """Schema for listing teams."""
    
    teams: List[TeamResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "teams": [
                    {
                        "id": 1,
                        "name": "Engineering Team",
                        "description": "Core engineering team",
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00",
                        "members": []
                    }
                ],
                "total": 1
            }
        }
