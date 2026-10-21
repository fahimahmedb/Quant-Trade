"""Compatibility re-export for the authority-sealed historical outcome firewall."""
from research.research_os.expansion.experiment_outcome_firewall import (
    LegacyOutcomeGate,
    OutcomeFirewallError,
    assert_pre_outcome_payload,
    hitl_outcome_gate,
    read_outcomes,
)

__all__ = [
    "LegacyOutcomeGate", "OutcomeFirewallError", "assert_pre_outcome_payload",
    "hitl_outcome_gate", "read_outcomes",
]
