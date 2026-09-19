"""Post-deployment monitoring: decay, drift, and retirement declared in advance.

A strategy that stops working is the expected case, not the surprise. What makes
decay expensive is deciding *afterwards* what would have counted as decay, because
by then the decision is a negotiation with a losing position.

So a :class:`RetirementRule` carries the instant it was declared, and monitoring
refuses a rule declared at or after the first observation window it is applied to.
The monitor then reports consecutive breaches against that rule and nothing else:
no discretionary override lives here.

``A state enum is not a capability``: this module reports what the declared rule
says about the windows it was given. It does not claim to manage decay.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Sequence


MONITOR_WITHIN_TOLERANCE = "WITHIN_DECLARED_TOLERANCE"
MONITOR_DRIFTING = "DRIFTING_BUT_NOT_RETIRED"
MONITOR_RETIRE = "RETIREMENT_TRIGGERED"
MONITOR_UNRESOLVED = "MONITORING_UNRESOLVED"

RULE_DECLARED_TOO_LATE = "RETIREMENT_RULE_MUST_BE_DECLARED_BEFORE_MONITORING"


def _instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class RetirementRule:
    """When a lane stops being run, decided before it is run."""

    rule_id: str
    declared_at: str
    #: Net effect, in the same coordinate as the confirmed expectation, below
    #: which a window counts as a breach.
    breach_floor: float
    #: Consecutive breaching windows that trigger retirement.
    consecutive_breaches: int
    #: Realised one-way friction above which capacity is considered eroded, bps.
    friction_drift_limit_bps: float | None = None

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.consecutive_breaches < 1:
            problems.append(f"{self.rule_id}: CONSECUTIVE_BREACHES_MUST_BE_POSITIVE")
        try:
            _instant(self.declared_at)
        except ValueError:
            problems.append(f"{self.rule_id}: DECLARED_AT_NOT_ISO8601")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MonitoringWindow:
    """One realised forward window of a deployed lane."""

    window_id: str
    observed_at: str
    #: Realised net effect on the confirmed coordinate.
    realised_net_effect: float
    #: Realised one-way friction actually paid, bps of notional.
    realised_friction_bps: float | None = None
    #: Exposure actually deployed in the window, account currency.
    deployed_exposure: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MonitoringVerdict:
    state: str
    rule_id: str
    #: Longest run of consecutive breaches seen, ending at the latest window.
    trailing_breaches: int
    breached_windows: tuple[str, ...]
    friction_drift: float | None = None
    violations: tuple[str, ...] = ()

    @property
    def retire(self) -> bool:
        return self.state == MONITOR_RETIRE

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def monitor(rule: RetirementRule, windows: Sequence[MonitoringWindow],
            expected_friction_bps: float | None = None) -> MonitoringVerdict:
    """Apply a pre-declared retirement rule to observed forward windows."""
    problems = rule.violations()
    ordered = sorted(windows, key=lambda window: window.observed_at)
    if not ordered:
        return MonitoringVerdict(MONITOR_UNRESOLVED, rule.rule_id, 0, (),
                                 violations=tuple(problems + ["NO_MONITORING_WINDOWS"]))
    try:
        declared = _instant(rule.declared_at)
        first_observation = _instant(ordered[0].observed_at)
    except ValueError:
        return MonitoringVerdict(MONITOR_UNRESOLVED, rule.rule_id, 0, (),
                                 violations=tuple(problems + ["TIMESTAMP_NOT_ISO8601"]))
    if declared >= first_observation:
        problems.append(RULE_DECLARED_TOO_LATE)
    if problems:
        return MonitoringVerdict(MONITOR_UNRESOLVED, rule.rule_id, 0, (),
                                 violations=tuple(sorted(set(problems))))

    breached = tuple(window.window_id for window in ordered
                     if window.realised_net_effect < rule.breach_floor)
    trailing = 0
    for window in reversed(ordered):
        if window.realised_net_effect < rule.breach_floor:
            trailing += 1
        else:
            break

    friction_drift = None
    if expected_friction_bps is not None:
        realised = [window.realised_friction_bps for window in ordered
                    if window.realised_friction_bps is not None]
        if realised:
            friction_drift = sum(realised) / len(realised) - expected_friction_bps

    state = MONITOR_WITHIN_TOLERANCE
    if trailing >= rule.consecutive_breaches:
        state = MONITOR_RETIRE
    elif breached or (rule.friction_drift_limit_bps is not None
                      and friction_drift is not None
                      and friction_drift > rule.friction_drift_limit_bps):
        state = MONITOR_DRIFTING
    if (rule.friction_drift_limit_bps is not None and friction_drift is not None
            and friction_drift > rule.friction_drift_limit_bps
            and state == MONITOR_WITHIN_TOLERANCE):
        state = MONITOR_DRIFTING
    return MonitoringVerdict(state, rule.rule_id, trailing, breached, friction_drift)
