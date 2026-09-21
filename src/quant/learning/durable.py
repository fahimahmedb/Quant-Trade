"""The durable Learning processed-id / payload-digest idempotence authority.

``LearningStore`` (`store.py`) keeps a human-readable ``lessons`` list that is
deliberately capped to the last 200 entries (``save()`` writes
``self.lessons[-200:]``). That cap makes it *not* a durable idempotence
authority: once 200 later lessons have been appended, replaying an old
processed id finds nothing there and would be recorded a second time. The
only structure in that file with true permanent membership today is
``build_tasks``, and it only covers one outcome kind (capability gaps).

This module is the general permanent authority for every other Learning
outcome the frozen M4 milestone names: Research results, Economic/Desk
terminal outcomes (``NO_TRADE``, ``RISK_VETO``, ``BOOKED``, ``INSUFFICIENT``),
expected-vs-realized shadow execution facts, and rejection/counterfactual
linkage. It follows the same operation-id replay guard shape already used by
``Ledger.apply_fill`` (`quant.book.ledger`) -- an unseen id is durably
recorded, a replay of an id with the *same* semantic payload is a no-op, and a
replay of an id with a *materially different* payload fails closed instead of
silently overwriting the earlier evidence.

Storage follows the existing convention (``LearningStore``, ``Ledger``,
``DeskJournal``): one JSON document, rewritten atomically in full by
``state.write_json`` on every accepted mutation, with an in-memory index
rebuilt from it at load time. That keeps every accepted record and every
processed-id membership fact in one atomically-written file, so a crash
mid-write leaves either the old, fully consistent document or the new one --
never a partially updated index next to a stale record log. Nothing is a
generic new framework: this is the smallest structure that gives whole-history
idempotence plus append-only raw evidence, reusing the read_json/write_json
primitives every other durable store in the repository already uses.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from ..state import read_json, utc_now, write_json


#: The outcome kinds M4 requires this authority to durably carry. Not
#: enforced anywhere else; kept as a closed check here so a caller's typo in
#: ``kind`` is caught at the call site instead of silently minting a new,
#: unrecognised outcome category.
RESEARCH_RESULT = "RESEARCH_RESULT"
ECONOMIC_ASSESSMENT = "ECONOMIC_ASSESSMENT"
NO_TRADE = "NO_TRADE"
KILL = "KILL"
RISK_VETO = "RISK_VETO"
BOOKED = "BOOKED"
INSUFFICIENT = "INSUFFICIENT"
SHADOW_EXECUTION_FACT = "SHADOW_EXECUTION_FACT"
REJECTION_COUNTERFACTUAL = "REJECTION_COUNTERFACTUAL"

KINDS = (RESEARCH_RESULT, ECONOMIC_ASSESSMENT, NO_TRADE, KILL, RISK_VETO, BOOKED,
         INSUFFICIENT, SHADOW_EXECUTION_FACT, REJECTION_COUNTERFACTUAL)


class LearningConflict(Exception):
    """A processed id was replayed with a materially different payload.

    Raised instead of overwriting, so a genuine data problem (a bug that
    reuses an id, or two distinct decisions colliding on one id) stops the
    write rather than silently destroying the first recorded outcome.
    """


def payload_digest(payload: dict[str, Any]) -> str:
    """A stable digest of a payload's semantic content.

    ``sort_keys=True`` makes key order irrelevant. Callers are responsible
    for excluding purely cosmetic fields (a wall-clock timestamp, a log
    line) from what they pass as ``payload``, the same way
    ``LearningStore._assessment_core`` strips ``assessed_at`` before
    comparing two assessments for equality.
    """
    canonical = json.dumps(payload, sort_keys=True, default=str, allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class OutcomeRecord:
    processed_id: str
    kind: str
    digest: str
    payload: dict[str, Any]
    links: dict[str, str] = field(default_factory=dict)
    recorded_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {"processed_id": self.processed_id, "kind": self.kind,
                "digest": self.digest, "payload": self.payload,
                "links": self.links, "recorded_at": self.recorded_at}


class DurableOutcomeStore:
    """Permanent processed-id membership plus append-only raw evidence.

    Every accepted record is kept forever, in acceptance order, in
    ``self.records``. ``self._index`` (processed_id -> digest/kind) is
    rebuilt from that list at load time, exactly the way ``Ledger`` rebuilds
    ``self._applied`` from ``state.applied_operations`` at load time. A
    record already accepted is never mutated or removed by a later call:
    a later evaluation of an earlier decision (e.g. a rejection
    counterfactual) must be given its *own* processed_id and reference the
    original through ``links``, not reuse the original's id.
    """

    def __init__(self, path: Path):
        self.path = path
        payload = read_json(path, {}) or {}
        self.records: list[dict[str, Any]] = payload.get("records", [])
        self._index: dict[str, dict[str, Any]] = {
            record["processed_id"]: record for record in self.records}

    def save(self) -> None:
        write_json(self.path, {"version": 1, "updated_at": utc_now(),
                               "records": self.records})

    # --- queries -------------------------------------------------------
    def has(self, processed_id: str) -> bool:
        return processed_id in self._index

    def get(self, processed_id: str) -> dict[str, Any] | None:
        record = self._index.get(processed_id)
        return dict(record) if record is not None else None

    def history(self, processed_id: str | None = None) -> Iterable[dict[str, Any]]:
        """Raw evidence in acceptance order.

        With no ``processed_id`` this is every accepted record. With one, it
        is that record's own entry (if any) plus every later record that
        links to it -- e.g. every rejection-counterfactual evaluation ever
        recorded against one original prospective decision -- which is what
        a "was this rejection later correct" query (Q10-Q12) needs, without
        ever reading a mutated original.
        """
        for record in self.records:
            if processed_id is None or record["processed_id"] == processed_id:
                yield dict(record)
            elif processed_id in (record.get("links") or {}).values():
                yield dict(record)

    # --- write -----------------------------------------------------------
    def record(self, processed_id: str, kind: str, payload: dict[str, Any],
               links: dict[str, str] | None = None) -> dict[str, Any]:
        """Durably record one outcome exactly once.

        Returns ``{"status": "RECORDED" | "NOOP", "record": {...}}``.
        ``"NOOP"`` means an identical ``(processed_id, payload)`` was already
        durable and nothing new was written -- the required idempotent
        no-duplicate-persisted behaviour. A processed id seen before with a
        payload whose digest differs raises ``LearningConflict`` and leaves
        the store file byte-for-byte unchanged (fail closed).
        """
        if not processed_id:
            raise ValueError("processed_id must be non-empty")
        if kind not in KINDS:
            raise ValueError(f"unknown durable Learning outcome kind: {kind!r}")
        # Round-trip through JSON so the stored payload can never later be
        # mutated via the caller's original dict object, and so the digest is
        # computed over exactly what will be persisted.
        canonical_payload = json.loads(
            json.dumps(payload, sort_keys=True, default=str, allow_nan=False))
        digest = payload_digest(canonical_payload)

        existing = self._index.get(processed_id)
        if existing is not None:
            if existing["digest"] == digest:
                return {"status": "NOOP", "record": dict(existing)}
            raise LearningConflict(
                f"processed_id {processed_id!r} already recorded as kind "
                f"{existing['kind']!r} with digest {existing['digest'][:12]}...; "
                f"refusing to overwrite with a conflicting {kind!r} payload "
                f"(digest {digest[:12]}...)")

        record = OutcomeRecord(processed_id=processed_id, kind=kind, digest=digest,
                               payload=canonical_payload, links=dict(links or {}))
        entry = record.to_dict()
        self.records.append(entry)
        self._index[processed_id] = entry
        self.save()
        return {"status": "RECORDED", "record": dict(entry)}
