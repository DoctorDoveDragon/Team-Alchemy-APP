"""
Team analysis example for Team Alchemy.
"""

from team_alchemy.core.archetypes.traits import TraitProfile
from team_alchemy.core.archetypes.classifier_logic import classify_team_composition
from team_alchemy.intelligence.optimizers.team_optimizer import TeamOptimizer, TeamMember


def main():
    """Demonstrate team analysis capabilities."""
    print("Team Alchemy - Team Analysis Example")
    print("=" * 50)
    
    # Create profiles for team members
    profiles = []
    
    # Member 1: Leader profile
    profile1 = TraitProfile()
    profile1.add_score("Extraversion", 85.0)
    profile1.add_score("Decisiveness", 90.0)
    profile1.add_score("Confidence", 88.0)
    profiles.append(profile1)
    
    # Member 2: Analyst profile
    profile2 = TraitProfile()
    profile2.add_score("Analytical Thinking", 92.0)
    profile2.add_score("Detail Orientation", 88.0)
    profile2.add_score("Logical Reasoning", 90.0)
    profiles.append(profile2)
    
    # Member 3: Harmonizer profile
    profile3 = TraitProfile()
    profile3.add_score("Empathy", 90.0)
    profile3.add_score("Communication", 85.0)
    profile3.add_score("Collaboration", 88.0)
    profiles.append(profile3)
    
    print(f"\nAnalyzing team with {len(profiles)} members...")
    
    # Analyze team composition
    composition = classify_team_composition(profiles)
    
    print(f"\nTeam Composition Analysis:")
    print(f"  Team Size: {composition['team_size']}")
    print(f"  Diversity Score: {composition['diversity_score']:.1f}%")
    print(f"\n  Archetype Distribution:")
    for archetype, count in composition['archetype_distribution'].items():
        print(f"    {archetype.value}: {count}")
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
