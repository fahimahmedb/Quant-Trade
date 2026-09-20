"""Astra Phase-7 durability falsification tests.

Synthetic bytes only. These tests cover publication durability boundaries that
can affect whether a raw object is legitimately acknowledged after a crash.
"""
from __future__ import annotations

import errno
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from quant.paths import QuantPaths
from quant.dataplane.sec.store import SecCaptureStore, SecStorageFailure, digest_bytes

ROOT = Path(__file__).resolve().parents[1]


class RawPublicationDurabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.paths = QuantPaths(Path(self.temp.name))
        self.store = SecCaptureStore(self.paths, root=ROOT)

    def test_retry_after_directory_fsync_failure_revalidates_durability(self) -> None:
        """A visible hardlink after failed fsync is not yet durable evidence."""
        body = b"synthetic-p0-raw-object"
        object_id = digest_bytes(body)
        target = self.store.object_path(object_id)

        with mock.patch.object(
            self.store,
            "_fsync_dir",
            side_effect=OSError(errno.EIO, "synthetic directory fsync failure"),
        ):
            with self.assertRaises(SecStorageFailure):
                self.store.put_object(body)

        self.assertTrue(
            target.exists(),
            "the adversarial boundary requires the link to exist after fsync failed",
        )

        original = SecCaptureStore._fsync_dir
        with mock.patch.object(
            self.store,
            "_fsync_dir",
            wraps=lambda path: original(path),
        ) as fsync_dir:
            result = self.store.put_object(body)

        self.assertTrue(result.deduplicated)
        touched = [call.args[0] for call in fsync_dir.call_args_list]
        self.assertIn(
            target.parent,
            touched,
            "retry must durably revalidate the directory containing the object",
        )
        self.assertIn(
            target.parent.parent,
            touched,
            "retry must also durably revalidate the hash-prefix directory entry",
        )

    def test_new_hash_prefix_is_fsynced_in_its_parent(self) -> None:
        """Creating <raw>/<prefix>/ must itself be durable before ACK."""
        body = b"synthetic-new-prefix"
        target = self.store.object_path(digest_bytes(body))

        with mock.patch.object(self.store, "_fsync_dir") as fsync_dir:
            self.store.put_object(body)

        touched = [call.args[0] for call in fsync_dir.call_args_list]
        self.assertIn(target.parent, touched)
        self.assertIn(
            target.parent.parent,
            touched,
            "fsync(prefix) does not by itself make creation of prefix durable in raw/",
        )


class SupervisorRealProcessBoundaryTests(unittest.TestCase):
    """Exercise real Linux fork/exec/signal boundaries without claiming systemd proof."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "scripts").mkdir(parents=True)
        child_script = """import os
import signal
import sys
import time
from pathlib import Path

root = Path(sys.argv[sys.argv.index("--root") + 1])
sec = root / "var" / "sec"
sec.mkdir(parents=True, exist_ok=True)
(sec / "test_child.pid").write_text(str(os.getpid()), encoding="utf-8")

def stop(signum, frame):
    raise SystemExit(0)

signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)
while True:
    time.sleep(0.05)
"""
        (self.root / "scripts" / "quant.py").write_text(child_script, encoding="utf-8")
        wrapper = f"""import importlib.util
import os
from pathlib import Path
from unittest import mock

repo = Path({str(ROOT)!r})
spec = importlib.util.spec_from_file_location(
    "p0_real_signal_launcher", repo / "deploy" / "quant_sec_supervisor.py")
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)
fp = "sha256:" + "a" * 64
with mock.patch.object(
        launcher, "_effective_environment",
        return_value=(dict(os.environ), 60.0)), \
     mock.patch.object(launcher, "current_fingerprint", return_value=fp), \
     mock.patch.object(launcher, "materialize_if_absent", return_value=fp), \
     mock.patch.object(launcher, "_consume_deployment_authority", return_value=None):
    raise SystemExit(launcher.main())
"""
        self.wrapper = self.root / "supervisor_wrapper.py"
        self.wrapper.write_text(wrapper, encoding="utf-8")
        self.processes: list[object] = []
        self.child_pids: set[int] = set()
        self.addCleanup(self._cleanup_processes)

    @staticmethod
    def _dead(pid: int) -> bool:
        try:
            stat = Path(f"/proc/{pid}/stat")
            if not stat.exists():
                return True
            fields = stat.read_text(encoding="utf-8").split()
            return len(fields) > 2 and fields[2] == "Z"
        except (FileNotFoundError, ProcessLookupError):
            return True

    def _wait_dead(self, pid: int, seconds: float = 5.0) -> None:
        import time
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if self._dead(pid):
                return
            time.sleep(0.05)
        self.fail(f"process {pid} survived its supervisor boundary")

    def _start(self):
        import subprocess
        import sys
        import time
        pid_file = self.root / "var" / "sec" / "test_child.pid"
        try:
            pid_file.unlink()
        except FileNotFoundError:
            pass
        process = subprocess.Popen(
            [sys.executable, str(self.wrapper), "--root", str(self.root)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.processes.append(process)
        deadline = time.monotonic() + 8.0
        state_path = self.root / "var" / "sec" / "supervisor_state.json"
        while time.monotonic() < deadline:
            if process.poll() is not None:
                self.fail(f"supervisor exited early with {process.returncode}")
            if pid_file.exists() and state_path.exists():
                child_pid = int(pid_file.read_text(encoding="utf-8"))
                self.child_pids.add(child_pid)
                return process, child_pid
            time.sleep(0.05)
        self.fail("supervisor/child did not become observable")

    def _cleanup_processes(self) -> None:
        import os
        import signal
        for process in reversed(self.processes):
            if process.poll() is None:
                try:
                    os.kill(process.pid, signal.SIGTERM)
                    process.wait(timeout=3)
                except Exception:
                    process.kill()
                    process.wait(timeout=3)
        for pid in self.child_pids:
            if not self._dead(pid):
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_sigterm_stop_is_clean_but_replacement_supervisor_is_manual(self) -> None:
        import json
        import os
        import signal
        first, child_pid = self._start()
        os.kill(first.pid, signal.SIGTERM)
        self.assertEqual(first.wait(timeout=8), 0)
        self._wait_dead(child_pid)

        events_path = self.root / "var" / "sec" / "supervisor_events.jsonl"
        events = [
            json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        exits = [record for record in events if record.get("event") == "CHILD_EXIT_OBSERVED"]
        self.assertTrue(exits)
        self.assertTrue(exits[-1]["stopped_by_supervisor"])
        self.assertFalse(exits[-1]["unexpected_termination"])

        replacement, replacement_child = self._start()
        state = json.loads(
            (self.root / "var" / "sec" / "supervisor_state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["lifecycle_cause"], "MANUAL_START")
        os.kill(replacement.pid, signal.SIGTERM)
        self.assertEqual(replacement.wait(timeout=8), 0)
        self._wait_dead(replacement_child)

    def test_sigkill_supervisor_kills_child_and_replacement_is_manual(self) -> None:
        import json
        import os
        import signal
        first, child_pid = self._start()
        os.kill(first.pid, signal.SIGKILL)
        first.wait(timeout=8)
        self._wait_dead(child_pid)

        replacement, replacement_child = self._start()
        state = json.loads(
            (self.root / "var" / "sec" / "supervisor_state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["lifecycle_cause"], "MANUAL_START")
        os.kill(replacement.pid, signal.SIGTERM)
        self.assertEqual(replacement.wait(timeout=8), 0)
        self._wait_dead(replacement_child)


class SecAuditStdoutFirewallTests(unittest.TestCase):
    def test_sec_audit_stdout_with_realistic_activity_has_no_signal_proxy(self) -> None:
        import contextlib
        import importlib.util
        import io
        import json
        from types import SimpleNamespace

        from quant.dataplane.sec.visibility import (
            assert_no_count_proxies, assert_no_scientific_content)
        from tests.test_sec_form4_capture import CollectorTestCase

        case = CollectorTestCase(methodName="runTest")
        case.setUp()
        self.addCleanup(case.doCleanups)
        collector = case.collector(case.fixture_router())
        collector.lifecycle.update({
            "lifecycle_cause": "DEPLOYMENT_RESTART",
            "boot_id": "synthetic-child",
            "supervisor_id": "synthetic-supervisor",
        })
        collector.record_service_start()
        collector.poll()
        collector.drain(max_items=3)

        spec = importlib.util.spec_from_file_location(
            "quant_cli_for_firewall_test", ROOT / "scripts" / "quant.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        args = SimpleNamespace(command="sec-audit", window_start=None)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            module.sec_command(SimpleNamespace(sec=collector), args)

        rendered = output.getvalue()
        payload = json.loads(rendered)
        assert_no_count_proxies(payload, "sec-audit stdout")
        assert_no_scientific_content(rendered, "sec-audit stdout")


if __name__ == "__main__":
    unittest.main()
