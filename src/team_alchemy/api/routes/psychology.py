"""
FastAPI routes for psychological analysis including Jungian and Freudian analysis.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from team_alchemy.core.archetypes.jungian_mapper import (
    JungianMapper,
    MBTIType,
    JungianProfile,
    JungianFunction,
)
from team_alchemy.core.psychology.freudian import (
    FreudianAnalyzer,
    DefenseProfile,
    DefenseMechanism,
)
from team_alchemy.core.psychology.case_study_mapper import (
    CaseStudyMapper,
    CaseStudy,
)

router = APIRouter(prefix="/psychology", tags=["psychology"])


# Request/Response models
class JungianProfileResponse(BaseModel):
    """Response model for Jungian profile."""
    mbti_type: str
    dominant_function: str
    auxiliary_function: str
    tertiary_function: str
    inferior_function: str
    function_stack: List[str]
    archetype_affinity: List[str]
    strengths: List[str]
    shadow: str


class DefenseMechanismRequest(BaseModel):
    """Request model for defense mechanism analysis."""
    behaviors: List[str] = Field(..., description="List of observed behaviors")
    stress_responses: Dict[str, Any] = Field(default_factory=dict, description="Stress response data")


class DefenseMechanismResponse(BaseModel):
    """Response model for defense mechanism."""
    mechanism: str
    frequency: float
    adaptiveness: float
    contexts: List[str]
    is_maladaptive: bool


class DefenseAnalysisResponse(BaseModel):
    """Response model for complete defense analysis."""
    defense_profiles: List[DefenseMechanismResponse]
    defensiveness_level: float
    defense_maturity: float
    maladaptive_count: int
    primary_conflicts: List[str]
    recommendations: List[str]


class CaseStudyResponse(BaseModel):
    """Response model for case study."""
    id: str
    title: str
    summary: str
    framework: str
    created_at: str


class CaseStudyDetailResponse(BaseModel):
    """Response model for detailed case study."""
    id: str
    title: str
    framework: str
    created_at: str
    profile: Dict[str, Any]
    interventions: List[str]
    outcomes: Dict[str, Any]


class SimilarCasesRequest(BaseModel):
    """Request model for finding similar cases."""
    profile: Dict[str, Any] = Field(..., description="Current assessment profile")
    limit: int = Field(default=5, ge=1, le=20, description="Maximum number of cases to return")


class RecommendationsResponse(BaseModel):
    """Response model for intervention recommendations."""
    recommendations: List[str]
    similar_cases: List[CaseStudyResponse]


# Jungian Psychology Endpoints

@router.get("/jungian/profile/{mbti_type}", response_model=JungianProfileResponse)
async def get_jungian_profile(mbti_type: str):
    """
    Get Jungian psychological profile for an MBTI type.
    
    Args:
        mbti_type: MBTI type (e.g., INTJ, ENFP)
        
    Returns:
        Jungian profile with function stack and archetype affinities
    """
    try:
        mbti_enum = MBTIType(mbti_type.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid MBTI type: {mbti_type}. Must be one of: {', '.join([t.value for t in MBTIType])}"
        )
    
    mapper = JungianMapper()
    profile = mapper.get_jungian_profile(mbti_enum)
    
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Profile not found for MBTI type: {mbti_type}"
        )
    
    # Get additional details from mappings
    mapping = mapper.type_mappings.get(mbti_enum, {})
    
    return JungianProfileResponse(
        mbti_type=profile.mbti_type.value,
        dominant_function=profile.dominant_function.value,
        auxiliary_function=profile.auxiliary_function.value,
        tertiary_function=profile.tertiary_function.value,
        inferior_function=profile.inferior_function.value,
        function_stack=[f.value for f in profile.get_function_stack()],
        archetype_affinity=mapping.get("archetype_affinity", []),
        strengths=mapping.get("strengths", []),
        shadow=mapping.get("shadow", ""),
    )


@router.get("/jungian/compatibility/{type1}/{type2}")
async def check_jungian_compatibility(type1: str, type2: str):
    """
    Check compatibility between two MBTI types.
    
    Args:
        type1: First MBTI type
        type2: Second MBTI type
        
    Returns:
        Compatibility analysis
    """
    try:
        mbti1 = MBTIType(type1.upper())
        mbti2 = MBTIType(type2.upper())
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid MBTI type: {str(e)}"
        )
    
    mapper = JungianMapper()
    compatibility = mapper.assess_type_compatibility(mbti1, mbti2)
    
    return compatibility


@router.get("/jungian/types")
async def list_mbti_types():
    """
    List all available MBTI types with their basic info.
    
    Returns:
        List of MBTI types with archetype affinities
    """
    mapper = JungianMapper()
    
    types_info = []
    for mbti_type in MBTIType:
        mapping = mapper.type_mappings.get(mbti_type, {})
        types_info.append({
            "mbti_type": mbti_type.value,
            "archetype_affinity": mapping.get("archetype_affinity", []),
            "strengths": mapping.get("strengths", []),
        })
    
    return {"types": types_info}


# Freudian Analysis Endpoints

@router.post("/freudian/defense-mechanisms", response_model=DefenseAnalysisResponse)
async def analyze_defense_mechanisms(request: DefenseMechanismRequest):
    """
    Identify Freudian defense mechanisms based on observed behaviors.
    
    Args:
        request: Defense mechanism analysis request with behaviors and stress responses
        
    Returns:
        Defense mechanism analysis with frequency, adaptiveness, and contexts
    """
    analyzer = FreudianAnalyzer()
    
    # Identify defense mechanisms
    profiles = analyzer.identify_defenses(
        request.behaviors,
        request.stress_responses
    )
    
    # Analyze conflict patterns
    from team_alchemy.core.psychology.freudian import analyze_conflict_patterns
    conflict_analysis = analyze_conflict_patterns(profiles)
    
    # Convert profiles to response format
    defense_responses = [
        DefenseMechanismResponse(
            mechanism=p.mechanism.value,
            frequency=p.frequency,
            adaptiveness=p.adaptiveness,
            contexts=p.contexts,
            is_maladaptive=p.is_maladaptive()
        )
        for p in profiles
    ]
    
    return DefenseAnalysisResponse(
        defense_profiles=defense_responses,
        defensiveness_level=conflict_analysis["defensiveness_level"],
        defense_maturity=conflict_analysis["defense_maturity"],
        maladaptive_count=conflict_analysis["maladaptive_count"],
        primary_conflicts=conflict_analysis["primary_conflicts"],
        recommendations=conflict_analysis["recommendations"],
    )


@router.get("/freudian/mechanisms")
async def list_defense_mechanisms():
    """
    List all Freudian defense mechanisms.
    
    Returns:
        List of defense mechanisms with descriptions
    """
    mechanisms = []
    for mechanism in DefenseMechanism:
        mechanisms.append({
            "name": mechanism.value,
            "type": mechanism.name,
        })
    
    return {"mechanisms": mechanisms}


# Case Study Endpoints

@router.get("/case-studies/frameworks")
async def list_frameworks():
    """
    List all psychological frameworks used in case studies.
    
    Returns:
        List of frameworks
    """
    mapper = CaseStudyMapper()
    frameworks = mapper.get_all_frameworks()
    
    return {"frameworks": frameworks}


@router.get("/case-studies", response_model=List[CaseStudyResponse])
async def list_case_studies():
    """
    List all available psychological case studies.
    
    Returns:
        List of case studies
    """
    mapper = CaseStudyMapper()
    
    studies = []
    for case in mapper.case_database.values():
        studies.append(CaseStudyResponse(
            id=case.id,
            title=case.title,
            summary=case.get_summary(),
            framework=case.psychological_framework,
            created_at=case.created_at.isoformat(),
        ))
    
    return studies


@router.get("/case-studies/{case_id}", response_model=CaseStudyDetailResponse)
async def get_case_study(case_id: str):
    """
    Get detailed information about a specific case study.
    
    Args:
        case_id: Case study ID
        
    Returns:
        Detailed case study information
    """
    mapper = CaseStudyMapper()
    case = mapper.get_case_by_id(case_id)
    
    if not case:
        raise HTTPException(
            status_code=404,
            detail=f"Case study not found: {case_id}"
        )
    
    return CaseStudyDetailResponse(
        id=case.id,
        title=case.title,
        framework=case.psychological_framework,
        created_at=case.created_at.isoformat(),
        profile=case.subject_profile,
        interventions=case.interventions,
        outcomes=case.outcomes,
    )


@router.post("/case-studies/similar", response_model=List[CaseStudyResponse])
async def find_similar_cases(request: SimilarCasesRequest):
    """
    Find case studies similar to a given profile.
    
    Args:
        request: Profile and limit for similar case search
        
    Returns:
        List of similar case studies
    """
    mapper = CaseStudyMapper()
    similar_cases = mapper.find_similar_cases(
        request.profile,
        limit=request.limit
    )
    
    return [
        CaseStudyResponse(
            id=case.id,
            title=case.title,
            summary=case.get_summary(),
            framework=case.psychological_framework,
            created_at=case.created_at.isoformat(),
        )
        for case in similar_cases
    ]


@router.post("/case-studies/recommendations", response_model=RecommendationsResponse)
async def get_intervention_recommendations(request: SimilarCasesRequest):
    """
    Get intervention recommendations based on similar case studies.
    
    Args:
        request: Profile for which to get recommendations
        
    Returns:
        Recommended interventions and similar cases
    """
    mapper = CaseStudyMapper()
    
    # Get similar cases
    similar_cases = mapper.find_similar_cases(
        request.profile,
        limit=request.limit
    )
    
    # Get recommendations
    recommendations = mapper.recommend_interventions(request.profile)
    
    return RecommendationsResponse(
        recommendations=recommendations,
        similar_cases=[
            CaseStudyResponse(
                id=case.id,
                title=case.title,
                summary=case.get_summary(),
                framework=case.psychological_framework,
                created_at=case.created_at.isoformat(),
            )
            for case in similar_cases
        ]
    )
