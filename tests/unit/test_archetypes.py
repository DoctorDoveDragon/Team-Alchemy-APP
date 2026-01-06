"""
Unit tests for archetype functionality.
"""

import pytest
from team_alchemy.core.archetypes.definitions import (
    ArchetypeType,
    ArchetypeDefinition,
    get_archetype_definitions,
)
from team_alchemy.core.archetypes.traits import TraitProfile, Trait, TraitCategory
from team_alchemy.core.archetypes.classifier_logic import ArchetypeClassifier


def test_archetype_definition_creation():
    """Test creating an archetype definition."""
    archetype = ArchetypeDefinition(
        archetype_type=ArchetypeType.LEADER,
        name="Test Leader",
        description="A test leader archetype",
        core_traits=["decisive", "confident"],
        strengths=["Leadership"],
        challenges=["Delegation"],
        jungian_mapping={"primary": "ENTJ"}
    )
    
    assert archetype.name == "Test Leader"
    assert archetype.archetype_type == ArchetypeType.LEADER
    assert len(archetype.core_traits) == 2


def test_get_archetype_definitions():
    """Test retrieving archetype definitions."""
    definitions = get_archetype_definitions()
    
    assert isinstance(definitions, dict)
    assert ArchetypeType.LEADER in definitions


def test_trait_profile():
    """Test trait profile functionality."""
    profile = TraitProfile()
    profile.add_score("Extraversion", 75.0)
    profile.add_score("Analytical", 60.0)
    
    assert profile.get_score("Extraversion") == 75.0
    assert profile.get_score("Analytical") == 60.0
    assert len(profile.get_all_scores()) == 2


def test_trait_profile_validation():
    """Test trait profile score validation."""
    profile = TraitProfile()
    
    with pytest.raises(ValueError):
        profile.add_score("Invalid", 150.0)  # Over 100


def test_archetype_classifier():
    """Test archetype classification."""
    classifier = ArchetypeClassifier()
    profile = TraitProfile()
    profile.add_score("Extraversion", 80.0)
    profile.add_score("Decisiveness", 85.0)
    
    result = classifier.classify(profile)
    
    assert result.primary_archetype is not None
    assert 0 <= result.confidence <= 1


def test_trait_creation():
    """Test trait creation and validation."""
    trait = Trait(
        name="Creativity",
        category=TraitCategory.COGNITIVE,
        description="Creative thinking ability",
        scale_low="Conventional",
        scale_high="Creative",
        weight=1.0
    )
    
    assert trait.name == "Creativity"
    assert trait.category == TraitCategory.COGNITIVE


def test_trait_weight_validation():
    """Test trait weight validation."""
    with pytest.raises(ValueError):
        Trait(
            name="Invalid",
            category=TraitCategory.COGNITIVE,
            description="Test",
            scale_low="Low",
            scale_high="High",
            weight=2.0  # Invalid weight
        )
