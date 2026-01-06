"""
Trait definitions and trait-based personality assessment.
"""

from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass


class TraitCategory(Enum):
    """Categories for personality traits."""
    COGNITIVE = "cognitive"
    EMOTIONAL = "emotional"
    BEHAVIORAL = "behavioral"
    INTERPERSONAL = "interpersonal"
    MOTIVATIONAL = "motivational"


@dataclass
class Trait:
    """
    Represents a single personality trait.
    """
    name: str
    category: TraitCategory
    description: str
    scale_low: str
    scale_high: str
    weight: float = 1.0
    
    def __post_init__(self):
        """Validate trait definition."""
        if self.weight < 0 or self.weight > 1:
            raise ValueError("Trait weight must be between 0 and 1")


class TraitProfile:
    """
    Represents a collection of trait scores for an individual.
    """
    
    def __init__(self):
        self.scores: Dict[str, float] = {}
        
    def add_score(self, trait_name: str, score: float):
        """
        Add or update a trait score.
        
        Args:
            trait_name: Name of the trait
            score: Score value (typically 0-100)
        """
        if score < 0 or score > 100:
            raise ValueError("Trait score must be between 0 and 100")
        self.scores[trait_name] = score
        
    def get_score(self, trait_name: str) -> Optional[float]:
        """Get the score for a specific trait."""
        return self.scores.get(trait_name)
        
    def get_all_scores(self) -> Dict[str, float]:
        """Get all trait scores."""
        return self.scores.copy()


def get_standard_traits() -> List[Trait]:
    """
    Returns the standard set of traits used in Team Alchemy assessments.
    
    Returns:
        List of Trait objects
    """
    return [
        Trait(
            name="Extraversion",
            category=TraitCategory.INTERPERSONAL,
            description="Tendency to seek stimulation from the external world",
            scale_low="Introverted",
            scale_high="Extraverted",
            weight=1.0
        ),
        Trait(
            name="Analytical Thinking",
            category=TraitCategory.COGNITIVE,
            description="Preference for logical and systematic analysis",
            scale_low="Intuitive",
            scale_high="Analytical",
            weight=1.0
        ),
        # Add more standard traits as needed
    ]


def calculate_trait_compatibility(profile1: TraitProfile, profile2: TraitProfile) -> float:
    """
    Calculate compatibility between two trait profiles.
    
    Args:
        profile1: First trait profile
        profile2: Second trait profile
        
    Returns:
        Compatibility score (0-100)
    """
    # Placeholder implementation
    common_traits = set(profile1.scores.keys()) & set(profile2.scores.keys())
    if not common_traits:
        return 50.0  # Neutral if no common traits
    
    total_diff = sum(abs(profile1.scores[t] - profile2.scores[t]) for t in common_traits)
    avg_diff = total_diff / len(common_traits)
    
    # Convert difference to compatibility (inverse relationship)
    compatibility = max(0, 100 - avg_diff)
    return compatibility
