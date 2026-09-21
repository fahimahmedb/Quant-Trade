from __future__ import annotations

import fcntl
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


runctl = load_module(
    "quant_gate_b_runctl_f11",
    ROOT / "scripts" / "quant_gate_b_runctl.py",
)


class LockHarness:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.checkout = self.root / "checkout"
        self.checkout.mkdir()
        self.registry_path = self.root / "state" / "registry.ndjson"
        self.registry = runctl.Registry(self.registry_path, self.checkout)

    def close(self):
        self.tmp.cleanup()

    def initialize(self):
        self.registry.set_revocation_epoch(
            epoch=1,
            reference="blue/f11",
        )
        anchors = self.registry._lock_authority_paths()
        assert len(anchors) == 1
        return anchors[0]


HOLDER = r"""
import fcntl, os, sys, time
path=sys.argv[1]
delay=float(sys.argv[2])
fd=os.open(path, os.O_RDWR)
fcntl.flock(fd, fcntl.LOCK_EX)
print("LOCKED", flush=True)
time.sleep(delay)
fcntl.flock(fd, fcntl.LOCK_UN)
os.close(fd)
"""


class GateBLockPathIdentityRepairTests(unittest.TestCase):
    def setUp(self):
        self.h = LockHarness()

    def tearDown(self):
        self.h.close()

    def _holder(self, delay: float = 1.25):
        proc = subprocess.Popen(
            [sys.executable, "-c", HOLDER, str(self.h.registry.lock), str(delay)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(proc.stdout.readline().strip(), "LOCKED")
        return proc

    def test_exact_astra_replacement_attack_blocks_then_fails_closed(self):
        anchor = self.h.initialize()
        original = os.lstat(self.h.registry.lock)
        self.assertEqual((original.st_dev, original.st_ino), (os.lstat(anchor).st_dev, os.lstat(anchor).st_ino))
        proc = self._holder()
        try:
            self.h.registry.lock.unlink()
            self.h.registry.lock.write_bytes(b"replacement")
            replacement = os.lstat(self.h.registry.lock)
            self.assertNotEqual((original.st_dev, original.st_ino), (replacement.st_dev, replacement.st_ino))
            started = time.monotonic()
            with self.assertRaises(runctl.AuthorityError):
                with self.h.registry._locked():
                    self.fail("replacement inode must never become a valid mutation domain")
            elapsed = time.monotonic() - started
            self.assertGreaterEqual(elapsed, 0.75)
        finally:
            proc.wait(timeout=5)
            self.assertEqual(proc.returncode, 0, proc.stderr.read())

    def test_stable_real_process_contention_serializes_normally(self):
        self.h.initialize()
        proc = self._holder()
        try:
            started = time.monotonic()
            with self.h.registry._locked():
                elapsed = time.monotonic() - started
            self.assertGreaterEqual(elapsed, 0.75)
        finally:
            proc.wait(timeout=5)
            self.assertEqual(proc.returncode, 0, proc.stderr.read())

    def test_replacement_before_acquisition_is_rejected(self):
        self.h.initialize()
        self.h.registry.lock.unlink()
        self.h.registry.lock.write_bytes(b"replacement")
        with self.assertRaises(runctl.AuthorityError):
            with self.h.registry._locked():
                pass

    def test_replacement_after_acquisition_is_rejected_before_success(self):
        self.h.initialize()
        with self.assertRaises(runctl.AuthorityError):
            with self.h.registry._locked():
                self.h.registry.lock.unlink()
                self.h.registry.lock.write_bytes(b"replacement")

    def test_authority_anchor_replacement_is_rejected(self):
        anchor = self.h.initialize()
        anchor.unlink()
        anchor.write_bytes(b"replacement-anchor")
        with self.assertRaises(runctl.AuthorityError):
            with self.h.registry._locked():
                pass

    def test_symlink_public_lock_is_rejected(self):
        anchor = self.h.initialize()
        self.h.registry.lock.unlink()
        self.h.registry.lock.symlink_to(anchor.name)
        with self.assertRaises(runctl.AuthorityError):
            with self.h.registry._locked():
                pass

    def test_directory_public_lock_is_rejected(self):
        self.h.initialize()
        self.h.registry.lock.unlink()
        self.h.registry.lock.mkdir()
        with self.assertRaises(runctl.AuthorityError):
            with self.h.registry._locked():
                pass

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO unavailable")
    def test_fifo_public_lock_is_rejected(self):
        self.h.initialize()
        self.h.registry.lock.unlink()
        os.mkfifo(self.h.registry.lock)
        with self.assertRaises(runctl.AuthorityError):
            with self.h.registry._locked():
                pass

    def test_unanchored_preexisting_lock_fails_closed(self):
        self.h.registry.lock.parent.mkdir(parents=True, exist_ok=True)
        self.h.registry.lock.write_bytes(b"legacy-or-ambiguous")
        with self.assertRaises(runctl.AuthorityError):
            with self.h.registry._locked():
                pass

    def test_fresh_registry_bootstraps_one_hardlink_authority(self):
        anchor = self.h.initialize()
        lock_st = os.lstat(self.h.registry.lock)
        anchor_st = os.lstat(anchor)
        self.assertEqual((lock_st.st_dev, lock_st.st_ino), (anchor_st.st_dev, anchor_st.st_ino))
        self.assertGreaterEqual(lock_st.st_nlink, 2)
        with self.h.registry._locked():
            pass


if __name__ == "__main__":
    unittest.main()
