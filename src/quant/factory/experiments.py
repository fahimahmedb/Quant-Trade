"""Compatibility surface for historical `quant.factory.experiments` imports.

Canonical Wave-1 experiment-registry law now lives with the current Research Core
under `research.research_os.expansion.experiment_registry`. Keeping this module as
a re-export avoids a second implementation and preserves historical import paths.
"""
from research.research_os.expansion.experiment_registry import (
    ExperimentLifecycle,
    ExperimentRegistryEntry,
    ExperimentRegistryError,
    assert_registry_matches,
    bind_execution_plan,
    bind_receipt,
    bind_replay,
    canonical_hash,
    create_registry_entry,
)

__all__ = [
    "ExperimentLifecycle", "ExperimentRegistryEntry", "ExperimentRegistryError",
    "assert_registry_matches", "bind_execution_plan", "bind_receipt", "bind_replay",
    "canonical_hash", "create_registry_entry",
]
