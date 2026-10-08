"""Static execution-policy trust anchor for Weather V4 A2.

This module carries the single permissive execution-policy root for the
documentary-integration route D2. The root binds the Owner execution authority
E (commit 6e0320f15d48a924cef9507af5641e47de9fe938), the historical
construction authority, the harness component and logical version, and the
final frozen policy identity. It exposes no caller-supplied setter, no
environment or configuration override and no permissive fallback. Its
existence in source is not an activation: the Owner execution authority takes
effect only under its own conditions and a separate Owner activation decision.
"""

from __future__ import annotations

from typing import Final

from .contract import TrustedExecutionPolicyRoot


CURRENT_OWNER_EXECUTION_POLICY_AUTHORITY: Final[str] = (
    "6e0320f15d48a924cef9507af5641e47de9fe938"
)
CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT: Final[TrustedExecutionPolicyRoot] = (
    TrustedExecutionPolicyRoot(
        execution_policy_authority_sha="6e0320f15d48a924cef9507af5641e47de9fe938",
        expected_construction_authority_sha="37e3b25f17a7c5d3b3bc8d37df730aa988585b6c",
        expected_harness_identity="research/weather_forward/v4/a2_harness",
        expected_harness_version_or_commit_identity="weather-v4-a2-doc-integration-v1",
        expected_policy_identity=(
            "sha256:2f761da560e2473bdcecc03a20a088b5ec59c112fb523ab2b0bf8a6ecab3de60"
        ),
    )
)


def get_trusted_execution_policy_root() -> TrustedExecutionPolicyRoot | None:
    """Return the independently anchored root defined in this source file."""
    return CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT
