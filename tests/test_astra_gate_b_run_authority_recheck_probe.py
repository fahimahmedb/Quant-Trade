from __future__ import annotations

import datetime as dt
import errno
import fcntl
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072"
TREE = "4d15ef6f471213ee6ab56337b555d2906ef9bf16"
INPUT = "sha256:" + "1" * 64

def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

runctl = load_module("astra_recheck_runctl", ROOT / "scripts" / "quant_gate_b_runctl.py")
verifier = load_module("astra_recheck_verifier", ROOT / "scripts" / "verify_gate_b_deployed_bytes.py")

def fd_path(fd: int) -> str:
    try:
        return os.readlink(f"/proc/self/fd/{fd}")
    except OSError:
        return ""

class RunHarness:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.state = self.root / "state"
        self.registry_path = self.state / "registry.ndjson"
        self.receipts = self.root / "receipts"
        self.registry = runctl.Registry(self.registry_path, ROOT)
        self.epoch = 7
        self.ref = "astra/recheck"

    def close(self):
        self.tmp.cleanup()

    def set_epoch(self, now=None):
        return self.registry.set_revocation_epoch(
            epoch=self.epoch,
            reference=self.ref,
            event_time=now or dt.datetime.now(dt.timezone.utc),
        )

    def reserve(self, run_id=None, now=None, host="astra-host"):
        rid = run_id or f"gate-b-{uuid.uuid4()}"
        return self.registry.reserve(
            candidate_sha=CANDIDATE,
            git_tree=TREE,
            verified_input_tree_digest=INPUT,
            target_host_opaque_id=host,
            blue_reference="blue/astra-recheck",
            operator_identity_reference="astra",
            run_id_factory=lambda: rid,
            event_time=now or dt.datetime.now(dt.timezone.utc),
        )

    def activation(self, reservation, *, issued=None, not_before=None, expires=None, activation_id=None, overrides=None):
        now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
        obj = {
            "schema": runctl.ACTIVATION_SCHEMA,
            "activation_id": activation_id or f"act-{uuid.uuid4()}",
            "run_id": reservation["run_id"],
            "attempt_number": reservation["attempt_number"],
            "reservation_digest": reservation["event_digest"],
            "candidate_sha": CANDIDATE,
            "git_tree": TREE,
            "verified_input_tree_digest": INPUT,
            "target_host_opaque_id": reservation["target_host_opaque_id"],
            "issued_at_utc": runctl.utc_text(issued or (now - dt.timedelta(seconds=2))),
            "not_before_utc": runctl.utc_text(not_before or (now - dt.timedelta(seconds=1))),
            "expires_at_utc": runctl.utc_text(expires or (now + dt.timedelta(minutes=2))),
            "revocation_epoch": self.epoch,
            "revocation_reference": self.ref,
            "gate_b_mutation_authorized": True,
        }
        if overrides:
            obj.update(overrides)
        raw = runctl.canonical_json_bytes(obj)
        return obj, raw, runctl.sha256_digest(raw)

    def sealed(self, **kwargs):
        self.set_epoch()
        r = self.reserve()
        obj, raw, digest = self.activation(r, **kwargs)
        self.registry.seal_activation(activation_bytes=raw, activation_digest=digest)
        return r, obj, raw, digest

    def consume(self, raw, digest, run_id, now=None):
        return self.registry.consume_activation(
            activation_bytes=raw,
            activation_digest=digest,
            receipt_dir=self.receipts,
            expected_run_id=run_id,
            expected_candidate=(CANDIDATE, TREE, INPUT),
            now=now,
        )

    def binding(self, reservation, activation_digest, ordinal=1, artifact_digest=None, extra=None):
        obj = {
            "schema": runctl.EVIDENCE_BINDING_SCHEMA,
            "run_id": reservation["run_id"],
            "attempt_number": reservation["attempt_number"],
            "activation_digest": activation_digest,
            "reservation_digest": reservation["event_digest"],
            "candidate_sha": CANDIDATE,
            "git_tree": TREE,
            "verified_input_tree_digest": INPUT,
            "target_host_opaque_id": reservation["target_host_opaque_id"],
            "artifact_type": "astra_probe",
            "artifact_ordinal": ordinal,
            "artifact_digest": artifact_digest or ("sha256:" + "a" * 64),
            "created_at_utc": runctl.utc_text(),
        }
        if extra:
            obj.update(extra)
        raw = runctl.canonical_json_bytes(obj)
        return raw, runctl.sha256_digest(raw)

def make_git_repo():
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    repo = root / "release"
    repo.mkdir()
    def git(*args, cwd=None, check=True, env=None):
        p = subprocess.run(
            ["git", "-C", str(cwd or repo), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=check,
            env=env,
        )
        return p.stdout
    git("init", "-q")
    git("config", "user.name", "Astra")
    git("config", "user.email", "astra@example.invalid")
    (repo / "src").mkdir()
    (repo / "scripts").mkdir()
    (repo / "deploy").mkdir()
    (repo / "src" / "main.py").write_text("print('frozen')\n")
    (repo / "scripts" / "tool.sh").write_text("#!/bin/sh\necho ok\n")
    (repo / "scripts" / "tool.sh").chmod(0o755)
    (repo / "deploy" / "unit.service").write_text("[Service]\nExecStart=/bin/true\n")
    (repo / "README.md").write_text("frozen\n")
    git("add", ".")
    git("commit", "-qm", "frozen")
    sha = git("rev-parse", "HEAD").strip()
    tree = git("rev-parse", "HEAD^{tree}").strip()
    return tmp, root, repo, git, sha, tree

class AstraGateBRecheckProbe(unittest.TestCase):
    def test_astra_independent_adversarial_matrix(self):
        # A1: independent exact-write / failure injection.
        h = RunHarness()
        try:
            h.set_epoch()
            real_write = os.write
            calls = {"n": 0}
            def tiny(fd, data):
                if fd_path(fd) == str(h.registry_path):
                    calls["n"] += 1
                    payload = bytes(data)
                    return real_write(fd, payload[: min(5, len(payload))])
                return real_write(fd, data)
            with mock.patch.object(runctl.os, "write", side_effect=tiny):
                h.reserve()
            self.assertGreater(calls["n"], 2)
            runctl.load_registry(h.registry_path)
        finally:
            h.close()

        h = RunHarness()
        try:
            h.set_epoch()
            r, _, raw, digest = h.sealed()[0:4]
        finally:
            h.close()

        h = RunHarness()
        try:
            r, _, raw, digest = h.sealed()
            real_write = os.write
            state = {"n": 0}
            def partial_then_eio(fd, data):
                if fd_path(fd) == str(h.registry_path):
                    payload = bytes(data)
                    if state["n"] == 0:
                        state["n"] = 1
                        return real_write(fd, payload[: max(1, len(payload)//4)])
                    if state["n"] == 1:
                        state["n"] = 2
                        raise OSError(errno.EIO, "astra injected")
                return real_write(fd, data)
            with mock.patch.object(runctl.os, "write", side_effect=partial_then_eio):
                with self.assertRaises(runctl.AuthorityError):
                    h.consume(raw, digest, r["run_id"])
            self.assertFalse(h.receipts.exists() and any(h.receipts.iterdir()))
            with self.assertRaises(runctl.AuthorityError):
                runctl.load_registry(h.registry_path)
        finally:
            h.close()
        print("ASTRA_A1_OK", flush=True)

        # A2: directory durability failures remain visible and consumption stays consumed.
        h = RunHarness()
        try:
            with mock.patch.object(runctl, "_fsync_dir", side_effect=runctl.AuthorityError("astra dir fsync")):
                with self.assertRaises(runctl.AuthorityError):
                    h.set_epoch()
            self.assertEqual(runctl.load_registry(h.registry_path)[-1]["event_type"], "REVOCATION_EPOCH_SET")
        finally:
            h.close()

        h = RunHarness()
        try:
            r, _, raw, digest = h.sealed()
            real_fsync_dir = runctl._fsync_dir
            def fail_receipt_dir(path):
                if Path(path) == h.receipts:
                    raise runctl.AuthorityError("astra receipt fsync")
                return real_fsync_dir(path)
            with mock.patch.object(runctl, "_fsync_dir", side_effect=fail_receipt_dir):
                with self.assertRaises(runctl.AuthorityError):
                    h.consume(raw, digest, r["run_id"])
            self.assertEqual(runctl.load_registry(h.registry_path)[-1]["event_type"], "ACTIVATION_CONSUMED")
            with self.assertRaises(runctl.AuthorityError):
                h.consume(raw, digest, r["run_id"])
        finally:
            h.close()
        print("ASTRA_A2_OK", flush=True)

        # A3: real independent flock contention, expiry while blocked.
        h = RunHarness()
        try:
            now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
            h.set_epoch(now)
            r = h.reserve(now=now)
            _, raw, digest = h.activation(
                r,
                issued=now-dt.timedelta(seconds=2),
                not_before=now-dt.timedelta(seconds=1),
                expires=now+dt.timedelta(seconds=1),
            )
            h.registry.seal_activation(activation_bytes=raw, activation_digest=digest, event_time=now)
            code = r"""
import fcntl, os, sys, time
p=sys.argv[1]
fd=os.open(p, os.O_RDWR|os.O_CREAT, 0o600)
fcntl.flock(fd, fcntl.LOCK_EX)
print("LOCKED", flush=True)
time.sleep(2.2)
fcntl.flock(fd, fcntl.LOCK_UN)
os.close(fd)
"""
            proc = subprocess.Popen([sys.executable, "-c", code, str(h.registry.lock)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertEqual(proc.stdout.readline().strip(), "LOCKED")
            with self.assertRaises(runctl.AuthorityError):
                h.consume(raw, digest, r["run_id"], now=None)
            proc.wait(timeout=10)
            self.assertEqual(proc.returncode, 0, proc.stderr.read())
            self.assertFalse(any(e["event_type"] == "ACTIVATION_CONSUMED" for e in runctl.load_registry(h.registry_path)))
        finally:
            h.close()
        print("ASTRA_A3_OK", flush=True)

        # A4: chronology and UTC boundaries.
        invalid_cases = [
            ("future-issued", dict(issued=dt.datetime.now(dt.timezone.utc)+dt.timedelta(minutes=1))),
            ("not-before-eq-expiry", dict(not_before=dt.datetime.now(dt.timezone.utc)+dt.timedelta(seconds=5), expires=dt.datetime.now(dt.timezone.utc)+dt.timedelta(seconds=5))),
            ("reversed", dict(not_before=dt.datetime.now(dt.timezone.utc)+dt.timedelta(seconds=6), expires=dt.datetime.now(dt.timezone.utc)+dt.timedelta(seconds=5))),
        ]
        for name, kw in invalid_cases:
            h = RunHarness()
            try:
                h.set_epoch(); r = h.reserve()
                _, raw, digest = h.activation(r, **kw)
                h.registry.seal_activation(activation_bytes=raw, activation_digest=digest)
                with self.assertRaises(runctl.AuthorityError, msg=name):
                    h.consume(raw, digest, r["run_id"], now=dt.datetime.now(dt.timezone.utc))
            finally:
                h.close()
        h = RunHarness()
        try:
            h.set_epoch(); r = h.reserve()
            _, raw, digest = h.activation(r, overrides={"issued_at_utc": "2026-09-21T10:00:00+00:00"})
            with self.assertRaises(runctl.AuthorityError):
                h.registry.seal_activation(activation_bytes=raw, activation_digest=digest)
        finally:
            h.close()
        h = RunHarness()
        try:
            r, _, raw, digest = h.sealed()
            ev, _ = h.consume(raw, digest, r["run_id"], now=dt.datetime.now(dt.timezone.utc))
            self.assertEqual(ev["event_type"], "ACTIVATION_CONSUMED")
        finally:
            h.close()
        print("ASTRA_A4_OK", flush=True)

        # A5: exact consumed activation binding and ordinal strictness.
        h = RunHarness()
        try:
            r, _, raw, digest = h.sealed()
            h.consume(raw, digest, r["run_id"], now=dt.datetime.now(dt.timezone.utc))
            wrong = "sha256:" + "b" * 64
            braw, bd = h.binding(r, wrong)
            with self.assertRaises(runctl.AuthorityError):
                h.registry.bind_evidence(binding_bytes=braw, binding_digest=bd)
            for ordinal in ("1", True, False, 0, -1):
                braw, bd = h.binding(r, digest, ordinal=ordinal)
                with self.assertRaises(runctl.AuthorityError):
                    h.registry.bind_evidence(binding_bytes=braw, binding_digest=bd)
            braw, bd = h.binding(r, digest, ordinal=1, artifact_digest="sha256:"+"c"*64)
            h.registry.bind_evidence(binding_bytes=braw, binding_digest=bd)
            braw, bd = h.binding(r, digest, ordinal=1, artifact_digest="sha256:"+"d"*64)
            with self.assertRaises(runctl.AuthorityError):
                h.registry.bind_evidence(binding_bytes=braw, binding_digest=bd)
        finally:
            h.close()
        print("ASTRA_A5_OK", flush=True)

        # A6/A7/A9/A10: independent disposable Git authority attacks.
        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            report, _ = verifier.verify(repo2, expected_sha=sha, expected_tree=tree)
            self.assertEqual(report["status"], "GREEN")
            index = repo2 / ".git" / "index"
            before = (index.stat().st_mtime_ns, index.read_bytes())
            report, _ = verifier.verify(repo2, expected_sha=sha, expected_tree=tree)
            after = (index.stat().st_mtime_ns, index.read_bytes())
            self.assertEqual(before, after)
            self.assertEqual(report["git_metadata_before"]["lock_paths"], report["git_metadata_after"]["lock_paths"])
        finally:
            tmp.cleanup()

        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            foreign = root / "foreign-objects"
            objects = repo2 / ".git" / "objects"
            shutil.copytree(objects, foreign, copy_function=shutil.copy2)
            shutil.rmtree(objects)
            os.symlink(foreign, objects)
            self.assertEqual(git("rev-parse", "HEAD^{tree}").strip(), tree)
            with self.assertRaises(verifier.VerifyError):
                verifier.verify(repo2, expected_sha=sha, expected_tree=tree)
        finally:
            tmp.cleanup()

        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            alt = repo2 / ".git" / "objects" / "info" / "alternates"
            alt.parent.mkdir(parents=True, exist_ok=True)
            alt.write_text("")
            with self.assertRaises(verifier.VerifyError):
                verifier.verify(repo2, expected_sha=sha, expected_tree=tree)
        finally:
            tmp.cleanup()

        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            with mock.patch.dict(os.environ, {"GIT_OBJECT_DIRECTORY": str(root / "foreign")}, clear=False):
                with self.assertRaises(verifier.VerifyError):
                    verifier.verify(repo2, expected_sha=sha, expected_tree=tree)
        finally:
            tmp.cleanup()
        print("ASTRA_A6_OK", flush=True)

        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            expected_tree = tree
            (repo2 / "src" / "main.py").write_text("print('poison')\n")
            git("add", "src/main.py")
            malicious_tree = git("write-tree").strip()
            malicious_listing = git("ls-tree", "-r", malicious_tree)
            git("reset", "--hard", "-q", sha)
            (repo2 / "src" / "main.py").write_text("print('poison')\n")
            git("replace", expected_tree, malicious_tree)
            self.assertEqual(git("rev-parse", "HEAD^{tree}").strip(), expected_tree)
            self.assertEqual(git("ls-tree", "-r", expected_tree), malicious_listing)
            with self.assertRaises(verifier.VerifyError):
                verifier.verify(repo2, expected_sha=sha, expected_tree=expected_tree)
        finally:
            tmp.cleanup()
        print("ASTRA_A7_OK", flush=True)

        # A8 exact frozen candidate from self-contained local clone.
        with tempfile.TemporaryDirectory() as td:
            clone = Path(td) / "frozen"
            subprocess.run(["git", "clone", "--no-local", "--no-checkout", "-q", str(ROOT), str(clone)], check=True)
            have = subprocess.run(["git", "-C", str(clone), "cat-file", "-e", f"{CANDIDATE}^{{commit}}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if have.returncode != 0:
                subprocess.run(["git", "-C", str(clone), "fetch", "-q", "--no-tags", str(ROOT), CANDIDATE], check=True)
            subprocess.run(["git", "-C", str(clone), "checkout", "-q", "--detach", CANDIDATE], check=True)
            self.assertEqual(subprocess.check_output(["git", "-C", str(clone), "rev-parse", "HEAD"], text=True).strip(), CANDIDATE)
            self.assertEqual(subprocess.check_output(["git", "-C", str(clone), "rev-parse", "HEAD^{tree}"], text=True).strip(), TREE)
            self.assertFalse((clone / ".git" / "objects" / "info" / "alternates").exists())
            report, _ = verifier.verify(clone, expected_sha=CANDIDATE, expected_tree=TREE)
            self.assertEqual(report["status"], "GREEN")
        print("ASTRA_A8_OK", flush=True)

        for mutation in ("mode", "missing", "critical-extra", "noncritical-extra", "symlink"):
            tmp, root, repo2, git, sha, tree = make_git_repo()
            try:
                if mutation == "mode":
                    (repo2 / "scripts" / "tool.sh").chmod(0o644)
                elif mutation == "missing":
                    (repo2 / "deploy" / "unit.service").unlink()
                elif mutation == "critical-extra":
                    (repo2 / "src" / "extra.py").write_text("pass\n")
                elif mutation == "noncritical-extra":
                    (repo2 / "notes.txt").write_text("x\n")
                else:
                    p = repo2 / "src" / "main.py"
                    p.unlink()
                    os.symlink("../README.md", p)
                report, _ = verifier.verify(repo2, expected_sha=sha, expected_tree=tree)
                self.assertEqual(report["status"], "RED", mutation)
            finally:
                tmp.cleanup()
        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            with self.assertRaises(verifier.VerifyError):
                verifier.verify(repo2, expected_sha=sha, expected_tree=tree, allowed_extra_prefixes=("../src",))
        finally:
            tmp.cleanup()
        print("ASTRA_A9_OK", flush=True)

        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            target = repo2 / "src" / "main.py"
            original_walk = verifier.walk_filesystem
            def swap_after_walk(*args, **kwargs):
                observed = original_walk(*args, **kwargs)
                target.unlink()
                os.symlink("../README.md", target)
                return observed
            with mock.patch.object(verifier, "walk_filesystem", side_effect=swap_after_walk):
                report, _ = verifier.verify(repo2, expected_sha=sha, expected_tree=tree)
            self.assertEqual(report["status"], "RED")
        finally:
            tmp.cleanup()
        print("ASTRA_A10_OK", flush=True)

        # Beyond A1-A10: lock pathname replacement must not split exclusivity.
        h = RunHarness()
        try:
            h.state.mkdir(parents=True, exist_ok=True)
            code = r"""
import fcntl, os, sys, time
p=sys.argv[1]
fd=os.open(p, os.O_RDWR|os.O_CREAT, 0o600)
fcntl.flock(fd, fcntl.LOCK_EX)
print("LOCKED", flush=True)
time.sleep(3.0)
fcntl.flock(fd, fcntl.LOCK_UN)
os.close(fd)
"""
            proc = subprocess.Popen([sys.executable, "-c", code, str(h.registry.lock)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertEqual(proc.stdout.readline().strip(), "LOCKED")
            original_inode = h.registry.lock.stat().st_ino
            h.registry.lock.unlink()
            h.registry.lock.write_bytes(b"")
            replacement_inode = h.registry.lock.stat().st_ino
            self.assertNotEqual(original_inode, replacement_inode)
            started = time.monotonic()
            with h.registry._locked():
                elapsed = time.monotonic() - started
            proc.wait(timeout=10)
            self.assertEqual(proc.returncode, 0, proc.stderr.read())
            print(f"ASTRA_LOCK_REPLACEMENT_ACQUIRE_SECONDS={elapsed:.6f}", flush=True)
            self.assertGreaterEqual(
                elapsed,
                2.0,
                "REAL_DEFECT: lock pathname replacement created a second independently-lockable inode",
            )
        finally:
            h.close()

if __name__ == "__main__":
    unittest.main()
