from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Dict, Iterable, List

from .control_plane import load_control_plane
from .legacy import LegacyKnowledgeBase


AUTHORITY_KEYS = (
    "economic_experiment_authorized",
    "prospective_observation_authorized",
    "real_capital_authorized",
    "live_trading_authorized",
)
TOKEN_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "into", "than", "only",
    "may", "can", "could", "would", "should", "being", "been", "are", "was", "were",
    "its", "their", "our", "not", "without", "while", "then", "when", "where", "which",
    "currently", "current", "candidate", "fundamental", "mechanism", "economic", "economics",
    "claim", "business", "medium", "term", "later", "simple", "generic", "new",
}
TOKEN_NORMALIZATION = {
    "upgrades": "upgrade",
    "upgraded": "upgrade",
    "upgrading": "upgrade",
    "systems": "system",
    "shipments": "shipment",
    "customers": "customer",
    "margins": "margin",
    "revenues": "revenue",
    "cancellations": "cancellation",
    "cancelled": "cancellation",
    "orders": "order",
}


class WorkerPreflightBlock(RuntimeError):
    """A wake cannot safely proceed."""


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(_text(item) for item in value.values())
    return ""


def mechanism_tokens(value: str) -> List[str]:
    out = set()
    for token in TOKEN_RE.findall((value or "").lower()):
        if len(token) < 3 or token in STOPWORDS:
            continue
        out.add(TOKEN_NORMALIZATION.get(token, token))
    return sorted(out)


def _hypothesis_id(record: Dict[str, Any], path: str) -> str:
    for key in ("hypothesis_id", "candidate_id"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            result = value.strip()
            if key == "candidate_id" and path != "<candidate>" and Path(path).stem != result:
                raise WorkerPreflightBlock(
                    f"CURRENT_CANDIDATE_ID_PATH_MISMATCH:{path}:{result}"
                )
            return result
    raise WorkerPreflightBlock(f"CURRENT_HYPOTHESIS_ID_MISSING:{path}")


def _entity(record: Dict[str, Any]) -> str:
    primary_document = record.get("primary_document") or {}
    decision_map = record.get("decision_map") or {}
    for value in (
        record.get("issuer"),
        decision_map.get("company"),
        record.get("company"),
        primary_document.get("issuer"),
    ):
        if isinstance(value, str) and value.strip():
            return " ".join(TOKEN_RE.findall(value.lower())) or "UNKNOWN"
    return "UNKNOWN"


def _generation(record: Dict[str, Any]) -> str:
    value = record.get("generation_id")
    if isinstance(value, str) and value.strip():
        return value.strip()
    value = record.get("generation")
    if type(value) is int and value >= 0:
        return f"G{value}"
    if isinstance(value, str) and value.strip():
        return value.strip()
    return "UNKNOWN"


def _mechanism(record: Dict[str, Any]) -> str:
    value = record.get("mechanism")
    if isinstance(value, str) and value.strip():
        return value.strip()

    thesis = record.get("thesis")
    chain = record.get("causal_chain")
    combined = " ".join(part for part in (_text(thesis), _text(chain)) if part)
    if combined.strip():
        return combined.strip()

    mechanism_family = record.get("mechanism_family")
    candidate = record.get("candidate_hypothesis") or {}
    candidate_text = " ".join(
        part
        for part in (
            _text(mechanism_family),
            _text(candidate.get("claim")),
            _text(candidate.get("causal_chain")),
        )
        if part
    )
    if candidate_text.strip():
        return candidate_text.strip()
    return ""


def _family(record: Dict[str, Any]) -> str:
    for value in (record.get("family_id"), record.get("mechanism_family")):
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    return "UNKNOWN"


def _freeze_state(record: Dict[str, Any]) -> str:
    value = record.get("freeze_status", record.get("status", "UNKNOWN"))
    return str(value or "UNKNOWN")


def normalize_hypothesis(record: Dict[str, Any], *, path: str) -> Dict[str, Any]:
    if not isinstance(record, dict):
        raise WorkerPreflightBlock(f"CURRENT_HYPOTHESIS_NOT_OBJECT:{path}")
    hypothesis_id = _hypothesis_id(record, path)
    generation_id = _generation(record)
    if generation_id == "UNKNOWN":
        raise WorkerPreflightBlock(f"CURRENT_HYPOTHESIS_GENERATION_UNSUPPORTED:{path}")
    mechanism = _mechanism(record)
    tokens = mechanism_tokens(mechanism)
    if not mechanism or not tokens:
        raise WorkerPreflightBlock(f"CURRENT_HYPOTHESIS_MECHANISM_UNSUPPORTED:{path}")

    authority = record.get("authority") or {}
    unsafe = [key for key in AUTHORITY_KEYS if authority.get(key) is not False]
    if unsafe:
        raise WorkerPreflightBlock(
            f"CURRENT_HYPOTHESIS_AUTHORITY_UNSAFE:{path}:" + ",".join(unsafe)
        )

    normalized = {
        "hypothesis_id": hypothesis_id,
        "generation_id": generation_id,
        "family_id": _family(record),
        "entity": _entity(record),
        "freeze_state": _freeze_state(record),
        "mechanism": mechanism,
        "mechanism_tokens": tokens,
        "source_path": path,
        "source_hash": canonical_hash(record),
    }
    return normalized


def load_current_hypothesis_corpus(base: Path) -> Dict[str, Any]:
    root = base / "hypotheses"
    if not root.is_dir():
        raise WorkerPreflightBlock("CURRENT_HYPOTHESIS_CORPUS_MISSING")
    paths = sorted(root.glob("*.json"))
    if not paths:
        raise WorkerPreflightBlock("CURRENT_HYPOTHESIS_CORPUS_EMPTY")

    identities = []
    for path in paths:
        try:
            record = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise WorkerPreflightBlock(
                f"CURRENT_HYPOTHESIS_INVALID_JSON:{path.name}:{exc}"
            ) from exc
        identities.append(
            normalize_hypothesis(record, path=str(path.relative_to(base)))
        )

    ids = [item["hypothesis_id"] for item in identities]
    if len(ids) != len(set(ids)):
        raise WorkerPreflightBlock("CURRENT_HYPOTHESIS_DUPLICATE_ID_IN_CORPUS")

    snapshot_payload = [
        {
            "hypothesis_id": item["hypothesis_id"],
            "generation_id": item["generation_id"],
            "source_path": item["source_path"],
            "source_hash": item["source_hash"],
        }
        for item in identities
    ]
    return {
        "status": "PASS",
        "count": len(identities),
        "snapshot_hash": canonical_hash(snapshot_payload),
        "identities": identities,
    }


def _jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    a, b = set(left), set(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def compare_current_identities(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    if left["hypothesis_id"] == right["hypothesis_id"]:
        return {
            "classification": "BLOCK_EXACT_CURRENT_DUPLICATE",
            "review_required": True,
            "mechanism_overlap": 1.0,
            "basis": ["hypothesis_id"],
        }

    entity_known = left["entity"] != "UNKNOWN" and right["entity"] != "UNKNOWN"
    same_entity = entity_known and left["entity"] == right["entity"]
    family_known = left["family_id"] != "UNKNOWN" and right["family_id"] != "UNKNOWN"
    same_family = family_known and left["family_id"] == right["family_id"]
    overlap = _jaccard(left["mechanism_tokens"], right["mechanism_tokens"])

    basis = []
    if same_entity:
        basis.append("entity")
    if same_family:
        basis.append("family_id")
    if overlap >= 0.22:
        basis.append("mechanism_tokens")

    if (same_entity and overlap >= 0.22) or (same_family and overlap >= 0.18) or overlap >= 0.50:
        return {
            "classification": "HIGH_CURRENT_EXPOSURE_OVERLAP_REVIEW",
            "review_required": True,
            "mechanism_overlap": round(overlap, 4),
            "basis": basis,
        }

    # Incomplete identity plus non-trivial mechanism overlap is unresolved. Very
    # low observed overlap is allowed to proceed without claiming proven semantic
    # distinctness; later validators may still restrict it.
    if (not entity_known or not family_known) and overlap >= 0.15:
        return {
            "classification": "UNKNOWN_CURRENT_EXPOSURE_RELATION",
            "review_required": True,
            "mechanism_overlap": round(overlap, 4),
            "basis": basis or ["insufficient_identity"],
        }

    return {
        "classification": "LOW_OBSERVED_OVERLAP_NO_DISTINCTNESS_CLAIM",
        "review_required": False,
        "mechanism_overlap": round(overlap, 4),
        "basis": basis,
    }


def current_corpus_overlap_map(corpus: Dict[str, Any]) -> Dict[str, Any]:
    identities = corpus["identities"]
    pairs = []
    reviews = []
    for index, left in enumerate(identities):
        for right in identities[index + 1 :]:
            relation = compare_current_identities(left, right)
            pair = {
                "left": left["hypothesis_id"],
                "right": right["hypothesis_id"],
                **relation,
            }
            pairs.append(pair)
            if relation["review_required"]:
                reviews.append(pair)
    return {
        "pair_count": len(pairs),
        "review_count": len(reviews),
        "review_pairs": reviews,
        "pairs": pairs,
        "map_hash": canonical_hash(pairs),
    }


def screen_candidate_against_current(
    candidate: Dict[str, Any], corpus: Dict[str, Any]
) -> Dict[str, Any]:
    identity = normalize_hypothesis(candidate, path="<candidate>")
    matches = []
    reasons = []
    for peer in corpus["identities"]:
        relation = compare_current_identities(identity, peer)
        if not relation["review_required"]:
            continue
        match = {
            "peer_hypothesis_id": peer["hypothesis_id"],
            "peer_generation_id": peer["generation_id"],
            **relation,
        }
        matches.append(match)
        if relation["classification"] == "BLOCK_EXACT_CURRENT_DUPLICATE":
            reasons.append("BLOCK_EXACT_CURRENT_DUPLICATE")
        elif relation["classification"] == "HIGH_CURRENT_EXPOSURE_OVERLAP_REVIEW":
            reasons.append("BLOCK_UNRESOLVED_CURRENT_EXPOSURE_OVERLAP")
        else:
            reasons.append("BLOCK_CURRENT_EXPOSURE_IDENTITY_INCOMPLETE")

    return {
        "status": "BLOCK" if reasons else "PASS_CURRENT_CORPUS_SCREEN",
        "candidate_hypothesis_id": identity["hypothesis_id"],
        "candidate_generation_id": identity["generation_id"],
        "current_corpus_snapshot_hash": corpus["snapshot_hash"],
        "block_reasons": sorted(set(reasons)),
        "matches": matches,
        "screen_hash": canonical_hash(
            {
                "candidate": identity,
                "corpus": corpus["snapshot_hash"],
                "matches": matches,
            }
        ),
    }


def verify_materialized_legacy(base: Path) -> Dict[str, Any]:
    manifest_path = base / "legacy" / "source_manifest.json"
    ledger_path = base / "legacy" / "LEGACY_RESEARCH_LEDGER.imported.json"
    if not manifest_path.is_file():
        raise WorkerPreflightBlock("LEGACY_SOURCE_MANIFEST_MISSING")
    if not ledger_path.is_file():
        raise WorkerPreflightBlock("LEGACY_LEDGER_NOT_MATERIALIZED")
    try:
        manifest = json.loads(manifest_path.read_text())
        data = ledger_path.read_bytes()
        ledger = json.loads(data.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorkerPreflightBlock(f"LEGACY_PREFLIGHT_PARSE_FAILED:{exc}") from exc

    expected = manifest.get("ledger_blob_sha")
    actual = git_blob_sha(data)
    if not isinstance(expected, str) or expected != actual:
        raise WorkerPreflightBlock(
            f"LEGACY_LEDGER_BLOB_MISMATCH:expected={expected}:actual={actual}"
        )
    if ledger.get("schema_version") != manifest.get("schema_version"):
        raise WorkerPreflightBlock("LEGACY_LEDGER_SCHEMA_MISMATCH")
    for governance, prefix in (
        (manifest.get("governance") or {}, "LEGACY_MANIFEST"),
        (ledger.get("governance") or {}, "LEGACY_LEDGER"),
    ):
        if governance.get("historical_result_immutability") is not True:
            raise WorkerPreflightBlock(prefix + "_HISTORICAL_IMMUTABILITY_UNSAFE")
        if governance.get("REAL_CAPITAL_AUTHORIZED") is not False:
            raise WorkerPreflightBlock(prefix + "_REAL_CAPITAL_AUTHORITY_UNSAFE")
        if governance.get("LIVE_TRADING_AUTHORIZED") is not False:
            raise WorkerPreflightBlock(prefix + "_LIVE_TRADING_AUTHORITY_UNSAFE")
    records = ledger.get("records")
    if not isinstance(records, list) or not records:
        raise WorkerPreflightBlock("LEGACY_LEDGER_EMPTY")

    knowledge = LegacyKnowledgeBase.load(base)
    summary = knowledge.summary()
    if summary.get("loaded_record_count") != len(records):
        raise WorkerPreflightBlock("LEGACY_KB_RECORD_COUNT_MISMATCH")
    return {
        "status": "PASS",
        "source_commit": manifest.get("source_commit"),
        "ledger_blob_sha": actual,
        "schema_version": ledger.get("schema_version"),
        "reconciliation_status": manifest.get("reconciliation_status"),
        "manifest_historical_research_items_found": manifest.get(
            "historical_research_items_found"
        ),
        "loaded_record_count": len(records),
    }


def verify_task_authority(task: Dict[str, Any]) -> Dict[str, Any]:
    authority = task.get("authority") or {}
    unsafe = [key for key in AUTHORITY_KEYS if authority.get(key) is not False]
    if unsafe:
        raise WorkerPreflightBlock("TASK_AUTHORITY_UNSAFE:" + ",".join(unsafe))
    if task.get("status") not in {"READY", "CLAIMED"}:
        raise WorkerPreflightBlock("TASK_NOT_ADMISSIBLE_FOR_WAKE")
    return {key: False for key in AUTHORITY_KEYS}


def run_worker_preflight(base: Path, *, task: Dict[str, Any] | None = None) -> Dict[str, Any]:
    control = load_control_plane(base)
    if control.get("status") != "PASS":
        raise WorkerPreflightBlock(
            "CONTROL_PLANE_FAIL:" + ",".join(control.get("errors") or [])
        )
    authority = control.get("global_authority") or {}
    for key in AUTHORITY_KEYS:
        if authority.get(key) is not False:
            raise WorkerPreflightBlock(f"CONTROL_PLANE_AUTHORITY_UNSAFE:{key}")

    legacy = verify_materialized_legacy(base)
    corpus = load_current_hypothesis_corpus(base)
    overlap = current_corpus_overlap_map(corpus)
    task_authority = verify_task_authority(task) if task is not None else None

    receipt = {
        "status": "PASS",
        "control_plane": {
            "mode": control.get("mode"),
            "workflow_model": control.get("workflow_model"),
            "authority": {key: False for key in AUTHORITY_KEYS},
        },
        "legacy": legacy,
        "current_corpus": {
            "count": corpus["count"],
            "snapshot_hash": corpus["snapshot_hash"],
            "overlap_map_hash": overlap["map_hash"],
            "review_count": overlap["review_count"],
            "review_pairs": overlap["review_pairs"],
        },
        "task_authority": task_authority,
    }
    receipt["preflight_hash"] = canonical_hash(receipt)
    return receipt
