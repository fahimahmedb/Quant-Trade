"""Fail-closed wrapper for divergent Policy C external backend calls."""
from __future__ import annotations

from typing import Any, Mapping

from .multi_source_ideation import ModelBackend, POLICIES, policy_c, raw_artifact, validate_policy_input


def safe_policy_c(*, snapshot: Mapping[str, Any], backend: ModelBackend | None, mandate: Mapping[str, Any]) -> tuple[dict, dict | None]:
    """Convert external backend exceptions to explicit SOURCE_FAILED; never fallback."""
    validate_policy_input(snapshot)
    try:
        return policy_c(snapshot=snapshot, backend=backend, mandate=mandate)
    except (ValueError, TypeError):
        raise
    except Exception as exc:  # external runtime boundary: fail closed, no provider fallback
        return raw_artifact(
            policy_kind=POLICIES[2], status="SOURCE_FAILED",
            context_snapshot_hash=snapshot["context_snapshot_hash"],
            reason="EXTERNAL_BACKEND_FAILURE:" + type(exc).__name__,
        ), None
