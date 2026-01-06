"""
Classifier logic for determining personality archetypes from assessment data.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from team_alchemy.core.archetypes.definitions import ArchetypeType, ArchetypeDefinition
from team_alchemy.core.archetypes.traits import TraitProfile


@dataclass
class ClassificationResult:
    """Result of archetype classification."""
    primary_archetype: ArchetypeType
    secondary_archetype: Optional[ArchetypeType]
    confidence: float
    trait_scores: Dict[str, float]
    
    def __post_init__(self):
        """Validate classification result."""
        if self.confidence < 0 or self.confidence > 1:
            raise ValueError("Confidence must be between 0 and 1")


class ArchetypeClassifier:
    """
    Classifies individuals into archetypes based on trait profiles.
    """
    
    def __init__(self):
        self.archetype_patterns: Dict[ArchetypeType, Dict[str, float]] = {}
        self._initialize_patterns()
        
    def _initialize_patterns(self):
        """Initialize archetype classification patterns."""
        # Placeholder patterns - would be loaded from config or ML model
        self.archetype_patterns[ArchetypeType.LEADER] = {
            "Extraversion": 80.0,
            "Decisiveness": 85.0,
            "Confidence": 90.0,
        }
        self.archetype_patterns[ArchetypeType.ANALYST] = {
            "Analytical Thinking": 90.0,
            "Detail Orientation": 85.0,
            "Logical Reasoning": 88.0,
        }
        # Add more patterns
        
    def classify(self, trait_profile: TraitProfile) -> ClassificationResult:
        """
        Classify a trait profile into an archetype.
        
        Args:
            trait_profile: The trait profile to classify
            
        Returns:
            ClassificationResult with primary and secondary archetypes
        """
        scores = self._calculate_archetype_scores(trait_profile)
        
        # Sort by score
        sorted_archetypes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        primary = sorted_archetypes[0][0]
        secondary = sorted_archetypes[1][0] if len(sorted_archetypes) > 1 else None
        confidence = sorted_archetypes[0][1] / 100.0
        
        return ClassificationResult(
            primary_archetype=primary,
            secondary_archetype=secondary,
            confidence=confidence,
            trait_scores=trait_profile.get_all_scores()
        )
        
    def _calculate_archetype_scores(self, trait_profile: TraitProfile) -> Dict[ArchetypeType, float]:
        """
        Calculate match scores for each archetype.
        
        Args:
            trait_profile: The trait profile to score
            
        Returns:
            Dictionary mapping archetype types to match scores
        """
        scores = {}
        
        for archetype_type, pattern in self.archetype_patterns.items():
            score = self._calculate_pattern_match(trait_profile, pattern)
            scores[archetype_type] = score
            
        return scores
        
    def _calculate_pattern_match(self, trait_profile: TraitProfile, pattern: Dict[str, float]) -> float:
        """
        Calculate how well a trait profile matches a pattern.
        
        Args:
            trait_profile: The trait profile
            pattern: The archetype pattern
            
        Returns:
            Match score (0-100)
        """
        if not pattern:
            return 0.0
            
        total_diff = 0.0
        count = 0
        
        for trait_name, expected_value in pattern.items():
            actual_value = trait_profile.get_score(trait_name)
            if actual_value is not None:
                diff = abs(expected_value - actual_value)
                total_diff += diff
                count += 1
                
        if count == 0:
            return 0.0
            
        avg_diff = total_diff / count
        # Convert difference to match score (inverse)
        match_score = max(0, 100 - avg_diff)
        
        return match_score


def classify_team_composition(profiles: List[TraitProfile]) -> Dict[str, any]:
    """
    Analyze the archetype composition of a team.
    
    Args:
        profiles: List of trait profiles for team members
        
    Returns:
        Dictionary with team composition analysis
    """
    classifier = ArchetypeClassifier()
    
    archetype_counts = {}
    classifications = []
    
    for profile in profiles:
        result = classifier.classify(profile)
        classifications.append(result)
        
        # Count archetypes
        archetype_counts[result.primary_archetype] = archetype_counts.get(
            result.primary_archetype, 0
        ) + 1
        
    return {
        "team_size": len(profiles),
        "archetype_distribution": archetype_counts,
        "classifications": classifications,
        "diversity_score": len(archetype_counts) / len(ArchetypeType) * 100,
    }
