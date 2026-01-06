"""
Metrics calculation utilities.
"""

from typing import List, Dict, Any
import statistics


def calculate_mean(values: List[float]) -> float:
    """Calculate mean of values."""
    return statistics.mean(values) if values else 0.0


def calculate_std_dev(values: List[float]) -> float:
    """Calculate standard deviation."""
    return statistics.stdev(values) if len(values) > 1 else 0.0


def calculate_percentile(values: List[float], percentile: int) -> float:
    """
    Calculate percentile value.
    
    Args:
        values: List of values
        percentile: Percentile (0-100)
        
    Returns:
        Percentile value
    """
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = int(len(sorted_values) * percentile / 100)
    return sorted_values[min(index, len(sorted_values) - 1)]


def normalize_score(score: float, min_val: float = 0, max_val: float = 100) -> float:
    """
    Normalize score to 0-1 range.
    
    Args:
        score: Score to normalize
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Normalized score (0-1)
    """
    if max_val == min_val:
        return 0.5
    return (score - min_val) / (max_val - min_val)


def calculate_correlation(values1: List[float], values2: List[float]) -> float:
    """
    Calculate Pearson correlation coefficient.
    
    Args:
        values1: First set of values
        values2: Second set of values
        
    Returns:
        Correlation coefficient (-1 to 1)
    """
    if len(values1) != len(values2) or len(values1) < 2:
        return 0.0
        
    try:
        return statistics.correlation(values1, values2)
    except statistics.StatisticsError:
        return 0.0


def calculate_diversity_index(distribution: Dict[Any, int]) -> float:
    """
    Calculate diversity index (Simpson's Index).
    
    Args:
        distribution: Distribution of categories
        
    Returns:
        Diversity index (0-1, higher is more diverse)
    """
    if not distribution:
        return 0.0
        
    total = sum(distribution.values())
    if total == 0:
        return 0.0
        
    # Simpson's Index: 1 - sum((n/N)^2)
    simpson = 1 - sum((count / total) ** 2 for count in distribution.values())
    return simpson


def calculate_team_metrics(individual_scores: List[float]) -> Dict[str, float]:
    """
    Calculate comprehensive team metrics.
    
    Args:
        individual_scores: Individual team member scores
        
    Returns:
        Dictionary of team metrics
    """
    if not individual_scores:
        return {
            "mean": 0.0,
            "median": 0.0,
            "std_dev": 0.0,
            "min": 0.0,
            "max": 0.0,
            "range": 0.0,
        }
        
    return {
        "mean": calculate_mean(individual_scores),
        "median": statistics.median(individual_scores),
        "std_dev": calculate_std_dev(individual_scores),
        "min": min(individual_scores),
        "max": max(individual_scores),
        "range": max(individual_scores) - min(individual_scores),
        "p25": calculate_percentile(individual_scores, 25),
        "p75": calculate_percentile(individual_scores, 75),
    }
