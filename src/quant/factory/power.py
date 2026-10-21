"""Compatibility re-export for historical Factory power imports."""
from research.research_os.expansion.experiment_power import (
    PowerDeclaration,
    PowerDeclarationError,
    PowerStatus,
    derive_normal_approximation,
    power_from_mapping,
    unknown_power,
)

__all__ = [
    "PowerDeclaration", "PowerDeclarationError", "PowerStatus",
    "derive_normal_approximation", "power_from_mapping", "unknown_power",
]
