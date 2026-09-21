"""Canonical hashing for economic recipe objects.

``RULE_BEFORE_VALUES`` is only enforceable if the rule is addressable.  Every
recipe object in this package can serialise itself to a plain document and be
hashed, so a later numerical instantiation can be checked against the recipe
that was frozen before any candidate value was inspected.

The hash covers the *rule*, never an outcome. Callers that mix an outcome into
a recipe document are defeating the firewall, so :func:`recipe_hash` refuses
documents carrying keys reserved for realised results.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


#: Keys that may never appear anywhere inside a hashed recipe document. A recipe
#: that embeds a realised Form 4 outcome is no longer outcome-blind, and a recipe
#: that embeds the threshold it produces could be tuned by it
#: (``MEUE_RESULT_CANNOT_TUNE_ITS_OWN_MARGIN``).
FORBIDDEN_RECIPE_KEYS = frozenset({
    "realised_outcome", "realized_outcome", "form4_outcome", "outcome_sample",
    "delta_hat", "observed_delta", "meue_value", "beee_value",
    "d05_ceiling", "ceiling_value", "filing_count", "event_count_observed",
})


class RecipeNotOutcomeBlind(ValueError):
    """A recipe document embedded a result it is not allowed to see."""


def _walk(document: Any, path: str = "") -> None:
    if isinstance(document, dict):
        for key, value in document.items():
            if key in FORBIDDEN_RECIPE_KEYS:
                raise RecipeNotOutcomeBlind(
                    f"recipe document carries result-bearing key {key!r} at {path or '<root>'}")
            _walk(value, f"{path}.{key}" if path else str(key))
    elif isinstance(document, (list, tuple)):
        for index, value in enumerate(document):
            _walk(value, f"{path}[{index}]")


def canonical_json(document: Any) -> str:
    """Stable serialisation: sorted keys, no insignificant whitespace."""
    return json.dumps(document, sort_keys=True, separators=(",", ":"), default=str)


def recipe_hash(document: Any) -> str:
    """Hash a recipe document after proving it carries no realised result."""
    _walk(document)
    payload = canonical_json(document).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()
