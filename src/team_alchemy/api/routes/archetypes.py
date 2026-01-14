"""
FastAPI routes for archetype definitions.
"""

from typing import Dict
from fastapi import APIRouter, HTTPException

from team_alchemy.core.archetypes.definitions import (
    ArchetypeType,
    ArchetypeDefinition,
    get_archetype_definitions,
    get_archetype_by_type,
)
from team_alchemy.api.schemas.archetypes import ArchetypeSchema, ArchetypesResponse

router = APIRouter(prefix="/archetypes", tags=["archetypes"])


def _archetype_to_schema(archetype_def: ArchetypeDefinition) -> ArchetypeSchema:
    """Convert ArchetypeDefinition to ArchetypeSchema."""
    return ArchetypeSchema(
        archetype_type=archetype_def.archetype_type.value,
        name=archetype_def.name,
        description=archetype_def.description,
        core_traits=archetype_def.core_traits,
        strengths=archetype_def.strengths,
        challenges=archetype_def.challenges,
        jungian_mapping=archetype_def.jungian_mapping,
    )


@router.get("/", response_model=ArchetypesResponse)
async def get_all_archetypes():
    """
    Get all archetype definitions.

    Returns:
        Dictionary of all archetype definitions keyed by archetype type
    """
    definitions = get_archetype_definitions()

    # Convert to serializable dictionary
    archetypes_dict: Dict[str, ArchetypeSchema] = {}
    for archetype_type, archetype_def in definitions.items():
        archetypes_dict[archetype_type.value] = _archetype_to_schema(archetype_def)

    return ArchetypesResponse(archetypes=archetypes_dict)


@router.get("/{archetype_type}", response_model=ArchetypeSchema)
async def get_archetype(archetype_type: str):
    """
    Get a specific archetype definition by type.

    Args:
        archetype_type: The archetype type identifier (e.g., 'leader', 'innovator')

    Returns:
        The archetype definition

    Raises:
        HTTPException: 404 if archetype type not found
    """
    # Try to convert string to ArchetypeType enum
    try:
        arch_type_enum = ArchetypeType(archetype_type.lower())
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Archetype type '{archetype_type}' not found",
        )

    # Get the archetype definition
    archetype_def = get_archetype_by_type(arch_type_enum)

    return _archetype_to_schema(archetype_def)
