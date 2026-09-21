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
            with self.assertRaises(runctl.AuthorityError):
                with self.h.registry._locked():
                    self.fail("replacement inode must never become a valid mutation domain")
            # Immediate fail-closed is valid: prove the original inode is still
            # locked by process A when the replacement is rejected.
            self.assertIsNone(proc.poll())
        finally:
            proc.wait(timeout=5)
            self.assertEqual(proc.returncode, 0, proc.stderr.read())

    def test_replacement_while_waiting_is_rejected_after_holder_releases(self):
        self.h.initialize()
        proc = self._holder()
        child = r"""
import importlib.util, pathlib, sys
root=pathlib.Path(sys.argv[1])
registry_path=pathlib.Path(sys.argv[2])
checkout=pathlib.Path(sys.argv[3])
spec=importlib.util.spec_from_file_location("f11_wait_runctl", root/"scripts"/"quant_gate_b_runctl.py")
m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)
r=m.Registry(registry_path, checkout)
try:
    with r._locked():
        print("ENTERED", flush=True)
except Exception as exc:
    print("REJECTED:"+type(exc).__name__+":"+str(exc), flush=True)
"""
        waiter = subprocess.Popen(
            [sys.executable, "-c", child, str(ROOT), str(self.h.registry_path), str(self.h.checkout)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            # Give B time to validate the original identity and block on flock.
            time.sleep(0.20)
            self.h.registry.lock.unlink()
            self.h.registry.lock.write_bytes(b"replacement-while-waiting")
            proc.wait(timeout=5)
            line = waiter.stdout.readline().strip()
            waiter.wait(timeout=5)
            self.assertTrue(line.startswith("REJECTED:AuthorityError:"), line)
            self.assertNotIn("ENTERED", line)
            self.assertEqual(waiter.returncode, 0, waiter.stderr.read())
        finally:
            if proc.poll() is None:
                proc.wait(timeout=5)
            if waiter.poll() is None:
                waiter.kill()
                waiter.wait(timeout=5)


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

    def test_coordinated_public_and_anchor_replacement_cannot_split_live_domain(self):
        anchor = self.h.initialize()
        contender = None
        child = r"""
import importlib.util, pathlib, sys
root=pathlib.Path(sys.argv[1])
registry_path=pathlib.Path(sys.argv[2])
checkout=pathlib.Path(sys.argv[3])
spec=importlib.util.spec_from_file_location("f11_dual_replace_runctl", root/"scripts"/"quant_gate_b_runctl.py")
m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)
r=m.Registry(registry_path, checkout)
try:
    with r._locked():
        print("ENTERED", flush=True)
except Exception as exc:
    print("REJECTED:"+type(exc).__name__+":"+str(exc), flush=True)
"""
        with self.assertRaises(runctl.AuthorityError):
            with self.h.registry._locked():
                # Replace both visible names with a fresh, internally consistent
                # hard-link pair. Without the outer parent-directory lock this
                # can form a second valid flock domain while the first holder is
                # still inside its mutation window.
                self.h.registry.lock.unlink()
                anchor.unlink()
                self.h.registry.lock.write_bytes(b"replacement-pair")
                st = os.lstat(self.h.registry.lock)
                replacement_anchor = self.h.registry.lock.parent / (
                    f"{self.h.registry.lock.name}.authority.{st.st_dev:x}.{st.st_ino:x}"
                )
                os.link(self.h.registry.lock, replacement_anchor, follow_symlinks=False)

                contender = subprocess.Popen(
                    [
                        sys.executable,
                        "-c",
                        child,
                        str(ROOT),
                        str(self.h.registry_path),
                        str(self.h.checkout),
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                time.sleep(0.30)
                self.assertIsNone(
                    contender.poll(),
                    "replacement authority pair must not create a concurrent mutation domain",
                )

        assert contender is not None
        line = contender.stdout.readline().strip()
        contender.wait(timeout=5)
        self.assertEqual(contender.returncode, 0, contender.stderr.read())
        self.assertEqual(line, "ENTERED")

    def test_repeated_public_lock_replacement_remains_fail_closed(self):
        self.h.initialize()
        with self.assertRaises(runctl.AuthorityError):
            with self.h.registry._locked():
                for i in range(8):
                    self.h.registry.lock.unlink()
                    self.h.registry.lock.write_bytes(f"replacement-{i}".encode())

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


HOLDER_ENTER_AND_SLEEP = r"""
import importlib.util, pathlib, sys, time
root=pathlib.Path(sys.argv[1])
registry_path=pathlib.Path(sys.argv[2])
checkout=pathlib.Path(sys.argv[3])
delay=float(sys.argv[4])
spec=importlib.util.spec_from_file_location("f11_parent_holder_runctl", root/"scripts"/"quant_gate_b_runctl.py")
m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)
r=m.Registry(registry_path, checkout)
try:
    with r._locked():
        print("ENTERED_A", flush=True)
        time.sleep(delay)
    print("A_EXIT_OK", flush=True)
except Exception as exc:
    print("A_REJECTED:"+type(exc).__name__+":"+str(exc), flush=True)
"""

CONTENDER_MUTATE = r"""
import importlib.util, pathlib, sys
root=pathlib.Path(sys.argv[1])
registry_path=pathlib.Path(sys.argv[2])
checkout=pathlib.Path(sys.argv[3])
reference=sys.argv[4]
spec=importlib.util.spec_from_file_location("f11_parent_contender_runctl", root/"scripts"/"quant_gate_b_runctl.py")
m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)
r=m.Registry(registry_path, checkout)
try:
    r.set_revocation_epoch(epoch=1, reference=reference)
    print("B_MUTATED", flush=True)
except Exception as exc:
    print("B_REJECTED:"+type(exc).__name__+":"+str(exc), flush=True)
"""


class GateBF11ParentPathIdentityTests(unittest.TestCase):
    """F11-P1/P2/P3: whole configured-parent-directory replacement while a real
    process is inside the production Registry._locked() critical section.

    Astra's original F11 finding replaced only the public lock pathname inside
    a stable parent directory; the repair above (hard-link lock authority +
    parent-directory flock) closes that. Blue's follow-on adversarial
    challenge replaces the parent directory itself -- the outer serialization
    object -- while a holder remains active inside it. These tests reproduce
    that exact sequence with disposable local directories and real
    independent OS processes against the actual production code path.
    """

    def setUp(self):
        self.h = LockHarness()

    def tearDown(self):
        self.h.close()

    def _swap_parent_directory(self) -> tuple[Path, Path]:
        """Replace the configured registry parent directory in place: move the
        real (locked) directory P1 aside and create a fresh empty directory P2
        at the original configured pathname."""
        original = self.h.registry.lock.parent
        replaced_away = original.parent / (original.name + ".swapped-away")
        os.rename(original, replaced_away)
        original.mkdir()
        return replaced_away, original

    def test_f11_p1_whole_parent_replacement_blocks_concurrent_second_domain(self):
        self.h.initialize()
        holder = subprocess.Popen(
            [
                sys.executable, "-c", HOLDER_ENTER_AND_SLEEP,
                str(ROOT), str(self.h.registry_path), str(self.h.checkout), "1.5",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            self.assertEqual(holder.stdout.readline().strip(), "ENTERED_A")
            time.sleep(0.15)
            original_p1, live_pathname = self._swap_parent_directory()
            self.assertNotEqual(
                os.lstat(original_p1).st_ino, os.lstat(live_pathname).st_ino
            )

            # B constructs the same logical Registry path and invokes the
            # actual production locking/mutation entrypoint while A remains
            # active inside the original parent-directory inode.
            contender = subprocess.run(
                [
                    sys.executable, "-c", CONTENDER_MUTATE,
                    str(ROOT), str(self.h.registry_path), str(self.h.checkout), "attacker-b",
                ],
                capture_output=True, text=True, timeout=10,
            )

            # The required invariant: A must still be active (unresolved) at
            # the moment B's attempt concludes -- proving B was rejected
            # concurrently with A, not merely after A finished.
            self.assertIsNone(
                holder.poll(),
                "process A must still be inside its critical section when B is evaluated",
            )
            self.assertTrue(
                contender.stdout.strip().startswith("B_REJECTED:AuthorityError:"),
                contender.stdout,
            )
            self.assertNotIn("B_MUTATED", contender.stdout)
        finally:
            holder.wait(timeout=5)
            tail = holder.stdout.readline().strip()
            self.assertTrue(tail == "" or tail.startswith("A_EXIT_OK") or tail.startswith("A_REJECTED"), tail)

    def test_f11_p2_rejected_parent_replacement_creates_no_mutation(self):
        self.h.initialize()
        holder = subprocess.Popen(
            [
                sys.executable, "-c", HOLDER_ENTER_AND_SLEEP,
                str(ROOT), str(self.h.registry_path), str(self.h.checkout), "1.0",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            self.assertEqual(holder.stdout.readline().strip(), "ENTERED_A")
            time.sleep(0.15)
            _, live_pathname = self._swap_parent_directory()

            before = sorted(p.name for p in live_pathname.iterdir())
            self.assertEqual(before, [])

            contender = subprocess.run(
                [
                    sys.executable, "-c", CONTENDER_MUTATE,
                    str(ROOT), str(self.h.registry_path), str(self.h.checkout), "attacker-b",
                ],
                capture_output=True, text=True, timeout=10,
            )
            self.assertTrue(
                contender.stdout.strip().startswith("B_REJECTED:AuthorityError:"),
                contender.stdout,
            )

            # No reservation, activation, evidence, registry event, terminal
            # mutation, or reusable authority artifact may exist under the
            # rejected replacement-parent contender.
            after = sorted(p.name for p in live_pathname.iterdir())
            self.assertEqual(after, [])
            self.assertFalse((live_pathname / self.h.registry_path.name).exists())
            self.assertFalse((live_pathname / self.h.registry.lock.name).exists())
        finally:
            holder.wait(timeout=5)

    def test_f11_p3_persistent_fail_closed_then_recovery_under_stable_authority(self):
        self.h.initialize()
        original_p1, live_pathname = self._swap_parent_directory()

        # While the replacement persists, every subsequent caller against the
        # configured pathname must deterministically fail closed -- no second
        # logical registry history is ever silently bootstrapped under P2.
        for reference in ("attacker-c1", "attacker-c2"):
            result = subprocess.run(
                [
                    sys.executable, "-c", CONTENDER_MUTATE,
                    str(ROOT), str(self.h.registry_path), str(self.h.checkout), reference,
                ],
                capture_output=True, text=True, timeout=10,
            )
            self.assertTrue(result.stdout.strip().startswith("B_REJECTED:AuthorityError:"), result.stdout)
        self.assertEqual(sorted(p.name for p in live_pathname.iterdir()), [])

        # Operator repair: remove the fake replacement directory and restore
        # the original authoritative directory at the configured pathname.
        live_pathname.rmdir()
        os.rename(original_p1, live_pathname)

        recovered = subprocess.run(
            [
                sys.executable, "-c", CONTENDER_MUTATE,
                str(ROOT), str(self.h.registry_path), str(self.h.checkout), "operator-recovered",
            ],
            capture_output=True, text=True, timeout=10,
        )
        # The attempted epoch is a duplicate of the original bootstrap epoch,
        # so it is rejected for being non-monotonic -- proof that recovery
        # continues the single original registry history rather than
        # accepting a fresh one, and proof the mutation channel is live again
        # under the one stable authority.
        self.assertTrue(
            recovered.stdout.strip().startswith("B_REJECTED:AuthorityError:")
            and "epoch" in recovered.stdout,
            recovered.stdout,
        )
        events = runctl.load_registry(self.h.registry_path)
        self.assertEqual([e["event_type"] for e in events], ["REVOCATION_EPOCH_SET"])
        self.assertEqual(events[0]["revocation_reference"], "blue/f11")


if __name__ == "__main__":
    unittest.main()
