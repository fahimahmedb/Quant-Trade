"""Bridges the forward ledger into Wave 1's admissibility / UseLedger machinery.

``admissibility.py`` already enforces every rule this mission needs for
forward confirmation: a historical dataset can never claim it
(``HISTORICAL_EVIDENCE_IS_NOT_INDEPENDENT_CONFIRMATION``), a pre-outcome seal
is required, and a version already used for ``EXPLORATORY_FIT`` cannot also
serve ``VALIDATION``. Nothing here changes, weakens or duplicates any of those
rules -- this module only builds the registry-record-shaped view of a
``ForwardRecorder`` that ``evaluate_admissibility`` already knows how to
judge, so the composition is proven by test rather than assumed. This is what
the mission means by "integrate with the Wave 1 UseLedger", not a second
admissibility engine.
"""

from __future__ import annotations

from typing import Any

from .admissibility import (ADMISSIBLE, CONSUMING_USES, INADMISSIBLE,
                            USE_FORWARD_CONFIRMATION, AdmissibilityVerdict, EvidenceUse,
                            UseLedger, evaluate_admissibility)
from .forward_recorder import TIME_AUTHORITY_UNATTESTED_LOCAL_CLOCK, ForwardRecorder

#: Additional to admissibility.py's own rules, not a replacement for any of
#: them: evaluate_admissibility's FORWARD_CONFIRMATION branch checks only
#: timing (recorded before the freeze?) and the pre-outcome seal -- it does
#: not itself cross-check the UseLedger's fit/validation history for the same
#: version, so a version already spent on EXPLORATORY_FIT or VALIDATION could
#: otherwise separately pass forward-confirmation's own timing check and be
#: laundered as independent evidence. Section 9 names exactly this failure
#: mode ("une version deja utilisee pour fit ne devient jamais forward
#: confirmation"), so this module closes it here, layered on top of the
#: untouched Wave 1 primitive, rather than editing admissibility.py itself.
FORWARD_CONFIRMATION_VERSION_ALREADY_CONSUMED = (
    "FORWARD_CONFIRMATION_VERSION_ALREADY_CONSUMED_BY_FIT_OR_VALIDATION")


def forward_dataset_view(recorder: ForwardRecorder, dataset_id: str) -> dict[str, Any]:
    """A registry-record-shaped view of a forward ledger's current state.

    ``recorded_from`` is what ``evaluate_admissibility`` checks a
    forward-confirmation protocol freeze against -- deliberately the earliest
    instant this recorder's own clock accepted a write
    (:meth:`ForwardRecorder.earliest_recorded_at`), not any session's calendar
    label. A session date is whatever the caller supplied when constructing an
    observation; ``recorded_at`` is bound by forward-only monotonicity and
    cannot be moved earlier after the fact, which is exactly the property a
    "was this data consumable before the freeze" check needs.
    """
    sessions = recorder.sessions()
    return {
        "dataset_id": dataset_id,
        "availability": "AVAILABLE" if len(recorder) else "MISSING",
        "fingerprint": recorder.ledger_fingerprint(),
        "point_in_time": {
            "as_of_rule": "FORWARD_RECORDER_APPEND_ONLY_WALL_CLOCK",
            "recorded_at_authority": TIME_AUTHORITY_UNATTESTED_LOCAL_CLOCK,
        },
        "first_date": sessions[0] if sessions else None,
        "last_date": sessions[-1] if sessions else None,
        "recorded_from": recorder.earliest_recorded_at(),
    }


def evaluate_forward_confirmation(recorder: ForwardRecorder, dataset_id: str, session_date: str,
                                  protocol_freeze_instant: str, decision_instant: str,
                                  subject: str = "",
                                  ledger: UseLedger | None = None) -> AdmissibilityVerdict:
    """Can this recorder's data for one session serve as forward confirmation
    of a protocol frozen at ``protocol_freeze_instant``?

    The forward seal is the recorder's own :meth:`ForwardRecorder.session_seal`
    -- published, addressable evidence that this exact content existed before
    anyone reads it for the confirmation decision.
    ``evaluate_admissibility`` still runs every rule unchanged; this only
    assembles its two forward-lane-specific inputs (the dataset view and the
    seal) so a caller cannot forget either one.
    """
    dataset = forward_dataset_view(recorder, dataset_id)
    seal = recorder.session_seal(session_date)
    version = f"{dataset_id}@{dataset['fingerprint'] or 'EMPTY_LEDGER'}"
    use = EvidenceUse(dataset_version=version, use_class=USE_FORWARD_CONFIRMATION,
                      decision_instant=decision_instant,
                      protocol_freeze_instant=protocol_freeze_instant, subject=subject)
    verdict = evaluate_admissibility(dataset, use, ledger, forward_seal=seal)
    if ledger is not None and verdict.state == ADMISSIBLE:
        prior_uses = ledger.uses_of(version) & set(CONSUMING_USES)
        if prior_uses:
            return AdmissibilityVerdict(
                INADMISSIBLE, use,
                (FORWARD_CONFIRMATION_VERSION_ALREADY_CONSUMED,
                 f"version already used for: {sorted(prior_uses)}"))
    return verdict
