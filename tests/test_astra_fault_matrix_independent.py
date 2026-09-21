"""Independent Astra review tests for the bounded Gate-A fault matrix.

Audit-only: this file does not alter production code or the frozen candidate.
It attacks citation fidelity, discriminating power, artifact determinism and
repository/target-host boundary claims from the Codex fault-matrix package.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

from quant.dataplane.sec.audit import audit_observation_window
from quant.dataplane.sec.collector import CollectorState, SecForm4Collector
from quant.state import read_json
from tests.test_sec_form4_capture import CollectorTestCase
from tools.p0_qualification.common.evidence import sha256_of, verified_input_tree_digest
from tools.p0_qualification.gate_a import fault_matrix as fm


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "tools/p0_qualification/evidence/gate_a/fault_matrix.json"

REQUIRED_PROPERTIES = {
    "before_after_raw_write",
    "before_after_file_fsync",
    "before_after_hardlink_publication",
    "before_after_directory_fsync",
    "before_after_envelope_append",
    "before_after_attempt_completion",
    "before_after_cursor_advancement",
    "before_after_successor_scheduler_obligation",
    "before_after_cooldown_persistence",
    "supervisor_death",
    "child_death",
    "corrupt_torn_journal_tail",
    "duplicate_replay",
    "state_newer_than_journal",
    "journal_newer_than_state",
    "missing_fingerprint",
    "foreign_fingerprint",
    "missing_deployment_authority",
    "restart_burst_limit",
}

INPUT_PATHS = (
    "tools/p0_qualification/common/evidence.py",
    "tools/p0_qualification/common/launcher_loader.py",
    "tools/p0_qualification/common/synthetic.py",
    "tools/p0_qualification/gate_a/fault_matrix.py",
    "tests/test_astra_pre_t0.py",
    "tests/test_gate_a_v3_red.py",
    "tests/test_p0_adversarial.py",
    "tests/test_p0_deployment_boundaries.py",
    "tests/test_sec_form4_capture.py",
)


class ExistingCitationFidelityTests(CollectorTestCase):
    def test_successor_scheduler_citation_hits_the_named_unexplained_obligation(self):
        c = self.collector(self.fixture_router())
        c.lifecycle.update(
            lifecycle_cause="DEPLOYMENT_RESTART", boot_id="b", supervisor_id="s"
        )
        c.record_service_start()
        c._request(
            "DISCOVERY",
            "/cgi-bin/browse-edgar",
            "https://www.sec.gov/cgi-bin/browse-edgar",
        )
        self.timebase.advance(3600)
        c.state.coverage_state = "COMPLETE"
        c.state.open_gaps = []
        report = audit_observation_window(c)
        self.assertFalse(report["accountable"])
        self.assertIn(
            "UNEXPLAINED_EXPECTED_ACTION",
            report["findings"],
            "the cited test must fail for the missing successor obligation, not merely "
            "because some unrelated audit invariant is already broken",
        )
        self.assertGreater(report["obligations_unexplained"], 0)

    def test_torn_scheduler_journal_reaches_the_real_audit_reader_and_fails_loudly(self):
        c = self.collector(self.fixture_router())
        c.poll()
        self.paths.sec_scheduler.write_bytes(b'{"transition_id":"torn"')
        with self.assertRaises((ValueError, json.JSONDecodeError)):
            audit_observation_window(c)


class NewDiscriminantSensitivityTests(unittest.TestCase):
    def test_all_four_new_discriminants_are_green_on_the_frozen_production_bytes(self):
        file_ok, file_detail = fm._file_fsync_discriminant()
        state_ok, state_detail = fm._state_journal_divergence_discriminant(
            journal_newer=False
        )
        journal_ok, journal_detail = fm._state_journal_divergence_discriminant(
            journal_newer=True
        )
        burst_ok, burst_detail = fm._restart_burst_limit_discriminant()
        self.assertTrue(file_ok, file_detail)
        self.assertTrue(state_ok, state_detail)
        self.assertTrue(journal_ok, journal_detail)
        self.assertTrue(burst_ok, burst_detail)
        self.assertIn("constant=5", burst_detail)

    def test_file_fsync_discriminant_turns_red_if_publication_bypasses_regular_fsync(self):
        def broken_link_into_place(store, body, target):
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)

        with mock.patch.object(
            fm.SecCaptureStore, "_link_into_place", broken_link_into_place
        ):
            passed, detail = fm._file_fsync_discriminant()
        self.assertFalse(passed, detail)

    def test_state_newer_discriminant_turns_red_if_loader_accepts_uncommitted_state(self):
        def unsafe_load_state(collector):
            payload = read_json(collector.paths.sec_collector_state)
            if not isinstance(payload, dict):
                return CollectorState()
            return CollectorState(**payload)

        with mock.patch.object(SecForm4Collector, "_load_state", unsafe_load_state):
            passed, detail = fm._state_journal_divergence_discriminant(
                journal_newer=False
            )
        self.assertFalse(passed, detail)

    def test_journal_newer_discriminant_turns_red_if_loader_ignores_commit_tip(self):
        def unsafe_load_state(collector):
            payload = read_json(collector.paths.sec_collector_state)
            if not isinstance(payload, dict):
                return CollectorState()
            return CollectorState(**payload)

        with mock.patch.object(SecForm4Collector, "_load_state", unsafe_load_state):
            passed, detail = fm._state_journal_divergence_discriminant(
                journal_newer=True
            )
        self.assertFalse(passed, detail)

    def test_restart_burst_discriminant_turns_red_if_loaded_value_is_not_validated(self):
        fake_launcher = SimpleNamespace(
            RESTART_BURST_LIMIT=5,
            subprocess=SimpleNamespace(run=lambda *args, **kwargs: None),
            _effective_systemd_definition=lambda root: "sha256:" + "0" * 64,
        )
        with mock.patch.object(fm, "stage_isolated_root", return_value=fake_launcher):
            passed, detail = fm._restart_burst_limit_discriminant()
        self.assertFalse(passed, detail)


class ArtifactContractTests(unittest.TestCase):
    def artifact(self):
        return json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_required_row_set_and_counts_are_derived_not_just_declared(self):
        artifact = self.artifact()
        rows = artifact["body"]["rows"]
        self.assertEqual(len(rows), 19)
        self.assertEqual({row["property"] for row in rows}, REQUIRED_PROPERTIES)
        self.assertEqual(len({row["property"] for row in rows}), 19)

        derived = {
            proof_class: sum(row["proof_class"] == proof_class for row in rows)
            for proof_class in fm.PROOF_CLASSES
        }
        self.assertEqual(artifact["body"]["proof_class_counts"], derived)
        self.assertEqual(
            derived,
            {
                "EXISTING_DISCRIMINATING_PROOF": 15,
                "NEW_DISCRIMINATING_PROOF": 4,
                "TARGET_HOST_ONLY": 0,
                "MISSING_PROOF": 0,
            },
        )
        self.assertEqual(
            artifact["body"]["non_issues"],
            sum(row["defect_classification"] == "NON_ISSUE" for row in rows),
        )
        self.assertEqual(
            artifact["body"]["real_defects"],
            sum(row["defect_classification"] == "REAL_DEFECT" for row in rows),
        )

    def test_all_existing_test_citations_resolve(self):
        artifact = self.artifact()
        cited = [
            test
            for row in artifact["body"]["rows"]
            for test in row["test_or_harness_function"]
            if test.startswith("tests.")
        ]
        self.assertEqual(len(cited), 18)
        missing = [test for test in cited if not fm._test_exists(test)]
        self.assertEqual(missing, [])

    def test_report_digest_and_input_tree_digest_are_self_consistent(self):
        artifact = self.artifact()
        payload_without_digest = {
            key: value for key, value in artifact.items() if key != "report_digest"
        }
        self.assertEqual(artifact["report_digest"], sha256_of(payload_without_digest))
        self.assertEqual(
            artifact["body"]["harness_input_tree_digest"],
            verified_input_tree_digest(INPUT_PATHS),
        )
        self.assertEqual(
            artifact["body"]["frozen_candidate_sha"],
            "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072",
        )
        self.assertFalse(artifact["body"]["production_code_changed"])
        self.assertEqual(artifact["body"]["target_host_ready"], "NOT_CLAIMED_BY_BUILDER")
        self.assertEqual(artifact["body"]["t0"], "NOT_DECLARED")
        self.assertTrue(artifact["no_target_host_claimed"])
        self.assertTrue(artifact["no_t0_declared"])
        self.assertTrue(artifact["no_p14d_amendment_claimed"])

    def test_harness_is_byte_reproducible_across_two_same_environment_runs(self):
        original = ARTIFACT.read_bytes()
        try:
            first = fm.run()
            first_bytes = ARTIFACT.read_bytes()
            first_file_digest = hashlib.sha256(first_bytes).hexdigest()
            second = fm.run()
            second_bytes = ARTIFACT.read_bytes()
            second_file_digest = hashlib.sha256(second_bytes).hexdigest()
        finally:
            ARTIFACT.write_bytes(original)

        self.assertEqual(first_bytes, second_bytes)
        self.assertEqual(first_file_digest, second_file_digest)
        self.assertEqual(first["report_digest"], second["report_digest"])
        self.assertEqual(
            first["body"]["frozen_candidate_sha"],
            "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072",
        )


if __name__ == "__main__":
    unittest.main()
