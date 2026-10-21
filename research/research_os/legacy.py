from __future__ import annotations

import json
import hashlib
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokens(*values: Iterable[str]) -> set[str]:
    out: set[str] = set()
    for value in values:
        if value is None:
            continue
        if isinstance(value, (list, tuple, set)):
            for item in value:
                out.update(TOKEN_RE.findall(str(item).lower()))
        else:
            out.update(TOKEN_RE.findall(str(value).lower()))
    return {t for t in out if len(t) >= 3}


class LegacyKnowledgeBase:
    def __init__(self, manifest: Dict[str, Any], ledger: Optional[Dict[str, Any]] = None):
        self.manifest = manifest
        self.ledger = ledger or {"records": []}
        self.records = list(self.ledger.get("records") or [])
        # Provenance recovery is separate from the immutable imported ledger.
        self.source_reviews = deepcopy(manifest.get("recovered_source_reviews", []))
        self._validate_source_reviews()
        self.by_id: Dict[str, Dict[str, Any]] = {}
        for record in self.records:
            for key in ("HYPOTHESIS_ID", "LEGACY_ID_IF_ANY"):
                value = record.get(key)
                if isinstance(value, str) and value and value != "UNKNOWN":
                    self.by_id[value] = record

    def _validate_source_reviews(self) -> None:
        fields = {"source_id", "historical_id", "mechanism", "classification",
                  "researcher_decision", "judge_verdict", "failure_scope",
                  "limitations", "revisit_conditions", "source_commit", "source_refs"}
        seen = set()
        if not isinstance(self.source_reviews, list):
            raise ValueError("LEGACY_SOURCE_REVIEWS_INVALID")
        for entry in self.source_reviews:
            if not isinstance(entry, dict) or set(entry) != fields:
                raise ValueError("LEGACY_SOURCE_REVIEW_FIELDS_INVALID")
            for key in fields - {"limitations", "revisit_conditions", "source_refs"}:
                if not isinstance(entry[key], str) or not entry[key].strip() or entry[key] == "UNKNOWN":
                    raise ValueError("LEGACY_SOURCE_REVIEW_VALUE_INVALID:" + key)
            if entry["source_id"] in seen:
                raise ValueError("LEGACY_SOURCE_REVIEW_DUPLICATE")
            seen.add(entry["source_id"])
            if (entry["classification"] != "HISTORICAL_NEGATIVE_WITH_LIMITATIONS"
                    or entry["researcher_decision"] != "KILL" or entry["judge_verdict"] != "REJECT"):
                raise ValueError("LEGACY_SOURCE_REVIEW_CLASSIFICATION_INVALID")
            for key in ("limitations", "revisit_conditions"):
                if (not isinstance(entry[key], list) or not entry[key]
                        or any(not isinstance(v, str) or not v.strip() for v in entry[key])):
                    raise ValueError("LEGACY_SOURCE_REVIEW_SCOPE_REQUIRED:" + key)
            if not re.fullmatch(r"[0-9a-f]{40}", entry["source_commit"]):
                raise ValueError("LEGACY_SOURCE_REVIEW_COMMIT_INVALID")
            if not isinstance(entry["source_refs"], list) or not entry["source_refs"]:
                raise ValueError("LEGACY_SOURCE_REVIEW_REFS_REQUIRED")
            for ref in entry["source_refs"]:
                if (not isinstance(ref, dict) or set(ref) != {"path", "blob_sha"}
                        or not isinstance(ref["path"], str) or not ref["path"]
                        or ref["path"].startswith("/") or ".." in ref["path"].split("/")
                        or not isinstance(ref["blob_sha"], str)
                        or not re.fullmatch(r"[0-9a-f]{40}", ref["blob_sha"])):
                    raise ValueError("LEGACY_SOURCE_REVIEW_REF_INVALID")

    def _source_review_hash(self) -> str:
        return hashlib.sha256(json.dumps(self.source_reviews, sort_keys=True,
                                       separators=(",", ":")).encode()).hexdigest()

    @classmethod
    def load(cls, base: Path, imported_ledger_path: Optional[Path] = None) -> "LegacyKnowledgeBase":
        manifest = json.loads((base / "legacy" / "source_manifest.json").read_text())
        ledger = None
        candidate = imported_ledger_path or (base / "legacy" / "LEGACY_RESEARCH_LEDGER.imported.json")
        if candidate.exists():
            ledger = json.loads(candidate.read_text())
            if ledger.get("schema_version") != manifest["schema_version"]:
                raise ValueError("legacy ledger schema version mismatch")
            if ledger.get("governance", {}).get("historical_result_immutability") is not True:
                raise ValueError("legacy ledger missing historical result immutability")
        return cls(manifest, ledger)

    def screen_candidate(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        cid = candidate.get("hypothesis_id")
        if cid in self.by_id:
            record = self.by_id[cid]
            return {
                "status": "BLOCK_EXACT_LEGACY_DUPLICATE",
                "matched_hypothesis_id": record.get("HYPOTHESIS_ID"),
                "historical_result": record.get("RESULT", "UNKNOWN"),
                "historical_decision": record.get("RESEARCH_DECISION", "UNKNOWN"),
                "next_legitimate_step": record.get("NEXT_LEGITIMATE_STEP", "UNKNOWN"),
            }

        c_tokens = _tokens(candidate.get("mechanism", ""), candidate.get("economic_tags", []))
        matches: List[Dict[str, Any]] = []
        for record in self.records:
            r_tokens = _tokens(
                record.get("MECHANISM", ""),
                record.get("TITLE", ""),
                record.get("RESEARCH_FAMILY_ID", ""),
            )
            if not c_tokens or not r_tokens:
                continue
            overlap = len(c_tokens & r_tokens) / len(c_tokens | r_tokens)
            if overlap >= 0.30:
                matches.append({
                    "hypothesis_id": record.get("HYPOTHESIS_ID"),
                    "research_family_id": record.get("RESEARCH_FAMILY_ID"),
                    "overlap": round(overlap, 4),
                    "historical_result": record.get("RESULT", "UNKNOWN"),
                    "decision": record.get("RESEARCH_DECISION", "UNKNOWN"),
                    "next_legitimate_step": record.get("NEXT_LEGITIMATE_STEP", "UNKNOWN"),
                })
        matches.sort(key=lambda x: x["overlap"], reverse=True)
        source_matches = []
        for entry in self.source_reviews:
            r_tokens = _tokens(entry["mechanism"])
            overlap = len(c_tokens & r_tokens) / len(c_tokens | r_tokens) if c_tokens and r_tokens else 0
            exact_id = cid == entry["historical_id"]
            if exact_id or overlap >= 0.30:
                source_matches.append(dict(deepcopy(entry), match_reason=(
                    "HISTORICAL_ID_REQUIRES_SCOPE_REVIEW" if exact_id else "MECHANISM_TOKEN_OVERLAP"),
                    overlap=round(overlap, 4), scientific_equivalence="NOT_ESTABLISHED"))
        return {
            "status": "REVIEW_LEGACY_OVERLAP" if matches or source_matches else "NO_EXACT_LEGACY_CONFLICT",
            "matches": matches[:5],
            "recovered_source_matches": source_matches,
            "recovered_source_reviews_hash": self._source_review_hash(),
        }

    def summary(self) -> Dict[str, Any]:
        return {
            "source_commit": self.manifest["source_commit"],
            "ledger_blob_sha": self.manifest["ledger_blob_sha"],
            "reconciliation_status": self.manifest["reconciliation_status"],
            "historical_research_items_found": self.manifest["historical_research_items_found"],
            "known_duplicate_or_variant_items": self.manifest["known_duplicate_or_variant_items"],
            "prospective_validated": self.manifest["prospective_validated"],
            "global_effective_trials": self.manifest["global_effective_trials"],
            "loaded_record_count": len(self.records),
            "recovered_source_review_count": len(self.source_reviews),
            "recovered_source_reviews_hash": self._source_review_hash(),
            "read_only": True,
        }
