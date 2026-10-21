from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .research_action_planner import plan_research_action
from .scientific_memory import ScientificMemoryIndex, normalize_legacy_record
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
    """Load optional planning context without converting absence into availability."""
    if not path.exists():
        return {}
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError("research planning context must be a JSON object: " + str(path))
    return payload


class LegacyKnowledgeBase:
    """Legacy compatibility surface over CP069 provenance and canonical Scientific Memory.

    CP069 remains authoritative for recovered-source review provenance. W1 Scientific
    Memory is additive: it normalizes the immutable imported ledger into the canonical
    fail-closed memory contract without replacing the CP069 source-review law.

    Mega-A adds read-only semantic feedback and a next-research-action recommendation.
    It does not create a second memory store or gain scheduler authority.
    """

    def __init__(
        self,
        manifest: Dict[str, Any],
        ledger: Optional[Dict[str, Any]] = None,
        research_context: Optional[Dict[str, Any]] = None,
    ):
        self.manifest = manifest
        self.ledger = ledger or {"records": []}
        self.records = list(self.ledger.get("records") or [])
        self.research_context = research_context or {}

        # CP069 law: provenance recovery remains separate from the immutable ledger.
        self.source_reviews = deepcopy(manifest.get("recovered_source_reviews", []))
        self._validate_source_reviews()

        self.by_id: Dict[str, Dict[str, Any]] = {}
        for record in self.records:
            for key in ("HYPOTHESIS_ID", "LEGACY_ID_IF_ANY"):
                value = record.get(key)
                if isinstance(value, str) and value and value != "UNKNOWN":
                    self.by_id[value] = record

        # W1 Memory law: one canonical normalized view over the existing immutable
        # source ledger; no second truth store is created here.
        self._memory_all = [normalize_legacy_record(record, self.manifest) for record in self.records]
        self._memory_by_source_id: Dict[str, Dict[str, Any]] = {}
        for record, memory in zip(self.records, self._memory_all):
            for key in ("HYPOTHESIS_ID", "LEGACY_ID_IF_ANY"):
                value = record.get(key)
                if isinstance(value, str) and value and value != "UNKNOWN":
                    self._memory_by_source_id[value] = memory
        self._memory_canonical = [record for record in self._memory_all if record.get("canonical") is True]
        self._memory_index = ScientificMemoryIndex(self._memory_canonical)

    def _validate_source_reviews(self) -> None:
        fields = {
            "source_id",
            "historical_id",
            "mechanism",
            "classification",
            "researcher_decision",
            "judge_verdict",
            "failure_scope",
            "limitations",
            "revisit_conditions",
            "source_commit",
            "source_refs",
        }
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
            if (
                entry["classification"] != "HISTORICAL_NEGATIVE_WITH_LIMITATIONS"
                or entry["researcher_decision"] != "KILL"
                or entry["judge_verdict"] != "REJECT"
            ):
                raise ValueError("LEGACY_SOURCE_REVIEW_CLASSIFICATION_INVALID")
            for key in ("limitations", "revisit_conditions"):
                if (
                    not isinstance(entry[key], list)
                    or not entry[key]
                    or any(not isinstance(v, str) or not v.strip() for v in entry[key])
                ):
                    raise ValueError("LEGACY_SOURCE_REVIEW_SCOPE_REQUIRED:" + key)
            if not re.fullmatch(r"[0-9a-f]{40}", entry["source_commit"]):
                raise ValueError("LEGACY_SOURCE_REVIEW_COMMIT_INVALID")
            if not isinstance(entry["source_refs"], list) or not entry["source_refs"]:
                raise ValueError("LEGACY_SOURCE_REVIEW_REFS_REQUIRED")
            for ref in entry["source_refs"]:
                if (
                    not isinstance(ref, dict)
                    or set(ref) != {"path", "blob_sha"}
                    or not isinstance(ref["path"], str)
                    or not ref["path"]
                    or ref["path"].startswith("/")
                    or ".." in ref["path"].split("/")
                    or not isinstance(ref["blob_sha"], str)
                    or not re.fullmatch(r"[0-9a-f]{40}", ref["blob_sha"])
                ):
                    raise ValueError("LEGACY_SOURCE_REVIEW_REF_INVALID")

    def _source_review_hash(self) -> str:
        return hashlib.sha256(
            json.dumps(self.source_reviews, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

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

    def scientific_memory_records(self, *, include_review: bool = False) -> List[Dict[str, Any]]:
        source = self._memory_all if include_review else self._memory_canonical
        return deepcopy(source)

    def scientific_memory_index(self) -> ScientificMemoryIndex:
        # Return a fresh read view so callers cannot mutate this base's internal view.
        return ScientificMemoryIndex(self._memory_canonical)

    def memory_normalization_report(self) -> Dict[str, Any]:
        dispositions: Dict[str, int] = {}
        review_reasons: Dict[str, int] = {}
        for record in self._memory_all:
            disposition = record["scientific_disposition"]
            dispositions[disposition] = dispositions.get(disposition, 0) + 1
            if record.get("canonical") is not True:
                for reason in record.get("reason_codes") or []:
                    review_reasons[reason] = review_reasons.get(reason, 0) + 1
        return {
            "source_record_count": len(self.records),
            "canonical_memory_count": len(self._memory_canonical),
            "review_memory_count": len(self._memory_all) - len(self._memory_canonical),
            "scientific_dispositions": dict(sorted(dispositions.items())),
            "review_reason_counts": dict(sorted(review_reasons.items())),
            "single_score_computed": False,
            "empirical_similarity_computed": False,
            "empirical_correlation": "UNKNOWN",
        }

    @staticmethod
    def _memory_public_view(memory: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "memory_id": memory["memory_id"],
            "canonical": memory["canonical"],
            "scientific_disposition": memory["scientific_disposition"],
            "epistemic_status": memory["epistemic_status"],
            "claim_ceiling": memory["claim_ceiling"],
            "record_status": memory["record_status"],
            "reason_codes": deepcopy(memory.get("reason_codes") or []),
            "identity": deepcopy(memory["identity"]),
        }

    def _recovered_source_matches(self, cid: Any, c_tokens: set[str]) -> List[Dict[str, Any]]:
        source_matches: List[Dict[str, Any]] = []
        for entry in self.source_reviews:
            r_tokens = _tokens(entry["mechanism"])
            overlap = len(c_tokens & r_tokens) / len(c_tokens | r_tokens) if c_tokens and r_tokens else 0
            exact_id = cid == entry["historical_id"]
            if exact_id or overlap >= 0.30:
                source_matches.append(
                    dict(
                        deepcopy(entry),
                        match_reason=(
                            "HISTORICAL_ID_REQUIRES_SCOPE_REVIEW"
                            if exact_id
                            else "MECHANISM_TOKEN_OVERLAP"
                        ),
                        overlap=round(overlap, 4),
                        scientific_equivalence="NOT_ESTABLISHED",
                    )
                )
        return source_matches

    def screen_candidate(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Apply CP079/W1 memory law, then add Mega-A read-only semantic feedback."""
        cid = candidate.get("hypothesis_id")
        c_tokens = _tokens(candidate.get("mechanism", ""), candidate.get("economic_tags", []))
        source_matches = self._recovered_source_matches(cid, c_tokens)

        candidate_facets = {
            "mechanism": candidate.get("mechanism"),
            "payer": candidate.get("payer"),
            "constrained_actor": candidate.get("constrained_actor"),
            "timing_clock": candidate.get("timing_clock") or candidate.get("clock"),
            "universe": candidate.get("universe"),
            "instrument": candidate.get("instrument"),
            "source_family": candidate.get("source_family"),
            "economic_exposure": candidate.get("economic_exposure"),
        }
        memory_matches = self._memory_index.structural_retrieval(candidate_facets)

        # Preserve CP079 lexical review hints; they remain review metadata only.
        hints: List[Dict[str, Any]] = []
        mega_matches: List[Dict[str, Any]] = []
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
                memory = self._memory_by_source_id.get(record.get("HYPOTHESIS_ID"))
                hints.append(
                    {
                        "hypothesis_id": record.get("HYPOTHESIS_ID"),
                        "research_family_id": record.get("RESEARCH_FAMILY_ID"),
                        "structural_token_overlap_hint": round(overlap, 4),
                        "similarity_kind": "LEGACY_TOKEN_OVERLAP_REVIEW_HINT_ONLY",
                        "empirical_similarity_computed": False,
                        "empirical_correlation": "UNKNOWN",
                        "scientific_memory": self._memory_public_view(memory) if memory else None,
                        "historical_result": record.get("RESULT", "UNKNOWN"),
                        "historical_result_is_scientific_authority": False,
                        "decision": record.get("RESEARCH_DECISION", "UNKNOWN"),
                        "next_legitimate_step": record.get("NEXT_LEGITIMATE_STEP", "UNKNOWN"),
                    }
                )
                mega_matches.append(
                    {
                        "hypothesis_id": record.get("HYPOTHESIS_ID"),
                        "research_family_id": record.get("RESEARCH_FAMILY_ID"),
                        "overlap": round(overlap, 4),
                        "historical_result": record.get("RESULT", "UNKNOWN"),
                        "decision": record.get("RESEARCH_DECISION", "UNKNOWN"),
                        "next_legitimate_step": record.get("NEXT_LEGITIMATE_STEP", "UNKNOWN"),
                        "scientific_equivalence": "NOT_ESTABLISHED_BY_TOKEN_OVERLAP",
                    }
                )
        hints.sort(key=lambda x: x["structural_token_overlap_hint"], reverse=True)
        mega_matches.sort(key=lambda x: x["overlap"], reverse=True)

        # Mega-A's adapter is read-only and is not a replacement for W1 normalized memory.
        memory_view = qualified_legacy_memory_view(self.records, self.manifest)
        feedback = scientific_memory_feedback(candidate, memory_view["canonical_records"])
        action_receipt = plan_research_action(feedback, self.research_context)

        status_by_action = {
            "NO_BUILD": "BLOCK_KNOWN_NEGATIVE_SAME_SEMANTIC_FAMILY",
            "REPAIR_PROTOCOL": "BLOCK_INVALIDATED_PROTOCOL_REPAIR_REQUIRED",
            "PARK": "BLOCK_HISTORICAL_BLOCKER_UNRESOLVED",
            "ESCALATE_VALIDATION": "BLOCK_POSITIVE_INSUFFICIENT_VALIDATION_REQUIRED",
        }

        exact_record = self.by_id.get(cid)
        if exact_record is not None:
            memory = self._memory_by_source_id[cid]
            scientific_memory = self._memory_public_view(memory)
            scientific_memory.update(
                {
                    "view_hash": memory_view["view_hash"],
                    "canonical_count": memory_view["canonical_count"],
                    "review_count": memory_view["review_count"],
                    "feedback": feedback,
                    "persistent_store_created": False,
                }
            )
            return {
                # Operational identity collision remains fail-closed. It is not a
                # scientific-equivalence claim.
                "status": "BLOCK_EXACT_LEGACY_DUPLICATE",
                "matched_hypothesis_id": exact_record.get("HYPOTHESIS_ID"),
                "scientific_memory": scientific_memory,
                "scientific_authority": (
                    "CANONICAL_SCIENTIFIC_MEMORY"
                    if memory["canonical"]
                    else "REVIEW_STILL_REQUIRED"
                ),
                "historical_result": exact_record.get("RESULT", "UNKNOWN"),
                "historical_result_is_scientific_authority": False,
                "historical_decision": exact_record.get("RESEARCH_DECISION", "UNKNOWN"),
                "next_legitimate_step": exact_record.get("NEXT_LEGITIMATE_STEP", "UNKNOWN"),
                "recovered_source_matches": source_matches,
                "recovered_source_reviews_hash": self._source_review_hash(),
                "matches": mega_matches[:5],
                "lexical_review_required": bool(mega_matches or source_matches),
                "lexical_review_status": (
                    "REVIEW_LEGACY_OVERLAP"
                    if mega_matches or source_matches
                    else "NO_LEXICAL_OVERLAP_REVIEW"
                ),
                "novelty_status": "NOT_INFERRED_BY_LEGACY_GATE",
                "next_research_action": action_receipt,
                "identifier_collision_scientific_equivalence": (
                    "NOT_ESTABLISHED_BY_IDENTIFIER_ALONE"
                ),
            }

        if feedback.get("allow_candidate_progress") is not True and feedback.get("action") in status_by_action:
            status = status_by_action[feedback["action"]]
        elif feedback.get("action") == "ARCHAEOLOGY_LOOKUP" and (mega_matches or source_matches):
            status = "REVIEW_LEGACY_OVERLAP"
        else:
            # Structural and lexical overlap remain review metadata. They cannot by
            # themselves establish scientific equivalence or upgrade the top-level gate.
            status = "NO_EXACT_LEGACY_CONFLICT"

        return {
            "status": status,
            "scientific_memory_matches": memory_matches,
            "legacy_overlap_hints": hints[:5],
            "recovered_source_matches": source_matches,
            "recovered_source_reviews_hash": self._source_review_hash(),
            "structural_overlap_is_empirical_correlation": False,
            "empirical_correlation": "UNKNOWN",
            "matches": mega_matches[:5],
            "lexical_review_required": bool(mega_matches or source_matches),
            "lexical_review_status": (
                "REVIEW_LEGACY_OVERLAP"
                if mega_matches or source_matches
                else "NO_LEXICAL_OVERLAP_REVIEW"
            ),
            "novelty_status": (
                "UNRESOLVED_NOT_CLAIMED"
                if feedback.get("action") == "ARCHAEOLOGY_LOOKUP"
                else "NOT_INFERRED_BY_LEGACY_GATE"
            ),
            "scientific_memory": {
                "view_hash": memory_view["view_hash"],
                "canonical_count": memory_view["canonical_count"],
                "review_count": memory_view["review_count"],
                "feedback": feedback,
                "persistent_store_created": False,
            },
            "next_research_action": action_receipt,
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
            "scientific_memory": self.memory_normalization_report(),
            "read_only": True,
        }
