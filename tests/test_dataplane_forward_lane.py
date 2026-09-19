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
