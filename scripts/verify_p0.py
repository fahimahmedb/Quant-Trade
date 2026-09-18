"""Produce and check a reproducible verification record for the P0 lane.

Blue's fourth finding: at the reviewed head, "232 tests pass" was a PR claim with
no workflow run attached, so it could not be independently observed. CI now runs
the suite, and this script writes the same facts into a committed artifact so the
claim is checkable from the repository alone, against a named commit.

It records what was run, on what, and what came back. It does not interpret
results and it publishes nothing about captured data: test counts are counts of
tests, and no SEC request is made.

    python3 scripts/verify_p0.py --write     # run the suites and record the result
    python3 scripts/verify_p0.py --check     # fail if the record does not match HEAD
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# The in-process test counts import the test modules, which import the package,
# so src must be importable here too. Without it unittest substitutes a single
# _FailedTest and the recorded count is silently wrong.
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

ARTIFACT = ROOT / "handoff" / "SEC_FORM4_P0_VERIFICATION.json"

#: Files whose content the recorded result actually depends on. A digest over
#: these is what makes the record checkable: the commit containing the record
#: cannot name its own SHA, but it can pin the tree it was produced from.
VERIFIED_TREES = ("src", "tests", "scripts")

SUITES = {
    "full_unit_suite": ["python3", "-m", "unittest", "discover", "-s", "tests"],
    "sec_p0_lane_suite": ["python3", "-m", "unittest", "tests.test_sec_form4_capture"],
}
CHECKS = {
    "generated_schema_drift": ["python3", "scripts/generate_schemas.py", "--check"],
    "status_artifact_freshness": ["python3", "scripts/status_artifacts.py", "--check"],
}


def git_sha() -> str:
    head = ROOT / ".git" / "HEAD"
    if not head.exists():
        return "unknown"
    content = head.read_text(encoding="utf-8").strip()
    if not content.startswith("ref:"):
        return content
    ref = content.split(":", 1)[1].strip()
    direct = ROOT / ".git" / ref
    if direct.exists():
        return direct.read_text(encoding="utf-8").strip()
    packed = ROOT / ".git" / "packed-refs"
    if packed.exists():
        for line in packed.read_text(encoding="utf-8").splitlines():
            if line.startswith("#") or " " not in line:
                continue
            sha, name = line.split(" ", 1)
            if name.strip() == ref:
                return sha.strip()
    return "unknown"


def verified_tree_digest() -> str:
    """Digest over the sources the recorded verification covers."""
    import hashlib
    digest = hashlib.sha256()
    for tree in VERIFIED_TREES:
        for path in sorted((ROOT / tree).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
            digest.update(path.read_bytes())
    return "sha256:" + digest.hexdigest()


def discovered_test_count() -> int:
    """What unittest discovery sees, without executing anything."""
    return unittest.TestLoader().discover(str(ROOT / "tests"),
                                          pattern="test*.py").countTestCases()


def lane_test_count() -> int:
    """Count the lane suite, failing loudly rather than recording a wrong number.

    ``loadTestsFromName`` substitutes a single ``_FailedTest`` when the module
    cannot be imported, which silently records 1. That is exactly the kind of
    fabricated-looking figure this artifact must not carry.
    """
    loaded = unittest.TestLoader().loadTestsFromName("tests.test_sec_form4_capture")
    count = loaded.countTestCases()
    if count <= 1:
        raise RuntimeError(
            "the lane suite did not load; refusing to record a placeholder count")
    return count


def run(command: list[str]) -> dict[str, object]:
    environment = {"PYTHONPATH": "src", "PATH": "/usr/bin:/bin:/usr/local/bin"}
    import os
    merged = {**os.environ, **environment}
    # Deliberately unset: the lane must fail closed during verification.
    merged.pop("QUANT_SEC_USER_AGENT", None)
    completed = subprocess.run(command, cwd=str(ROOT), env=merged,
                               capture_output=True, text=True, timeout=1800)
    tail = (completed.stderr or completed.stdout or "").strip().splitlines()
    return {"command": " ".join(command),
            "exit_code": completed.returncode,
            "result": "PASS" if completed.returncode == 0 else "FAIL",
            "last_line": tail[-1] if tail else ""}


def build_record() -> dict[str, object]:
    suites = {name: run(command) for name, command in SUITES.items()}
    checks = {name: run(command) for name, command in CHECKS.items()}
    return {
        "artifact": "sec_form4_p0_verification",
        "purpose": ("Reproducible record of the verification actually executed, so the "
                    "test claim on the pull request is checkable from the repository "
                    "rather than asserted in prose."),
        # The commit at the time of recording. The commit that *contains* this
        # record cannot name its own SHA, so this is the parent and the tree
        # digest below is what --check actually enforces.
        "verified_sha": git_sha(),
        "verified_tree_digest": verified_tree_digest(),
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "tests_discovered": discovered_test_count(),
        "sec_p0_lane_tests_discovered": lane_test_count(),
        "suites": suites,
        "checks": checks,
        "all_passed": all(entry["result"] == "PASS"
                          for entry in list(suites.values()) + list(checks.values())),
        "network_requests_made": 0,
        "sec_identity_configured_during_verification": False,
        "note": ("Counts here are counts of tests and checks. Nothing in this artifact "
                 "describes captured SEC data, and no SEC request is made while "
                 "producing it."),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--sha", help="expected commit, for CI")
    args = parser.parse_args()

    if args.write:
        record = build_record()
        ARTIFACT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
        print(json.dumps({key: record[key] for key in
                          ("verified_sha", "tests_discovered",
                           "sec_p0_lane_tests_discovered", "all_passed")},
                         indent=2, sort_keys=True))
        return 0 if record["all_passed"] else 1

    if not ARTIFACT.exists():
        print(f"missing verification artifact: {ARTIFACT.relative_to(ROOT)}")
        return 1
    record = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    problems: list[str] = []
    if not record.get("all_passed"):
        problems.append("the recorded verification did not pass")
    discovered = discovered_test_count()
    if record.get("tests_discovered") != discovered:
        problems.append(f"tests_discovered {record.get('tests_discovered')} "
                        f"!= {discovered} discovered now")
    lane = lane_test_count()
    if record.get("sec_p0_lane_tests_discovered") != lane:
        problems.append(f"sec_p0_lane_tests_discovered "
                        f"{record.get('sec_p0_lane_tests_discovered')} != {lane}")
    # The tree digest is the real gate: it fails if any verified source changed
    # after the record was written, whatever the commit graph looks like.
    digest = verified_tree_digest()
    if record.get("verified_tree_digest") != digest:
        problems.append("verified_tree_digest does not match the working tree")
    if problems:
        print("verification record is stale or inconsistent:")
        for problem in problems:
            print(f"  - {problem}")
        print("run: python3 scripts/verify_p0.py --write")
        return 1
    print(f"verification record matches this tree: {record['tests_discovered']} tests "
          f"({record['sec_p0_lane_tests_discovered']} in the SEC P0 lane), all passed; "
          f"recorded against commit {record.get('verified_sha')}")
    if args.sha and record.get("verified_sha") != args.sha:
        # Expected for the commit that carries the record. Reported, not failed.
        print(f"note: recorded against {record.get('verified_sha')}, "
              f"now checked at {args.sha}; the tree digest is what was enforced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
