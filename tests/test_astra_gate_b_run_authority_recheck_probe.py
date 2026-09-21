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
import threading
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


        # Independent completeness sweep for mission-mandated variants that are
        # deliberately separate from the Builder-authored repair tests.

        # A1: EINTR, zero-progress, receipt partial writes and receipt failure.
        h = RunHarness()
        try:
            h.set_epoch()
            real_write = os.write
            state = {"raised": False}
            def eintr_once(fd, data):
                if fd_path(fd) == str(h.registry_path) and not state["raised"]:
                    state["raised"] = True
                    raise InterruptedError(errno.EINTR, "astra eintr")
                return real_write(fd, data)
            with mock.patch.object(runctl.os, "write", side_effect=eintr_once):
                h.reserve()
            self.assertTrue(state["raised"])
            runctl.load_registry(h.registry_path)
        finally:
            h.close()

        h = RunHarness()
        try:
            h.set_epoch()
            real_write = os.write
            def zero_registry(fd, data):
                if fd_path(fd) == str(h.registry_path):
                    return 0
                return real_write(fd, data)
            with mock.patch.object(runctl.os, "write", side_effect=zero_registry):
                with self.assertRaises(runctl.AuthorityError):
                    h.reserve()
            self.assertEqual(runctl.load_registry(h.registry_path)[-1]["event_type"], "REVOCATION_EPOCH_SET")
        finally:
            h.close()

        h = RunHarness()
        try:
            r, _, raw, digest = h.sealed()
            real_write = os.write
            receipt_calls = {"n": 0}
            def partial_receipt(fd, data):
                opened = fd_path(fd)
                if opened.startswith(str(h.receipts)):
                    receipt_calls["n"] += 1
                    payload = bytes(data)
                    return real_write(fd, payload[: max(1, min(7, len(payload)))])
                return real_write(fd, data)
            with mock.patch.object(runctl.os, "write", side_effect=partial_receipt):
                _, receipt = h.consume(raw, digest, r["run_id"], now=dt.datetime.now(dt.timezone.utc))
            final_bytes = Path(receipt["path"]).read_bytes()
            self.assertGreater(receipt_calls["n"], 1)
            self.assertEqual(runctl.sha256_digest(final_bytes), receipt["digest"])
        finally:
            h.close()

        h = RunHarness()
        try:
            r, _, raw, digest = h.sealed()
            real_write = os.write
            def zero_receipt(fd, data):
                if fd_path(fd).startswith(str(h.receipts)):
                    return 0
                return real_write(fd, data)
            with mock.patch.object(runctl.os, "write", side_effect=zero_receipt):
                with self.assertRaises(runctl.AuthorityError):
                    h.consume(raw, digest, r["run_id"], now=dt.datetime.now(dt.timezone.utc))
            self.assertEqual(runctl.load_registry(h.registry_path)[-1]["event_type"], "ACTIVATION_CONSUMED")
            with self.assertRaises(runctl.AuthorityError):
                h.consume(raw, digest, r["run_id"], now=dt.datetime.now(dt.timezone.utc))
        finally:
            h.close()

        # A2: existing-registry append, placement/link failure, final collision.
        h = RunHarness()
        try:
            h.set_epoch()
            with mock.patch.object(runctl, "_fsync_dir", side_effect=runctl.AuthorityError("unexpected directory fsync")):
                h.reserve()
        finally:
            h.close()

        h = RunHarness()
        try:
            r, _, raw, digest = h.sealed()
            with mock.patch.object(runctl.os, "link", side_effect=OSError(errno.EIO, "astra link failure")):
                with self.assertRaises((runctl.AuthorityError, OSError)):
                    h.consume(raw, digest, r["run_id"], now=dt.datetime.now(dt.timezone.utc))
            self.assertEqual(runctl.load_registry(h.registry_path)[-1]["event_type"], "ACTIVATION_CONSUMED")
            with self.assertRaises(runctl.AuthorityError):
                h.consume(raw, digest, r["run_id"], now=dt.datetime.now(dt.timezone.utc))
        finally:
            h.close()

        h = RunHarness()
        try:
            r, a, raw, digest = h.sealed()
            decision = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
            receipt_obj = {
                "schema": runctl.RECEIPT_SCHEMA,
                "run_id": a["run_id"],
                "attempt_number": a["attempt_number"],
                "activation_id": a["activation_id"],
                "activation_digest": digest,
                "reservation_digest": r["event_digest"],
                "candidate_sha": a["candidate_sha"],
                "git_tree": a["git_tree"],
                "verified_input_tree_digest": a["verified_input_tree_digest"],
                "target_host_opaque_id": a["target_host_opaque_id"],
                "consumed_at_utc": runctl.utc_text(decision),
            }
            rb = runctl.canonical_json_bytes(receipt_obj) + b"\n"
            rd = runctl.sha256_digest(rb)
            final = h.receipts / (rd.split(":", 1)[1] + ".json")
            final.parent.mkdir(parents=True, exist_ok=True)
            final.write_bytes(b"preexisting")
            with self.assertRaises(runctl.AuthorityError):
                h.consume(raw, digest, r["run_id"], now=decision)
            self.assertEqual(final.read_bytes(), b"preexisting")
            self.assertEqual(runctl.load_registry(h.registry_path)[-1]["event_type"], "ACTIVATION_CONSUMED")
            with self.assertRaises(runctl.AuthorityError):
                h.consume(raw, digest, r["run_id"], now=decision)
        finally:
            h.close()

        # A4: all remaining chronology/freshness boundaries.
        fixed = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
        chronology_cases = [
            ("future-not-before", fixed-dt.timedelta(seconds=2), fixed+dt.timedelta(seconds=1), fixed+dt.timedelta(minutes=1), fixed),
            ("issued-after-not-before", fixed, fixed-dt.timedelta(seconds=1), fixed+dt.timedelta(minutes=1), fixed),
            ("already-expired", fixed-dt.timedelta(seconds=3), fixed-dt.timedelta(seconds=2), fixed-dt.timedelta(seconds=1), fixed),
            ("exact-expiry", fixed-dt.timedelta(seconds=2), fixed-dt.timedelta(seconds=1), fixed, fixed),
        ]
        for name, issued, not_before, expires, decision in chronology_cases:
            h = RunHarness()
            try:
                h.set_epoch(fixed)
                r = h.reserve(now=fixed)
                _, raw, digest = h.activation(r, issued=issued, not_before=not_before, expires=expires)
                h.registry.seal_activation(activation_bytes=raw, activation_digest=digest, event_time=fixed)
                with self.assertRaises(runctl.AuthorityError, msg=name):
                    h.consume(raw, digest, r["run_id"], now=decision)
            finally:
                h.close()

        h = RunHarness()
        try:
            h.set_epoch(fixed); r = h.reserve(now=fixed)
            _, raw, digest = h.activation(r, overrides={"expires_at_utc": "not-a-timestamp"})
            with self.assertRaises(runctl.AuthorityError):
                h.registry.seal_activation(activation_bytes=raw, activation_digest=digest, event_time=fixed)
        finally:
            h.close()

        # A5: cross-run, sealed-unconsumed, unknown-field and malformed fields.
        h = RunHarness()
        try:
            h.set_epoch()
            r1 = h.reserve(run_id="gate-b-11111111-1111-4111-8111-111111111111")
            _, raw1, d1 = h.activation(r1, activation_id="act-astra-one")
            h.registry.seal_activation(activation_bytes=raw1, activation_digest=d1)
            h.consume(raw1, d1, r1["run_id"], now=dt.datetime.now(dt.timezone.utc))
            h.registry.terminal(run_id=r1["run_id"], status="FAILED_TERMINAL", reason="astra complete")
            r2 = h.reserve(run_id="gate-b-22222222-2222-4222-8222-222222222222")
            _, raw2, d2 = h.activation(r2, activation_id="act-astra-two")
            h.registry.seal_activation(activation_bytes=raw2, activation_digest=d2)
            h.consume(raw2, d2, r2["run_id"], now=dt.datetime.now(dt.timezone.utc))
            braw, bd = h.binding(r2, d1, artifact_digest="sha256:"+"e"*64)
            with self.assertRaises(runctl.AuthorityError):
                h.registry.bind_evidence(binding_bytes=braw, binding_digest=bd)
        finally:
            h.close()

        h = RunHarness()
        try:
            h.set_epoch(); r = h.reserve()
            _, raw, digest = h.activation(r)
            h.registry.seal_activation(activation_bytes=raw, activation_digest=digest)
            braw, bd = h.binding(r, digest)
            with self.assertRaises(runctl.AuthorityError):
                h.registry.bind_evidence(binding_bytes=braw, binding_digest=bd)
        finally:
            h.close()

        h = RunHarness()
        try:
            r, _, raw, digest = h.sealed()
            h.consume(raw, digest, r["run_id"], now=dt.datetime.now(dt.timezone.utc))
            for kwargs in (
                {"extra": {"unexpected_authority": "x"}},
                {"artifact_digest": "sha256:bad"},
                {"extra": {"artifact_type": "bad/type"}},
            ):
                braw, bd = h.binding(r, digest, **kwargs)
                with self.assertRaises(runctl.AuthorityError):
                    h.registry.bind_evidence(binding_bytes=braw, binding_digest=bd)
        finally:
            h.close()

        # A6/A7: additional Git authority indirection / legacy replacement variants.
        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            foreign = root / "foreign-git"
            (repo2 / ".git").rename(foreign)
            os.symlink(foreign, repo2 / ".git")
            with self.assertRaises(verifier.VerifyError):
                verifier.verify(repo2, expected_sha=sha, expected_tree=tree)
        finally:
            tmp.cleanup()

        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            foreign = root / "foreign-git"
            (repo2 / ".git").rename(foreign)
            (repo2 / ".git").write_text(f"gitdir: {foreign}\n")
            with self.assertRaises(verifier.VerifyError):
                verifier.verify(repo2, expected_sha=sha, expected_tree=tree)
        finally:
            tmp.cleanup()

        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            worktree = root / "linked"
            git("worktree", "add", "--detach", str(worktree), sha)
            with self.assertRaises(verifier.VerifyError):
                verifier.verify(worktree, expected_sha=sha, expected_tree=tree)
        finally:
            tmp.cleanup()

        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            foreign = root / "common"
            shutil.copytree(repo2 / ".git", foreign, copy_function=shutil.copy2)
            (repo2 / ".git" / "commondir").write_text(str(foreign) + "\n")
            with self.assertRaises(verifier.VerifyError):
                verifier.verify(repo2, expected_sha=sha, expected_tree=tree)
        finally:
            tmp.cleanup()

        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            with mock.patch.dict(os.environ, {"GIT_ALTERNATE_OBJECT_DIRECTORIES": str(root / "foreign")}, clear=False):
                with self.assertRaises(verifier.VerifyError):
                    verifier.verify(repo2, expected_sha=sha, expected_tree=tree)
            with mock.patch.dict(os.environ, {"GIT_OBJECT_DIRECTORY": ""}, clear=False):
                with self.assertRaises(verifier.VerifyError):
                    verifier.verify(repo2, expected_sha=sha, expected_tree=tree)
        finally:
            tmp.cleanup()

        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            alias = root / "alias"
            os.symlink(root, alias)
            with self.assertRaises(verifier.VerifyError):
                verifier.verify(alias / "release", expected_sha=sha, expected_tree=tree)
        finally:
            tmp.cleanup()

        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            objects = repo2 / ".git" / "objects"
            shard = next(p for p in objects.iterdir() if p.is_dir() and len(p.name) == 2)
            foreign = root / "foreign-shard"
            shutil.copytree(shard, foreign, copy_function=shutil.copy2)
            shutil.rmtree(shard)
            os.symlink(foreign, shard)
            with self.assertRaises(verifier.VerifyError):
                verifier.verify(repo2, expected_sha=sha, expected_tree=tree)
        finally:
            tmp.cleanup()

        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            grafts = repo2 / ".git" / "info" / "grafts"
            grafts.parent.mkdir(parents=True, exist_ok=True)
            grafts.write_text(sha + "\n")
            with self.assertRaises(verifier.VerifyError):
                verifier.verify(repo2, expected_sha=sha, expected_tree=tree)
        finally:
            tmp.cleanup()

        # A9: remaining byte/type and allowlist controls.
        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            (repo2 / "src" / "main.py").write_text("print('changed')\n")
            report, _ = verifier.verify(repo2, expected_sha=sha, expected_tree=tree)
            self.assertEqual(report["status"], "RED")
        finally:
            tmp.cleanup()

        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            (repo2 / "docs").mkdir()
            (repo2 / "docs" / "target.txt").write_text("target\n")
            os.symlink("target.txt", repo2 / "docs" / "link")
            git("add", ".")
            git("commit", "-qm", "tracked symlink")
            sha2 = git("rev-parse", "HEAD").strip()
            tree2 = git("rev-parse", "HEAD^{tree}").strip()
            (repo2 / "docs" / "link").unlink()
            (repo2 / "docs" / "link").write_text("target.txt")
            report, _ = verifier.verify(repo2, expected_sha=sha2, expected_tree=tree2)
            self.assertEqual(report["status"], "RED")
        finally:
            tmp.cleanup()

        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            (repo2 / "var").mkdir()
            (repo2 / "var" / "runtime.db").write_text("runtime")
            report, _ = verifier.verify(repo2, expected_sha=sha, expected_tree=tree, allowed_extra_prefixes=("var",))
            self.assertEqual(report["status"], "GREEN")
        finally:
            tmp.cleanup()

        for bad_prefix in ("/tmp", "src/../deploy", "src", "scripts/generated"):
            tmp, root, repo2, git, sha, tree = make_git_repo()
            try:
                with self.assertRaises(verifier.VerifyError, msg=bad_prefix):
                    verifier.verify(repo2, expected_sha=sha, expected_tree=tree, allowed_extra_prefixes=(bad_prefix,))
            finally:
                tmp.cleanup()

        # A10: concurrent content mutation during inspection.
        tmp, root, repo2, git, sha, tree = make_git_repo()
        try:
            target = repo2 / "src" / "main.py"
            original_read = verifier.os.read
            started = threading.Event()
            mutated = threading.Event()
            first = {"done": False}
            def mutate_target():
                self.assertTrue(started.wait(2))
                target.write_text("print('raced')\n")
                mutated.set()
            def slow_read(fd, size):
                opened = fd_path(fd)
                if not first["done"] and opened == str(target):
                    first["done"] = True
                    started.set()
                    self.assertTrue(mutated.wait(2))
                return original_read(fd, size)
            thread = threading.Thread(target=mutate_target)
            thread.start()
            try:
                with mock.patch.object(verifier.os, "read", side_effect=slow_read):
                    report, _ = verifier.verify(repo2, expected_sha=sha, expected_tree=tree)
                self.assertEqual(report["status"], "RED")
            finally:
                thread.join(timeout=2)
            self.assertFalse(thread.is_alive())
        finally:
            tmp.cleanup()

        print("ASTRA_MATRIX_COMPLETENESS_OK", flush=True)

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
