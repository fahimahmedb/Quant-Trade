from __future__ import annotations

import json
import hashlib
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .research_action_planner import plan_research_action
from .scientific_memory_feedback import qualified_legacy_memory_view, scientific_memory_feedback


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


def _optional_json_object(path: Path) -> Dict[str, Any]:
    """Load optional planning context without turning absence into a Legacy crash.

    The Legacy knowledge base is also used by historical/minimal fixtures that do not
    materialize the runtime control surfaces. Missing optional context therefore means
    "capability/route not proven" to the downstream planner, not "assume available".
    A present but malformed/non-object control artifact remains a hard error.
    """
    if not path.exists():
        return {}
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError("research planning context must be a JSON object: " + str(path))
    return payload


class LegacyKnowledgeBase:
    def __init__(self, manifest: Dict[str, Any], ledger: Optional[Dict[str, Any]] = None,
                 research_context: Optional[Dict[str, Any]] = None):
        self.manifest = manifest
        self.ledger = ledger or {"records": []}
        self.records = list(self.ledger.get("records") or [])
        self.research_context = research_context or {}
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
        context = {
            "capability_registry": _optional_json_object(base / "runtime" / "CAPABILITY_REGISTRY.json"),
            "workflow_lanes": _optional_json_object(base / "runtime" / "WORKFLOW_LANES.json"),
            "control_plane": _optional_json_object(base / "runtime" / "CONTROL_PLANE.json"),
        }
        return cls(manifest, ledger, research_context=context)

    def screen_candidate(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Screen legacy history while keeping semantic truth and review distinct.

        Exact identifier reuse is an operational collision and retains the historical
        fail-closed status. Lexical overlap remains scoped review evidence. Qualified
        Scientific Memory may suppress/park/repair/escalate only after semantic identity
        is complete enough to establish the relation. Missing identity stays explicitly
        unresolved but does not, by itself, rewrite the Legacy gate as a duplicate veto.
        """
        cid = candidate.get("hypothesis_id")
        exact_record = self.by_id.get(cid)
        c_tokens = _tokens(candidate.get("mechanism", ""), candidate.get("economic_tags", []))

        matches: List[Dict[str, Any]] = []
        for record in self.records:
            r_tokens = _tokens(record.get("MECHANISM", ""), record.get("TITLE", ""), record.get("RESEARCH_FAMILY_ID", ""))
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
                    "scientific_equivalence": "NOT_ESTABLISHED_BY_TOKEN_OVERLAP",
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

        memory_view = qualified_legacy_memory_view(self.records, self.manifest)
        feedback = scientific_memory_feedback(candidate, memory_view["canonical_records"])
        action_receipt = plan_research_action(feedback, self.research_context)
        status_by_action = {
            "NO_BUILD": "BLOCK_KNOWN_NEGATIVE_SAME_SEMANTIC_FAMILY",
            "REPAIR_PROTOCOL": "BLOCK_INVALIDATED_PROTOCOL_REPAIR_REQUIRED",
            "PARK": "BLOCK_HISTORICAL_BLOCKER_UNRESOLVED",
            "ESCALATE_VALIDATION": "BLOCK_POSITIVE_INSUFFICIENT_VALIDATION_REQUIRED",
        }

        # Preserve the original operational identity collision exactly. This is not a
        # scientific-equivalence claim; it prevents accidental reuse of a historical ID.
        if exact_record is not None:
            status = "BLOCK_EXACT_LEGACY_DUPLICATE"
        elif feedback.get("allow_candidate_progress") is not True and feedback.get("action") in status_by_action:
            status = status_by_action[feedback["action"]]
        elif feedback.get("action") == "ARCHAEOLOGY_LOOKUP" and (matches or source_matches):
            # Sparse semantic identity cannot dismiss a plausible historical overlap.
            # Keep the historical scoped-review behavior until identity is resolved.
            status = "REVIEW_LEGACY_OVERLAP"
        else:
            # An unresolved identity with no actual legacy collision is not called novel;
            # the additive feedback/action receipt carries that uncertainty forward.
            status = "NO_EXACT_LEGACY_CONFLICT"

        result = {
            "status": status,
            "matches": matches[:5],
            "lexical_review_required": bool(matches or source_matches),
            "lexical_review_status": "REVIEW_LEGACY_OVERLAP" if matches or source_matches else "NO_LEXICAL_OVERLAP_REVIEW",
            "novelty_status": (
                "UNRESOLVED_NOT_CLAIMED" if feedback.get("action") == "ARCHAEOLOGY_LOOKUP"
                else "NOT_INFERRED_BY_LEGACY_GATE"
            ),
            "recovered_source_matches": source_matches,
            "recovered_source_reviews_hash": self._source_review_hash(),
            "scientific_memory": {
                "view_hash": memory_view["view_hash"],
                "canonical_count": memory_view["canonical_count"],
                "review_count": memory_view["review_count"],
                "feedback": feedback,
                "persistent_store_created": False,
            },
            "next_research_action": action_receipt,
        }
        if exact_record is not None:
            result.update({
                "matched_hypothesis_id": exact_record.get("HYPOTHESIS_ID"),
                "historical_result": exact_record.get("RESULT", "UNKNOWN"),
                "historical_decision": exact_record.get("RESEARCH_DECISION", "UNKNOWN"),
                "next_legitimate_step": exact_record.get("NEXT_LEGITIMATE_STEP", "UNKNOWN"),
                "identifier_collision_scientific_equivalence": "NOT_ESTABLISHED_BY_IDENTIFIER_ALONE",
            })
        return result

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
