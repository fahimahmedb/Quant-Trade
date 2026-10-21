"""Fail-closed pre-outcome membrane for experiment infrastructure.

This is an adaptation of the historical Factory outcome firewall.  The historical
rail could open outcomes after a Blue-Team capability token.  Wave-1 deliberately
removes that opening: campaign authority keeps outcome access closed, and this
module only validates that pre-outcome artifacts remain outcome blind.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Mapping

NOT_OBSERVED = "NOT_OBSERVED"
UNKNOWN = "UNKNOWN"


class OutcomeFirewallError(PermissionError):
    """Raised when outcome-bearing material crosses the pre-outcome membrane."""


AUTHORITY_FIELDS = (
    "economic_experiment_authorized",
    "prospective_observation_authorized",
    "real_capital_authorized",
    "live_trading_authorized",
)

# Exact keys only.  Names such as ``outcome_definition`` and decision-map labels
# are legitimate preregistration material and must not be confused with outcomes.
_OUTCOME_VALUE_KEYS = {
    "outcome_payload",
    "outcome_values",
    "future_return",
    "future_returns",
    "realized_return",
    "realized_returns",
    "realized_pnl",
    "pnl",
    "returns",
    "observed_effect",
    "test_statistic",
    "p_value",
    "sharpe",
    "hit_rate",
    "win_rate",
    "evaluation_result",
}

_CLOSED_FALSE_KEYS = {
    "outcome_opened",
    "outcome_accessed",
    "outcome_gate_opened",
    "observation_started",
}

_CLOSED_ZERO_KEYS = {"future_outcomes_consumed", "outcomes_consumed"}
_SENTINEL_RESULT_KEYS = {"result", "economic_result"}


def _path(parent: str, key: Any) -> str:
    return f"{parent}.{key}" if parent else str(key)


def assert_pre_outcome_payload(value: Any, *, path: str = "$") -> None:
    """Recursively reject materially plausible outcome leakage.

    The rule is intentionally value-aware.  A frozen protocol may define an
    ``outcome_definition`` or decision map; it may not carry realized outcome
    vectors, result metrics, an opened gate, or relaxed authority flags.
    """
    if isinstance(value, Mapping):
        role = value.get("role")
        column_role = value.get("column_role")
        if isinstance(role, str) and role.upper() == "OUTCOME":
            raise OutcomeFirewallError(f"OUTCOME_ROLE_FORBIDDEN:{path}.role")
        if isinstance(column_role, str) and column_role.upper() == "OUTCOME":
            raise OutcomeFirewallError(f"OUTCOME_ROLE_FORBIDDEN:{path}.column_role")

        for raw_key, item in value.items():
            key = str(raw_key)
            lowered = key.lower()
            current = _path(path, key)
            if lowered in AUTHORITY_FIELDS and item is not False:
                raise OutcomeFirewallError(f"AUTHORITY_MUST_REMAIN_FALSE:{current}")
            if lowered in _CLOSED_FALSE_KEYS and item is not False:
                raise OutcomeFirewallError(f"OUTCOME_STATE_MUST_REMAIN_CLOSED:{current}")
            if lowered in _CLOSED_ZERO_KEYS and (isinstance(item, bool) or item != 0):
                raise OutcomeFirewallError(f"OUTCOME_COUNT_MUST_REMAIN_ZERO:{current}")
            if lowered in _SENTINEL_RESULT_KEYS and item not in (None, NOT_OBSERVED, UNKNOWN):
                raise OutcomeFirewallError(f"OBSERVED_RESULT_FORBIDDEN:{current}")
            if lowered == "outcome_digest" and item not in (None, ""):
                raise OutcomeFirewallError(f"OUTCOME_DIGEST_FORBIDDEN:{current}")
            if lowered in _OUTCOME_VALUE_KEYS:
                # Even zero/empty realized values encode outcome access.  Definitions
                # use different field names and remain admissible.
                raise OutcomeFirewallError(f"OUTCOME_VALUE_FORBIDDEN:{current}")
            assert_pre_outcome_payload(item, path=current)
        return

    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            assert_pre_outcome_payload(item, path=f"{path}[{index}]")
        return

    # Scalars are permitted when their containing field is admissible.  Reject
    # non-finite floats because NaN/Infinity can otherwise evade canonical hashes.
    if isinstance(value, float) and not isfinite(value):
        raise OutcomeFirewallError(f"NONFINITE_PRE_OUTCOME_VALUE:{path}")


@dataclass(frozen=True)
class LegacyOutcomeGate:
    """Opaque compatibility object that intentionally confers no authority."""

    token: str = "SEALED_BY_AUTHORITY"


def read_outcomes(*_args: Any, **_kwargs: Any) -> Any:
    """Historical API kept only as an explicit fail-closed compatibility surface."""
    raise OutcomeFirewallError("SEALED_BY_AUTHORITY:OUTCOME_ACCESS_FORBIDDEN")


def hitl_outcome_gate(*_args: Any, **_kwargs: Any) -> LegacyOutcomeGate:
    """Never reads environment variables and never opens the historical gate."""
    return LegacyOutcomeGate()
