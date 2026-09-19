"""Capital-readiness V3. Five gates, and none of them authorises real capital.

Readiness is not a score to be argued up. Each gate is a separate question with
its own evidence, and the framework reports the weakest one rather than an
average, because an average lets strong statistics cover for absent capacity or
unhandled operational failure.

The terminal state this module can reach is ``PAPER_SHADOW_READY``. Real capital
is not a state the system may assign itself: it requires the project owner, and
``CLAUDE.md`` is explicit that no engineering artifact grants that authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

from ..economics.decision import PAPER_SHADOW_ONLY


GATE_SATISFIED = "SATISFIED"
GATE_UNSATISFIED = "UNSATISFIED"
GATE_UNRESOLVED = "UNRESOLVED"

PAPER_SHADOW_READY = "PAPER_SHADOW_READY"
NOT_READY = "NOT_READY"

#: The five gates, in the order a reader should think about them.
GATE_STATISTICAL = "STATISTICAL_EVIDENCE"
GATE_ECONOMIC = "ECONOMIC_SUFFICIENCY_AFTER_FRICTIONS"
GATE_CAPACITY = "CAPACITY_HEADROOM"
GATE_OPERATIONAL = "OPERATIONAL_FAILURE_HANDLING"
GATE_MONITORING = "POST_DEPLOYMENT_MONITORING"

GATES = (GATE_STATISTICAL, GATE_ECONOMIC, GATE_CAPACITY, GATE_OPERATIONAL, GATE_MONITORING)


@dataclass(frozen=True)
class Gate:
    """One readiness gate with the evidence behind its state."""

    name: str
    state: str
    evidence: str = ""
    #: Identifier of the artifact the evidence lives in, for audit.
    evidence_reference: str = ""

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.name not in GATES:
            problems.append(f"{self.name}: GATE_NOT_DECLARED")
        if self.state not in (GATE_SATISFIED, GATE_UNSATISFIED, GATE_UNRESOLVED):
            problems.append(f"{self.name}: GATE_STATE_NOT_RECOGNISED")
        if self.state == GATE_SATISFIED and not self.evidence_reference:
            problems.append(f"{self.name}: SATISFIED_GATE_WITHOUT_EVIDENCE_REFERENCE")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReadinessVerdict:
    subject: str
    state: str
    gates: tuple[Gate, ...]
    #: The gate a reader should look at first: the weakest one.
    binding_gate: str | None
    capital_authority: str = PAPER_SHADOW_ONLY
    violations: tuple[str, ...] = ()

    @property
    def ready_for_paper_shadow(self) -> bool:
        return self.state == PAPER_SHADOW_READY

    def to_dict(self) -> dict[str, Any]:
        return {"subject": self.subject, "state": self.state,
                "gates": [gate.to_dict() for gate in self.gates],
                "binding_gate": self.binding_gate,
                "capital_authority": self.capital_authority,
                "real_capital_authorized": False,
                "violations": list(self.violations)}


def assess_readiness(subject: str, gates: Iterable[Gate]) -> ReadinessVerdict:
    """Report the weakest gate. Missing gates are missing, not passed."""
    supplied = tuple(gates)
    problems: list[str] = []
    for gate in supplied:
        problems.extend(gate.violations())
    by_name = {gate.name: gate for gate in supplied}
    duplicates = len(supplied) != len(by_name)
    if duplicates:
        problems.append("DUPLICATE_GATE_DECLARED")
    missing = [name for name in GATES if name not in by_name]
    for name in missing:
        problems.append(f"{name}: GATE_NOT_ASSESSED")

    unsatisfied = [name for name in GATES
                   if name in by_name and by_name[name].state == GATE_UNSATISFIED]
    unresolved = [name for name in GATES
                  if name in by_name and by_name[name].state == GATE_UNRESOLVED]
    binding = None
    if missing:
        binding = missing[0]
    elif unsatisfied:
        binding = unsatisfied[0]
    elif unresolved:
        binding = unresolved[0]

    state = (PAPER_SHADOW_READY
             if not missing and not unsatisfied and not unresolved and not problems
             else NOT_READY)
    return ReadinessVerdict(subject, state, supplied, binding,
                            violations=tuple(sorted(set(problems))))
