"""
Unit tests for scoring functionality.
"""

import pytest
from team_alchemy.core.scoring.composite_scorer import CompositeScorer


def test_composite_scorer_initialization():
    """Test composite scorer initialization."""
    scorer = CompositeScorer()
    
    assert scorer is not None
    assert len(scorer.dimension_weights) > 0


def test_calculate_composite_score():
    """Test composite score calculation."""
    scorer = CompositeScorer()
    
    dimension_scores = {
        "personality": 75.0,
        "skills": 80.0,
        "values": 70.0,
    }
    
    composite = scorer.calculate_composite(dimension_scores)
    
    assert 0 <= composite <= 100
    assert composite > 0  # Should have a positive score


def test_calculate_team_score():
    """Test team score calculation."""
    scorer = CompositeScorer()
    
    individual_scores = [75.0, 80.0, 70.0, 85.0, 78.0]
    team_dynamics = 72.0
    
    result = scorer.calculate_team_score(individual_scores, team_dynamics)
    
    assert "team_score" in result
    assert "individual_average" in result
    assert "variance" in result
    assert 0 <= result["team_score"] <= 100


def test_empty_scores():
    """Test handling of empty scores."""
    scorer = CompositeScorer()
    
    composite = scorer.calculate_composite({})
    assert composite == 0.0
    
    team_result = scorer.calculate_team_score([], 0)
    assert team_result["team_score"] == 0.0


def test_custom_weights():
    """Test custom dimension weights."""
    custom_weights = {
        "personality": 2.0,
        "skills": 1.0,
    }
    
    scorer = CompositeScorer(dimension_weights=custom_weights)
    
    dimension_scores = {
        "personality": 50.0,
        "skills": 50.0,
    }
    
    # With custom weights, personality should have more impact
    composite = scorer.calculate_composite(dimension_scores)
    assert composite == 50.0  # Equal scores should yield 50
