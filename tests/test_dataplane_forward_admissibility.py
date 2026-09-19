"""Tests proving the forward ledger composes correctly with Wave 1's
admissibility/UseLedger machinery -- without changing any of its rules.

Section 9 of the mission: "Une version deja utilisee pour fit ne devient
jamais forward confirmation simplement parce qu'on l'a renommee. Forward
confirmation exige preuve que la donnee n'existait pas sous forme consommable
avant la freeze pertinente." These tests exercise exactly that boundary using
real ForwardRecorder timing, not a hand-built fixture dict.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from quant.dataplane.admissibility import ADMISSIBLE, INADMISSIBLE, USE_EXPLORATORY_FIT, UseLedger
from quant.dataplane.forward_admissibility import evaluate_forward_confirmation, forward_dataset_view
from quant.dataplane.forward_recorder import ForwardObservation, ForwardRecorder


def joined(reasons) -> str:
    return " | ".join(reasons)


class ForwardDatasetViewTest(unittest.TestCase):
    def test_empty_ledger_is_not_available(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = ForwardRecorder(Path(directory) / "forward.jsonl")
            view = forward_dataset_view(recorder, "forward_yahoo_daily_chart")
            self.assertEqual(view["availability"], "MISSING")
            self.assertIsNone(view["fingerprint"])
            self.assertIsNone(view["recorded_from"])

    def test_recorded_from_is_the_earliest_write_not_a_session_label(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = ForwardRecorder(Path(directory) / "forward.jsonl")
            # A caller could label session_date far in the past; recorded_from
            # must still reflect this process's own forward-only clock, not
            # that label.
            recorder.record(ForwardObservation(
                symbol="XLK", session_date="2010-01-01", fields={"close": 1.0},
                source="yahoo_daily_chart", source_fingerprint="sha256:aa",
                recorded_at="2026-09-19T21:00:00+00:00"))
            view = forward_dataset_view(recorder, "forward_yahoo_daily_chart")
            self.assertEqual(view["recorded_from"], "2026-09-19T21:00:00+00:00")
            self.assertEqual(view["first_date"], "2010-01-01")  # session label, unrelated
            self.assertEqual(view["availability"], "AVAILABLE")
            self.assertIsNotNone(view["fingerprint"])

    def test_fingerprint_changes_as_the_ledger_grows(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = ForwardRecorder(Path(directory) / "forward.jsonl")
            recorder.record(ForwardObservation(
                symbol="XLK", session_date="2026-09-18", fields={"close": 1.0},
                source="s", source_fingerprint="sha256:aa",
                recorded_at="2026-09-18T21:00:00+00:00"))
            before = forward_dataset_view(recorder, "d")["fingerprint"]
            recorder.record(ForwardObservation(
                symbol="XLK", session_date="2026-09-19", fields={"close": 2.0},
                source="s", source_fingerprint="sha256:bb",
                recorded_at="2026-09-19T21:00:00+00:00"))
            after = forward_dataset_view(recorder, "d")["fingerprint"]
            self.assertNotEqual(before, after)


class ForwardConfirmationCompositionTest(unittest.TestCase):
    def test_data_recorded_after_the_freeze_is_admissible_forward_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = ForwardRecorder(Path(directory) / "forward.jsonl")
            recorder.record(ForwardObservation(
                symbol="XLK", session_date="2026-09-20", fields={"close": 1.0},
                source="yahoo_daily_chart", source_fingerprint="sha256:aa",
                recorded_at="2026-09-20T21:00:00+00:00"))
            verdict = evaluate_forward_confirmation(
                recorder, "forward_yahoo_daily_chart", session_date="2026-09-20",
                protocol_freeze_instant="2026-09-19T00:00:00+00:00",
                decision_instant="2026-09-21T00:00:00+00:00", subject="D07_TEST")
            self.assertEqual(verdict.state, ADMISSIBLE, joined(verdict.reasons))

    def test_data_that_existed_before_the_freeze_can_never_be_forward_confirmation(self):
        """The exact fabrication the mission names: relabelling old evidence."""
        with tempfile.TemporaryDirectory() as directory:
            recorder = ForwardRecorder(Path(directory) / "forward.jsonl")
            recorder.record(ForwardObservation(
                symbol="XLK", session_date="2026-09-10", fields={"close": 1.0},
                source="yahoo_daily_chart", source_fingerprint="sha256:aa",
                recorded_at="2026-09-10T21:00:00+00:00"))
            # The protocol is "frozen" only after this data already existed in
            # consumable form -- exactly the case that must be refused.
            verdict = evaluate_forward_confirmation(
                recorder, "forward_yahoo_daily_chart", session_date="2026-09-10",
                protocol_freeze_instant="2026-09-19T00:00:00+00:00",
                decision_instant="2026-09-21T00:00:00+00:00")
            self.assertEqual(verdict.state, INADMISSIBLE)
            self.assertIn("HISTORICAL_EVIDENCE_IS_NOT_INDEPENDENT_CONFIRMATION",
                          joined(verdict.reasons))

    def test_empty_ledger_cannot_confirm_anything(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = ForwardRecorder(Path(directory) / "forward.jsonl")
            verdict = evaluate_forward_confirmation(
                recorder, "forward_yahoo_daily_chart", session_date="2026-09-20",
                protocol_freeze_instant="2026-09-19T00:00:00+00:00",
                decision_instant="2026-09-21T00:00:00+00:00")
            self.assertEqual(verdict.state, INADMISSIBLE)
            self.assertTrue(any("DATASET_NOT_AVAILABLE" in reason for reason in verdict.reasons))

    def test_a_version_already_used_for_a_fit_cannot_also_be_forward_confirmation(self):
        """Section 9's exact failure mode: a version already spent on a fit
        must never separately pass as forward confirmation merely because its
        *timing* also happens to satisfy the freeze/seal check. This is
        proven through the real UseLedger and the real timing check together,
        not asserted in isolation."""
        with tempfile.TemporaryDirectory() as directory:
            recorder = ForwardRecorder(Path(directory) / "forward.jsonl")
            recorder.record(ForwardObservation(
                symbol="XLK", session_date="2026-09-20", fields={"close": 1.0},
                source="yahoo_daily_chart", source_fingerprint="sha256:aa",
                recorded_at="2026-09-20T21:00:00+00:00"))
            dataset_id = "forward_yahoo_daily_chart"
            view = forward_dataset_view(recorder, dataset_id)
            version = f"{dataset_id}@{view['fingerprint']}"

            ledger = UseLedger(Path(directory) / "uses.jsonl")
            from quant.dataplane.admissibility import EvidenceUse
            ledger.record(EvidenceUse(dataset_version=version, use_class=USE_EXPLORATORY_FIT,
                                      decision_instant="2026-09-20T22:00:00+00:00"))

            # On timing alone (recorded after the freeze, properly sealed) this
            # would pass -- confirmed by the sibling test with no ledger.
            # Passing the *same* ledger that already recorded a fit on this
            # exact version must flip the verdict.
            verdict = evaluate_forward_confirmation(
                recorder, dataset_id, session_date="2026-09-20",
                protocol_freeze_instant="2026-09-19T00:00:00+00:00",
                decision_instant="2026-09-21T00:00:00+00:00", ledger=ledger)
            self.assertEqual(verdict.state, INADMISSIBLE)
            self.assertIn("FORWARD_CONFIRMATION_VERSION_ALREADY_CONSUMED_BY_FIT_OR_VALIDATION",
                          joined(verdict.reasons))
            # The fit itself is still durably on record -- nothing here erases
            # or weakens the underlying UseLedger.
            self.assertIn(USE_EXPLORATORY_FIT, ledger.uses_of(version))

    def test_without_a_ledger_the_same_version_passes_on_timing_alone(self):
        """Contrast case: no ledger supplied means no fit history to check
        against, so only the timing/seal rule applies -- this is what proves
        the guard above is doing real work, not just always refusing."""
        with tempfile.TemporaryDirectory() as directory:
            recorder = ForwardRecorder(Path(directory) / "forward.jsonl")
            recorder.record(ForwardObservation(
                symbol="XLK", session_date="2026-09-20", fields={"close": 1.0},
                source="yahoo_daily_chart", source_fingerprint="sha256:aa",
                recorded_at="2026-09-20T21:00:00+00:00"))
            verdict = evaluate_forward_confirmation(
                recorder, "forward_yahoo_daily_chart", session_date="2026-09-20",
                protocol_freeze_instant="2026-09-19T00:00:00+00:00",
                decision_instant="2026-09-21T00:00:00+00:00", ledger=None)
            self.assertEqual(verdict.state, ADMISSIBLE)


if __name__ == "__main__":
    unittest.main()
