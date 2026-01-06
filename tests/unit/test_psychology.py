"""
Unit tests for psychology modules.
"""

import pytest
from team_alchemy.core.psychology.jungian import (
    JungianAnalyzer,
    Archetype,
    ArchetypalPattern,
)
from team_alchemy.core.psychology.freudian import (
    FreudianAnalyzer,
    DefenseMechanism,
)
from team_alchemy.core.psychology.shadow_work import (
    ShadowWorkAnalyzer,
    ShadowAspect,
    ShadowElement,
)


def test_jungian_analyzer():
    """Test Jungian analyzer initialization."""
    analyzer = JungianAnalyzer()
    
    assert analyzer is not None
    assert len(analyzer.archetype_indicators) > 0


def test_identify_active_archetypes():
    """Test archetype identification."""
    analyzer = JungianAnalyzer()
    behaviors = ["overcomes challenges", "seeks achievement", "competitive nature"]
    responses = {}
    
    patterns = analyzer.identify_active_archetypes(behaviors, responses)
    
    assert isinstance(patterns, list)
    # Should identify HERO archetype based on behaviors
    hero_patterns = [p for p in patterns if p.archetype == Archetype.HERO]
    assert len(hero_patterns) > 0


def test_archetypal_pattern():
    """Test archetypal pattern creation."""
    pattern = ArchetypalPattern(
        archetype=Archetype.HERO,
        strength=0.8,
        manifestations=["achievement seeking"],
        integration_level=0.6
    )
    
    assert pattern.is_dominant()
    assert not pattern.needs_integration()


def test_freudian_analyzer():
    """Test Freudian analyzer initialization."""
    analyzer = FreudianAnalyzer()
    
    assert analyzer is not None
    assert len(analyzer.mechanism_indicators) > 0


def test_identify_defense_mechanisms():
    """Test defense mechanism identification."""
    analyzer = FreudianAnalyzer()
    behaviors = ["justifies behavior", "creates logical explanations"]
    stress_responses = {}
    
    profiles = analyzer.identify_defenses(behaviors, stress_responses)
    
    assert isinstance(profiles, list)
    # Should identify rationalization based on behaviors
    rationalization = [p for p in profiles if p.mechanism == DefenseMechanism.RATIONALIZATION]
    assert len(rationalization) > 0


def test_shadow_work_analyzer():
    """Test shadow work analyzer."""
    analyzer = ShadowWorkAnalyzer()
    
    assert analyzer is not None
    assert len(analyzer.integration_techniques) > 0


def test_shadow_element_creation():
    """Test shadow element creation."""
    element = ShadowElement(
        aspect_type=ShadowAspect.REPRESSED_DESIRE,
        description="Test desire",
        intensity=0.7,
        triggers=["goal situations"],
        integration_status="aware"
    )
    
    assert element.aspect_type == ShadowAspect.REPRESSED_DESIRE
    assert element.needs_work()
    assert not element.is_integrated()


def test_create_integration_plan():
    """Test shadow integration plan creation."""
    analyzer = ShadowWorkAnalyzer()
    element = ShadowElement(
        aspect_type=ShadowAspect.DENIED_TRAIT,
        description="Test trait",
        intensity=0.6,
        triggers=["specific situations"],
        integration_status="aware"
    )
    
    plan = analyzer.create_integration_plan(element)
    
    assert plan.target_element == element
    assert len(plan.techniques) > 0
    assert plan.timeline is not None
