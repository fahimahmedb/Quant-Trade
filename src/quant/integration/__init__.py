"""The Research -> Economic admission boundary.

Frozen topology (``governance/BLUE_FIRST_VERTICAL_ONE_BIG_BUILD_FROZEN_SPEC_2026-09-21.md``
section 4):

    ForwardObservation -> ResearchTicket -> ScientificEffectArtifact ->
    AssessmentRecord -> VALIDATED -> SHADOW admission -> OpportunityTicket -> ...

``forward_adapter`` scopes forward evidence identity to exactly the evidence a
``quant.science.effect.ScientificEffectArtifact`` consumed. ``econ_bridge`` runs
that identity through ``quant.economics.decision.economic_gate`` and the durable
``quant.economics.journal.EconomicAssessmentJournal``, and is the only place
allowed to transition a strategy ``VALIDATED -> SHADOW``.

This package does not create a second scheduler, sizing authority, execution
authority or ticket family; it only sits between ``quant.factory.workers`` and
``quant.desk.desk.CapitalDesk.actionable()`` selection.
"""

from .econ_bridge import ADMITTED, REFUSED, AdmissionOutcome, assess_and_admit
from .forward_adapter import ForwardEvidenceIdentity, classify_effect_refusal

__all__ = [
    "ADMITTED",
    "REFUSED",
    "AdmissionOutcome",
    "assess_and_admit",
    "ForwardEvidenceIdentity",
    "classify_effect_refusal",
]
