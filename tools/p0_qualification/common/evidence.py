"""Evidence classification and deterministic artifact serialization.

Every material conclusion this harness produces carries one of the five
epistemic classifications required by the mission contract, and every
defect-like result carries one of the five defect classes. Nothing here
infers a stronger classification than the evidence supports; when in doubt
the more conservative label is used.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[3]

#: Epistemic classification of a conclusion. Never inferred beyond the
#: evidence actually gathered.
EPISTEMIC_CLASSES = ("FACT", "CLAIM", "INFERENCE", "RECOMMENDATION", "UNKNOWN")

#: Defect classification, exactly as the mission contract requires.
DEFECT_CLASSES = (
    "REAL_DEFECT", "TEST_DEFECT", "MISSING_PROOF", "TARGET_HOST_ONLY", "NON_ISSUE",
)

#: Which repository/target/live domain a property still depends on.
DOMAINS = ("REPOSITORY", "TARGET_HOST", "LIVE_SOURCE")


class EvidenceError(RuntimeError):
    """Raised when an evidence artifact would misrepresent what was proven."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_head_sha(root: Path = REPO_ROOT) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def git_is_clean(root: Path = REPO_ROOT) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True, check=True)
    return result.stdout.strip() == ""


def canonical_json(payload: Any) -> str:
    """One rendering, matching the production fingerprint convention."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_of(payload: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def verified_input_tree_digest(paths: Iterable[str], root: Path = REPO_ROOT) -> str:
    """Digest over exact file bytes under the named repo-relative paths.

    This is independent of ``git rev-parse HEAD``: it proves the bytes on disk
    match what the report claims, even if HEAD were later moved or the tree
    were dirty. Deterministic, sorted by relative path.
    """
    digests: dict[str, str] = {}
    for rel in sorted(paths):
        base = root / rel
        if base.is_file():
            digests[rel] = "sha256:" + hashlib.sha256(base.read_bytes()).hexdigest()
            continue
        if not base.exists():
            raise EvidenceError(f"VERIFIED_INPUT_TREE_PATH_MISSING:{rel}")
        for file_path in sorted(base.rglob("*")):
            if file_path.is_file() and "__pycache__" not in file_path.parts:
                relative = str(file_path.relative_to(root))
                digests[relative] = "sha256:" + hashlib.sha256(file_path.read_bytes()).hexdigest()
    return sha256_of(digests)


@dataclass
class EvidenceRecord:
    """One classified conclusion, bound to exact SHA and reproduction command."""

    property_name: str
    classification: str
    defect_class: str
    domain: str
    detail: str
    exact_sha: str
    reproduce_command: str | None = None
    residual: str | None = None

    def __post_init__(self) -> None:
        if self.classification not in EPISTEMIC_CLASSES:
            raise EvidenceError(f"INVALID_EPISTEMIC_CLASS:{self.classification}")
        if self.defect_class not in DEFECT_CLASSES:
            raise EvidenceError(f"INVALID_DEFECT_CLASS:{self.defect_class}")
        if self.domain not in DOMAINS:
            raise EvidenceError(f"INVALID_DOMAIN:{self.domain}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "property": self.property_name,
            "classification": self.classification,
            "defect_class": self.defect_class,
            "domain": self.domain,
            "detail": self.detail,
            "exact_sha": self.exact_sha,
            "reproduce_command": self.reproduce_command,
            "residual": self.residual,
        }


@dataclass
class Report:
    """A machine-readable, hash-addressable qualification-harness artifact."""

    gate: str
    exact_sha: str
    generated_at_utc: str = field(default_factory=utc_now_iso)
    python_version: str = field(default_factory=lambda: sys.version)
    records: list[EvidenceRecord] = field(default_factory=list)
    body: dict[str, Any] = field(default_factory=dict)

    def add(self, record: EvidenceRecord) -> None:
        self.records.append(record)

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "gate": self.gate,
            "exact_sha": self.exact_sha,
            "generated_at_utc": self.generated_at_utc,
            "python_version": self.python_version,
            "records": [record.to_dict() for record in self.records],
            "body": self.body,
            "no_t0_declared": True,
            "no_target_host_claimed": True,
            "no_p14d_amendment_claimed": True,
        }
        payload["report_digest"] = sha256_of({k: v for k, v in payload.items()
                                              if k != "report_digest"})
        return payload

    def write(self, path: Path) -> dict[str, Any]:
        payload = self.to_dict()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return payload
