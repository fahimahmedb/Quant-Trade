from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from research.research_os.github_state import PREFIX, Snapshot, StateUnavailable, json_bytes
from research.research_os.worker_preflight import git_blob_sha
from research.research_os.oracle_worker import ASSERTION
from research.research_os.expansion.edge_observation_reader_v2 import (
    observe_edge_task,
)
from research.research_os.expansion.v2_core import CLOSED_AUTHORITY, build_epoch_manifest, canonical_hash
from research.research_os.expansion.v2_state import POLICY_PATH
from research.research_os.expansion.v2_stage_executor import ACTIVE_EPOCH_PATH
from research.research_os.tests.test_producer_economic_readiness import _candidate_output, _event_detail
from scripts.observe_edge_task_v2 import LocalGitObservationSnapshot


ROOT = Path(__file__).resolve().parents[1]
TASK = "OBSERVE-FIXTURE-001"
TASK_PATH = PREFIX + f"tasks/{TASK}.json"
STAGE = "document_or_fundamental_research"
RESEARCH_PATH = PREFIX + f"artifacts/{TASK}/oracle-worker/{STAGE}.json"
SOURCE_PATH = PREFIX + "sources/observation-fixture.json"


class TrackingSnapshot(Snapshot):
    def read(self, path):
        self.reads.append(path)
        return super().read(path)


class EdgeObservationReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        policy = json.loads((ROOT / POLICY_PATH).read_text())
        epoch = json.loads((ROOT / ACTIVE_EPOCH_PATH).read_text())
        binding = {
            "research_epoch_id": epoch["research_epoch_id"],
            "epoch_manifest_hash": build_epoch_manifest(epoch)["epoch_manifest_hash"],
            "policy_hash": canonical_hash(policy),
        }
        output = _candidate_output("EVENT_DOCUMENT")
        output["candidate"]["generation_id"] = "G1"
        research = {
            "stage": STAGE, "authority": dict(CLOSED_AUTHORITY),
            "outcome_accessed": False, "economic_result": "NOT_OBSERVED",
            "research_contract_version": "v2-core", **{k:binding[k] for k in ("research_epoch_id", "epoch_manifest_hash")},
            "engine_output": output, "candidate": deepcopy(output["candidate"]),
            "dossier": {"dossier": _event_detail()},
            "source_path": SOURCE_PATH, "source_blob": git_blob_sha(json_bytes({"fixture_only": True})),
            "input_head": "b" * 40,
        }
        task = {
            "task_id": TASK, "task_type": "EVENT_DOCUMENT", "research_contract_version": "v2-core",
            "status": "READY", "authority": dict(CLOSED_AUTHORITY), "lease": {"generation": 2},
            "execution": {"v2_epoch_binding": binding, "session_id": TASK + "-g2-fixture",
                          "completed_stages": {STAGE: {"artifact": RESEARCH_PATH, "artifact_hash": canonical_hash(research)}}},
        }
        self.values = {POLICY_PATH: policy, ACTIVE_EPOCH_PATH: epoch, TASK_PATH: task,
                       RESEARCH_PATH: research, SOURCE_PATH: {"fixture_only": True},
                       PREFIX + "evaluation/must-not-be-read.json": {"pnl": 999}}

    def snapshot(self):
        blobs = {}
        for path, value in self.values.items():
            raw = json_bytes(value)
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            blobs[path] = git_blob_sha(raw)
        result = TrackingSnapshot("a" * 40, self.root, blobs)
        result.reads = []
        return result

    def rebind_research(self):
        self.values[TASK_PATH]["execution"]["completed_stages"][STAGE]["artifact_hash"] = canonical_hash(self.values[RESEARCH_PATH])

    def blocked_receipt(self, *, early=False):
        task = self.values[TASK_PATH]
        task["status"] = "BLOCKED"
        task["execution"]["completed_stages"] = {}
        if early:
            self.values[RESEARCH_PATH] = {
                "stage": STAGE, "blocker": "MISSING_QUALIFIED_DOCUMENTARY_SOURCE",
                "authority": dict(CLOSED_AUTHORITY), "outcome_accessed": False,
                "economic_result": "NOT_OBSERVED", "input_head": "b" * 40,
            }
        else:
            self.values[RESEARCH_PATH]["screen"] = {"status": "BLOCK", "block_reasons": ["STRUCTURAL_OVERLAP"]}
            self.values[RESEARCH_PATH].pop("dossier")
        session = task["execution"]["session_id"]
        receipt_path = PREFIX + f"receipts/{TASK}/{session}.json"
        task["execution"]["last_receipt"] = receipt_path
        self.values[receipt_path] = {
            "receipt_id": session, "session_id": session, "task_id": TASK, "lease_generation": 2,
            "input_head": "b" * 40, "artifacts": [RESEARCH_PATH], "status": "BLOCKED",
            "authority_assertion": dict(ASSERTION),
        }
        return receipt_path

    def test_projects_only_bound_producer_evidence_with_exact_read_set(self):
        snapshot = self.snapshot()
        before = deepcopy(self.values)
        with patch("socket.socket", side_effect=AssertionError("network forbidden")), \
             patch("pathlib.Path.write_bytes", side_effect=AssertionError("writes forbidden")), \
             patch("subprocess.run", side_effect=AssertionError("process forbidden")):
            first = observe_edge_task(snapshot, TASK)
        self.assertEqual(self.values, before)
        self.assertEqual(set(snapshot.reads), {POLICY_PATH, ACTIVE_EPOCH_PATH, TASK_PATH, RESEARCH_PATH})
        self.assertEqual(set(first["source_artifacts"]), set(snapshot.reads))
        self.assertEqual(first["source_packet_binding"]["blob"], snapshot.blobs[SOURCE_PATH])
        self.assertEqual(first["snapshot_head"], "a" * 40)
        self.assertEqual(first["acquisition_projection_state"], "PROJECTED_FROM_BOUND_RESEARCH_DOSSIER")
        self.assertEqual(first, observe_edge_task(snapshot, TASK))
        edge = first["edge_projection"]
        self.assertEqual(edge["experiment_readiness"], "INCOMPLETE")
        self.assertEqual(edge["scientific_maturity"], "EVIDENCE_BOUND")
        self.assertTrue(any(r["status"] == "UNRESOLVED_NO_DECLARED_ROUTE" for r in edge["evidence_acquisition"]["intents"]))
        self.assertEqual(edge["evidence_acquisition"]["summary"]["blocked_count"], 0)
        self.assertEqual(edge["evidence_acquisition"]["summary"]["unresolved_count"], 4)
        self.assertFalse(first["network_call_performed"])

    def test_blocked_stage_uses_own_receipt_and_never_invents_dossier(self):
        original = deepcopy(self.values)
        for early in (False, True):
            with self.subTest(early=early):
                self.values = deepcopy(original)
                receipt = self.blocked_receipt(early=early)
                snapshot = self.snapshot()
                result = observe_edge_task(snapshot, TASK)
                self.assertIn(receipt, snapshot.reads)
                self.assertEqual(result["task_status"], "BLOCKED")
                self.assertEqual(result["edge_projection"]["interpretation"], "BLOCKED_NOT_FAILED")
                self.assertEqual(result["acquisition_projection_state"], "NOT_PROJECTED_UPSTREAM_BLOCKED")
                self.assertNotIn("evidence_acquisition", result["edge_projection"])

    def test_unexecuted_task_has_no_manufactured_research_or_readiness(self):
        self.values.pop(RESEARCH_PATH)
        self.values[TASK_PATH]["execution"] = {}
        result = observe_edge_task(self.snapshot(), TASK)
        self.assertEqual(result["task_epoch_binding"], "NOT_BOUND_UNEXECUTED")
        self.assertEqual(result["research_artifact_status"], "ABSENT")
        self.assertFalse(result["edge_projection"]["stages"]["research_attempted"])

    def test_missing_dossier_blocks_but_native_fundamental_can_project_requirements(self):
        self.values[RESEARCH_PATH].pop("dossier")
        self.rebind_research()
        out = observe_edge_task(self.snapshot(), TASK)
        self.assertEqual(out["acquisition_projection_state"], "NOT_PROJECTED_NO_DOSSIER")
        self.values[RESEARCH_PATH]["dossier"] = {"dossier": {
            "issuer_identity": {"status": "SUPPORTED", "values": {"issuer_id": "FIXTURE"}},
        }}
        self.values[TASK_PATH]["task_type"] = "FUNDAMENTAL_RESEARCH"
        self.values[RESEARCH_PATH]["engine_output"]["engine_family"] = "FUNDAMENTAL"
        self.rebind_research()
        out = observe_edge_task(self.snapshot(), TASK)
        self.assertEqual(out["acquisition_projection_state"], "PROJECTED_FROM_BOUND_RESEARCH_DOSSIER")
        acquisition = out["edge_projection"]["evidence_acquisition"]
        self.assertEqual(acquisition["summary"]["unresolved_count"], 5)
        self.assertEqual(acquisition["summary"]["ready_count"], 0)
        self.assertNotEqual(out["edge_projection"]["experiment_readiness"], "READY")
        self.assertEqual(out["edge_projection"]["empirical_correlation"], "UNKNOWN")
        self.assertFalse(out["network_call_performed"])

    def test_traversal_and_cross_task_references_fail_before_artifact_read(self):
        snapshot = self.snapshot()
        for identity in ("../evaluation", "/tmp/secret", "T\nOTHER"):
            with self.subTest(identity=identity), self.assertRaisesRegex(ValueError, "TASK_ID"):
                observe_edge_task(snapshot, identity)
        self.values[TASK_PATH]["execution"]["completed_stages"][STAGE]["artifact"] = PREFIX + "artifacts/OTHER/oracle-worker/" + STAGE + ".json"
        snapshot = self.snapshot()
        with self.assertRaisesRegex(ValueError, "REFERENCE_MISMATCH"):
            observe_edge_task(snapshot, TASK)
        self.assertNotIn(RESEARCH_PATH, snapshot.reads)

    def test_uncommitted_stage_or_bad_content_hash_cannot_be_projected(self):
        self.values[TASK_PATH]["execution"]["completed_stages"] = {}
        with self.assertRaisesRegex(ValueError, "RECEIPT_PATH_MISMATCH"):
            observe_edge_task(self.snapshot(), TASK)
        self.values[TASK_PATH]["execution"]["completed_stages"] = {STAGE: {"artifact": RESEARCH_PATH, "artifact_hash": "forged"}}
        with self.assertRaisesRegex(ValueError, "CONTENT_HASH_MISMATCH"):
            observe_edge_task(self.snapshot(), TASK)

    def test_real_snapshot_rejects_modified_bytes(self):
        snapshot = self.snapshot()
        (self.root / RESEARCH_PATH).write_bytes(b'{}')
        with self.assertRaisesRegex(StateUnavailable, "STATE_BLOB_MISMATCH"):
            observe_edge_task(snapshot, TASK)

    def test_wrong_epoch_or_unsealed_policy_fails_closed(self):
        self.values[TASK_PATH]["execution"]["v2_epoch_binding"]["research_epoch_id"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "TASK_EPOCH_BINDING_MISMATCH"):
            observe_edge_task(self.snapshot(), TASK)
        self.values[POLICY_PATH]["evaluation_membrane"]["status"] = "OPEN"
        with self.assertRaisesRegex(RuntimeError, "MEMBRANE_NOT_SEALED"):
            observe_edge_task(self.snapshot(), TASK)

    def test_stale_receipt_or_open_assertion_is_rejected(self):
        receipt = self.blocked_receipt()
        for mutation in ({"lease_generation": 1}, {"session_id": "OTHER"},
                         {"artifacts": [PREFIX + "evaluation/must-not-be-read.json"]},
                         {"authority_assertion": {"real_capital_used": True}}):
            original = deepcopy(self.values[receipt])
            self.values[receipt].update(mutation)
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, "RECEIPT_BINDING_MISMATCH"):
                observe_edge_task(self.snapshot(), TASK)
            self.values[receipt] = original

    def test_receipt_path_cannot_escape_task(self):
        self.blocked_receipt()
        self.values[TASK_PATH]["execution"]["last_receipt"] = PREFIX + "evaluation/must-not-be-read.json"
        snapshot = self.snapshot()
        with self.assertRaisesRegex(ValueError, "RECEIPT_PATH_MISMATCH"):
            observe_edge_task(snapshot, TASK)
        self.assertNotIn(PREFIX + "evaluation/must-not-be-read.json", snapshot.reads)

    def test_outcome_injection_and_missing_markers_are_rejected(self):
        for mutation in ({"pnl": 1}, {"outcome_accessed": True}, {"economic_result": "POSITIVE"},
                         {"authority": {"real_capital_authorized": True}}):
            before = deepcopy(self.values[RESEARCH_PATH])
            self.values[RESEARCH_PATH].update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                observe_edge_task(self.snapshot(), TASK)
            self.values[RESEARCH_PATH] = before
        self.values[RESEARCH_PATH].pop("outcome_accessed")
        with self.assertRaisesRegex(ValueError, "MARKERS_REQUIRED"):
            observe_edge_task(self.snapshot(), TASK)

    def test_source_candidate_and_lineage_bindings_are_checked(self):
        for mutate, message in (
            (lambda: self.values[SOURCE_PATH].update(changed=True), "SOURCE_BLOB_BINDING_MISMATCH"),
            (lambda: self.values[RESEARCH_PATH]["candidate"].update(hypothesis_id="OTHER"), "CANDIDATE_BINDING_MISMATCH"),
            (lambda: self.values[TASK_PATH].update(lineage={"generation_id": "G999"}), "LINEAGE_GENERATION_MISMATCH"),
        ):
            original = deepcopy(self.values)
            mutate()
            self.rebind_research()
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                observe_edge_task(self.snapshot(), TASK)
            self.values = original

    def test_head_and_task_blob_changes_alter_observation_identity(self):
        snapshot = self.snapshot()
        first = observe_edge_task(snapshot, TASK)
        snapshot.head = "c" * 40
        self.assertNotEqual(first["observation_hash"], observe_edge_task(snapshot, TASK)["observation_hash"])
        self.values[TASK_PATH]["status"] = "COMPLETE"
        second = observe_edge_task(self.snapshot(), TASK)
        self.assertNotEqual(first["observation_hash"], second["observation_hash"])
        snapshot.head = "main"
        with self.assertRaisesRegex(ValueError, "EXACT_SNAPSHOT_HEAD_REQUIRED"):
            observe_edge_task(snapshot, TASK)

    def test_offline_cli_reads_exact_real_git_objects_without_changing_repository(self):
        self.snapshot()
        def git(*args):
            return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.DEVNULL, text=True).strip()
        git("init")
        git("add", ".")
        git("-c", "user.name=Fixture", "-c", "user.email=fixture@localhost", "commit", "-m", "fixture")
        sha = git("rev-parse", "HEAD")
        before = git("status", "--porcelain")
        commands = []
        real_run = subprocess.run
        def trace(command, **kwargs):
            commands.append(command)
            return real_run(command, **kwargs)
        with patch("subprocess.run", side_effect=trace):
            result = observe_edge_task(LocalGitObservationSnapshot(self.root, sha, TASK), TASK)
        self.assertEqual(result["snapshot_head"], sha)
        self.assertTrue(all(command[5] in ("rev-parse", "ls-tree", "cat-file") for command in commands))
        process = subprocess.run([sys.executable, str(ROOT / "scripts/observe_edge_task_v2.py"),
                                  "--repository", str(self.root), "--commit", sha, "--task-id", TASK],
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout), result)
        self.assertEqual(git("status", "--porcelain"), before)
        self.assertEqual(git("rev-parse", "HEAD"), sha)
        with self.assertRaisesRegex(ValueError, "EXACT_LOCAL_COMMIT_REQUIRED"):
            LocalGitObservationSnapshot(self.root, "HEAD", TASK)


if __name__ == "__main__":
    unittest.main()
