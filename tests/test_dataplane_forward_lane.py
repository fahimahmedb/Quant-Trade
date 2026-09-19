"""Forward recorder, Form 4 structure extraction, and dataset admissibility.

Every Form 4 document in this file is synthetic. The CIKs and symbols are
invented, the numbers are made up, and nothing here reads the P0 capture
reservoir: the parser under test takes bytes and has no filesystem access at all.
"""

from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from quant.dataplane.admissibility import (ADMISSIBLE, INADMISSIBLE, UNRESOLVED,
                                           USE_EXPLORATORY_FIT, USE_FORWARD_CONFIRMATION,
                                           USE_VALIDATION, EvidenceUse, UseLedger,
                                           evaluate_admissibility)
from quant.dataplane.form4_parse import (PARSE_MALFORMED_XML, PARSE_NOT_FORM_4,
                                         PARSE_NOT_OWNERSHIP_DOCUMENT, PARSE_OK,
                                         PRICE_IN_FOOTNOTE, PRICE_PRESENT,
                                         PUBLIC_OBSERVABILITY_UNAVAILABLE,
                                         parse_form4_document)
from quant.dataplane.forward_recorder import (COVERAGE_COMPLETE, COVERAGE_INCOMPLETE,
                                              COVERAGE_UNKNOWN, RECORD_ACCEPTED,
                                              RECORD_BACKDATED, RECORD_CONFLICT,
                                              RECORD_DUPLICATE, RECORD_INVALID,
                                              SOURCE_TIMESTAMP_ABSENT,
                                              SOURCE_TIMESTAMP_PRESENT,
                                              TIME_AUTHORITY_UNATTESTED_LOCAL_CLOCK,
                                              ForwardObservation, ForwardRecorder)


def joined(problems) -> str:
    return " | ".join(problems)


def observation(symbol: str = "AAA", session: str = "2026-09-18",
                recorded_at: str = "2026-09-18T21:00:00+00:00",
                close: float = 100.0) -> ForwardObservation:
    return ForwardObservation(symbol=symbol, session_date=session,
                              fields={"open": 99.0, "close": close, "volume": 1_000_000.0},
                              source="SYNTHETIC_TEST_SOURCE",
                              source_fingerprint="sha256:" + "0" * 8,
                              recorded_at=recorded_at)


class ForwardRecorderTest(unittest.TestCase):
    def recorder(self, directory: str) -> ForwardRecorder:
        return ForwardRecorder(Path(directory) / "forward.jsonl")

    def test_first_observation_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = self.recorder(directory)
            outcome = recorder.record(observation())
            self.assertEqual(outcome.state, RECORD_ACCEPTED)
            self.assertEqual(len(recorder), 1)

    def test_identical_observation_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = self.recorder(directory)
            recorder.record(observation())
            self.assertEqual(recorder.record(observation()).state, RECORD_DUPLICATE)
            self.assertEqual(len(recorder.accepted()), 1)

    def test_revision_of_a_recorded_value_is_refused_not_applied(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = self.recorder(directory)
            recorder.record(observation(close=100.0))
            outcome = recorder.record(observation(close=101.0,
                                                recorded_at="2026-09-19T21:00:00+00:00"))
            self.assertEqual(outcome.state, RECORD_CONFLICT)
            stored = recorder.accepted()
            self.assertEqual(len(stored), 1)
            self.assertEqual(stored[0]["fields"]["close"], 100.0)
            self.assertEqual(len(recorder.conflicts()), 1)

    def test_backdated_observation_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = self.recorder(directory)
            recorder.record(observation(session="2026-09-18",
                                       recorded_at="2026-09-18T21:00:00+00:00"))
            late = observation(symbol="BBB", session="2026-09-17",
                               recorded_at="2026-09-17T21:00:00+00:00")
            self.assertEqual(recorder.record(late).state, RECORD_BACKDATED)

    def test_observation_without_source_fingerprint_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = self.recorder(directory)
            outcome = recorder.record(replace(observation(), source_fingerprint=""))
            self.assertEqual(outcome.state, RECORD_INVALID)
            self.assertIn("SOURCE_FINGERPRINT_UNDECLARED", outcome.detail)

    def test_as_of_hides_observations_recorded_later(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = self.recorder(directory)
            recorder.record(observation(session="2026-09-18",
                                       recorded_at="2026-09-18T21:00:00+00:00"))
            recorder.record(observation(session="2026-09-21",
                                       recorded_at="2026-09-21T21:00:00+00:00"))
            visible = recorder.as_of("2026-09-19T00:00:00+00:00")
            self.assertEqual([row["session_date"] for row in visible], ["2026-09-18"])

    def test_as_of_filters_by_symbol(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = self.recorder(directory)
            recorder.record(observation(symbol="AAA"))
            recorder.record(observation(symbol="BBB",
                                        recorded_at="2026-09-18T21:00:01+00:00"))
            visible = recorder.as_of("2026-09-19T00:00:00+00:00", symbols=["BBB"])
            self.assertEqual([row["symbol"] for row in visible], ["BBB"])

    def test_session_seal_is_stable_and_absent_for_unknown_sessions(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = self.recorder(directory)
            recorder.record(observation())
            seal = recorder.session_seal("2026-09-18")
            self.assertTrue(seal.startswith("sha256:"))
            self.assertEqual(seal, recorder.session_seal("2026-09-18"))
            self.assertIsNone(recorder.session_seal("2026-09-19"))

    def test_coverage_is_unknown_without_an_independent_calendar(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = self.recorder(directory)
            recorder.record(observation())
            coverage = recorder.coverage()
            self.assertEqual(coverage["state"], COVERAGE_UNKNOWN)
            self.assertIn("completeness cannot be asserted", coverage["reason"])

    def test_coverage_against_a_declared_calendar(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = self.recorder(directory)
            recorder.record(observation(symbol="AAA"))
            complete = recorder.coverage(["2026-09-18"], ["AAA"])
            self.assertEqual(complete["state"], COVERAGE_COMPLETE)
            incomplete = recorder.coverage(["2026-09-18"], ["AAA", "BBB"])
            self.assertEqual(incomplete["state"], COVERAGE_INCOMPLETE)
            self.assertEqual(incomplete["missing_count"], 1)

    def test_state_survives_a_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forward.jsonl"
            ForwardRecorder(path).record(observation())
            reopened = ForwardRecorder(path)
            self.assertEqual(reopened.record(observation()).state, RECORD_DUPLICATE)
            self.assertEqual(reopened.symbols(), ["AAA"])
            self.assertEqual(reopened.sessions(), ["2026-09-18"])

    # -- time authority (mission section 2) --------------------------------

    def test_recorded_at_is_never_presented_as_externally_attested(self):
        provenance = observation().time_provenance()
        self.assertEqual(provenance["system_recorded_at_authority"],
                         TIME_AUTHORITY_UNATTESTED_LOCAL_CLOCK)
        self.assertEqual(provenance["system_recorded_at"], "2026-09-18T21:00:00+00:00")

    def test_time_provenance_names_every_distinct_time_concept(self):
        rich = replace(observation(), market_session="REGULAR",
                       fetch_started_at="2026-09-18T20:59:58+00:00",
                       fetch_completed_at="2026-09-18T20:59:59+00:00",
                       source_timestamp="2026-09-18T20:00:00+00:00",
                       source_timestamp_state=SOURCE_TIMESTAMP_PRESENT)
        provenance = rich.time_provenance()
        self.assertEqual(provenance["source_event_session"], "2026-09-18")
        self.assertEqual(provenance["market_session"], "REGULAR")
        self.assertEqual(provenance["fetch_started_at"], "2026-09-18T20:59:58+00:00")
        self.assertEqual(provenance["fetch_completed_at"], "2026-09-18T20:59:59+00:00")
        self.assertEqual(provenance["source_timestamp"], "2026-09-18T20:00:00+00:00")
        self.assertEqual(provenance["source_timestamp_state"], SOURCE_TIMESTAMP_PRESENT)
        self.assertEqual(rich.violations(), [])

    def test_fetch_completed_before_started_is_a_violation(self):
        broken = replace(observation(), fetch_started_at="2026-09-18T21:00:00+00:00",
                         fetch_completed_at="2026-09-18T20:00:00+00:00")
        self.assertIn("FETCH_COMPLETED_BEFORE_STARTED", broken.violations())

    def test_fetch_completed_without_started_is_a_violation(self):
        broken = replace(observation(), fetch_completed_at="2026-09-18T20:00:00+00:00")
        self.assertIn("FETCH_STARTED_AT_MISSING_WITH_COMPLETED", broken.violations())

    def test_source_timestamp_state_must_match_whether_a_value_is_given(self):
        claims_present_but_empty = replace(observation(),
                                           source_timestamp_state=SOURCE_TIMESTAMP_PRESENT)
        self.assertIn("SOURCE_TIMESTAMP_STATE_PRESENT_BUT_VALUE_MISSING",
                      claims_present_but_empty.violations())
        claims_absent_but_has_value = replace(
            observation(), source_timestamp="2026-09-18T20:00:00+00:00",
            source_timestamp_state=SOURCE_TIMESTAMP_ABSENT)
        self.assertIn("SOURCE_TIMESTAMP_STATE_ABSENT_BUT_VALUE_GIVEN",
                      claims_absent_but_has_value.violations())

    def test_market_session_cannot_be_declared_empty(self):
        broken = replace(observation(), market_session="")
        self.assertIn("MARKET_SESSION_UNDECLARED", broken.violations())

    def test_out_of_order_fetch_delivery_is_tolerated_ledger_order_is_not(self):
        """Fetch start/finish ordering is informational; only recorded_at governs."""
        with tempfile.TemporaryDirectory() as directory:
            recorder = self.recorder(directory)
            first_fetch_started_late = replace(
                observation(symbol="AAA", recorded_at="2026-09-18T21:00:00+00:00"),
                fetch_started_at="2026-09-18T20:59:00+00:00",
                fetch_completed_at="2026-09-18T20:59:59+00:00")
            second_fetch_started_earlier_finished_later = replace(
                observation(symbol="BBB", recorded_at="2026-09-18T21:00:01+00:00"),
                fetch_started_at="2026-09-18T20:58:00+00:00",
                fetch_completed_at="2026-09-18T21:00:00+00:00")
            self.assertTrue(recorder.record(first_fetch_started_late).accepted)
            self.assertTrue(recorder.record(second_fetch_started_earlier_finished_later).accepted)
            self.assertEqual(recorder.symbols(), ["AAA", "BBB"])

    def test_timezone_offsets_are_normalised_for_monotonicity(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = self.recorder(directory)
            recorder.record(observation(symbol="AAA",
                                        recorded_at="2026-09-18T21:00:00+00:00"))
            # 17:00-04:00 is the same instant as 21:00+00:00: not a back-date.
            same_instant_other_offset = observation(
                symbol="BBB", recorded_at="2026-09-18T17:00:00-04:00")
            self.assertTrue(recorder.record(same_instant_other_offset).accepted)
            earlier_in_utc_disguised = observation(
                symbol="CCC", recorded_at="2026-09-18T16:59:59-04:00")
            self.assertEqual(recorder.record(earlier_in_utc_disguised).state,
                             RECORD_BACKDATED)

    # -- adversarial failure model (mission section 8) ----------------------

    def test_torn_final_write_does_not_corrupt_recorder_state(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forward.jsonl"
            recorder = ForwardRecorder(path)
            recorder.record(observation(symbol="AAA"))
            # Simulate a crash mid-append: a second, syntactically incomplete
            # record with no trailing newline, exactly what a kill -9 between
            # write() and flush leaves on some filesystems.
            with path.open("a", encoding="utf-8") as handle:
                handle.write('{"symbol": "BBB", "state": "ACCEPTED", "key":')

            recovered = ForwardRecorder(path)
            self.assertEqual(recovered.symbols(), ["AAA"])
            self.assertEqual(len(recovered), 1)
            # The recorder must repair-on-append (truncate the torn tail) rather
            # than append after it and leave two records sharing one line.
            outcome = recovered.record(observation(symbol="BBB"))
            self.assertTrue(outcome.accepted)
            self.assertEqual(ForwardRecorder(path).symbols(), ["AAA", "BBB"])
            self.assertTrue(path.read_bytes().endswith(b"\n"))

    def test_two_writers_racing_the_same_new_key_cannot_produce_two_truths(self):
        """Two ForwardRecorder instances, neither aware of the other's write yet.

        This is the scenario the mission's failure model names explicitly: two
        writers must not be able to produce an incoherent history. Both accept
        locally (each has an empty in-memory guard for a brand-new key); the
        file ends up with two different ACCEPTED rows for the same key. Every
        reader -- including a third, freshly opened recorder -- must resolve
        that to exactly one authoritative value, and must say so rather than
        silently pick one.
        """
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forward.jsonl"
            writer_one = ForwardRecorder(path)
            writer_two = ForwardRecorder(path)  # opened before writer_one wrote anything

            first = observation(symbol="RACE", close=100.0,
                                recorded_at="2026-09-18T21:00:00+00:00")
            second = observation(symbol="RACE", close=101.0,
                                 recorded_at="2026-09-18T21:00:01+00:00")

            outcome_one = writer_one.record(first)
            outcome_two = writer_two.record(second)
            # Neither writer saw a conflict locally -- both believed they were first.
            self.assertTrue(outcome_one.accepted)
            self.assertTrue(outcome_two.accepted)

            referee = ForwardRecorder(path)
            stored = referee.accepted()
            self.assertEqual(len(stored), 1)
            self.assertEqual(stored[0]["fields"]["close"], 100.0)  # first in append order
            races = referee.race_conflicts()
            self.assertEqual(len(races), 1)
            self.assertEqual(races[0]["fields"]["close"], 101.0)
            self.assertEqual(len(referee), 1)
            # The coverage report must not hide that a race was detected.
            self.assertEqual(referee.coverage()["race_conflicts"], 1)

    def test_two_writers_racing_an_identical_value_is_not_a_race(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forward.jsonl"
            writer_one = ForwardRecorder(path)
            writer_two = ForwardRecorder(path)
            same = observation(symbol="TWIN")
            writer_one.record(same)
            writer_two.record(replace(same))  # same content_address, not a race
            referee = ForwardRecorder(path)
            self.assertEqual(len(referee.accepted()), 1)
            self.assertEqual(referee.race_conflicts(), [])

    def test_vendor_restatement_is_visible_not_silently_applied(self):
        """A vendor that later revises an adjusted close must not rewrite history."""
        with tempfile.TemporaryDirectory() as directory:
            recorder = self.recorder(directory)
            original = observation(symbol="AAA", close=100.0,
                                   recorded_at="2026-09-18T21:00:00+00:00")
            recorder.record(original)
            restated = replace(observation(symbol="AAA", close=100.5,
                                           recorded_at="2026-09-25T21:00:00+00:00"),
                               note="vendor restated adj_close after a dividend")
            outcome = recorder.record(restated)
            self.assertEqual(outcome.state, RECORD_CONFLICT)
            self.assertEqual(recorder.accepted()[0]["fields"]["close"], 100.0)
            self.assertEqual(len(recorder.conflicts()), 1)

    def test_late_correction_of_an_already_sealed_session_is_a_conflict_not_an_edit(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = self.recorder(directory)
            recorder.record(observation(symbol="AAA", close=50.0))
            seal_before = recorder.session_seal("2026-09-18")
            correction = replace(observation(symbol="AAA", close=50.25,
                                             recorded_at="2026-09-19T09:00:00+00:00"),
                                 note="broker corrected a fat-fingered print")
            self.assertEqual(recorder.record(correction).state, RECORD_CONFLICT)
            self.assertEqual(recorder.session_seal("2026-09-18"), seal_before)


SYNTHETIC_FORM4 = b"""<?xml version="1.0"?>
<ownershipDocument>
  <schemaVersion>X0508</schemaVersion>
  <documentType>4</documentType>
  <periodOfReport>2026-09-15</periodOfReport>
  <issuer>
    <issuerCik>0009999991</issuerCik>
    <issuerName>SYNTHETIC TEST CORP</issuerName>
    <issuerTradingSymbol>ZZTEST</issuerTradingSymbol>
  </issuer>
  <reportingOwner>
    <reportingOwnerId>
      <rptOwnerCik>0009999992</rptOwnerCik>
      <rptOwnerName>FICTIONAL, INSIDER</rptOwnerName>
    </reportingOwnerId>
    <reportingOwnerRelationship>
      <isDirector>1</isDirector>
      <isOfficer>1</isOfficer>
      <isTenPercentOwner>0</isTenPercentOwner>
      <isOther>0</isOther>
      <officerTitle>Chief Invented Officer</officerTitle>
    </reportingOwnerRelationship>
  </reportingOwner>
  <nonDerivativeTable>
    <nonDerivativeTransaction>
      <securityTitle><value>Common Stock</value></securityTitle>
      <transactionDate><value>2026-09-15</value></transactionDate>
      <transactionCoding>
        <transactionFormType>4</transactionFormType>
        <transactionCode>P</transactionCode>
        <equitySwapInvolved>0</equitySwapInvolved>
      </transactionCoding>
      <transactionAmounts>
        <transactionShares><value>1000</value></transactionShares>
        <transactionPricePerShare><value>150.25</value></transactionPricePerShare>
        <transactionAcquiredDisposedCode><value>A</value></transactionAcquiredDisposedCode>
      </transactionAmounts>
      <postTransactionAmounts>
        <sharesOwnedFollowingTransaction><value>5000</value></sharesOwnedFollowingTransaction>
      </postTransactionAmounts>
      <ownershipNature>
        <directOrIndirectOwnership><value>D</value></directOrIndirectOwnership>
      </ownershipNature>
    </nonDerivativeTransaction>
    <nonDerivativeTransaction>
      <securityTitle><value>Common Stock</value></securityTitle>
      <transactionDate><value>2026-09-15</value></transactionDate>
      <transactionCoding>
        <transactionFormType>4</transactionFormType>
        <transactionCode>A</transactionCode>
      </transactionCoding>
      <transactionAmounts>
        <transactionShares><value>4000</value></transactionShares>
        <transactionPricePerShare><footnoteId id="F1"/></transactionPricePerShare>
        <transactionAcquiredDisposedCode><value>A</value></transactionAcquiredDisposedCode>
      </transactionAmounts>
    </nonDerivativeTransaction>
  </nonDerivativeTable>
  <derivativeTable>
    <derivativeTransaction>
      <securityTitle><value>Employee Stock Option</value></securityTitle>
      <transactionDate><value>2026-09-15</value></transactionDate>
      <transactionCoding><transactionCode>P</transactionCode></transactionCoding>
      <transactionAmounts>
        <transactionShares><value>2000</value></transactionShares>
        <transactionPricePerShare><value>1.00</value></transactionPricePerShare>
        <transactionAcquiredDisposedCode><value>A</value></transactionAcquiredDisposedCode>
      </transactionAmounts>
    </derivativeTransaction>
  </derivativeTable>
  <footnotes>
    <footnote id="F1">Award granted under the invented 2026 plan.</footnote>
  </footnotes>
</ownershipDocument>
"""

NAMESPACED_FORM4 = b"""<?xml version="1.0"?>
<ns:ownershipDocument xmlns:ns="http://example.invalid/ownership">
  <ns:documentType>4</ns:documentType>
  <ns:periodOfReport>2026-09-15</ns:periodOfReport>
  <ns:issuer><ns:issuerCik>0009999991</ns:issuerCik></ns:issuer>
  <ns:reportingOwner>
    <ns:reportingOwnerId><ns:rptOwnerCik>0009999992</ns:rptOwnerCik></ns:reportingOwnerId>
    <ns:reportingOwnerRelationship><ns:isOfficer>1</ns:isOfficer></ns:reportingOwnerRelationship>
  </ns:reportingOwner>
  <ns:nonDerivativeTable>
    <ns:nonDerivativeTransaction>
      <ns:transactionDate><ns:value>2026-09-15</ns:value></ns:transactionDate>
      <ns:transactionCoding><ns:transactionCode>S</ns:transactionCode></ns:transactionCoding>
      <ns:transactionAmounts>
        <ns:transactionShares><ns:value>500</ns:value></ns:transactionShares>
        <ns:transactionPricePerShare><ns:value>10.5</ns:value></ns:transactionPricePerShare>
        <ns:transactionAcquiredDisposedCode><ns:value>D</ns:value></ns:transactionAcquiredDisposedCode>
      </ns:transactionAmounts>
    </ns:nonDerivativeTransaction>
  </ns:nonDerivativeTable>
</ns:ownershipDocument>
"""


class Form4ParseTest(unittest.TestCase):
    def test_document_parses_into_facts(self):
        facts = parse_form4_document(SYNTHETIC_FORM4)
        self.assertEqual(facts.state, PARSE_OK)
        self.assertEqual(facts.issuer_cik, "0009999991")
        self.assertEqual(facts.issuer_trading_symbol, "ZZTEST")
        self.assertEqual(facts.period_of_report, "2026-09-15")
        self.assertEqual(len(facts.owners), 1)
        self.assertTrue(facts.owners[0].is_officer)
        self.assertFalse(facts.owners[0].is_ten_percent_owner)
        self.assertEqual(len(facts.transactions), 3)

    def test_public_observability_is_never_taken_from_the_document(self):
        facts = parse_form4_document(SYNTHETIC_FORM4)
        self.assertIsNone(facts.public_observability_instant)
        self.assertEqual(facts.public_observability_state, PUBLIC_OBSERVABILITY_UNAVAILABLE)
        # periodOfReport exists but is not promoted into an observability instant.
        self.assertIsNotNone(facts.period_of_report)

    def test_a_grant_is_not_an_open_market_purchase(self):
        facts = parse_form4_document(SYNTHETIC_FORM4)
        purchases = facts.open_market_purchases
        self.assertEqual(len(purchases), 1)
        self.assertEqual(purchases[0].shares, 1000.0)
        grant = facts.transactions[1]
        self.assertEqual(grant.transaction_code, "A")
        self.assertFalse(grant.is_open_market_purchase)

    def test_footnote_only_price_is_a_state_not_zero(self):
        facts = parse_form4_document(SYNTHETIC_FORM4)
        grant = facts.transactions[1]
        self.assertIsNone(grant.price_per_share)
        self.assertEqual(grant.price_state, PRICE_IN_FOOTNOTE)
        self.assertIsNone(grant.notional)
        self.assertIn(PRICE_IN_FOOTNOTE, joined(grant.violations()))

    def test_derivative_transaction_is_not_an_open_market_purchase(self):
        facts = parse_form4_document(SYNTHETIC_FORM4)
        derivative = facts.transactions[2]
        self.assertTrue(derivative.derivative)
        self.assertFalse(derivative.is_open_market_purchase)

    def test_notional_uses_shares_times_price(self):
        purchase = parse_form4_document(SYNTHETIC_FORM4).open_market_purchases[0]
        self.assertAlmostEqual(purchase.notional, 150_250.0, places=6)
        self.assertEqual(purchase.price_state, PRICE_PRESENT)

    def test_namespaced_document_parses(self):
        facts = parse_form4_document(NAMESPACED_FORM4)
        self.assertEqual(facts.state, PARSE_OK)
        self.assertTrue(facts.transactions[0].is_open_market_sale)

    def test_malformed_xml_is_a_state_not_an_exception(self):
        facts = parse_form4_document(b"<ownershipDocument><documentType>4")
        self.assertEqual(facts.state, PARSE_MALFORMED_XML)
        self.assertFalse(facts.parsed)

    def test_wrong_root_element_is_refused(self):
        facts = parse_form4_document(b"<html><body>not a filing</body></html>")
        self.assertEqual(facts.state, PARSE_NOT_OWNERSHIP_DOCUMENT)

    def test_form_3_is_not_accepted_as_form_4(self):
        document = SYNTHETIC_FORM4.replace(b"<documentType>4</documentType>",
                                           b"<documentType>3</documentType>")
        self.assertEqual(parse_form4_document(document).state, PARSE_NOT_FORM_4)

    def test_amendment_is_flagged_as_superseding(self):
        document = SYNTHETIC_FORM4.replace(b"<documentType>4</documentType>",
                                           b"<documentType>4/A</documentType>")
        facts = parse_form4_document(document)
        self.assertEqual(facts.state, PARSE_OK)
        self.assertTrue(facts.is_amendment)
        self.assertIn("AMENDMENT_SUPERSEDES_PRIOR_FILING", joined(facts.violations()))

    def test_missing_relationship_is_a_violation(self):
        document = SYNTHETIC_FORM4.replace(b"<isDirector>1</isDirector>", b"") \
            .replace(b"<isOfficer>1</isOfficer>", b"") \
            .replace(b"<isTenPercentOwner>0</isTenPercentOwner>", b"") \
            .replace(b"<isOther>0</isOther>", b"")
        facts = parse_form4_document(document)
        self.assertIn("REPORTING_OWNER_RELATIONSHIP_UNDECLARED", joined(facts.violations()))


def dataset(**overrides) -> dict:
    document = {"dataset_id": "us_sector_etfs_daily", "availability": "AVAILABLE",
                "fingerprint": "sha256:" + "a" * 8,
                "point_in_time": {"as_of_rule": "SESSION_CLOSE_SAME_DAY"},
                "first_date": "2015-01-02", "last_date": "2026-09-18"}
    document.update(overrides)
    return document


class AdmissibilityTest(unittest.TestCase):
    def use(self, use_class: str, **overrides) -> EvidenceUse:
        fields = dict(dataset_version="us_sector_etfs_daily@sha256:aaaaaaaa",
                      use_class=use_class, decision_instant="2026-09-19T12:00:00+00:00")
        fields.update(overrides)
        return EvidenceUse(**fields)

    def test_exploratory_fit_on_a_traceable_dataset_is_admissible(self):
        verdict = evaluate_admissibility(dataset(), self.use(USE_EXPLORATORY_FIT))
        self.assertEqual(verdict.state, ADMISSIBLE)

    def test_unavailable_dataset_is_inadmissible(self):
        verdict = evaluate_admissibility(dataset(availability="STALE"),
                                         self.use(USE_EXPLORATORY_FIT))
        self.assertEqual(verdict.state, INADMISSIBLE)
        self.assertIn("DATASET_NOT_AVAILABLE:STALE", joined(verdict.reasons))

    def test_undeclared_point_in_time_semantics_is_unresolved(self):
        verdict = evaluate_admissibility(dataset(point_in_time={}),
                                         self.use(USE_EXPLORATORY_FIT))
        self.assertEqual(verdict.state, UNRESOLVED)
        self.assertIn("POINT_IN_TIME_SEMANTICS_UNDECLARED", joined(verdict.reasons))

    def test_validation_on_an_already_fitted_version_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = UseLedger(Path(directory) / "uses.jsonl")
            ledger.record(self.use(USE_EXPLORATORY_FIT))
            verdict = evaluate_admissibility(dataset(), self.use(USE_VALIDATION), ledger)
            self.assertEqual(verdict.state, INADMISSIBLE)
            self.assertIn("VALIDATION_ON_ALREADY_FITTED_DATASET_VERSION",
                          joined(verdict.reasons))

    def test_a_new_fingerprint_is_a_new_version_and_stays_admissible(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = UseLedger(Path(directory) / "uses.jsonl")
            ledger.record(self.use(USE_EXPLORATORY_FIT))
            refreshed = evaluate_admissibility(
                dataset(fingerprint="sha256:" + "b" * 8),
                self.use(USE_VALIDATION,
                         dataset_version="us_sector_etfs_daily@sha256:bbbbbbbb"), ledger)
            self.assertEqual(refreshed.state, ADMISSIBLE)

    def test_historical_data_can_never_be_forward_confirmation(self):
        verdict = evaluate_admissibility(
            dataset(), self.use(USE_FORWARD_CONFIRMATION,
                                protocol_freeze_instant="2026-09-19T00:00:00+00:00"),
            forward_seal="sha256:deadbeef")
        self.assertEqual(verdict.state, INADMISSIBLE)
        self.assertIn("HISTORICAL_EVIDENCE_IS_NOT_INDEPENDENT_CONFIRMATION",
                      joined(verdict.reasons))

    def test_forward_confirmation_needs_a_pre_outcome_seal(self):
        verdict = evaluate_admissibility(
            dataset(recorded_from="2026-09-20"),
            self.use(USE_FORWARD_CONFIRMATION,
                     protocol_freeze_instant="2026-09-19T00:00:00+00:00"))
        self.assertEqual(verdict.state, INADMISSIBLE)
        self.assertIn("FORWARD_CONFIRMATION_REQUIRES_A_PRE_OUTCOME_SEAL",
                      joined(verdict.reasons))

    def test_forward_confirmation_recorded_after_the_freeze_is_admissible(self):
        verdict = evaluate_admissibility(
            dataset(recorded_from="2026-09-20"),
            self.use(USE_FORWARD_CONFIRMATION,
                     protocol_freeze_instant="2026-09-19T00:00:00+00:00"),
            forward_seal="sha256:deadbeef")
        self.assertEqual(verdict.state, ADMISSIBLE)

    def test_forward_confirmation_without_a_freeze_instant_is_unresolved(self):
        verdict = evaluate_admissibility(dataset(), self.use(USE_FORWARD_CONFIRMATION))
        self.assertEqual(verdict.state, UNRESOLVED)
        self.assertIn("FORWARD_CONFIRMATION_REQUIRES_A_PROTOCOL_FREEZE_INSTANT",
                      joined(verdict.reasons))

    def test_use_ledger_is_idempotent_and_survives_a_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "uses.jsonl"
            ledger = UseLedger(path)
            self.assertTrue(ledger.record(self.use(USE_EXPLORATORY_FIT)))
            self.assertFalse(ledger.record(self.use(USE_EXPLORATORY_FIT)))
            reopened = UseLedger(path)
            self.assertIn(USE_EXPLORATORY_FIT,
                          reopened.uses_of("us_sector_etfs_daily@sha256:aaaaaaaa"))
            self.assertEqual(len(reopened), 1)


if __name__ == "__main__":
    unittest.main()
