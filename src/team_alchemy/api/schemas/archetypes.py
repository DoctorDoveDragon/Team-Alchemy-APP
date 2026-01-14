"""
Pydantic schemas for archetype API endpoints.
"""

from typing import Dict, List
from pydantic import BaseModel, Field


class ArchetypeSchema(BaseModel):
    """Schema for archetype definition in API responses."""

    archetype_type: str = Field(..., description="The archetype type identifier")
    name: str = Field(..., description="Human-readable name of the archetype")
    description: str = Field(..., description="Description of the archetype")
    core_traits: List[str] = Field(..., description="Core personality traits")
    strengths: List[str] = Field(..., description="Key strengths of this archetype")
    challenges: List[str] = Field(..., description="Common challenges faced")
    jungian_mapping: Dict[str, str] = Field(
        ..., description="Mapping to Jungian personality types"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "archetype_type": "leader",
                "name": "The Leader",
                "description": "Natural leader who takes charge and inspires others",
                "core_traits": ["decisive", "confident", "charismatic"],
                "strengths": ["Strategic thinking", "Team motivation", "Decision making"],
                "challenges": ["Can be domineering", "May overlook details"],
                "jungian_mapping": {"primary": "ENTJ", "secondary": "ESTJ"},
            }
        }


class ArchetypesResponse(BaseModel):
    """Schema for response containing all archetypes."""

    archetypes: Dict[str, ArchetypeSchema] = Field(
        ..., description="Dictionary of archetypes keyed by archetype type"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "archetypes": {
                    "leader": {
                        "archetype_type": "leader",
                        "name": "The Leader",
                        "description": "Natural leader who takes charge and inspires others",
                        "core_traits": ["decisive", "confident", "charismatic"],
                        "strengths": [
                            "Strategic thinking",
                            "Team motivation",
                            "Decision making",
                        ],
                        "challenges": ["Can be domineering", "May overlook details"],
                        "jungian_mapping": {"primary": "ENTJ", "secondary": "ESTJ"},
                    }
                }
            }
        }
