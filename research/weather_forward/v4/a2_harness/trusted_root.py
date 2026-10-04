"""Static execution-policy trust anchor for Weather V4 A2.

The current Owner governance state provides no permissive execution-policy
root.  This module intentionally exposes no caller-supplied setter or
constructor path for the active root.  A future permissive root requires a
separate Owner authority and a source-level change under that authority.
"""

from __future__ import annotations

from typing import Final

from .contract import TrustedExecutionPolicyRoot


CURRENT_OWNER_EXECUTION_POLICY_AUTHORITY: Final[None] = None
CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT: Final[None] = None


def get_trusted_execution_policy_root() -> TrustedExecutionPolicyRoot | None:
    """Return the independently anchored root; currently fail-closed NONE."""
    return None
