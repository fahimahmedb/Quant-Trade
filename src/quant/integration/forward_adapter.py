"""Forward evidence identity, scoped to exactly the evidence consumed.

The Economic admission boundary must not key its durable assessment identity
off anything that can drift when unrelated data arrives later — a whole-file
dataset fingerprint, a growing ledger digest, or a caller-asserted boolean.
``quant.science.effect.ScientificEffectArtifact`` already carries the exact
scoped facts a scientific producer consumed: the frozen protocol/cohort
identity, the sorted allocation commitment (content-address) hashes, the
delta-coordinate binding hash, and (via a
``quant.science.effect.ForwardConfirmationReceipt``) the session seal and
UseLedger identity. :func:`derive_forward_evidence_identity` reads those
fields off the artifact; it never re-derives identity from a live, growing
ledger and never accepts a caller-provided ``forward_confirmed`` flag as
authority.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Any

from ..economics.fingerprint import canonical_json
from ..economics.states import DELTA_COORDINATE_MISMATCH, DELTA_COORDINATE_UNRESOLVED
from ..science.effect import EFFECT_UNAVAILABLE, ForwardConfirmationReceipt, ScientificEffectArtifact

#: Distinct refusal reasons the M2 boundary must report, never collapsed to a
#: generic ``NO_TRADE``.
EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE = EFFECT_UNAVAILABLE

REFUSAL_REASONS = (
    EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE,
    DELTA_COORDINATE_UNRESOLVED,
    DELTA_COORDINATE_MISMATCH,
)


@dataclass(frozen=True)
class ForwardEvidenceIdentity:
    """The exact evidence one economic assessment is scoped to.

    Every field is a fact about the specific scientific artifact consumed,
    never about the state of a ledger or dataset as a whole. Appending
    unrelated Forward observations elsewhere cannot change any field here.
    """

    dataset_id: str
    protocol_id: str
    protocol_hash: str
    sample_id: str
    cohort_ids: tuple[str, ...]
    #: Sorted, exact content addresses of the components this estimate used.
    contributing_content_addresses: tuple[str, ...]
    delta_coordinate_hash: str
    #: "" (honestly undeclared) unless a real ForwardConfirmationReceipt supplied one.
    session_seal: str
    use_ledger_id: str
    subject_id: str

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        document["cohort_ids"] = list(self.cohort_ids)
        document["contributing_content_addresses"] = list(self.contributing_content_addresses)
        return document


def classify_effect_refusal(artifact: ScientificEffectArtifact | None) -> str:
    """The specific reason an effect estimate is not usable for admission.

    Undeclared/unresolved and mismatched are reported distinctly from a
    generically unavailable estimate, and none of the three ever collapse to
    a bare ``NO_TRADE`` — that verdict is reserved for ``economic_gate``
    itself, reached only once a usable estimate exists.
    """
    if artifact is not None and artifact.effect_estimate is None:
        codes = set(artifact.reason_codes)
        if DELTA_COORDINATE_MISMATCH in codes:
            return DELTA_COORDINATE_MISMATCH
        if DELTA_COORDINATE_UNRESOLVED in codes:
            return DELTA_COORDINATE_UNRESOLVED
    return EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_UNAVAILABLE


def derive_forward_evidence_identity(
    *, artifact: ScientificEffectArtifact | None, ticket_id: str, strategy_id: str,
    forward_receipt: ForwardConfirmationReceipt | None = None,
) -> ForwardEvidenceIdentity | None:
    """Build the scoped identity, or ``None`` when no usable estimate exists.

    Deliberately reads only artifact-carried, evidence-scoped fields.
    ``forward_receipt`` is a structured, independently verifiable object
    (``ForwardConfirmationReceipt.valid_for``); a bare boolean is never
    accepted in its place, here or anywhere downstream.
    """
    if artifact is None or artifact.effect_estimate is None:
        return None
    return ForwardEvidenceIdentity(
        dataset_id=artifact.sample_provenance,
        protocol_id=artifact.protocol_id,
        protocol_hash=artifact.protocol_hash,
        sample_id=artifact.sample_id,
        cohort_ids=tuple(artifact.cohort_ids),
        contributing_content_addresses=tuple(sorted(artifact.allocation_commitment_hashes)),
        delta_coordinate_hash=artifact.delta_coordinate_hash or "",
        session_seal=forward_receipt.session_seals_hash if forward_receipt is not None else "",
        use_ledger_id=forward_receipt.use_ledger_receipt if forward_receipt is not None else "",
        subject_id=f"{ticket_id}:{strategy_id}",
    )


def assessment_id_for(identity: ForwardEvidenceIdentity) -> str:
    """A deterministic id scoped to exactly this evidence identity.

    Same identity fields (in particular the same sorted content addresses,
    protocol hash, sample/cohort identity and subject) always produce the
    same id; unrelated Forward ledger growth cannot change any input here,
    so it cannot change the id either.
    """
    digest = hashlib.sha256(canonical_json(identity.to_dict()).encode("utf-8")).hexdigest()
    return f"ADM-{digest[:40]}"


def refusal_identity_seed(
    ticket_id: str, strategy_id: str, artifact: ScientificEffectArtifact | None,
) -> str:
    """A deterministic id for a refusal recorded before any identity resolves.

    Scoped to the ticket/strategy subject and whatever the (possibly absent)
    artifact itself declares — never to a whole ledger or dataset state.
    """
    payload = {
        "subject_id": f"{ticket_id}:{strategy_id}",
        "artifact_status": artifact.status if artifact is not None else None,
        "artifact_protocol_hash": artifact.protocol_hash if artifact is not None else None,
        "artifact_sample_id": artifact.sample_id if artifact is not None else None,
        "reason_codes": sorted(artifact.reason_codes) if artifact is not None else [],
    }
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return f"ADM-REFUSED-{digest[:40]}"
