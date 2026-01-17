"""
Pydantic schemas for team API endpoints.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class TeamCreate(BaseModel):
    """Schema for creating a new team."""

    name: str = Field(..., description="The name of the team", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Team description", max_length=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Engineering Team",
                "description": "Core engineering team for product development",
            }
        }


class UserResponse(BaseModel):
    """Schema for user in team member list."""

    id: int
    email: str
    name: str

    class Config:
        from_attributes = True


class TeamResponse(BaseModel):
    """Schema for team response."""

    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    members: List[UserResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Engineering Team",
                "description": "Core engineering team for product development",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "members": [
                    {"id": 1, "email": "user@example.com", "name": "John Doe"}
                ],
            }
        }


class TeamMemberResponse(BaseModel):
    """Schema for team member add response."""

    message: str
    team_id: int
    user_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "message": "User added to team successfully",
                "team_id": 1,
                "user_id": 2,
            }
        }
