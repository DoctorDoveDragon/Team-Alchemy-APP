"""
Team Alchemy - A comprehensive team dynamics and psychological assessment platform.
"""

__version__ = "0.1.0"
__author__ = "Team Alchemy Development Team"

from team_alchemy.core.archetypes import definitions, traits
from team_alchemy.core.assessment import models, calculator

__all__ = [
    "__version__",
    "definitions",
    "traits",
    "models",
    "calculator",
]
