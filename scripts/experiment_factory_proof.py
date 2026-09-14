#!/usr/bin/env python3
"""Exact-head proof checks for the V2 outcome-blind Research Factory core."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "37f298423ca4a100c1c633da2c3c6c2641d8dd8e"
ALLOWED_PREFIXES = (
    "src/quant/factory/",
    "schemas/experiment_",
    "tests/test_experiment_",
    "tests/test_outcome_firewall_",
    "tests/test_power_",
    "scripts/experiment_",
)
FORBIDDEN_PREFIXES = (
    "artifacts/sec_form4_census/",
    "src/quant/dataplane/sec_form4.py",
)
sys.path.insert(0, str(ROOT / "src"))

from quant.factory.experiments import ExperimentStatus, PreregistrationContract


def check_schemas() -> None:
    prereg = json.loads((ROOT / "schemas" / "experiment_preregistration.json").read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "schemas" / "experiment_registry.json").read_text(encoding="utf-8"))
    expected_immutable = list(PreregistrationContract("schema", "schema", 20, "SPY", (), "schema").immutable_fields)
    if prereg["properties"]["immutable_fields"]["const"] != expected_immutable:
        raise SystemExit("experiment preregistration schema drift")
    if registry["properties"]["status"]["enum"] != [status.value for status in ExperimentStatus]:
        raise SystemExit("experiment registry state schema drift")
    expected_fields = {"experiment_id", "experiment_key", "version", "lane", "status", "dataset_refs", "protocol", "protocol_hash"}
    if set(registry["required"]) != expected_fields:
        raise SystemExit("experiment registry required-field drift")


def run_pattern(pattern: str) -> int:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-p", pattern, "-v"],
        env=env,
        check=False,
    )
    return completed.returncode


def git_capture(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def check_exact_head_repository() -> str:
    try:
        head = git_capture("rev-parse", "HEAD")
        merge_base = git_capture("merge-base", BASE_SHA, "HEAD")
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise SystemExit("exact-head proof requires a git checkout containing the mandated base commit") from exc
    if merge_base != BASE_SHA:
        raise SystemExit(f"HEAD is not descended from mandated base {BASE_SHA}: merge-base={merge_base}")
    subprocess.run(["git", "diff", "--check", f"{BASE_SHA}...HEAD"], cwd=ROOT, check=True)
    changed = [line for line in git_capture("diff", "--name-only", f"{BASE_SHA}...HEAD").splitlines() if line]
    outside = [path for path in changed if not path.startswith(ALLOWED_PREFIXES)]
    forbidden = [path for path in changed if path.startswith(FORBIDDEN_PREFIXES)]
    if outside:
        raise SystemExit(f"changed paths outside Builder B ownership: {outside}")
    if forbidden:
        raise SystemExit(f"forbidden paths changed: {forbidden}")
    status = git_capture("status", "--porcelain")
    if status:
        raise SystemExit(f"working tree is not clean:\n{status}")
    print(f"exact-head: {head}")
    print(f"base: {BASE_SHA}")
    print(f"changed owned paths: {len(changed)}")
    return head


def main() -> int:
    check_schemas()
    for pattern in ("test_experiment_*.py", "test_outcome_firewall_*.py", "test_power_*.py"):
        code = run_pattern(pattern)
        if code:
            return code
    check_exact_head_repository()
    print("Builder B exact-head proof gate: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
