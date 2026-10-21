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
import re

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

_OUTCOME_VALUE_KEYS = {
    "outcome_payload", "outcome_values", "future_return", "future_returns",
    "realized_return", "realized_returns", "realized_pnl", "pnl", "returns",
    "observed_effect", "test_statistic", "p_value", "sharpe", "hit_rate",
    "win_rate", "evaluation_result",
}
_CLOSED_FALSE_KEYS = {"outcome_opened", "outcome_accessed", "outcome_gate_opened", "observation_started"}
_CLOSED_ZERO_KEYS = {"future_outcomes_consumed", "outcomes_consumed"}
_SENTINEL_RESULT_KEYS = {"result", "economic_result"}
_ROLE_KEYS = {"role", "column_role", "dataset_role", "field_role"}
_LINEAGE_KEYS = {"alias_of", "derived_from", "lineage", "sources", "source_columns", "input_columns"}
_OUTCOME_BOOLEAN_KEYS = {"contains_outcome", "outcome_derived", "derived_from_outcome", "contains_future_outcomes"}
_OUTCOME_ID_RE = re.compile(r"(?:^|[_\-.])(outcome|future[_\-.]?return|realized[_\-.]?(?:return|pnl)|response|target)(?:$|[_\-.])", re.I)


def _path(parent: str, key: Any) -> str:
    return f"{parent}.{key}" if parent else str(key)


def _lineage_mentions_outcome(value: Any) -> bool:
    if isinstance(value, str):
        return bool(_OUTCOME_ID_RE.search(value.strip()))
    if isinstance(value, (list, tuple, set)):
        return any(_lineage_mentions_outcome(item) for item in value)
    if isinstance(value, Mapping):
        return any(_lineage_mentions_outcome(k) or _lineage_mentions_outcome(v) for k, v in value.items())
    return False


def assert_pre_outcome_payload(value: Any, *, path: str = "$") -> None:
    """Recursively reject materially plausible outcome leakage.

    Definitions such as ``outcome_definition`` remain legal, but data-bearing
    outcome values, outcome-labelled datasets/columns, outcome-derived lineage,
    opened state, relaxed authority, and non-finite values are rejected.
    """
    if isinstance(value, Mapping):
        for role_key in _ROLE_KEYS:
            role = value.get(role_key)
            if isinstance(role, str) and role.upper() == "OUTCOME":
                raise OutcomeFirewallError(f"OUTCOME_ROLE_FORBIDDEN:{path}.{role_key}")
        for marker in _OUTCOME_BOOLEAN_KEYS:
            if value.get(marker) is True:
                raise OutcomeFirewallError(f"OUTCOME_MARKER_FORBIDDEN:{path}.{marker}")

        # A derived field with no lineage cannot prove that it is formation-only.
        role = value.get("role") or value.get("column_role") or value.get("field_role")
        if isinstance(role, str) and role.upper() == "DERIVED":
            if not any(key in value for key in _LINEAGE_KEYS):
                raise OutcomeFirewallError(f"UNKNOWN_DERIVED_LINEAGE:{path}")

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
                raise OutcomeFirewallError(f"OUTCOME_VALUE_FORBIDDEN:{current}")
            if lowered in _OUTCOME_BOOLEAN_KEYS and item not in (False, None):
                raise OutcomeFirewallError(f"OUTCOME_MARKER_FORBIDDEN:{current}")
            if lowered in _LINEAGE_KEYS and _lineage_mentions_outcome(item):
                raise OutcomeFirewallError(f"OUTCOME_LINEAGE_FORBIDDEN:{current}")
            assert_pre_outcome_payload(item, path=current)
        return

    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            assert_pre_outcome_payload(item, path=f"{path}[{index}]")
        return

    if isinstance(value, float) and not isfinite(value):
        raise OutcomeFirewallError(f"NONFINITE_PRE_OUTCOME_VALUE:{path}")


@dataclass(frozen=True)
class LegacyOutcomeGate:
    """Opaque compatibility object that intentionally confers no authority."""
    token: str = "SEALED_BY_AUTHORITY"


def read_outcomes(*_args: Any, **_kwargs: Any) -> Any:
    raise OutcomeFirewallError("SEALED_BY_AUTHORITY:OUTCOME_ACCESS_FORBIDDEN")


def hitl_outcome_gate(*_args: Any, **_kwargs: Any) -> LegacyOutcomeGate:
    return LegacyOutcomeGate()
