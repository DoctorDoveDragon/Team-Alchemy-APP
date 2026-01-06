"""
Jungian personality type mapping and integration.
"""

from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass


class JungianFunction(Enum):
    """Jungian cognitive functions."""
    INTROVERTED_THINKING = "Ti"
    EXTRAVERTED_THINKING = "Te"
    INTROVERTED_FEELING = "Fi"
    EXTRAVERTED_FEELING = "Fe"
    INTROVERTED_SENSING = "Si"
    EXTRAVERTED_SENSING = "Se"
    INTROVERTED_INTUITION = "Ni"
    EXTRAVERTED_INTUITION = "Ne"


class MBTIType(Enum):
    """Myers-Briggs Type Indicator types."""
    INTJ = "INTJ"
    INTP = "INTP"
    ENTJ = "ENTJ"
    ENTP = "ENTP"
    INFJ = "INFJ"
    INFP = "INFP"
    ENFJ = "ENFJ"
    ENFP = "ENFP"
    ISTJ = "ISTJ"
    ISFJ = "ISFJ"
    ESTJ = "ESTJ"
    ESFJ = "ESFJ"
    ISTP = "ISTP"
    ISFP = "ISFP"
    ESTP = "ESTP"
    ESFP = "ESFP"


@dataclass
class JungianProfile:
    """
    Represents a Jungian psychological profile.
    """
    mbti_type: MBTIType
    dominant_function: JungianFunction
    auxiliary_function: JungianFunction
    tertiary_function: JungianFunction
    inferior_function: JungianFunction
    
    def get_function_stack(self) -> List[JungianFunction]:
        """Returns the ordered function stack."""
        return [
            self.dominant_function,
            self.auxiliary_function,
            self.tertiary_function,
            self.inferior_function,
        ]


class JungianMapper:
    """
    Maps between Team Alchemy archetypes and Jungian types.
    """
    
    def __init__(self):
        self.type_mappings = self._initialize_mappings()
        
    def _initialize_mappings(self) -> Dict[MBTIType, Dict[str, any]]:
        """Initialize MBTI type characteristic mappings."""
        return {
            MBTIType.INTJ: {
                "function_stack": [
                    JungianFunction.INTROVERTED_INTUITION,
                    JungianFunction.EXTRAVERTED_THINKING,
                    JungianFunction.INTROVERTED_FEELING,
                    JungianFunction.EXTRAVERTED_SENSING,
                ],
                "archetype_affinity": ["VISIONARY", "ANALYST"],
                "strengths": ["Strategic planning", "Systems thinking", "Independence"],
                "shadow": "May neglect emotional considerations",
            },
            MBTIType.ENFP: {
                "function_stack": [
                    JungianFunction.EXTRAVERTED_INTUITION,
                    JungianFunction.INTROVERTED_FEELING,
                    JungianFunction.EXTRAVERTED_THINKING,
                    JungianFunction.INTROVERTED_SENSING,
                ],
                "archetype_affinity": ["INNOVATOR", "HARMONIZER"],
                "strengths": ["Creativity", "Enthusiasm", "Understanding people"],
                "shadow": "May struggle with follow-through",
            },
            # Add more MBTI types
        }
        
    def get_jungian_profile(self, mbti_type: MBTIType) -> Optional[JungianProfile]:
        """
        Get the Jungian profile for an MBTI type.
        
        Args:
            mbti_type: The MBTI type
            
        Returns:
            JungianProfile or None if not found
        """
        mapping = self.type_mappings.get(mbti_type)
        if not mapping:
            return None
            
        functions = mapping["function_stack"]
        return JungianProfile(
            mbti_type=mbti_type,
            dominant_function=functions[0],
            auxiliary_function=functions[1],
            tertiary_function=functions[2],
            inferior_function=functions[3],
        )
        
    def get_shadow_functions(self, profile: JungianProfile) -> List[JungianFunction]:
        """
        Get the shadow function stack for a profile.
        
        Args:
            profile: The Jungian profile
            
        Returns:
            List of shadow functions
        """
        # Shadow functions are the opposite orientation of the primary stack
        shadow_map = {
            JungianFunction.INTROVERTED_THINKING: JungianFunction.EXTRAVERTED_THINKING,
            JungianFunction.EXTRAVERTED_THINKING: JungianFunction.INTROVERTED_THINKING,
            JungianFunction.INTROVERTED_FEELING: JungianFunction.EXTRAVERTED_FEELING,
            JungianFunction.EXTRAVERTED_FEELING: JungianFunction.INTROVERTED_FEELING,
            JungianFunction.INTROVERTED_SENSING: JungianFunction.EXTRAVERTED_SENSING,
            JungianFunction.EXTRAVERTED_SENSING: JungianFunction.INTROVERTED_SENSING,
            JungianFunction.INTROVERTED_INTUITION: JungianFunction.EXTRAVERTED_INTUITION,
            JungianFunction.EXTRAVERTED_INTUITION: JungianFunction.INTROVERTED_INTUITION,
        }
        
        return [shadow_map[func] for func in profile.get_function_stack()]
        
    def assess_type_compatibility(self, type1: MBTIType, type2: MBTIType) -> Dict[str, any]:
        """
        Assess compatibility between two MBTI types.
        
        Args:
            type1: First MBTI type
            type2: Second MBTI type
            
        Returns:
            Dictionary with compatibility analysis
        """
        profile1 = self.get_jungian_profile(type1)
        profile2 = self.get_jungian_profile(type2)
        
        if not profile1 or not profile2:
            return {"compatible": False, "reason": "Unknown types"}
            
        # Simple compatibility: check if auxiliary of one matches dominant of other
        complementary = (
            profile1.auxiliary_function == profile2.dominant_function or
            profile2.auxiliary_function == profile1.dominant_function
        )
        
        return {
            "compatible": complementary,
            "type1": type1.value,
            "type2": type2.value,
            "complementary_functions": complementary,
            "compatibility_score": 75 if complementary else 50,
        }
