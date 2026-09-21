from __future__ import annotations

import datetime as dt
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


runctl = load_module("quant_gate_b_runctl", ROOT / "scripts" / "quant_gate_b_runctl.py")
verifier = load_module("verify_gate_b_deployed_bytes", ROOT / "scripts" / "verify_gate_b_deployed_bytes.py")


CANDIDATE = "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072"
TREE = "4d15ef6f471213ee6ab56337b555d2906ef9bf16"
INPUT = "sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2"
RUN1 = "gate-b-11111111-1111-4111-8111-111111111111"
RUN2 = "gate-b-22222222-2222-4222-8222-222222222222"
NOW = dt.datetime(2026, 9, 21, 10, 0, 0, tzinfo=dt.timezone.utc)


class AuthorityHarness:
    def __init__(self, case: unittest.TestCase):
        self.case = case
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.checkout = self.root / "checkout"
        self.checkout.mkdir()
        self.state = self.root / "state"
        self.registry_path = self.state / "registry.jsonl"
        self.receipts = self.state / "receipts"
        self.registry = runctl.Registry(self.registry_path, self.checkout)

    def close(self):
        self.tmp.cleanup()

    def set_epoch(self, epoch=1, reference="blue/revocation/1"):
        return self.registry.set_revocation_epoch(epoch=epoch, reference=reference, event_time=NOW)

    def reserve(self, run_id=RUN1, host="host-A"):
        return self.registry.reserve(
            candidate_sha=CANDIDATE,
            git_tree=TREE,
            verified_input_tree_digest=INPUT,
            target_host_opaque_id=host,
            blue_reference="blue/decision",
            operator_identity_reference="operator/ref",
            run_id_factory=lambda: run_id,
            event_time=NOW,
        )

    def activation(
        self,
        reservation,
        *,
        activation_id="activation-1",
        candidate_sha=CANDIDATE,
        git_tree=TREE,
        input_digest=INPUT,
        epoch=1,
        revocation_reference="blue/revocation/1",
        issued=NOW - dt.timedelta(minutes=1),
        not_before=NOW - dt.timedelta(seconds=30),
        expires=NOW + dt.timedelta(minutes=5),
    ):
        obj = {
            "schema": runctl.ACTIVATION_SCHEMA,
            "activation_id": activation_id,
            "run_id": reservation["run_id"],
            "attempt_number": reservation["attempt_number"],
            "reservation_digest": reservation["event_digest"],
            "candidate_sha": candidate_sha,
            "git_tree": git_tree,
            "verified_input_tree_digest": input_digest,
            "target_host_opaque_id": reservation["target_host_opaque_id"],
            "issued_at_utc": runctl.utc_text(issued),
            "not_before_utc": runctl.utc_text(not_before),
            "expires_at_utc": runctl.utc_text(expires),
            "revocation_epoch": epoch,
            "revocation_reference": revocation_reference,
            "gate_b_mutation_authorized": True,
        }
        raw = runctl.canonical_json_bytes(obj)
        return obj, raw, runctl.sha256_digest(raw)

    def seal(self, reservation, **kwargs):
        obj, raw, digest = self.activation(reservation, **kwargs)
        event = self.registry.seal_activation(activation_bytes=raw, activation_digest=digest, event_time=NOW)
        return obj, raw, digest, event

    def consume(self, raw, digest, *, run_id=RUN1, expected_candidate=(CANDIDATE, TREE, INPUT), now=NOW):
        return self.registry.consume_activation(
            activation_bytes=raw,
            activation_digest=digest,
            receipt_dir=self.receipts,
            expected_run_id=run_id,
            expected_candidate=expected_candidate,
            now=now,
        )


class GateBRunAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.h = AuthorityHarness(self)

    def tearDown(self):
        self.h.close()

    def test_registry_must_be_outside_source_checkout(self):
        with self.assertRaises(runctl.AuthorityError):
            runctl.Registry(self.h.checkout / "registry.jsonl", self.h.checkout)

    def test_duplicate_run_reservation_red_and_attempt_monotonic_after_terminal(self):
        self.h.set_epoch()
        r1 = self.h.reserve(RUN1)
        self.h.registry.terminal(run_id=RUN1, status="RUN_BLOCKED_TERMINAL", reason="pre-mutation block", event_time=NOW)
        with self.assertRaisesRegex(runctl.AuthorityError, "duplicate run id"):
            self.h.reserve(RUN1)
        r2 = self.h.reserve(RUN2)
        self.assertEqual(r2["attempt_number"], 2)
        self.assertNotEqual(r1["run_id"], r2["run_id"])

    def test_concurrent_nonterminal_run_red(self):
        self.h.set_epoch()
        self.h.reserve(RUN1)
        with self.assertRaisesRegex(runctl.AuthorityError, "concurrent nonterminal"):
            self.h.reserve(RUN2)

    def test_failed_terminal_is_preserved_and_old_run_cannot_be_reused(self):
        self.h.set_epoch()
        r1 = self.h.reserve(RUN1)
        _, raw, digest, _ = self.h.seal(r1)
        self.h.consume(raw, digest)
        failed = self.h.registry.terminal(
            run_id=RUN1, status="FAILED_TERMINAL", reason="mandatory discriminant failed", event_time=NOW
        )
        self.assertEqual(failed["event_type"], "FAILED_TERMINAL")
        with self.assertRaisesRegex(runctl.AuthorityError, "terminal run|already been consumed"):
            self.h.consume(raw, digest)
        r2 = self.h.reserve(RUN2)
        self.assertEqual(r2["attempt_number"], 2)
        events = runctl.load_registry(self.h.registry_path)
        self.assertIn("FAILED_TERMINAL", [e["event_type"] for e in events if e.get("run_id") == RUN1])

    def test_consume_without_reservation_red(self):
        fake_res = {
            "run_id": RUN1,
            "attempt_number": 1,
            "event_digest": "sha256:" + "a" * 64,
            "target_host_opaque_id": "host-A",
        }
        self.h.set_epoch()
        _, raw, digest = self.h.activation(fake_res)
        with self.assertRaisesRegex(runctl.AuthorityError, "reservation missing"):
            self.h.consume(raw, digest)

    def test_wrong_activation_digest_red(self):
        self.h.set_epoch()
        r = self.h.reserve()
        _, raw, digest, _ = self.h.seal(r)
        wrong = "sha256:" + ("0" if digest[-1] != "0" else "1") + digest.split(":", 1)[1][1:]
        with self.assertRaisesRegex(runctl.AuthorityError, "activation digest mismatch"):
            self.h.consume(raw, wrong)

    def test_wrong_candidate_red_at_consumer(self):
        self.h.set_epoch()
        r = self.h.reserve()
        _, raw, digest, _ = self.h.seal(r)
        wrong_candidate = ("0" * 40, TREE, INPUT)
        with self.assertRaisesRegex(runctl.AuthorityError, "expected candidate"):
            self.h.consume(raw, digest, expected_candidate=wrong_candidate)

    def test_expired_activation_red(self):
        self.h.set_epoch()
        r = self.h.reserve()
        _, raw, digest, _ = self.h.seal(
            r,
            issued=NOW - dt.timedelta(minutes=10),
            not_before=NOW - dt.timedelta(minutes=9),
            expires=NOW - dt.timedelta(seconds=1),
        )
        with self.assertRaisesRegex(runctl.AuthorityError, "stale/expired"):
            self.h.consume(raw, digest)

    def test_revocation_epoch_change_red(self):
        self.h.set_epoch()
        r = self.h.reserve()
        _, raw, digest, _ = self.h.seal(r)
        self.h.registry.set_revocation_epoch(epoch=2, reference="blue/revocation/2", event_time=NOW)
        with self.assertRaisesRegex(runctl.AuthorityError, "stale"):
            self.h.consume(raw, digest)

    def test_explicit_activation_revocation_red(self):
        self.h.set_epoch()
        r = self.h.reserve()
        obj, raw, digest, _ = self.h.seal(r)
        self.h.registry.revoke_activation(activation_id=obj["activation_id"], event_time=NOW)
        with self.assertRaisesRegex(runctl.AuthorityError, "explicitly revoked"):
            self.h.consume(raw, digest)

    def test_second_consume_red_and_receipt_is_hash_addressed(self):
        self.h.set_epoch()
        r = self.h.reserve()
        _, raw, digest, _ = self.h.seal(r)
        consume_event, receipt = self.h.consume(raw, digest)
        receipt_path = Path(receipt["path"])
        self.assertTrue(receipt_path.exists())
        self.assertEqual(runctl.sha256_digest(receipt_path.read_bytes()), receipt["digest"])
        self.assertEqual(consume_event["receipt_digest"], receipt["digest"])
        self.assertEqual(receipt_path.stem, receipt["digest"].split(":", 1)[1])
        with self.assertRaisesRegex(runctl.AuthorityError, "already been consumed"):
            self.h.consume(raw, digest)

    def test_malformed_and_truncated_registry_red(self):
        self.h.state.mkdir(parents=True, exist_ok=True)
        self.h.registry_path.write_bytes(b'{"not":"canonical"')
        with self.assertRaisesRegex(runctl.AuthorityError, "truncated"):
            runctl.load_registry(self.h.registry_path)
        self.h.registry_path.write_bytes(b'not-json\n')
        with self.assertRaisesRegex(runctl.AuthorityError, "malformed"):
            runctl.load_registry(self.h.registry_path)

    def test_digest_chain_tamper_red(self):
        self.h.set_epoch()
        self.h.reserve()
        lines = self.h.registry_path.read_text().splitlines()
        obj = json.loads(lines[-1])
        obj["target_host_opaque_id"] = "host-B"
        lines[-1] = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        self.h.registry_path.write_text("\n".join(lines) + "\n")
        with self.assertRaisesRegex(runctl.AuthorityError, "digest mismatch"):
            runctl.load_registry(self.h.registry_path)

    def test_cross_run_evidence_relabel_red(self):
        self.h.set_epoch()
        r1 = self.h.reserve(RUN1)
        _, raw1, digest1, _ = self.h.seal(r1, activation_id="activation-1")
        self.h.consume(raw1, digest1)
        binding1 = {
            "schema": runctl.EVIDENCE_BINDING_SCHEMA,
            "run_id": RUN1,
            "attempt_number": 1,
            "activation_digest": digest1,
            "reservation_digest": r1["event_digest"],
            "candidate_sha": CANDIDATE,
            "git_tree": TREE,
            "verified_input_tree_digest": INPUT,
            "target_host_opaque_id": "host-A",
            "artifact_type": "diagnostic",
            "artifact_ordinal": 1,
            "artifact_digest": "sha256:" + "a" * 64,
            "created_at_utc": runctl.utc_text(NOW),
        }
        rawb1 = runctl.canonical_json_bytes(binding1)
        self.h.registry.bind_evidence(binding_bytes=rawb1, binding_digest=runctl.sha256_digest(rawb1), event_time=NOW)
        self.h.registry.terminal(run_id=RUN1, status="FAILED_TERMINAL", reason="red evidence", event_time=NOW)

        r2 = self.h.reserve(RUN2)
        _, raw2, digest2, _ = self.h.seal(r2, activation_id="activation-2")
        self.h.consume(raw2, digest2, run_id=RUN2)
        binding2 = dict(binding1)
        binding2.update({
            "run_id": RUN2,
            "attempt_number": 2,
            "activation_digest": digest2,
            "reservation_digest": r2["event_digest"],
        })
        rawb2 = runctl.canonical_json_bytes(binding2)
        with self.assertRaisesRegex(runctl.AuthorityError, "another run"):
            self.h.registry.bind_evidence(binding_bytes=rawb2, binding_digest=runctl.sha256_digest(rawb2), event_time=NOW)


class GateBDeployedByteVerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "release"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "GateB Test")
        self.git("config", "user.email", "gateb@example.invalid")
        (self.repo / "src").mkdir()
        (self.repo / "scripts").mkdir()
        (self.repo / "deploy").mkdir()
        (self.repo / "src" / "main.py").write_text("print('frozen')\n")
        (self.repo / "scripts" / "tool.sh").write_text("#!/bin/sh\necho ok\n")
        (self.repo / "scripts" / "tool.sh").chmod(0o755)
        (self.repo / "deploy" / "unit.service").write_text("[Service]\nExecStart=/bin/true\n")
        (self.repo / "README.md").write_text("frozen\n")
        self.git("add", ".")
        self.git("commit", "-qm", "frozen")
        self.sha = self.git("rev-parse", "HEAD").strip()
        self.tree = self.git("rev-parse", "HEAD^{tree}").strip()

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args, cwd=None):
        proc = subprocess.run(
            ["git", "-C", str(cwd or self.repo), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return proc.stdout

    def verify(self, repo=None):
        return verifier.verify(repo or self.repo, expected_sha=self.sha, expected_tree=self.tree)

    def test_exact_frozen_tree_green(self):
        report, digest = self.verify()
        self.assertEqual(report["status"], "GREEN")
        self.assertTrue(digest.startswith("sha256:"))
        self.assertEqual(report["git_optional_locks"], "0")
        self.assertTrue(report["git_metadata_unchanged"])
        self.assertEqual(report["missing_tracked_paths"], [])
        self.assertEqual(report["tracked_mismatches"], [])

    def test_deployed_byte_mutation_red_even_without_git_status(self):
        (self.repo / "src" / "main.py").write_text("print('mutated')\n")
        report, _ = self.verify()
        self.assertEqual(report["status"], "RED")
        self.assertIn("tracked_byte_or_mode_mismatch", report["reasons"])
        self.assertTrue(any(x["path"] == "src/main.py" for x in report["tracked_mismatches"]))

    def test_missing_tracked_file_red(self):
        (self.repo / "deploy" / "unit.service").unlink()
        report, _ = self.verify()
        self.assertEqual(report["status"], "RED")
        self.assertIn("deploy/unit.service", report["missing_tracked_paths"])

    def test_untracked_execution_critical_path_reported_and_red(self):
        (self.repo / "src" / "shadow.py").write_text("pass\n")
        report, _ = self.verify()
        self.assertEqual(report["status"], "RED")
        self.assertIn("src/shadow.py", report["untracked_execution_critical_paths"])

    def test_foreign_git_alternate_red(self):
        foreign = self.root / "foreign"
        foreign.mkdir()
        subprocess.run(["git", "-C", str(foreign), "init", "-q"], check=True)
        alt = self.repo / ".git" / "objects" / "info" / "alternates"
        alt.parent.mkdir(parents=True, exist_ok=True)
        alt.write_text(str((foreign / ".git" / "objects").resolve()) + "\n")
        with self.assertRaisesRegex(verifier.VerifyError, "alternate"):
            self.verify()

    def test_linked_worktree_dependency_red(self):
        worktree = self.root / "linked"
        self.git("worktree", "add", "--detach", str(worktree), self.sha)
        with self.assertRaisesRegex(verifier.VerifyError, "linked worktree"):
            verifier.verify(worktree, expected_sha=self.sha, expected_tree=self.tree)

    def test_allowed_runtime_prefix_can_be_excluded_explicitly(self):
        (self.repo / "var").mkdir()
        (self.repo / "var" / "runtime.db").write_text("runtime")
        report, _ = verifier.verify(
            self.repo,
            expected_sha=self.sha,
            expected_tree=self.tree,
            allowed_extra_prefixes=("var",),
        )
        self.assertEqual(report["status"], "GREEN")


if __name__ == "__main__":
    unittest.main()
