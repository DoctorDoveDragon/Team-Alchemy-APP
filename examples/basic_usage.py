"""
Basic usage example for Team Alchemy.
"""

from team_alchemy.core.archetypes.traits import TraitProfile
from team_alchemy.core.archetypes.classifier_logic import ArchetypeClassifier


def main():
    """Demonstrate basic usage of Team Alchemy."""
    print("Team Alchemy - Basic Usage Example")
    print("=" * 50)
    
    # Create a trait profile
    profile = TraitProfile()
    profile.add_score("Extraversion", 75.0)
    profile.add_score("Analytical Thinking", 85.0)
    profile.add_score("Decisiveness", 80.0)
    
    print("\nTrait Profile Created:")
    for trait, score in profile.get_all_scores().items():
        print(f"  {trait}: {score}")
    
    # Classify the profile
    classifier = ArchetypeClassifier()
    result = classifier.classify(profile)
    
    print(f"\nClassification Result:")
    print(f"  Primary Archetype: {result.primary_archetype.value}")
    if result.secondary_archetype:
        print(f"  Secondary Archetype: {result.secondary_archetype.value}")
    print(f"  Confidence: {result.confidence:.2%}")
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
