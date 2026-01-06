"""
Archetype definitions for personality types in the Team Alchemy system.
"""

from enum import Enum
from typing import Dict, List
from dataclasses import dataclass


class ArchetypeType(Enum):
    """Core archetype types based on psychological frameworks."""
    LEADER = "leader"
    INNOVATOR = "innovator"
    HARMONIZER = "harmonizer"
    ANALYST = "analyst"
    IMPLEMENTER = "implementer"
    VISIONARY = "visionary"
    COLLABORATOR = "collaborator"
    SPECIALIST = "specialist"


@dataclass
class ArchetypeDefinition:
    """
    Defines an archetype with its characteristics and behaviors.
    """
    archetype_type: ArchetypeType
    name: str
    description: str
    core_traits: List[str]
    strengths: List[str]
    challenges: List[str]
    jungian_mapping: Dict[str, str]
    
    def __post_init__(self):
        """Validate archetype definition."""
        if not self.name:
            raise ValueError("Archetype name cannot be empty")
        if not self.core_traits:
            raise ValueError("Archetype must have at least one core trait")


def get_archetype_definitions() -> Dict[ArchetypeType, ArchetypeDefinition]:
    """
    Returns all standard archetype definitions.
    
    Returns:
        Dictionary mapping archetype types to their definitions
    """
    return {
        ArchetypeType.LEADER: ArchetypeDefinition(
            archetype_type=ArchetypeType.LEADER,
            name="The Leader",
            description="Natural leader who takes charge and inspires others",
            core_traits=["decisive", "confident", "charismatic"],
            strengths=["Strategic thinking", "Team motivation", "Decision making"],
            challenges=["Can be domineering", "May overlook details"],
            jungian_mapping={"primary": "ENTJ", "secondary": "ESTJ"}
        ),
        # Add more archetypes as needed
    }


def get_archetype_by_type(archetype_type: ArchetypeType) -> ArchetypeDefinition:
    """
    Retrieve a specific archetype definition by type.
    
    Args:
        archetype_type: The type of archetype to retrieve
        
    Returns:
        ArchetypeDefinition for the specified type
    """
    definitions = get_archetype_definitions()
    return definitions.get(archetype_type)
