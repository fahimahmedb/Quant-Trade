"""Provenance-only archaeology for historical Research OS scientific memory.

This module does not store scientific outcomes.  It tracks *where* durable
historical evidence or governance artifacts live, whether those anchors are
immutable enough to support reuse, and what history-first disposition applies.
Scientific conclusions continue to live in the canonical scientific-memory
records carried by the existing append-only scientific ledger.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence
import json
import re


SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
SHA64_RE = re.compile(r"^[0-9a-f]{64}$")

HISTORY_DISPOSITIONS = {
    "REUSE_CURRENT",
    "IMPORT_EXACT",
    "ADAPT_EXISTING",
    "HARDEN_EXISTING",
    "BUILD_MISSING",
    "NO_BUILD_REQUIRED",
    "SUPERSEDED_WITH_PROOF",
    "REVIEW_STILL_REQUIRED",
    "SEALED_BY_AUTHORITY",
    "EXTERNAL_ACCESS_REQUIRED",
}

TERMINAL_STATES = {
    "QUALIFIED_CURRENT",
    "PARTIAL_WITH_EXPLICIT_BLOCKER",
    "SEALED_BY_AUTHORITY",
    "EXTERNAL_ACCESS_REQUIRED",
    "NO_BUILD_REQUIRED",
}

MEMORY_ACTIONS = {
    "NORMALIZE_CANONICAL_MEMORY",
    "PRESERVE_DISTINCT_MEMORY_GENERATIONS",
    "PRESERVE_PROTOCOL_MEMORY_ONLY",
    "PRESERVE_STRUCTURAL_MEMORY_ONLY",
    "KEEP_REVIEW_ONLY",
    "NO_MEMORY_MUTATION",
}

IMMUTABLE_KINDS = {
    "GIT_BLOB",
    "GIT_COMMIT_PATH",
    "PINNED_LEDGER_BLOB",
    "PINNED_LEDGER_COMMIT",
}

FORBIDDEN_FINDING_FIELDS = {
    "result", "results", "return", "returns", "pnl", "sharpe", "correlation",
    "score", "metric", "metrics", "effect_size", "economic_evidence",
    "statistical_evidence",
}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_sha(value: str, *, lengths: Sequence[int]) -> bool:
    if not isinstance(value, str):
        return False
    if 40 in lengths and SHA40_RE.fullmatch(value):
        return True
    if 64 in lengths and SHA64_RE.fullmatch(value):
        return True
    return False


def validate_source_ref(ref: Mapping[str, Any]) -> None:
    allowed = {"kind", "path", "branch", "commit_sha", "blob_sha", "content_sha256", "note"}
    extra = sorted(set(ref) - allowed)
    if extra:
        raise ValueError(f"archaeology source ref contains unsupported fields: {', '.join(extra)}")
    kind = ref.get("kind")
    if kind not in IMMUTABLE_KINDS | {"BRANCH_LOCATOR", "OWNER_ASSERTION"}:
        raise ValueError(f"unsupported archaeology source kind: {kind}")
    if kind in {"GIT_BLOB", "PINNED_LEDGER_BLOB"}:
        if not _validate_sha(str(ref.get("blob_sha", "")), lengths=(40,)):
            raise ValueError("immutable blob source requires a 40-hex blob_sha")
    if kind in {"GIT_COMMIT_PATH", "PINNED_LEDGER_COMMIT"}:
        if not _validate_sha(str(ref.get("commit_sha", "")), lengths=(40,)):
            raise ValueError("immutable commit source requires a 40-hex commit_sha")
    if kind == "GIT_COMMIT_PATH" and not _nonempty(ref.get("path")):
        raise ValueError("GIT_COMMIT_PATH requires a repository path")
    if "content_sha256" in ref and not _validate_sha(str(ref["content_sha256"]), lengths=(64,)):
        raise ValueError("content_sha256 must be 64 lowercase hex characters")


def is_immutable_source(ref: Mapping[str, Any]) -> bool:
    try:
        validate_source_ref(ref)
    except ValueError:
        return False
    return ref.get("kind") in IMMUTABLE_KINDS


def validate_finding(finding: Mapping[str, Any]) -> None:
    allowed = {
        "archaeology_id", "subject_id", "subject_kind", "mechanism",
        "history_disposition", "terminal_state", "memory_action", "claim_limit",
        "source_refs", "blockers", "supersedes_subject_ids", "notes",
        "outcome_accessed",
    }
    extra = sorted(set(finding) - allowed)
    if extra:
        forbidden = sorted(set(extra) & FORBIDDEN_FINDING_FIELDS)
        if forbidden:
            raise ValueError(
                "archaeology is provenance-only; result/metric fields are forbidden: "
                + ", ".join(forbidden)
            )
        raise ValueError(f"archaeology finding contains unsupported fields: {', '.join(extra)}")

    for key in (
        "archaeology_id", "subject_id", "subject_kind", "history_disposition",
        "terminal_state", "memory_action", "claim_limit",
    ):
        if not _nonempty(finding.get(key)):
            raise ValueError(f"archaeology finding missing {key}")
    if finding["history_disposition"] not in HISTORY_DISPOSITIONS:
        raise ValueError("invalid history-first disposition")
    if finding["terminal_state"] not in TERMINAL_STATES:
        raise ValueError("invalid terminal archaeology state")
    if finding["memory_action"] not in MEMORY_ACTIONS:
        raise ValueError("invalid scientific-memory action")
    if finding.get("outcome_accessed") is not False:
        raise ValueError("W1 archaeology findings must preserve OUTCOME_ACCESSED=FALSE")

    refs = list(finding.get("source_refs") or [])
    for ref in refs:
        validate_source_ref(ref)

    immutable = [ref for ref in refs if is_immutable_source(ref)]
    if finding["terminal_state"] == "QUALIFIED_CURRENT" and not immutable:
        raise ValueError("QUALIFIED_CURRENT archaeology requires an immutable source anchor")

    disposition = finding["history_disposition"]
    if disposition in {
        "REUSE_CURRENT", "IMPORT_EXACT", "ADAPT_EXISTING", "HARDEN_EXISTING",
        "SUPERSEDED_WITH_PROOF",
    } and not immutable:
        raise ValueError(f"{disposition} requires an immutable source anchor")
    if disposition == "SUPERSEDED_WITH_PROOF" and not finding.get("supersedes_subject_ids"):
        raise ValueError("SUPERSEDED_WITH_PROOF requires explicit superseded subject ids")


def finding_provenance_refs(finding: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Convert only immutable source anchors to scientific-memory provenance refs."""
    validate_finding(finding)
    refs: List[Dict[str, Any]] = []
    for source in finding.get("source_refs") or []:
        if not is_immutable_source(source):
            continue
        kind = source["kind"]
        if kind in {"GIT_BLOB", "PINNED_LEDGER_BLOB"}:
            ref = f"blob:{source['blob_sha']}"
            if source.get("path"):
                ref += f":{source['path']}"
        else:
            ref = f"commit:{source['commit_sha']}"
            if source.get("path"):
                ref += f":{source['path']}"
        refs.append({"kind": "ARCHAEOLOGY_IMMUTABLE_SOURCE", "ref": ref})
    return refs


class ArchaeologyCatalog:
    """Read-only provenance map; never a scientific result store."""

    def __init__(self, findings: Iterable[Mapping[str, Any]]):
        items: Dict[str, Dict[str, Any]] = {}
        for raw in findings:
            item = deepcopy(dict(raw))
            validate_finding(item)
            aid = item["archaeology_id"]
            if aid in items:
                raise ValueError(f"duplicate archaeology_id: {aid}")
            items[aid] = item
        self._items = items

    @classmethod
    def load(cls, path: Path) -> "ArchaeologyCatalog":
        payload = json.loads(path.read_text())
        if payload.get("schema_version") != "archaeology-source-catalog-v1":
            raise ValueError("unsupported archaeology source catalog schema")
        if payload.get("scientific_truth_store") is not False:
            raise ValueError("archaeology catalog must explicitly deny scientific truth-store authority")
        if payload.get("outcome_accessed") is not False:
            raise ValueError("archaeology catalog must preserve OUTCOME_ACCESSED=FALSE")
        return cls(payload.get("findings") or [])

    @property
    def findings(self) -> List[Dict[str, Any]]:
        return [deepcopy(self._items[key]) for key in sorted(self._items)]

    def query(
        self,
        *,
        subject_id: Optional[str] = None,
        mechanism: Optional[str] = None,
        history_disposition: Optional[str] = None,
        terminal_state: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        for item in self._items.values():
            if subject_id and item["subject_id"] != subject_id:
                continue
            if mechanism and item.get("mechanism") != mechanism:
                continue
            if history_disposition and item["history_disposition"] != history_disposition:
                continue
            if terminal_state and item["terminal_state"] != terminal_state:
                continue
            result.append(deepcopy(item))
        return sorted(result, key=lambda item: item["archaeology_id"])

    def report(self) -> Dict[str, Any]:
        by_terminal: Dict[str, int] = {}
        by_disposition: Dict[str, int] = {}
        immutable_qualified = 0
        for item in self._items.values():
            by_terminal[item["terminal_state"]] = by_terminal.get(item["terminal_state"], 0) + 1
            by_disposition[item["history_disposition"]] = by_disposition.get(item["history_disposition"], 0) + 1
            if item["terminal_state"] == "QUALIFIED_CURRENT":
                immutable_qualified += 1
        return {
            "finding_count": len(self._items),
            "terminal_states": dict(sorted(by_terminal.items())),
            "history_dispositions": dict(sorted(by_disposition.items())),
            "qualified_with_immutable_anchor": immutable_qualified,
            "scientific_truth_store": False,
            "single_score_computed": False,
            "outcome_accessed": False,
        }
