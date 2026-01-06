"""
Freudian psychology concepts and defense mechanisms analysis.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class DefenseMechanism(Enum):
    """Freudian defense mechanisms."""
    REPRESSION = "repression"
    DENIAL = "denial"
    PROJECTION = "projection"
    DISPLACEMENT = "displacement"
    RATIONALIZATION = "rationalization"
    REACTION_FORMATION = "reaction_formation"
    SUBLIMATION = "sublimation"
    REGRESSION = "regression"
    INTELLECTUALIZATION = "intellectualization"
    HUMOR = "humor"


class StructuralElement(Enum):
    """Freudian structural model of psyche."""
    ID = "id"
    EGO = "ego"
    SUPEREGO = "superego"


@dataclass
class DefenseProfile:
    """Profile of defense mechanisms in use."""
    mechanism: DefenseMechanism
    frequency: float  # How often used (0-1)
    adaptiveness: float  # How adaptive (0-1)
    contexts: List[str]  # Contexts where observed
    
    def is_maladaptive(self) -> bool:
        """Check if defense is maladaptive."""
        return self.adaptiveness < 0.4


class FreudianAnalyzer:
    """
    Analyzes behavior through Freudian psychology lens.
    """
    
    def __init__(self):
        self.mechanism_indicators = self._load_indicators()
        self.adaptive_mechanisms = {
            DefenseMechanism.SUBLIMATION,
            DefenseMechanism.HUMOR,
            DefenseMechanism.INTELLECTUALIZATION,
        }
        
    def _load_indicators(self) -> Dict[DefenseMechanism, List[str]]:
        """Load behavioral indicators for defense mechanisms."""
        return {
            DefenseMechanism.DENIAL: [
                "refuses to acknowledge",
                "ignores reality",
                "dismisses evidence"
            ],
            DefenseMechanism.PROJECTION: [
                "attributes own feelings to others",
                "accuses others of own faults",
                "externalizes blame"
            ],
            DefenseMechanism.RATIONALIZATION: [
                "justifies behavior",
                "creates logical explanations",
                "excuses actions"
            ],
            DefenseMechanism.SUBLIMATION: [
                "channels energy productively",
                "transforms impulses creatively",
                "redirects to socially acceptable"
            ],
            # Add more indicators
        }
        
    def identify_defenses(
        self,
        behaviors: List[str],
        stress_responses: Dict[str, any]
    ) -> List[DefenseProfile]:
        """
        Identify active defense mechanisms.
        
        Args:
            behaviors: Observed behaviors
            stress_responses: Responses to stress situations
            
        Returns:
            List of active defense profiles
        """
        profiles = []
        
        for mechanism, indicators in self.mechanism_indicators.items():
            matching_behaviors = [
                b for b in behaviors
                if any(ind.lower() in b.lower() for ind in indicators)
            ]
            
            if matching_behaviors:
                frequency = min(1.0, len(matching_behaviors) / 5.0)
                adaptiveness = self._assess_adaptiveness(mechanism, matching_behaviors)
                
                profile = DefenseProfile(
                    mechanism=mechanism,
                    frequency=frequency,
                    adaptiveness=adaptiveness,
                    contexts=matching_behaviors[:3]  # Top 3 examples
                )
                profiles.append(profile)
                
        return sorted(profiles, key=lambda p: p.frequency, reverse=True)
        
    def _assess_adaptiveness(
        self,
        mechanism: DefenseMechanism,
        behaviors: List[str]
    ) -> float:
        """Assess how adaptive a defense mechanism is."""
        # Mature defenses are more adaptive
        if mechanism in self.adaptive_mechanisms:
            return 0.8
        # Primitive defenses are less adaptive
        elif mechanism in {DefenseMechanism.DENIAL, DefenseMechanism.PROJECTION}:
            return 0.3
        else:
            return 0.5  # Neurotic defenses - moderately adaptive
            
    def analyze_structural_balance(
        self,
        personality_data: Dict[str, any]
    ) -> Dict[str, float]:
        """
        Analyze balance between Id, Ego, and Superego.
        
        Args:
            personality_data: Personality assessment data
            
        Returns:
            Structural balance scores
        """
        # Placeholder implementation
        # Would analyze impulse control, reality testing, and moral standards
        
        return {
            "id_strength": 0.6,      # Impulse and drives
            "ego_strength": 0.7,     # Reality testing and executive function
            "superego_strength": 0.6, # Moral standards and ideals
            "balance_score": 0.7,    # Overall balance
        }
        
    def assess_psychosexual_development(
        self,
        developmental_data: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Assess psychosexual development stages.
        
        Args:
            developmental_data: Development history data
            
        Returns:
            Analysis of psychosexual development
        """
        # Placeholder - would assess fixations at different stages
        return {
            "dominant_stage": "genital",
            "fixations": [],
            "overall_maturity": 0.8,
        }


def analyze_conflict_patterns(defense_profiles: List[DefenseProfile]) -> Dict[str, any]:
    """
    Analyze patterns of psychological conflict.
    
    Args:
        defense_profiles: List of defense mechanism profiles
        
    Returns:
        Conflict pattern analysis
    """
    # Identify maladaptive patterns
    maladaptive = [p for p in defense_profiles if p.is_maladaptive()]
    
    # Calculate overall defensiveness
    avg_frequency = (
        sum(p.frequency for p in defense_profiles) / len(defense_profiles)
        if defense_profiles else 0
    )
    
    # Assess maturity of defenses
    avg_adaptiveness = (
        sum(p.adaptiveness for p in defense_profiles) / len(defense_profiles)
        if defense_profiles else 0
    )
    
    return {
        "defensiveness_level": avg_frequency,
        "defense_maturity": avg_adaptiveness,
        "maladaptive_count": len(maladaptive),
        "primary_conflicts": [p.mechanism.value for p in maladaptive],
        "recommendations": _generate_recommendations(maladaptive),
    }


def _generate_recommendations(maladaptive: List[DefenseProfile]) -> List[str]:
    """Generate recommendations based on maladaptive defenses."""
    recommendations = []
    
    for profile in maladaptive:
        if profile.mechanism == DefenseMechanism.DENIAL:
            recommendations.append("Work on acknowledging difficult realities")
        elif profile.mechanism == DefenseMechanism.PROJECTION:
            recommendations.append("Practice self-reflection and ownership")
        elif profile.mechanism == DefenseMechanism.REGRESSION:
            recommendations.append("Develop mature coping strategies")
            
    return recommendations
