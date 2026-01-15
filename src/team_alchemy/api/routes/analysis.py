"""
FastAPI routes for analysis and insights.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from team_alchemy.core.archetypes.jungian_mapper import JungianMapper, MBTIType
from team_alchemy.core.psychology.jungian import JungianAnalyzer, Archetype
from team_alchemy.core.psychology.freudian import FreudianAnalyzer
from team_alchemy.core.psychology.case_study_mapper import CaseStudyMapper

router = APIRouter(prefix="/analysis", tags=["analysis"])


class TeamMemberInput(BaseModel):
    """Input model for team member."""
    user_id: int
    mbti_type: str
    behaviors: List[str] = Field(default_factory=list)
    archetype: str = ""


class TeamAnalysisRequest(BaseModel):
    """Request model for team analysis."""
    team_id: int
    members: List[TeamMemberInput]


class IndividualAnalysisResponse(BaseModel):
    """Response model for individual analysis."""
    user_id: int
    mbti_type: str
    jungian_profile: Dict[str, Any]
    dominant_archetypes: List[Dict[str, Any]]
    defense_mechanisms: List[Dict[str, Any]]
    recommendations: List[str]


class TeamAnalysisResponse(BaseModel):
    """Response model for team analysis."""
    team_id: int
    team_size: int
    member_analyses: List[IndividualAnalysisResponse]
    team_dynamics: Dict[str, Any]
    collective_patterns: Dict[str, Any]
    recommendations: List[str]


@router.post("/team/{team_id}", response_model=TeamAnalysisResponse)
async def analyze_team(team_id: int, request: TeamAnalysisRequest) -> TeamAnalysisResponse:
    """
    Analyze team dynamics and composition.
    
    Integrates Jungian profiles, archetypes, and psychological patterns
    to provide comprehensive team insights.
    """
    if team_id != request.team_id:
        raise HTTPException(status_code=400, detail="Team ID mismatch")
    
    if not request.members:
        raise HTTPException(status_code=400, detail="No team members provided")
    
    jungian_mapper = JungianMapper()
    jungian_analyzer = JungianAnalyzer()
    freudian_analyzer = FreudianAnalyzer()
    
    member_analyses = []
    all_archetypes = []
    
    for member in request.members:
        # Get Jungian profile
        try:
            mbti_enum = MBTIType(member.mbti_type.upper())
        except ValueError:
            continue
            
        profile = jungian_mapper.get_jungian_profile(mbti_enum)
        mapping = jungian_mapper.type_mappings.get(mbti_enum, {})
        
        # Identify archetypes
        archetype_patterns = jungian_analyzer.identify_active_archetypes(
            member.behaviors,
            {}
        )
        all_archetypes.append(archetype_patterns)
        
        # Identify defense mechanisms
        defense_profiles = freudian_analyzer.identify_defenses(
            member.behaviors,
            {}
        )
        
        member_analysis = IndividualAnalysisResponse(
            user_id=member.user_id,
            mbti_type=member.mbti_type,
            jungian_profile={
                "function_stack": [f.value for f in profile.get_function_stack()] if profile else [],
                "archetype_affinity": mapping.get("archetype_affinity", []),
                "strengths": mapping.get("strengths", []),
                "shadow": mapping.get("shadow", ""),
            },
            dominant_archetypes=[
                {
                    "archetype": p.archetype.value,
                    "strength": p.strength,
                    "is_dominant": p.is_dominant()
                }
                for p in archetype_patterns[:3]
            ],
            defense_mechanisms=[
                {
                    "mechanism": p.mechanism.value,
                    "frequency": p.frequency,
                    "adaptiveness": p.adaptiveness
                }
                for p in defense_profiles[:3]
            ],
            recommendations=_generate_individual_recommendations(
                member.mbti_type,
                archetype_patterns,
                defense_profiles
            )
        )
        member_analyses.append(member_analysis)
    
    # Analyze collective patterns
    from team_alchemy.core.psychology.jungian import assess_collective_unconscious_patterns
    collective = assess_collective_unconscious_patterns(all_archetypes)
    
    # Assess team dynamics
    team_dynamics = _assess_team_dynamics(request.members, jungian_mapper)
    
    # Generate team recommendations
    team_recommendations = _generate_team_recommendations(
        member_analyses,
        collective,
        team_dynamics
    )
    
    return TeamAnalysisResponse(
        team_id=team_id,
        team_size=len(request.members),
        member_analyses=member_analyses,
        team_dynamics=team_dynamics,
        collective_patterns=collective,
        recommendations=team_recommendations
    )


@router.get("/individual/{user_id}", response_model=IndividualAnalysisResponse)
async def get_individual_analysis(
    user_id: int,
    mbti_type: str = "",
    behaviors: str = ""
) -> IndividualAnalysisResponse:
    """
    Get individual personality analysis.
    
    Args:
        user_id: User ID
        mbti_type: MBTI type (optional)
        behaviors: Comma-separated list of behaviors (optional)
    """
    if not mbti_type:
        raise HTTPException(
            status_code=400,
            detail="mbti_type is required"
        )
    
    try:
        mbti_enum = MBTIType(mbti_type.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid MBTI type: {mbti_type}"
        )
    
    behavior_list = [b.strip() for b in behaviors.split(",")] if behaviors else []
    
    jungian_mapper = JungianMapper()
    jungian_analyzer = JungianAnalyzer()
    freudian_analyzer = FreudianAnalyzer()
    
    profile = jungian_mapper.get_jungian_profile(mbti_enum)
    mapping = jungian_mapper.type_mappings.get(mbti_enum, {})
    
    archetype_patterns = jungian_analyzer.identify_active_archetypes(
        behavior_list,
        {}
    )
    
    defense_profiles = freudian_analyzer.identify_defenses(
        behavior_list,
        {}
    )
    
    return IndividualAnalysisResponse(
        user_id=user_id,
        mbti_type=mbti_type,
        jungian_profile={
            "function_stack": [f.value for f in profile.get_function_stack()] if profile else [],
            "archetype_affinity": mapping.get("archetype_affinity", []),
            "strengths": mapping.get("strengths", []),
            "shadow": mapping.get("shadow", ""),
        },
        dominant_archetypes=[
            {
                "archetype": p.archetype.value,
                "strength": p.strength,
                "is_dominant": p.is_dominant()
            }
            for p in archetype_patterns[:3]
        ],
        defense_mechanisms=[
            {
                "mechanism": p.mechanism.value,
                "frequency": p.frequency,
                "adaptiveness": p.adaptiveness
            }
            for p in defense_profiles[:3]
        ],
        recommendations=_generate_individual_recommendations(
            mbti_type,
            archetype_patterns,
            defense_profiles
        )
    )


@router.post("/compatibility")
async def check_compatibility(
    user_ids: List[int],
    mbti_types: List[str]
) -> Dict[str, Any]:
    """
    Check compatibility between team members.
    
    Args:
        user_ids: List of user IDs
        mbti_types: List of corresponding MBTI types
    """
    if len(user_ids) != len(mbti_types):
        raise HTTPException(
            status_code=400,
            detail="user_ids and mbti_types must have same length"
        )
    
    if len(user_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 users required for compatibility check"
        )
    
    jungian_mapper = JungianMapper()
    
    compatibility_matrix = []
    for i in range(len(user_ids)):
        for j in range(i + 1, len(user_ids)):
            try:
                type1 = MBTIType(mbti_types[i].upper())
                type2 = MBTIType(mbti_types[j].upper())
                
                compat = jungian_mapper.assess_type_compatibility(type1, type2)
                compatibility_matrix.append({
                    "user1": user_ids[i],
                    "user2": user_ids[j],
                    "mbti1": mbti_types[i],
                    "mbti2": mbti_types[j],
                    **compat
                })
            except ValueError:
                continue
    
    # Calculate overall team compatibility
    avg_score = (
        sum(c["compatibility_score"] for c in compatibility_matrix) / len(compatibility_matrix)
        if compatibility_matrix else 0
    )
    
    return {
        "compatibility_matrix": compatibility_matrix,
        "overall_compatibility": avg_score,
        "total_pairs": len(compatibility_matrix)
    }


def _generate_individual_recommendations(
    mbti_type: str,
    archetypes: List,
    defenses: List
) -> List[str]:
    """Generate personalized recommendations."""
    recommendations = []
    
    # MBTI-based recommendations
    if mbti_type in ["INTJ", "INTP"]:
        recommendations.append("Consider balancing analytical thinking with emotional awareness")
    elif mbti_type in ["ENFP", "ENFJ"]:
        recommendations.append("Practice structured planning to complement your creativity")
    
    # Archetype-based recommendations
    for pattern in archetypes[:2]:
        if pattern.needs_integration():
            recommendations.append(
                f"Work on integrating {pattern.archetype.value} archetype more consciously"
            )
    
    # Defense-based recommendations
    maladaptive = [d for d in defenses if d.is_maladaptive()]
    if maladaptive:
        recommendations.append(
            f"Consider developing healthier coping strategies for {maladaptive[0].mechanism.value}"
        )
    
    return recommendations


def _assess_team_dynamics(members: List[TeamMemberInput], mapper: JungianMapper) -> Dict[str, Any]:
    """Assess overall team dynamics."""
    mbti_distribution = {}
    for member in members:
        mbti_distribution[member.mbti_type] = mbti_distribution.get(member.mbti_type, 0) + 1
    
    # Check for diversity
    diversity_score = len(mbti_distribution) / len(members) if members else 0
    
    return {
        "mbti_distribution": mbti_distribution,
        "diversity_score": diversity_score,
        "balance": "balanced" if diversity_score > 0.6 else "homogeneous",
    }


def _generate_team_recommendations(
    analyses: List,
    collective: Dict,
    dynamics: Dict
) -> List[str]:
    """Generate team-level recommendations."""
    recommendations = []
    
    if dynamics.get("diversity_score", 0) < 0.4:
        recommendations.append(
            "Consider diversifying team composition for better perspective balance"
        )
    
    if collective.get("archetype_diversity", 0) < 3:
        recommendations.append(
            "Team may benefit from including members with different archetypal strengths"
        )
    
    recommendations.append(
        "Leverage individual strengths while supporting areas of development"
    )
    
    return recommendations
