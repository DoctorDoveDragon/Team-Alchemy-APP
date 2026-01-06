"""
Data transformation utilities.
"""

from typing import List, Dict, Any, Callable
import json


def normalize_range(
    value: float,
    old_min: float,
    old_max: float,
    new_min: float = 0,
    new_max: float = 100
) -> float:
    """
    Transform value from one range to another.
    
    Args:
        value: Value to transform
        old_min: Original range minimum
        old_max: Original range maximum
        new_min: New range minimum
        new_max: New range maximum
        
    Returns:
        Transformed value
    """
    if old_max == old_min:
        return new_min
        
    normalized = (value - old_min) / (old_max - old_min)
    return new_min + (normalized * (new_max - new_min))


def transform_dict_keys(
    data: Dict[str, Any],
    transformer: Callable[[str], str]
) -> Dict[str, Any]:
    """
    Transform dictionary keys using a function.
    
    Args:
        data: Dictionary to transform
        transformer: Function to transform keys
        
    Returns:
        Dictionary with transformed keys
    """
    return {transformer(k): v for k, v in data.items()}


def flatten_nested_dict(
    data: Dict[str, Any],
    parent_key: str = '',
    separator: str = '.'
) -> Dict[str, Any]:
    """
    Flatten nested dictionary.
    
    Args:
        data: Nested dictionary
        parent_key: Parent key for recursion
        separator: Separator for nested keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    
    for k, v in data.items():
        new_key = f"{parent_key}{separator}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_nested_dict(v, new_key, separator).items())
        else:
            items.append((new_key, v))
            
    return dict(items)


def batch_transform(
    items: List[Any],
    transformer: Callable[[Any], Any]
) -> List[Any]:
    """
    Apply transformation to list of items.
    
    Args:
        items: Items to transform
        transformer: Transformation function
        
    Returns:
        Transformed items
    """
    return [transformer(item) for item in items]


def filter_by_threshold(
    data: Dict[str, float],
    threshold: float,
    above: bool = True
) -> Dict[str, float]:
    """
    Filter dictionary by value threshold.
    
    Args:
        data: Dictionary with numeric values
        threshold: Threshold value
        above: If True, keep values above threshold; if False, keep below
        
    Returns:
        Filtered dictionary
    """
    if above:
        return {k: v for k, v in data.items() if v >= threshold}
    else:
        return {k: v for k, v in data.items() if v <= threshold}


def aggregate_by_category(
    items: List[Dict[str, Any]],
    category_key: str,
    value_key: str,
    aggregation: str = "sum"
) -> Dict[str, float]:
    """
    Aggregate values by category.
    
    Args:
        items: List of items to aggregate
        category_key: Key for category grouping
        value_key: Key for value to aggregate
        aggregation: Type of aggregation (sum, avg, count)
        
    Returns:
        Aggregated values by category
    """
    categories: Dict[str, List[float]] = {}
    
    for item in items:
        category = item.get(category_key)
        value = item.get(value_key)
        
        if category is not None and value is not None:
            if category not in categories:
                categories[category] = []
            categories[category].append(float(value))
            
    # Apply aggregation
    if aggregation == "sum":
        return {cat: sum(vals) for cat, vals in categories.items()}
    elif aggregation == "avg":
        return {cat: sum(vals) / len(vals) for cat, vals in categories.items()}
    elif aggregation == "count":
        return {cat: len(vals) for cat, vals in categories.items()}
    else:
        return {}


def to_json_serializable(data: Any) -> Any:
    """
    Convert data to JSON-serializable format.
    
    Args:
        data: Data to convert
        
    Returns:
        JSON-serializable data
    """
    if isinstance(data, dict):
        return {k: to_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [to_json_serializable(item) for item in data]
    elif hasattr(data, '__dict__'):
        return to_json_serializable(data.__dict__)
    else:
        return data
