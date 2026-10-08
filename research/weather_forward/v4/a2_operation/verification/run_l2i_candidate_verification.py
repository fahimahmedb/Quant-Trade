"""L2-I verification of the L2-H root candidate; execute with -I -S -B under a 600 s supervisor.

Run from an isolated assembled working directory (tooling snapshot + candidate trusted_root.py);
the repository root is derived from this file's location. The runner modifies nothing, activates
nothing, evaluates the real configuration only in refusal mode (see test_l2i_candidate.py) and
reports the 279 legacy tests apart from the new tests. Exit 0 = composite criterion met, not
"279 green".
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import re
import sys
import sysconfig
import time
import unittest

ROOT = Path(__file__).resolve().parents[5]
BASE = "research/weather_forward/v4/"
PINS = {  # H blobs, candidate blob, frozen contents (E table A)
    "a2_harness/__init__.py": "bf9a2bdba7658454ea10009a28c975024365cfe1",
    "a2_harness/contract.py": "f6f94a4a472e3f6652a1502f6afb5825721364d0",
    "a2_harness/harness.py": "00ae81d2823b7d30d72aabe8d82ac051dbfcf5c4",
    "a2_harness/trusted_root.py": "9704a844bae0ef54637c76dded5bb82d9f4c334f",
    "a2_harness/test_bounded_runtime.py": "aa0159c2a470da034c6611e207687997294fb236",
    "a2_harness/test_d5_public_state_types.py": "52bb94ed7fa497bb9756afe02052b855dcd3d9f5",
    "a2_harness/run_bounded_runtime_tests.py": "25b7d3bde54e412a51df45059a65283479420725",
    "a2_harness/run_d5_type_regression_tests.py": "f660a24d969e50db62ed6165c15272d90cb86b4b",
    "a2_operation/frozen/input_manifest_d2_v1.json": "f85205f33a232de6fabd83c17c52a25d4634e374",
    "a2_operation/frozen/output_manifest_d2_v1.json": "7651de7e718a276b596f2256aff0877e771e5d6d",
    "a2_operation/frozen/harness_policy_d2_v1.json": "6a1fa30fac327c0183b2931550bd4c730195529c",
}
P = "research.weather_forward.v4.a2_harness.test_bounded_runtime.TrustedRootTests."
EXPECTED_DIFFERENCES = {
    P + "test_production_root_absent_denies_all_authority_bearing_paths": ("AssertionError", 198, ()),
    P + "test_coordinated_caller_substitution_cannot_create_production_root":
        ("AssertionError", 212, ("179", "EXECUTION_POLICY_ROOT_MISMATCH", "MISSING_EXECUTION_POLICY_ROOT")),
    P + "test_test_only_root_exercises_positive_paths_and_is_restored": ("AssertionError", 227, ()),
}
NEW_MODULE = "research.weather_forward.v4.a2_operation.verification.test_l2i_candidate"


def git_blob(payload):
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload).hexdigest()


def main(argv):
    if argv or not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode):
        raise SystemExit("USE_PYTHON_I_S_B_NO_ARGUMENTS")
    started = time.monotonic()
    observed = {BASE + k: git_blob((ROOT / BASE / k).read_bytes()) for k in PINS}
    mismatched = sorted(BASE + k for k, v in PINS.items() if observed[BASE + k] != v)
    print("PINS_MISMATCH=" + json.dumps(mismatched))
    if mismatched:
        return 2
    own = {p: git_blob((ROOT / BASE / p).read_bytes()) for p in (
        "a2_operation/verification/run_l2i_candidate_verification.py",
        "a2_operation/verification/test_l2i_candidate.py")}
    print("SOURCE_BLOBS=" + json.dumps(observed, sort_keys=True))
    print("RUNNER_AND_NEW_TEST_BLOBS=" + json.dumps(own, sort_keys=True))
    print("ENVIRONMENT=" + json.dumps({"python": sys.version.split()[0], "architecture": platform.machine(),
        "implementation": sys.implementation.name, "system": platform.platform(),
        "flags": "-I -S -B", "external_limit_seconds": 600}, sort_keys=True))
    sys.path.insert(0, str(ROOT))
    from research.weather_forward.v4.a2_operation.verification.audit_boundary import decide
    stdlib = str(Path(sysconfig.get_path("stdlib")).resolve())
    allowed = frozenset(str(p.resolve()) for p in (ROOT / BASE).rglob("*") if p.is_file()
                        and p.suffix in {".py", ".json", ".sh"})
    caches = frozenset(str(Path(importlib.util.cache_from_source(p)).resolve()) for p in allowed if p.endswith(".py"))
    audit = {"network_attempts": 0, "subprocess_attempts": 0, "forbidden_file_attempts": 0,
             "allowed_reads": 0, "expected_cache_refusals": 0}

    def hook(event, args):
        verdict = decide(event, args, allowed_reads=allowed, expected_caches=caches, stdlib_root=stdlib)
        if verdict == "ALLOW":
            if event == "open":
                audit["allowed_reads"] += 1
            return
        if verdict == "EXPECTED_CACHE_REFUSAL":
            audit["expected_cache_refusals"] += 1
        else:
            audit["network_attempts" if verdict == "NETWORK" else "subprocess_attempts" if verdict == "SUBPROCESS"
                  else "forbidden_file_attempts"] += 1
        raise PermissionError("OFFLINE_TEST_" + verdict)

    sys.addaudithook(hook)
    loader = unittest.TestLoader()
    suites = [loader.loadTestsFromName("research.weather_forward.v4.a2_harness." + n)
              for n in ("test_bounded_runtime", "test_d5_public_state_types")]
    sizes = [s.countTestCases() for s in suites]
    new_suite = loader.loadTestsFromName(NEW_MODULE)
    new_count = new_suite.countTestCases()
    print("COLLECTION=" + json.dumps({"legacy": sizes, "new": new_count, "loader_errors": len(loader.errors)}))
    if sizes != [145, 134] or loader.errors or not new_count:
        return 3
    from research.weather_forward.v4.a2_harness import harness, trusted_root
    from research.weather_forward.v4.a2_operation.verification import test_l2i_candidate as new_module
    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
    legacy = runner.run(unittest.TestSuite(suites))
    new = runner.run(new_suite)

    observed_diffs = {}
    for kind, items in (("failure", legacy.failures), ("error", legacy.errors)):
        for test, text in items:
            lines = [int(m) for m in re.findall(r'test_bounded_runtime\.py", line (\d+)', text)]
            observed_diffs[test.id()] = {"kind": kind, "type": text.strip().splitlines()[-1].split(":")[0],
                                         "test_file_lines": lines, "traceback": text}
    matched = set(observed_diffs) == set(EXPECTED_DIFFERENCES)
    for tid, (etype, eline, needles) in EXPECTED_DIFFERENCES.items():
        d = observed_diffs.get(tid)
        matched = matched and d is not None and d["kind"] == "failure" and d["type"] == etype \
            and eline in d["test_file_lines"] and all(n in d["traceback"] for n in needles)
    for tid, d in sorted(observed_diffs.items()):
        print("LEGACY_DIFFERENCE=" + json.dumps({k: d[k] for k in ("kind", "type", "test_file_lines")} | {"id": tid}))
        print("LEGACY_DIFFERENCE_TRACEBACK[" + tid + "]\n" + d["traceback"])
    legacy_clean = legacy.testsRun == 279 and not legacy.errors and not legacy.skipped \
        and not legacy.expectedFailures and not legacy.unexpectedSuccesses and len(legacy.failures) == 3
    root_now = trusted_root.get_trusted_execution_policy_root()
    intact = harness.get_trusted_execution_policy_root() is root_now \
        and root_now is trusted_root.CURRENT_PERMISSIVE_EXECUTION_POLICY_ROOT
    integrity = all(git_blob((ROOT / BASE / k).read_bytes()) == v for k, v in PINS.items())
    guards = all(audit[k] == 0 for k in ("network_attempts", "subprocess_attempts", "forbidden_file_attempts"))
    counters = dict(new_module.COUNTERS)
    no_real_permit = counters["real_tuple_permits"] == 0 and counters["authorized_real_refused_by_guard"] == 1
    new_ok = new.wasSuccessful() and new.testsRun == new_count and not new.skipped \
        and not new.expectedFailures and not new.unexpectedSuccesses
    passed = legacy_clean and matched and new_ok and intact and integrity and guards and no_real_permit
    summary = {"legacy": {"collected": sum(sizes), "run": legacy.testsRun,
                          "passed": legacy.testsRun - len(legacy.failures) - len(legacy.errors) - len(legacy.skipped),
                          "failures": len(legacy.failures), "errors": len(legacy.errors),
                          "skips": len(legacy.skipped), "expected_failures": len(legacy.expectedFailures),
                          "unexpected_successes": len(legacy.unexpectedSuccesses)},
        "legacy_differences_match_decision": matched, "legacy_differences": sorted(observed_diffs),
        "legacy_verdict": "LEGACY_BASELINE_EXPECTED_DIFFERENCES_MATCHED" if legacy_clean and matched else "FAILED",
        "new": {"collected": new_count, "run": new.testsRun, "failures": len(new.failures),
                "errors": len(new.errors), "skips": len(new.skipped)},
        "real_tuple_counters": counters, "offline_audit": audit, "root_state_intact": intact,
        "pinned_bytes_unchanged": integrity, "elapsed_seconds": round(time.monotonic() - started, 2),
        "candidate_loaded": True, "real_configuration_evaluated_permissively": counters["real_tuple_permits"] != 0,
        "activation": False, "vm_accessed": False,
        "verdict": "L2_I_VERIFICATION_PASS" if passed else "L2_I_VERIFICATION_FAILED"}
    print("L2I_SUMMARY=" + json.dumps(summary, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
