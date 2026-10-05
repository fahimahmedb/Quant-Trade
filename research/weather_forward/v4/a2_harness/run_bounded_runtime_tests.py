"""Run only the bounded A2 governance suite with standard-library isolation.

Run with python -I -S -B. No network, subprocess, data or fixture reads.
The in-process audit boundary is test evidence, not a deployed security control.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import sysconfig
import unittest

DIRECTORY = Path(__file__).resolve().parent
REPOSITORY_ROOT = DIRECTORY.parents[3]
AUDITED_BLOBS = {
    "__init__.py": "bf9a2bdba7658454ea10009a28c975024365cfe1",
    "contract.py": "db978016cb2eab91e3b7569de350d0fc65641889",
    "harness.py": "00ae81d2823b7d30d72aabe8d82ac051dbfcf5c4",
    "trusted_root.py": "9d8adeca4b61e42c40bd7f9ec85e4f3b676b1b94",
    "README.md": "b3b74326d2d41f1d88c9e891186a5af9a663f095"
}
SOURCE_NAMES = tuple(AUDITED_BLOBS)
ALLOW_REPAIR = sys.argv[1:] == ["--allow-in-scope-repair"]
if sys.argv[1:] and not ALLOW_REPAIR:
    raise SystemExit("Only --allow-in-scope-repair is a permitted argument.")

def git_blob_id(payload):
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload).hexdigest()

source_blobs = {name: git_blob_id((DIRECTORY / name).read_bytes()) for name in SOURCE_NAMES}
changed = {name: blob for name, blob in source_blobs.items() if blob != AUDITED_BLOBS[name]}
if changed and not ALLOW_REPAIR:
    raise SystemExit("AUDITED_SOURCE_BYTES_MISMATCH: " + json.dumps(changed, sort_keys=True))
if "trusted_root.py" in changed:
    raise SystemExit("PRODUCTION_TRUSTED_ROOT_MODIFIED")
if set(changed) - {"contract.py", "harness.py"}:
    raise SystemExit("UNEXPECTED_PRODUCTION_SOURCE_CHANGE")
print("SOURCE_BLOBS=" + json.dumps(source_blobs, sort_keys=True))
print("PRODUCTION_SOURCE_DIFFERENCES=" + json.dumps(changed, sort_keys=True))
print("TEST_SOURCE_BLOB=" + git_blob_id((DIRECTORY / "test_bounded_runtime.py").read_bytes()))
print("RUNNER_SOURCE_BLOB=" + git_blob_id(Path(__file__).read_bytes()))
print("TEST_ONLY_TRUSTED_ROOT_IS_NOT_EXECUTION_AUTHORITY=TRUE")

stdlib = Path(sysconfig.get_path("stdlib")).resolve()
allowed_local_reads = {
    (DIRECTORY / name).resolve() for name in
    ("__init__.py", "contract.py", "harness.py", "trusted_root.py", "test_bounded_runtime.py")
}
blocked_code_paths = []
blocked_cache_paths = []
expected_cache_paths = {
    Path(importlib.util.cache_from_source(str(source))).resolve()
    for source in allowed_local_reads
}
audit_counts = {"network_attempts": 0, "subprocess_attempts": 0,
                "forbidden_file_attempts": 0, "allowed_code_reads": 0,
                "code_cache_reads_blocked": 0}

def audit_boundary(event, args):
    if event.startswith("socket.") or event.startswith("http.client.") or event.startswith("urllib."):
        audit_counts["network_attempts"] += 1
        raise PermissionError("OFFLINE_TEST_NETWORK_PROHIBITED")
    if event in ("subprocess.Popen", "os.system", "os.posix_spawn", "os.posix_spawnp",
                 "os.exec", "os.fork", "os.forkpty"):
        audit_counts["subprocess_attempts"] += 1
        raise PermissionError("OFFLINE_TEST_SUBPROCESS_PROHIBITED")
    if event != "open":
        return
    path, mode, flags = args
    if not isinstance(path, (str, bytes)):
        audit_counts["forbidden_file_attempts"] += 1
        raise PermissionError("OFFLINE_TEST_FD_OPEN_PROHIBITED")
    candidate = Path(path.decode() if isinstance(path, bytes) else path).resolve()
    write_flags = 1 | 2 | 64 | 512 | 1024  # O_WRONLY/O_RDWR/O_CREAT/O_TRUNC/O_APPEND
    if (flags is not None and flags & write_flags) or (mode and any(x in mode for x in "wax+")):
        audit_counts["forbidden_file_attempts"] += 1
        raise PermissionError("OFFLINE_TEST_FILE_WRITE_PROHIBITED")
    is_stdlib = (candidate.is_relative_to(stdlib)
                 and "site-packages" not in candidate.parts
                 and candidate.suffix in (".py", ".pyc", ".so"))
    if candidate in expected_cache_paths:
        # importlib handles this denial by loading the exact allowlisted .py.
        # Never read local bytecode or allow an unverified cache to replace source.
        blocked_cache_paths.append(str(candidate))
        audit_counts["code_cache_reads_blocked"] += 1
        raise PermissionError("OFFLINE_TEST_LOAD_VERIFIED_SOURCE_ONLY")
    if candidate not in allowed_local_reads and not is_stdlib:
        blocked_code_paths.append(str(candidate))
        audit_counts["forbidden_file_attempts"] += 1
        raise PermissionError("OFFLINE_TEST_UNALLOWLISTED_FILE_READ")
    audit_counts["allowed_code_reads"] += 1

sys.addaudithook(audit_boundary)
sys.path.insert(0, str(REPOSITORY_ROOT))
suite = unittest.defaultTestLoader.loadTestsFromName(
    "research.weather_forward.v4.a2_harness.test_bounded_runtime"
)
collected = suite.countTestCases()
result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
summary = {
    "framework": "Python standard library unittest + unittest.mock",
    "collected": collected, "run": result.testsRun,
    "passed": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
    "failed": len(result.failures), "errors": len(result.errors),
    "skipped": len(result.skipped),
    "expected_failures": len(result.expectedFailures),
    "unexpected_successes": len(result.unexpectedSuccesses),
    "offline_audit": audit_counts,
    "denied_read_paths": blocked_code_paths,
    "blocked_code_cache_paths": blocked_cache_paths,
}
print("BOUNDED_TEST_SUMMARY=" + json.dumps(summary, sort_keys=True))
guards_clear = all(audit_counts[key] == 0 for key in
                   ("network_attempts", "subprocess_attempts", "forbidden_file_attempts"))
raise SystemExit(0 if result.wasSuccessful() and guards_clear else 1)
