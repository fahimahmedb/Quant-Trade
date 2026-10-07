"""L2-B synthetic verification only; execute with -I -S -B and a 600s supervisor.

No candidate is loaded here. L2-I remains blocked until E, the ratified freezes
and a separately constructed candidate exist. The historical H baseline is
expected to have 279 passing tests; its future three candidate incompatibilities
are neither waived nor claimed observed by this runner.

The pins file and this entry point must be checked against their approved Git
blobs outside the process. The pins authenticate local bytes only under that
external check; they do not authenticate Owner/Astra decisions.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import sysconfig
import unittest

ROOT = Path(__file__).resolve().parents[5]
BASE = "research/weather_forward/v4/"
H_BLOBS = {
    "a2_harness/__init__.py": "bf9a2bdba7658454ea10009a28c975024365cfe1",
    "a2_harness/contract.py": "f6f94a4a472e3f6652a1502f6afb5825721364d0",
    "a2_harness/harness.py": "00ae81d2823b7d30d72aabe8d82ac051dbfcf5c4",
    "a2_harness/trusted_root.py": "9d8adeca4b61e42c40bd7f9ec85e4f3b676b1b94",
    "a2_harness/test_bounded_runtime.py": "aa0159c2a470da034c6611e207687997294fb236",
    "a2_harness/test_d5_public_state_types.py": "52bb94ed7fa497bb9756afe02052b855dcd3d9f5",
    "a2_harness/run_bounded_runtime_tests.py": "25b7d3bde54e412a51df45059a65283479420725",
    "a2_harness/run_d5_type_regression_tests.py": "f660a24d969e50db62ed6165c15272d90cb86b4b",
}
TEST_MODULE = "research.weather_forward.v4.a2_operation.verification.test_tooling"


def git_blob(payload):
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload).hexdigest()


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def preflight(argv):
    if argv or not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode):
        raise ValueError("USE_PYTHON_I_S_B_NO_ARGUMENTS")
    pins_path = ROOT / BASE / "a2_operation/verification/source_pins.json"
    pins = json.loads(pins_path.read_text(encoding="ascii"), object_pairs_hook=_unique)
    if set(pins) != {"schema", "mode", "sources"} or pins["schema"] != "A2_TOOLING_SOURCE_PINS_V1" \
            or pins["mode"] != "L2_B_SYNTHETIC_ONLY" or type(pins["sources"]) is not dict:
        raise ValueError("SOURCE_PINS_SCHEMA_MISMATCH")
    observed = {}
    for relative, blob in pins["sources"].items():
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or not relative.startswith(BASE) \
                or path.suffix not in {".py", ".json", ".sh"}:
            raise ValueError("SOURCE_PIN_OUTSIDE_SCOPE")
        observed[relative] = git_blob((ROOT / path).read_bytes())
        if observed[relative] != blob:
            raise ValueError("PINNED_SOURCE_BYTES_MISMATCH:" + relative)
    for suffix, blob in H_BLOBS.items():
        if pins["sources"].get(BASE + suffix) != blob:
            raise ValueError("H_BASELINE_PIN_MISMATCH:" + suffix)
    entry = BASE + "a2_operation/verification/run_tooling_tests.py"
    if entry not in observed or BASE + "a2_operation/verification/test_tooling.py" not in observed:
        raise ValueError("RUNNER_AND_TEST_PINS_REQUIRED")
    print("MODE=L2_B_SYNTHETIC_ONLY")
    print("SOURCE_PINS_BLOB=" + git_blob(pins_path.read_bytes()))
    print("SOURCE_BLOBS=" + json.dumps(observed, sort_keys=True))
    print("ENVIRONMENT=" + json.dumps({"python": sys.version.split()[0],
        "architecture": platform.machine(), "implementation": sys.implementation.name,
        "flags": "-I -S -B", "external_limit_seconds": 600}, sort_keys=True))
    return observed


def counts(result, collected):
    return {"collected": collected, "run": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors)
                  - len(result.skipped) - len(result.expectedFailures) - len(result.unexpectedSuccesses),
        "failures": len(result.failures), "errors": len(result.errors),
        "skips": len(result.skipped), "expected_failures": len(result.expectedFailures),
        "unexpected_successes": len(result.unexpectedSuccesses)}


def main(argv):
    observed = preflight(argv)
    sys.path.insert(0, str(ROOT))
    from research.weather_forward.v4.a2_operation.verification.audit_boundary import decide
    stdlib = str(Path(sysconfig.get_path("stdlib")).resolve())
    allowed = frozenset(str((ROOT / p).resolve()) for p in observed)
    caches = frozenset(str(Path(importlib.util.cache_from_source(p)).resolve())
                       for p in allowed if p.endswith(".py"))
    audit = {"network_attempts": 0, "subprocess_attempts": 0, "forbidden_file_attempts": 0,
             "allowed_reads": 0, "expected_cache_refusals": 0}

    def hook(event, args):
        verdict = decide(event, args, allowed_reads=allowed, expected_caches=caches,
                         stdlib_root=stdlib)
        if verdict == "ALLOW":
            if event == "open":
                audit["allowed_reads"] += 1
            return
        if verdict == "EXPECTED_CACHE_REFUSAL":
            audit["expected_cache_refusals"] += 1
        else:
            key = ("network_attempts" if verdict == "NETWORK" else
                   "subprocess_attempts" if verdict == "SUBPROCESS" else "forbidden_file_attempts")
            audit[key] += 1
        raise PermissionError("OFFLINE_TEST_" + verdict)

    sys.addaudithook(hook)
    loader = unittest.TestLoader()
    suites = [loader.loadTestsFromName("research.weather_forward.v4.a2_harness." + name)
              for name in ("test_bounded_runtime", "test_d5_public_state_types")]
    sizes = [suite.countTestCases() for suite in suites]
    if sizes != [145, 134] or loader.errors:
        raise ValueError("LEGACY_COLLECTION_NOT_145_PLUS_134")
    new_suite = loader.loadTestsFromName(TEST_MODULE)
    new_count = new_suite.countTestCases()
    if not new_count or loader.errors:
        raise ValueError("NEW_TEST_COLLECTION_FAILED")
    from research.weather_forward.v4.a2_harness import harness, trusted_root
    if trusted_root.CURRENT_OWNER_EXECUTION_POLICY_AUTHORITY is not None \
            or trusted_root.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT is not None \
            or harness.get_trusted_execution_policy_root() is not None:
        raise ValueError("SYNTHETIC_MODE_REQUIRES_UNCHANGED_DENY_ALL_ROOT_H")
    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
    legacy = runner.run(unittest.TestSuite(suites))
    new = runner.run(new_suite)
    restored = trusted_root.get_trusted_execution_policy_root() is None \
        and harness.get_trusted_execution_policy_root() is None
    integrity = all(git_blob((ROOT / p).read_bytes()) == b for p, b in observed.items())
    from research.weather_forward.v4 import a2_harness as api
    from research.weather_forward.v4.a2_operation.identity import identity_stdlib, identity_via_harness
    vector = json.loads((ROOT / BASE / "a2_operation/identity/calibration_test_only_output_manifest.json")
                        .read_text(encoding="ascii"))
    calibration = {"H": identity_via_harness.identity(api, vector["document"]),
                   "stdlib": identity_stdlib.identity(vector["document"]),
                   "expected": vector["calibration_vector"]["expected_identity"],
                   "scope": "TEST_ONLY_OUTPUT_MANIFEST"}
    calibrated = calibration["H"] == calibration["stdlib"] == calibration["expected"]
    guards = all(audit[k] == 0 for k in ("network_attempts", "subprocess_attempts", "forbidden_file_attempts"))
    passed = legacy.wasSuccessful() and new.wasSuccessful() and legacy.testsRun == 279 \
        and new.testsRun == new_count and not legacy.skipped and not new.skipped \
        and not legacy.expectedFailures and not new.expectedFailures \
        and restored and integrity and calibrated and guards
    summary = {"legacy": counts(legacy, 279), "new": counts(new, new_count),
        "legacy_verdict": "LEGACY_H_BASELINE_279_GREEN" if legacy.wasSuccessful() else "FAILED",
        "calibration": calibration, "offline_audit": audit, "root_restored": restored,
        "pinned_bytes_unchanged": integrity, "candidate_loaded": False,
        "real_configuration_evaluated": False, "vm_accessed": False,
        "verdict": "L2_B_SYNTHETIC_VERIFICATION_PASS" if passed else "L2_B_SYNTHETIC_VERIFICATION_FAILED",
        "L2_I_candidate_verification": "NOT_PERFORMED_MISSING_DEPENDENCIES"}
    print("TOOLING_TEST_SUMMARY=" + json.dumps(summary, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
