"""Compatibility re-export for historical Factory geometry imports."""
from research.research_os.expansion.experiment_geometry import (
    GeometryDeclaration,
    GeometryDeclarationError,
    GeometryStatus,
    geometry_from_mapping,
    unknown_geometry,
)

__all__ = [
    "GeometryDeclaration", "GeometryDeclarationError", "GeometryStatus",
    "geometry_from_mapping", "unknown_geometry",
]
