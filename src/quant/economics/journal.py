"""The durable economic assessment journal.

Wave 1 and Codex independently named the same top gap (Wave 1 WS31: "not yet
populated"; Codex W1-EVID-001 / self red team item 3: "no durable
conflict-aware economic-assessment registry ... kill the process after
assessment and before Desk submission"). This module closes it.

Two rules, enforced structurally rather than by convention:

* same ``assessment_id`` + same ``input_fingerprint`` -> idempotent replay.
  No second record is appended; the caller gets back the fact that this
  exact assessment was already durably decided.
* same ``assessment_id`` + a *different* ``input_fingerprint`` -> conflict,
  fails closed. Two different sets of inputs cannot share one assessment
  identity; recording one over the other would let a crash-and-retry with
  slightly different inputs (a re-run against a moved recipe, say) silently
  overwrite the decision an interrupted Desk session might already be acting
  on.

Persistence reuses ``state.append_jsonl``/``read_jsonl`` exactly as
``operations.registry.EvidenceRegistry`` and ``economics.timeline.
CausalEventLedger`` already do: durable fsync'd append, and a torn final
line from a process killed mid-write is recovered rather than corrupting the
journal or being mistaken for a second record.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ..state import append_jsonl, read_jsonl, utc_now
from .capacity import CapacityOutcome
from .consistency import ResearchExecutionConsistency
from .decision import EconomicVerdict, EffectEstimate, PortfolioInteraction
from .fingerprint import canonical_json
from .recipe import MEUEResult
from .theta import ThetaState


RECORD_ACCEPTED = "ASSESSMENT_RECORDED"
RECORD_CONFLICT = "ASSESSMENT_ID_CONFLICT_DIFFERENT_FINGERPRINT"


class AssessmentConflict(RuntimeError):
    """Same ``assessment_id``, a different ``input_fingerprint``. Fails closed."""

    def __init__(self, assessment_id: str, existing_fingerprint: str, new_fingerprint: str):
        super().__init__(
            f"{assessment_id}: existing fingerprint {existing_fingerprint!r} != "
            f"new fingerprint {new_fingerprint!r}; refusing to overwrite a durable "
            "assessment with different inputs")
        self.assessment_id = assessment_id
        self.existing_fingerprint = existing_fingerprint
        self.new_fingerprint = new_fingerprint


def compute_input_fingerprint(estimate: EffectEstimate, meue_result: MEUEResult,
                              theta: ThetaState, interaction: PortfolioInteraction,
                              capacity: CapacityOutcome | None = None,
                              consistency: ResearchExecutionConsistency | None = None) -> str:
    """Hash every input ``economic_gate`` actually consumed for one verdict.

    Deliberately *not* ``fingerprint.recipe_hash``: that function refuses to
    hash a document carrying a realised value such as ``delta_hat`` (the
    rule-before-values firewall), which is exactly backwards for an
    assessment fingerprint — the whole point here is to detect when the
    realised inputs to a decision have changed.
    """
    payload = {
        "estimate": estimate.to_dict(),
        "recipe_hash": meue_result.recipe_hash,
        "theta_hash": meue_result.theta_hash,
        "theta": theta.to_dict(),
        "interaction": interaction.to_dict(),
        "capacity": capacity.to_dict() if capacity is not None else None,
        "consistency": consistency.to_dict() if consistency is not None else None,
    }
    return "sha256:" + hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class AssessmentRecord:
    """One durable economic assessment, complete enough to replay or audit.

    The contextual fields below (``effect_version`` through
    ``protocol_hash``) are supplied by the caller when known and default to
    ``""`` — an empty string is an honest "not supplied", never a fabricated
    value. Only ``assessment_id``, ``input_fingerprint`` and the fields
    mechanically derived from a real ``EconomicVerdict``/``MEUEResult`` are
    required.
    """

    assessment_id: str
    input_fingerprint: str
    decision: str
    capital_order_eligibility: str
    reason_codes: tuple[str, ...]
    recipe_version: str = ""
    effect_version: str = ""
    parameter_provenance: str = ""
    cost_scenario: str = ""
    capacity_state: str = ""
    portfolio_context_ref: str = ""
    code_sha: str = ""
    protocol_hash: str = ""
    #: The strategy this assessment was made for. Added so downstream
    #: consumers (M3 SIZE) can look up "the durable assessment for strategy
    #: X" without decoding the content-addressed ``assessment_id``. Empty
    #: string for any record persisted before this field existed.
    strategy_id: str = ""
    #: ``EconomicVerdict.margin_of_safety`` at the moment of assessment, so
    #: M3 SIZE can size a lane from the same number Economic already computed
    #: rather than re-deriving or inventing a parallel one. ``None`` exactly
    #: when the verdict itself carried no margin (gate stopped before it was
    #: computed) or for any record persisted before this field existed.
    margin_of_safety: float | None = None
    recorded_at: str = field(default_factory=utc_now)

    @classmethod
    def from_verdict(cls, assessment_id: str, input_fingerprint: str,
                     verdict: EconomicVerdict, meue_result: MEUEResult, *,
                     effect_version: str = "", parameter_provenance: str = "",
                     cost_scenario: str = "", capacity_state: str = "",
                     portfolio_context_ref: str = "", code_sha: str = "",
                     protocol_hash: str = "", strategy_id: str = "") -> "AssessmentRecord":
        return cls(
            assessment_id=assessment_id, input_fingerprint=input_fingerprint,
            decision=verdict.verdict, capital_order_eligibility=verdict.capital_order_eligibility,
            reason_codes=(verdict.reason,) + tuple(verdict.violations),
            recipe_version=meue_result.recipe_hash or "", effect_version=effect_version,
            parameter_provenance=parameter_provenance, cost_scenario=cost_scenario,
            capacity_state=capacity_state, portfolio_context_ref=portfolio_context_ref,
            code_sha=code_sha, protocol_hash=protocol_hash, strategy_id=strategy_id,
            margin_of_safety=verdict.margin_of_safety)

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        document["reason_codes"] = list(self.reason_codes)
        return document


class EconomicAssessmentJournal:
    """Append-only, idempotent-by-id-and-fingerprint, conflict-detecting.

    Restart-safe by construction: the constructor replays every
    ``ASSESSMENT_RECORDED`` line to rebuild ``assessment_id ->
    AssessmentRecord`` in memory, so a fresh instance opened after a crash
    (or by a different process) sees exactly the same state a live one
    would. Exactly one ``ASSESSMENT_RECORDED`` line can ever exist per
    ``assessment_id``: a repeat with the same fingerprint appends nothing
    (idempotent replay), and a repeat with a different fingerprint raises
    before appending an ``ASSESSMENT_RECORDED`` line at all (only an audit
    ``ASSESSMENT_ID_CONFLICT_DIFFERENT_FINGERPRINT`` line is appended), so
    replay never has to choose between two accepted records for one id.
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._by_id: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        self._by_id.clear()
        for record in read_jsonl(self.path):
            if record.get("state") != RECORD_ACCEPTED:
                continue
            assessment_id = str(record.get("assessment_id", ""))
            if assessment_id:
                self._by_id[assessment_id] = dict(record)

    def record(self, assessment: AssessmentRecord) -> str:
        """Durably record one assessment. Raises :class:`AssessmentConflict`
        rather than silently accepting a second, different, decision under
        the same identity."""
        existing = self._by_id.get(assessment.assessment_id)
        if existing is not None:
            if existing.get("input_fingerprint") == assessment.input_fingerprint:
                return RECORD_ACCEPTED  # idempotent replay: already durable, nothing to append
            append_jsonl(self.path, {**assessment.to_dict(), "state": RECORD_CONFLICT,
                                     "conflicting_with_fingerprint":
                                         existing.get("input_fingerprint"),
                                     "journaled_at": utc_now()})
            raise AssessmentConflict(assessment.assessment_id,
                                     str(existing.get("input_fingerprint")),
                                     assessment.input_fingerprint)
        append_jsonl(self.path, {**assessment.to_dict(), "state": RECORD_ACCEPTED,
                                 "journaled_at": utc_now()})
        self._by_id[assessment.assessment_id] = assessment.to_dict()
        return RECORD_ACCEPTED

    def get(self, assessment_id: str) -> dict[str, Any] | None:
        return self._by_id.get(assessment_id)

    def latest_for_strategy(self, strategy_id: str) -> dict[str, Any] | None:
        """The most recently recorded durable assessment for one strategy.

        M3 SIZE's real splice point onto the boundary: rather than
        re-deriving admission from a live ``EconomicVerdict`` (which SIZE
        never sees directly), it reads the durable record M2 already wrote.
        Records from before ``strategy_id`` was added to the schema cannot be
        matched and are skipped rather than guessed at.
        """
        candidates = [record for record in self._by_id.values()
                     if record.get("strategy_id") == strategy_id]
        if not candidates:
            return None
        return max(candidates, key=lambda record: str(record.get("recorded_at", "")))

    def replay(self) -> dict[str, dict[str, Any]]:
        """Rebuild state from the file alone, ignoring in-memory cache.

        The crash-then-restart proof: construct a journal, record into it,
        discard it, and check a *new* instance's :meth:`replay` (or a fresh
        constructor call) reaches byte-for-byte the same state.
        """
        state: dict[str, dict[str, Any]] = {}
        for record in read_jsonl(self.path):
            if record.get("state") != RECORD_ACCEPTED:
                continue
            assessment_id = str(record.get("assessment_id", ""))
            if assessment_id:
                state[assessment_id] = dict(record)
        return state

    def __len__(self) -> int:
        return len(self._by_id)
