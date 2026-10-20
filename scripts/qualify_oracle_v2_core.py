#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from research.research_os.expansion.v2_pipeline import run_pre_outcome_pipeline


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
