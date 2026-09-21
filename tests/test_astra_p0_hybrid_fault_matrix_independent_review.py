"""Independent Astra falsifiers for the P0 hybrid Gate-A fault matrix.

Audit-only tests. They do not modify the frozen production candidate.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from quant.dataplane.sec.collector import CollectorState, SecForm4Collector

from tools.p0_qualification.gate_a import fault_matrix as fm


ROOT = Path(__file__).resolve().parents[1]


class AstraFaultMatrixIndependentReview(unittest.TestCase):
    def test_file_fsync_discriminant_turns_red_if_regular_fsync_is_removed(self) -> None:
        """F4/F10: omitting the staging-file fsync must make the discriminant fail."""

        def mutant_link_without_regular_fsync(store, body: bytes, target: Path) -> None:
            target.parent.mkdir(parents=True, exist_ok=True)
            staging = store.paths.sec_staging / "astra-no-fsync.part"
            staging.write_bytes(body)
            os.chmod(staging, 0o444)
            try:
                os.link(staging, target)
            except FileExistsError:
                pass
            finally:
                staging.unlink(missing_ok=True)

        with mock.patch.object(
            fm.SecCaptureStore,
            "_link_into_place",
            mutant_link_without_regular_fsync,
        ):
            passed, detail = fm._file_fsync_discriminant()

        self.assertFalse(
            passed,
            f"file-fsync discriminant stayed green after fsync removal: {detail}",
        )

    def test_state_journal_discriminants_turn_red_if_loader_accepts_divergence(self) -> None:
        """F5/F10: both divergence directions must depend on the real fail-closed loader."""

        def lax_loader(collector: SecForm4Collector) -> CollectorState:
            payload = fm.read_json(collector.paths.sec_collector_state)
            if isinstance(payload, dict):
                return CollectorState(**payload)
            return CollectorState()

        with mock.patch.object(SecForm4Collector, "_load_state", lax_loader):
            state_newer_passed, state_newer_detail = (
                fm._state_journal_divergence_discriminant(journal_newer=False)
            )
            journal_newer_passed, journal_newer_detail = (
                fm._state_journal_divergence_discriminant(journal_newer=True)
            )

        self.assertFalse(
            state_newer_passed,
            f"state-newer discriminant stayed green with mismatch acceptance: "
            f"{state_newer_detail}",
        )
        self.assertFalse(
            journal_newer_passed,
            f"journal-newer discriminant stayed green with mismatch acceptance: "
            f"{journal_newer_detail}",
        )

    def test_codex_restart_burst_discriminant_stays_green_when_frozen_value_drifts(self) -> None:
        """F6/F10 red precondition: Codex check follows the mutable constant instead of pinning 5."""

        real_stage = fm.stage_isolated_root

        def stage_with_wrong_constant(root: Path):
            launcher = real_stage(root)
            launcher.RESTART_BURST_LIMIT = 4
            return launcher

        with mock.patch.object(
            fm,
            "stage_isolated_root",
            side_effect=stage_with_wrong_constant,
        ):
            passed, detail = fm._restart_burst_limit_discriminant()

        self.assertTrue(
            passed,
            "red precondition failed: expected the Codex discriminant to remain "
            f"green under 5->4 drift, detail={detail}",
        )
        self.assertIn("constant=4", detail)

    def test_current_frozen_candidate_restart_burst_fact_is_five(self) -> None:
        """Independent FACT check: the audited production bytes currently pin 5."""

        spec = importlib.util.spec_from_file_location(
            "astra_fault_matrix_launcher_fact",
            ROOT / "deploy" / "quant_sec_supervisor.py",
        )
        launcher = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(launcher)

        self.assertEqual(launcher.RESTART_BURST_LIMIT, 5)
        unit = (ROOT / "deploy" / "quant-sec-capture.service").read_text(
            encoding="utf-8"
        )
        self.assertIn("StartLimitBurst=5", unit)

    def test_fault_matrix_artifact_is_byte_identical_across_two_runs(self) -> None:
        """F8/F9: two same-environment runs must be byte-identical and digest-consistent."""

        original_artifact = fm.ARTIFACT
        try:
            with tempfile.TemporaryDirectory(prefix="astra-fault-matrix-repro-") as directory:
                first = Path(directory) / "first.json"
                second = Path(directory) / "second.json"

                fm.ARTIFACT = first
                first_result = fm.run()
                first_bytes = first.read_bytes()

                fm.ARTIFACT = second
                second_result = fm.run()
                second_bytes = second.read_bytes()
        finally:
            fm.ARTIFACT = original_artifact

        self.assertEqual(first_bytes, second_bytes)
        self.assertEqual(first_result["report_digest"], second_result["report_digest"])

        payload = json.loads(first_bytes)
        reported = payload.pop("report_digest")
        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        expected = "sha256:" + hashlib.sha256(canonical).hexdigest()
        self.assertEqual(reported, expected)

        rows = payload["body"]["rows"]
        self.assertEqual(len(rows), 19)
        self.assertEqual(
            payload["body"]["proof_class_counts"],
            {
                "EXISTING_DISCRIMINATING_PROOF": 15,
                "MISSING_PROOF": 0,
                "NEW_DISCRIMINATING_PROOF": 4,
                "TARGET_HOST_ONLY": 0,
            },
        )
        self.assertEqual(
            payload["body"]["frozen_candidate_sha"],
            "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072",
        )


if __name__ == "__main__":
    unittest.main()
