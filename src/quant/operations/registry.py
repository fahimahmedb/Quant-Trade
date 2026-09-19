"""The evidence registry: dataset -> protocol -> code SHA -> result -> decision.

Small on purpose. Its whole job is to make a decision traceable back to the exact
data, protocol and code that produced it, so that a result cannot be cited later
without the conditions that made it true.

A record missing any link in the chain is refused. An incomplete provenance chain
recorded as "mostly complete" is worse than no record, because it looks like
evidence.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

from ..state import append_jsonl, read_jsonl, utc_now


REQUIRED_LINKS = ("dataset_version", "protocol_hash", "code_sha", "result_summary",
                  "decision")

RECORD_ACCEPTED = "EVIDENCE_RECORDED"
RECORD_DUPLICATE = "EVIDENCE_DUPLICATE_IGNORED"
RECORD_INCOMPLETE = "EVIDENCE_CHAIN_INCOMPLETE"

#: Evidence labels, identical to the economic gate's, so one vocabulary governs.
LABELS = ("EXPLORATION", "TRAINING", "DEVELOPMENT", "FORWARD_CONFIRMATION")


@dataclass(frozen=True)
class EvidenceRecord:
    """One complete provenance chain behind one decision."""

    evidence_id: str
    dataset_version: str
    protocol_hash: str
    code_sha: str
    result_summary: str
    decision: str
    label: str
    recorded_at: str = field(default_factory=utc_now)
    note: str = ""

    def violations(self) -> list[str]:
        problems: list[str] = []
        for link in REQUIRED_LINKS:
            if not getattr(self, link):
                problems.append(f"{self.evidence_id}: MISSING_LINK:{link}")
        if self.label not in LABELS:
            problems.append(f"{self.evidence_id}: EVIDENCE_LABEL_NOT_RECOGNISED")
        if not self.evidence_id:
            problems.append("EVIDENCE_ID_MISSING")
        return problems

    @property
    def chain_hash(self) -> str:
        payload = "|".join(str(getattr(self, link)) for link in REQUIRED_LINKS)
        return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        document["chain_hash"] = self.chain_hash
        return document


class EvidenceRegistry:
    """Append-only registry, idempotent on the provenance chain hash."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._chains: set[str] = set()
        self._by_id: dict[str, dict[str, Any]] = {}
        for record in read_jsonl(self.path):
            if record.get("state") != RECORD_ACCEPTED:
                continue
            chain = str(record.get("chain_hash", ""))
            if chain:
                self._chains.add(chain)
            evidence_id = str(record.get("evidence_id", ""))
            if evidence_id:
                self._by_id[evidence_id] = dict(record)

    def record(self, record: EvidenceRecord) -> str:
        problems = record.violations()
        if problems:
            append_jsonl(self.path, {**record.to_dict(), "state": RECORD_INCOMPLETE,
                                     "violations": problems, "journaled_at": utc_now()})
            return RECORD_INCOMPLETE
        if record.chain_hash in self._chains:
            return RECORD_DUPLICATE
        append_jsonl(self.path, {**record.to_dict(), "state": RECORD_ACCEPTED,
                                 "journaled_at": utc_now()})
        self._chains.add(record.chain_hash)
        self._by_id[record.evidence_id] = record.to_dict()
        return RECORD_ACCEPTED

    def get(self, evidence_id: str) -> dict[str, Any] | None:
        return self._by_id.get(evidence_id)

    def incomplete(self) -> list[dict[str, Any]]:
        return [record for record in read_jsonl(self.path)
                if record.get("state") == RECORD_INCOMPLETE]

    def citations_for(self, decision: str) -> list[dict[str, Any]]:
        return [record for record in self._by_id.values()
                if record.get("decision") == decision]

    def confirmation_records(self) -> list[dict[str, Any]]:
        return [record for record in self._by_id.values()
                if record.get("label") == "FORWARD_CONFIRMATION"]

    def __len__(self) -> int:
        return len(self._by_id)
