#!/usr/bin/env python3
"""Proof checks for the V2 outcome-blind Research Factory core."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
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
        [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-p", pattern],
        env=env,
        check=False,
    )
    return completed.returncode


def main() -> int:
    check_schemas()
    for pattern in ("test_experiment_*.py", "test_outcome_firewall_*.py", "test_power_*.py"):
        code = run_pattern(pattern)
        if code:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())