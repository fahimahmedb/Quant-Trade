"""Research Factory: continuous discovery, falsification and strategy lifecycle."""

from .signals import StrategySpec, cross_sectional_scores, target_weights
from .strategies import StrategyDefinition, StrategyRegistry

__all__ = ["StrategyDefinition", "StrategyRegistry", "StrategySpec",
           "cross_sectional_scores", "target_weights"]
