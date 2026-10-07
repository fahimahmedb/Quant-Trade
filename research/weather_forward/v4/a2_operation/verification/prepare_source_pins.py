"""Supervisory pin preparation, not an audited test or identity calculation.

Reads only the immutable H code/test baseline, local tooling source files and
the published TEST_ONLY calibration vector. Writes the two tooling pin files.
Do not run in a process whose audit contract forbids all writes. Approved blob
checks of these generated files remain external to the verification runner.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
V4 = ROOT / "research/weather_forward/v4"
QUALIFICATION_PATHS = (
    "__init__.py", "common/__init__.py", "common/bounded_output.py", "common/a2_unit_profile.sh",
    "qualification/__init__.py", "qualification/host_facts.sh",
    "qualification/qualification_probes.py", "qualification/run_qualification.sh",
    "qualification/setup_host.sh", "qualification/summarize_qualification.py",
    "qualification/deploy_files.sh",
)
H_NAMES = ("__init__.py", "contract.py", "harness.py", "trusted_root.py",
           "test_bounded_runtime.py", "test_d5_public_state_types.py",
           "run_bounded_runtime_tests.py", "run_d5_type_regression_tests.py")


def blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def main():
    operation = V4 / "a2_operation"
    paths = [operation / "__init__.py"]
    for name in ("common", "identity", "operation", "qualification", "verification"):
        paths.extend(p for p in (operation / name).rglob("*") if p.suffix in {".py", ".sh"})
    paths.append(operation / "identity/calibration_test_only_output_manifest.json")
    paths.extend(V4 / "a2_harness" / name for name in H_NAMES)
    pins = {"schema": "A2_TOOLING_SOURCE_PINS_V1", "mode": "L2_B_SYNTHETIC_ONLY",
            "sources": {str(p.relative_to(ROOT)): blob(p) for p in sorted(paths)}}
    target = operation / "verification/source_pins.json"
    target.write_text(json.dumps(pins, indent=2, sort_keys=True) + "\n", encoding="ascii")
    qual_target = operation / "qualification/file_pins.tsv"
    qual_target.write_text("".join(blob(operation / p) + "\t" + str((operation / p).relative_to(ROOT)) + "\n"
                                  for p in QUALIFICATION_PATHS), encoding="ascii")
    print("SOURCE_PINS_BLOB=" + blob(target))
    print("QUALIFICATION_PINS_BLOB=" + blob(qual_target))
    print("QUALIFICATION_FILES=" + str(len(QUALIFICATION_PATHS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
