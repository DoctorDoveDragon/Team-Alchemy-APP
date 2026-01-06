"""
Jungian psychology concepts and analysis.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class Archetype(Enum):
    """Jungian archetypes."""
    SELF = "self"
    SHADOW = "shadow"
    ANIMA = "anima"
    ANIMUS = "animus"
    PERSONA = "persona"
    WISE_OLD_MAN = "wise_old_man"
    GREAT_MOTHER = "great_mother"
    HERO = "hero"
    TRICKSTER = "trickster"


@dataclass
class ArchetypalPattern:
    """Represents an archetypal pattern in behavior or personality."""
    archetype: Archetype
    strength: float  # 0-1 scale
    manifestations: List[str]
    integration_level: float  # How well integrated this archetype is
    
    def is_dominant(self) -> bool:
        """Check if this is a dominant archetype."""
        return self.strength > 0.7
        
    def needs_integration(self) -> bool:
        """Check if archetype needs better integration."""
        return self.integration_level < 0.5


class JungianAnalyzer:
    """
    Analyzes personality from a Jungian psychology perspective.
    """
    
    def __init__(self):
        self.archetype_indicators: Dict[Archetype, List[str]] = self._load_indicators()
        
    def _load_indicators(self) -> Dict[Archetype, List[str]]:
        """Load behavioral indicators for each archetype."""
        return {
            Archetype.HERO: [
                "overcomes challenges",
                "seeks achievement",
                "competitive nature",
                "goal-oriented"
            ],
            Archetype.SHADOW: [
                "hidden tendencies",
                "repressed desires",
                "unconscious behaviors",
                "denied aspects"
            ],
            Archetype.WISE_OLD_MAN: [
                "seeks wisdom",
                "mentoring others",
                "reflective nature",
                "values knowledge"
            ],
            # Add more indicators
        }
        
    def identify_active_archetypes(
        self,
        behaviors: List[str],
        responses: Dict[str, any]
    ) -> List[ArchetypalPattern]:
        """
        Identify which archetypes are active in an individual.
        
        Args:
            behaviors: Observed behaviors
            responses: Assessment responses
            
        Returns:
            List of active archetypal patterns
        """
        patterns = []
        
        for archetype, indicators in self.archetype_indicators.items():
            # Count matching indicators
            matches = sum(
                1 for behavior in behaviors
                if any(ind.lower() in behavior.lower() for ind in indicators)
            )
            
            if matches > 0:
                strength = min(1.0, matches / len(indicators))
                integration = self._assess_integration(archetype, responses)
                
                pattern = ArchetypalPattern(
                    archetype=archetype,
                    strength=strength,
                    manifestations=[b for b in behaviors if any(
                        ind.lower() in b.lower() for ind in indicators
                    )],
                    integration_level=integration
                )
                patterns.append(pattern)
                
        # Sort by strength
        patterns.sort(key=lambda p: p.strength, reverse=True)
        return patterns
        
    def _assess_integration(
        self,
        archetype: Archetype,
        responses: Dict[str, any]
    ) -> float:
        """Assess how well an archetype is integrated."""
        # Placeholder logic
        # Would analyze for balance, acceptance, and conscious awareness
        return 0.6  # Default moderate integration
        
    def analyze_individuation_progress(
        self,
        patterns: List[ArchetypalPattern]
    ) -> Dict[str, any]:
        """
        Analyze progress toward individuation (wholeness).
        
        Args:
            patterns: Active archetypal patterns
            
        Returns:
            Analysis of individuation progress
        """
        # Check for Self archetype activation
        self_pattern = next(
            (p for p in patterns if p.archetype == Archetype.SELF),
            None
        )
        
        # Check shadow integration
        shadow_pattern = next(
            (p for p in patterns if p.archetype == Archetype.SHADOW),
            None
        )
        
        # Assess balance
        avg_integration = (
            sum(p.integration_level for p in patterns) / len(patterns)
            if patterns else 0
        )
        
        return {
            "self_realization": self_pattern.strength if self_pattern else 0,
            "shadow_integration": shadow_pattern.integration_level if shadow_pattern else 0,
            "overall_integration": avg_integration,
            "active_archetypes": len(patterns),
            "individuation_stage": self._determine_stage(avg_integration),
        }
        
    def _determine_stage(self, integration: float) -> str:
        """Determine current stage of individuation."""
        if integration < 0.3:
            return "early"
        elif integration < 0.6:
            return "developing"
        elif integration < 0.8:
            return "advanced"
        else:
            return "integrated"


def assess_collective_unconscious_patterns(
    group_patterns: List[List[ArchetypalPattern]]
) -> Dict[str, any]:
    """
    Analyze collective unconscious patterns in a group.
    
    Args:
        group_patterns: List of archetypal patterns for each group member
        
    Returns:
        Analysis of collective patterns
    """
    # Count archetype frequencies
    archetype_counts: Dict[Archetype, int] = {}
    
    for patterns in group_patterns:
        for pattern in patterns:
            if pattern.is_dominant():
                archetype_counts[pattern.archetype] = archetype_counts.get(
                    pattern.archetype, 0
                ) + 1
                
    # Find dominant collective archetypes
    total_members = len(group_patterns)
    dominant_collective = {
        arch: count / total_members
        for arch, count in archetype_counts.items()
        if count / total_members > 0.3  # 30% threshold
    }
    
    return {
        "collective_archetypes": dominant_collective,
        "archetype_diversity": len(archetype_counts),
        "group_size": total_members,
        "dominant_pattern": max(archetype_counts.items(), key=lambda x: x[1])[0].value
        if archetype_counts else None,
    }
