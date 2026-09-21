"""Which dataset version may be used for which kind of claim.

The mission separates four uses of data — dataset discovery, exploratory fit,
validation, forward confirmation — and the separation is only real if something
enforces it across runs.  A dataset version that has already been fitted cannot
later serve as its own validation, and no historical dataset can ever serve as
forward confirmation, however carefully it was held back: it existed before the
protocol was frozen, so the protocol could have been shaped by it.

The ledger here is a one-way ratchet keyed on the dataset *version* (id plus
fingerprint). Refreshing a dataset produces a new fingerprint and therefore a new
version, which is the honest outcome: new data is new evidence, not a licence to
re-validate on data already fitted.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from ..state import append_jsonl, read_jsonl, utc_now


USE_DISCOVERY = "DATASET_DISCOVERY"
USE_EXPLORATORY_FIT = "EXPLORATORY_FIT"
USE_VALIDATION = "VALIDATION"
USE_FORWARD_CONFIRMATION = "FORWARD_CONFIRMATION"

USE_CLASSES = (USE_DISCOVERY, USE_EXPLORATORY_FIT, USE_VALIDATION, USE_FORWARD_CONFIRMATION)

#: Uses that consume a version's evidential independence.
CONSUMING_USES = (USE_EXPLORATORY_FIT, USE_VALIDATION)

ADMISSIBLE = "ADMISSIBLE"
INADMISSIBLE = "INADMISSIBLE"
UNRESOLVED = "ADMISSIBILITY_UNRESOLVED"


def _instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class EvidenceUse:
    """A proposed use of one dataset version."""

    dataset_version: str
    use_class: str
    #: Instant the decision that consumes this evidence is taken.
    decision_instant: str
    #: Instant the protocol that this evidence is meant to confirm was frozen.
    protocol_freeze_instant: str | None = None
    subject: str = ""

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.use_class not in USE_CLASSES:
            problems.append("USE_CLASS_NOT_RECOGNISED")
        if not self.dataset_version:
            problems.append("DATASET_VERSION_UNDECLARED")
        try:
            _instant(self.decision_instant)
        except ValueError:
            problems.append("DECISION_INSTANT_NOT_ISO8601")
        if self.use_class == USE_FORWARD_CONFIRMATION and not self.protocol_freeze_instant:
            problems.append("FORWARD_CONFIRMATION_REQUIRES_A_PROTOCOL_FREEZE_INSTANT")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AdmissibilityVerdict:
    state: str
    use: EvidenceUse
    reasons: tuple[str, ...] = ()

    @property
    def admissible(self) -> bool:
        return self.state == ADMISSIBLE

    def to_dict(self) -> dict[str, Any]:
        return {"state": self.state, "use": self.use.to_dict(),
                "reasons": list(self.reasons)}


class UseLedger:
    """Durable record of how each dataset version has already been used."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._uses: dict[str, set[str]] = {}
        for record in read_jsonl(self.path):
            version = str(record.get("dataset_version", ""))
            use_class = str(record.get("use_class", ""))
            if version and use_class:
                self._uses.setdefault(version, set()).add(use_class)

    def uses_of(self, dataset_version: str) -> set[str]:
        return set(self._uses.get(dataset_version, set()))

    def record(self, use: EvidenceUse) -> bool:
        """Record a use. Returns False when that exact use is already recorded."""
        existing = self._uses.setdefault(use.dataset_version, set())
        if use.use_class in existing:
            return False
        append_jsonl(self.path, {**use.to_dict(), "recorded_at": utc_now()})
        existing.add(use.use_class)
        return True

    def __len__(self) -> int:
        return sum(len(values) for values in self._uses.values())


def evaluate_admissibility(dataset: Mapping[str, Any], use: EvidenceUse,
                           ledger: UseLedger | None = None,
                           forward_seal: str | None = None) -> AdmissibilityVerdict:
    """Decide whether this dataset version may serve this use.

    ``dataset`` is a registry record document (``DatasetRecord.to_dict()`` shape).
    Nothing here inspects the data itself; admissibility is a property of
    provenance and of use history, and must be decidable before the values are
    read.
    """
    reasons = list(use.violations())
    if reasons:
        return AdmissibilityVerdict(UNRESOLVED, use, tuple(reasons))

    availability = dataset.get("availability")
    fingerprint = dataset.get("fingerprint")
    point_in_time = dataset.get("point_in_time") or {}

    if not fingerprint:
        reasons.append("DATASET_NOT_FINGERPRINTED")
    if availability != "AVAILABLE":
        reasons.append(f"DATASET_NOT_AVAILABLE:{availability}")
    if not point_in_time:
        return AdmissibilityVerdict(
            UNRESOLVED, use, tuple(reasons + ["POINT_IN_TIME_SEMANTICS_UNDECLARED"]))

    if use.use_class == USE_VALIDATION and ledger is not None:
        if USE_EXPLORATORY_FIT in ledger.uses_of(use.dataset_version):
            reasons.append("VALIDATION_ON_ALREADY_FITTED_DATASET_VERSION")

    if use.use_class == USE_FORWARD_CONFIRMATION:
        freeze = _instant(use.protocol_freeze_instant or use.decision_instant)
        first = dataset.get("first_date")
        recorded_from = dataset.get("recorded_from") or first
        if not recorded_from:
            reasons.append("FORWARD_CONFIRMATION_REQUIRES_A_RECORDING_START")
        else:
            try:
                start = _instant(str(recorded_from))
            except ValueError:
                reasons.append("RECORDING_START_NOT_ISO8601")
                start = None
            if start is not None and start < freeze:
                reasons.append("HISTORICAL_EVIDENCE_IS_NOT_INDEPENDENT_CONFIRMATION")
        if not forward_seal:
            reasons.append("FORWARD_CONFIRMATION_REQUIRES_A_PRE_OUTCOME_SEAL")

    if reasons:
        return AdmissibilityVerdict(INADMISSIBLE, use, tuple(sorted(set(reasons))))
    return AdmissibilityVerdict(ADMISSIBLE, use, ())
