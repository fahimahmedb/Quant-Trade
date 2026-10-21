#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from research.research_os.expansion.v2_pipeline import run_pre_outcome_pipeline


ROOT = Path(__file__).resolve().parents[1]


def assert_exact_source(sha: str) -> None:
    try:
        observed = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                           stderr=subprocess.DEVNULL, text=True).strip()
        if observed != sha:
            raise SystemExit("CODE_HEAD_MISMATCH")
        changed = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", "src", "research", "deploy", "scripts",
             "tests/fixtures"], cwd=ROOT, capture_output=True)
    except (OSError, subprocess.CalledProcessError):
        raise SystemExit("EXACT_SOURCE_CHECK_UNAVAILABLE") from None
    if changed.returncode == 1:
        raise SystemExit("DIRTY_EXECUTABLE_TREE_CANNOT_PROVE_EXACT_SHA")
    if changed.returncode:
        raise SystemExit("EXACT_SOURCE_CHECK_UNAVAILABLE")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an exact-head Oracle V2 Core pre-outcome qualification receipt.")
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    fixture_path = Path(args.fixture)
    output_path = Path(args.output)
    if len(args.sha) != 40 or any(c not in "0123456789abcdef" for c in args.sha):
        raise SystemExit("--sha must be a full lowercase Git commit SHA")
    assert_exact_source(args.sha)

    bundle = json.loads(fixture_path.read_text(encoding="utf-8"))
    receipt = run_pre_outcome_pipeline(bundle)
    if receipt["status"] != "READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY":
        raise SystemExit("unexpected candidate qualification status")
    if receipt["system_qualification"] != "AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED":
        raise SystemExit("unexpected V2 Core qualification status")
    if receipt["outcome_accessed"] is not False or receipt["economic_claim_authorized"] is not False:
        raise SystemExit("qualification must remain pre-outcome and non-economic")
    if any(receipt["authority"].values()):
        raise SystemExit("V2 Core authority must remain fully closed")

    artifact = {
        "schema_version": "oracle-v2-core-exact-head-verification-v1",
        "verified_commit_sha": args.sha,
        "fixture_path": str(fixture_path),
        "fixture_sha256": sha256_file(fixture_path),
        "receipt": receipt,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": artifact["receipt"]["system_qualification"],
        "verified_commit_sha": args.sha,
        "fixture_sha256": artifact["fixture_sha256"],
        "receipt_hash": receipt["receipt_hash"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
