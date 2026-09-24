"""Fast-lane PIT event builder: population rules, uniqueness, dates.

All fixtures are SYNTHETIC, built in-test; no market or SEC data is embedded.
"""

import io
import tempfile
import unittest
import zipfile
from array import array
from datetime import date
from pathlib import Path

from quant.fastlane import events as ev
from quant.fastlane.firewall import Firewall
from quant.fastlane.sec_insider import (REQUIRED_COLUMNS, SecParseError, parse_number,
                                        parse_sec_date)

SUB_COLS = list(REQUIRED_COLUMNS["SUBMISSION.tsv"]) + ["REMARKS"]
OWN_COLS = list(REQUIRED_COLUMNS["REPORTINGOWNER.tsv"]) + ["RPTOWNERNAME"]
TR_COLS = list(REQUIRED_COLUMNS["NONDERIV_TRANS.tsv"]) + ["TRANS_SHARES_FN",
                                                          "TRANS_PRICEPERSHARE_FN"]
FN_COLS = list(REQUIRED_COLUMNS["FOOTNOTES.tsv"])


def _tsv(cols, rows):
    lines = ["\t".join(cols)]
    for row in rows:
        lines.append("\t".join(str(row.get(c, "")) for c in cols))
    return ("\n".join(lines) + "\n").encode("utf-8")


def synthetic_zip(submissions, owners, trans, footnotes=()) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("SUBMISSION.tsv", _tsv(SUB_COLS, submissions))
        z.writestr("REPORTINGOWNER.tsv", _tsv(OWN_COLS, owners))
        z.writestr("NONDERIV_TRANS.tsv", _tsv(TR_COLS, trans))
        z.writestr("FOOTNOTES.tsv", _tsv(FN_COLS, [
            {"ACCESSION_NUMBER": a, "FOOTNOTE_ID": f, "FOOTNOTE_TXT": t} for a, f, t in footnotes]))
    return buf.getvalue()


def sub(acc, doc="4", filing="15-FEB-2010", issuer="0000000001", ticker="SYNA", remarks=""):
    return {"ACCESSION_NUMBER": acc, "FILING_DATE": filing, "PERIOD_OF_REPORT": "11-FEB-2010",
            "DATE_OF_ORIG_SUB": "", "DOCUMENT_TYPE": doc, "ISSUERCIK": issuer,
            "ISSUERNAME": "SYNTHETIC ISSUER", "ISSUERTRADINGSYMBOL": ticker, "REMARKS": remarks}


def owner(acc, cik="0000000100", rel="Officer", title="Chief Executive Officer"):
    return {"ACCESSION_NUMBER": acc, "RPTOWNERCIK": cik, "RPTOWNER_RELATIONSHIP": rel,
            "RPTOWNER_TITLE": title, "RPTOWNER_TXT": "", "RPTOWNERNAME": "SYNTHETIC PERSON"}


def trans(acc, sk, code="P", acq="A", shares="1000", price="10.5", tdate="11-FEB-2010",
          title="Common Stock", shares_fn="", price_fn=""):
    return {"ACCESSION_NUMBER": acc, "NONDERIV_TRANS_SK": sk, "SECURITY_TITLE": title,
            "TRANS_DATE": tdate, "DEEMED_EXECUTION_DATE": "", "TRANS_FORM_TYPE": "4",
            "TRANS_CODE": code, "EQUITY_SWAP_INVOLVED": "0", "TRANS_SHARES": shares,
            "TRANS_PRICEPERSHARE": price, "TRANS_ACQUIRED_DISP_CD": acq,
            "SHRS_OWND_FOLWNG_TRANS": "5000", "DIRECT_INDIRECT_OWNERSHIP": "D",
            "TRANS_SHARES_FN": shares_fn, "TRANS_PRICEPERSHARE_FN": price_fn}


A1, A2, A3, A4, A5, A6 = (f"0000000009-10-00000{i}" for i in range(1, 7))


class PopulationRuleTests(unittest.TestCase):
    def build(self, subs, owners, trs, quarter="2010q1", footnotes=()):
        data = synthetic_zip(subs, owners, trs, footnotes)
        counters = ev.BuildCounters()
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            result = ev.build_quarter(z, quarter, counters)
        return result, counters

    def test_only_original_form4_purchase_acquired_rows_create_events(self):
        subs = [sub(A1), sub(A2, doc="4/A"), sub(A3), sub(A4), sub(A5, doc="5"), sub(A6)]
        owners = [owner(a) for a in (A1, A2, A3, A4, A5, A6)]
        trs = [trans(A1, "1"), trans(A2, "2"),                     # 4/A never counts
               trans(A3, "3", code="S", acq="D"),                  # sale
               trans(A4, "4", acq="D"),                            # P but disposed
               trans(A5, "5"),                                     # Form 5
               trans(A6, "6", code="A")]                           # grant code A
        result, counters = self.build(subs, owners, trs)
        self.assertEqual([e["accession"] for e in result.events], [A1])
        self.assertEqual(counters.exclusions["document_type_not_original_form4"], 2)
        self.assertEqual(counters.excluded_by_document_type["4/A"], 1)
        self.assertEqual(counters.excluded_by_document_type["5"], 1)
        self.assertEqual(counters.exclusions["trans_code_not_P"], 2)
        self.assertEqual(counters.exclusions["P_acquired_disposed_not_A"], 1)
        # every row is either in an event or counted under exactly one reason
        self.assertEqual(sum(counters.exclusions.values())
                         + counters.population["transaction_rows_in_events"],
                         counters.population["nonderiv_trans_rows"])

    def test_amendment_does_not_modify_the_original_event(self):
        subs = [sub(A1), sub(A2, doc="4/A")]
        owners = [owner(A1), owner(A2)]
        trs = [trans(A1, "1", shares="100"), trans(A2, "2", shares="999999")]
        result, _ = self.build(subs, owners, trs)
        self.assertEqual(len(result.events), 1)
        self.assertEqual(result.events[0]["shares"], 100.0)

    def test_event_fields_are_point_in_time(self):
        result, _ = self.build([sub(A1, filing="16-FEB-2010")], [owner(A1)],
                               [trans(A1, "1", tdate="10-FEB-2010"),
                                trans(A1, "2", tdate="12-FEB-2010", price="")])
        e = result.events[0]
        self.assertEqual(e["available_after_date"], "2010-02-16")
        self.assertEqual(e["filing_date"], "2010-02-16")
        self.assertEqual(e["filing_lag_days"], 6)
        self.assertEqual(e["entry_rule"], ev.ENTRY_RULE)
        self.assertEqual(e["ticker_as_filed"], "SYNA")
        self.assertFalse(e["ticker_is_pit_security_mapping"])
        self.assertEqual(e["value_usd"], 10500.0)       # unpriced row contributes 0
        self.assertEqual(e["shares"], 2000.0)
        self.assertTrue(e["any_ceo_cfo"])
        self.assertEqual(e["owner_ciks"], ["0000000100"])

    def test_ten_percent_only_owner_is_not_officer_or_director(self):
        result, _ = self.build([sub(A1)], [owner(A1, rel="TenPercentOwner", title="")],
                               [trans(A1, "1")])
        e = result.events[0]
        self.assertFalse(e["any_officer_or_director"])
        self.assertTrue(e["ten_percent_only"])
        self.assertEqual(e["od_owner_ciks"], [])

    def test_backdated_accession_year_is_excluded(self):
        # probe p1b: an accession numbered in 2011 cannot have been filed on 2010-02-15
        late, early = "0000000009-11-000001", "0000000009-09-000002"
        result, counters = self.build([sub(late), sub(early)], [owner(late), owner(early)],
                                      [trans(late, "1"), trans(early, "2")])
        self.assertEqual([e["accession"] for e in result.events], [early])
        self.assertEqual(counters.exclusions["accession_year_after_filing_year"], 1)

    def test_ceo_title_does_not_promote_a_ten_percent_owner(self):
        # probe p4e: role comes from relationship flags; CEO/CFO needs the Officer flag
        result, _ = self.build([sub(A1), sub(A2)],
                               [owner(A1, rel="TenPercentOwner", title="CEO"),
                                owner(A2, rel="Director", title="Chief Financial Officer")],
                               [trans(A1, "1"), trans(A2, "2")])
        by_acc = {e["accession"]: e for e in result.events}
        self.assertFalse(by_acc[A1]["any_officer_or_director"])
        self.assertFalse(by_acc[A1]["any_ceo_cfo"])
        self.assertEqual(by_acc[A1]["primary_role_class"], "TEN_PERCENT_OWNER")
        self.assertFalse(by_acc[A2]["any_ceo_cfo"])
        self.assertEqual(by_acc[A2]["primary_role_class"], "DIRECTOR")

    def test_primary_keeps_only_common_equity_titles(self):
        subs = [sub(A1)]
        trs = [trans(A1, "1", title="Class A Common Stock"),
               trans(A1, "2", title="Series A Preferred Stock"),
               trans(A1, "3", title="Common Units representing LP interests"),
               trans(A1, "4", title="Community Bancorp Common Stock"),
               trans(A1, "5", title="Shares of Beneficial Interest")]
        result, counters = self.build(subs, [owner(A1)], trs)
        self.assertEqual(result.events[0]["n_transactions"], 5)            # unfiltered
        kept = [t["sk"] for t in result.primary_events[0]["transactions"]]
        self.assertEqual(kept, ["1", "4"])
        self.assertEqual(counters.primary_exclusions["security_title_not_common_equity"], 3)

    def test_primary_footnote_and_remarks_exclusions(self):
        # probes p4c/p4d: plan/DRIP/fees, IPO/underwritten, conversion, private placement
        subs = [sub(A1), sub(A2, remarks="Shares acquired through the dividend reinvestment plan")]
        trs = [trans(A1, "1", shares_fn="F1"),
               trans(A1, "2", price_fn="F2"),
               trans(A1, "3", price_fn="F3"),
               trans(A2, "4")]
        notes = [(A1, "F1", "Purchased in the issuer's initial public offering at the offering price."),
                 (A1, "F2", "Weighted average price; open market purchases."),
                 (A1, "F3", "Acquired in a private placement with accredited investors.")]
        result, counters = self.build(subs, [owner(A1), owner(A2)], trs, footnotes=notes)
        self.assertEqual(len(result.events), 2)
        self.assertEqual([e["accession"] for e in result.primary_events], [A1])
        self.assertEqual([t["sk"] for t in result.primary_events[0]["transactions"]], ["2"])
        self.assertEqual(counters.footnote_categories["ipo_underwritten"], 1)
        self.assertEqual(counters.footnote_categories["private_placement"], 1)
        self.assertEqual(counters.footnote_categories["remarks:plan_drip_fees"], 1)
        # every base-event row is kept in primary or counted under one primary reason
        self.assertEqual(sum(counters.primary_exclusions.values())
                         + sum(e["n_transactions"] for e in result.primary_events),
                         counters.population["transaction_rows_in_events"])

    def test_footnote_regexes_are_frozen_categories(self):
        self.assertEqual(sorted(ev.FOOTNOTE_EXCLUSION),
                         ["conversion", "ipo_underwritten", "plan_drip_fees", "private_placement"])
        self.assertEqual(ev.footnote_category(["upon conversion of the Series B notes"]),
                         "conversion")
        self.assertEqual(ev.footnote_category(["in lieu of director fees"]), "plan_drip_fees")
        self.assertIsNone(ev.footnote_category(["open market purchase at $10.02"]))

    def test_missing_owner_rows_are_counted_not_silently_dropped(self):
        result, counters = self.build([sub(A1)], [], [trans(A1, "1")])
        self.assertEqual(result.events, [])
        self.assertEqual(counters.exclusions["no_reporting_owner_rows"], 1)


class DuplicateAccessionTests(unittest.TestCase):
    def test_duplicate_within_a_quarter_is_an_error(self):
        data = synthetic_zip([sub(A1), sub(A1)], [owner(A1)], [trans(A1, "1")])
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            with self.assertRaises(ev.DuplicateAccessionError):
                ev.build_quarter(z, "2010q1", ev.BuildCounters())

    def test_duplicate_across_quarters_is_an_error(self):
        acc = ev.accession_int(A1)
        with self.assertRaises(ev.DuplicateAccessionError) as ctx:
            ev.check_cross_quarter_duplicates({"2010q1": array("Q", [acc, 5]),
                                               "2010q2": array("Q", [7, acc])})
        self.assertIn(A1, str(ctx.exception))
        ok = ev.check_cross_quarter_duplicates({"2010q1": array("Q", [1, 2]),
                                                "2010q2": array("Q", [3])})
        self.assertEqual(ok["duplicates"], 0)

    def test_build_all_fails_loudly_on_cross_quarter_duplicate(self):
        from quant.fastlane import sec_insider as si
        with tempfile.TemporaryDirectory() as tmp:
            fw = Firewall(Path(tmp))
            for quarter, filing in (("2010q1", "15-FEB-2010"), ("2010q2", "15-MAY-2010")):
                data = synthetic_zip([sub(A1, filing=filing)], [owner(A1)], [trans(A1, "1")])
                fw.write_bytes_atomic(si.raw_path(fw, quarter), data)
                fw.write_json_atomic(si.manifest_path(fw, quarter), {
                    "quarter": quarter, "sha256": fw.sha256_file(si.raw_path(fw, quarter))})
            with self.assertRaises(ev.DuplicateAccessionError):
                ev.build_all(fw, ["2010q1", "2010q2"], log=lambda m: None)
            self.assertFalse(ev.events_path(fw).exists())

    def test_exact_duplicates_dropped_first_seen(self):
        # probe p4b: an identical re-filing must not double-count value or create an event
        from quant.fastlane import sec_insider as si
        with tempfile.TemporaryDirectory() as tmp:
            fw = Firewall(Path(tmp))
            data = synthetic_zip([sub(A1, filing="15-FEB-2010"), sub(A2, filing="16-FEB-2010"),
                                  sub(A3, filing="16-FEB-2010")],
                                 [owner(A1), owner(A2), owner(A3, cik="0000000200")],
                                 [trans(A1, "1"), trans(A2, "2"), trans(A3, "3")])
            fw.write_bytes_atomic(si.raw_path(fw, "2010q1"), data)
            fw.write_json_atomic(si.manifest_path(fw, "2010q1"), {
                "quarter": "2010q1", "sha256": fw.sha256_file(si.raw_path(fw, "2010q1"))})
            manifest = ev.build_all(fw, ["2010q1"], log=lambda m: None)
            self.assertEqual(manifest["outputs"]["events_unfiltered"]["rows"], 3)
            table = manifest["outputs"]["primary_table"]
            self.assertEqual(table["rows"], 2)
            rows = list(ev.read_jsonl_gz(fw, fw.repo_root / table["relpath"]))
            self.assertEqual([r["accession"] for r in rows], [A1, A3])
            self.assertEqual(manifest["counts"]["primary_excluded_transaction_rows"]
                             ["exact_duplicate_of_earlier_accession"], 1)
            self.assertTrue(table["relpath"].startswith("research/fastlane/data/"))
            self.assertEqual(fw.sha256_file(fw.repo_root / table["relpath"]), table["sha256"])

    def test_build_all_is_deterministic(self):
        from quant.fastlane import sec_insider as si
        with tempfile.TemporaryDirectory() as tmp:
            fw = Firewall(Path(tmp))
            data = synthetic_zip([sub(A1), sub(A2)], [owner(A1), owner(A2, cik="0000000200")],
                                 [trans(A1, "1"), trans(A2, "2")])
            fw.write_bytes_atomic(si.raw_path(fw, "2010q1"), data)
            fw.write_json_atomic(si.manifest_path(fw, "2010q1"), {
                "quarter": "2010q1", "sha256": fw.sha256_file(si.raw_path(fw, "2010q1"))})
            first = ev.build_all(fw, ["2010q1"], log=lambda m: None)["outputs"]
            second = ev.build_all(fw, ["2010q1"], log=lambda m: None)["outputs"]
            self.assertEqual(first, second)
            self.assertEqual(first["events_unfiltered"]["rows"], 2)
            self.assertEqual(first["primary_table"]["rows"], 2)
            self.assertEqual(first["issuer_days"]["rows"], 1)


class DateAndNumberParsingTests(unittest.TestCase):
    def test_sec_dates(self):
        self.assertEqual(parse_sec_date("31-MAR-2006"), date(2006, 3, 31))
        self.assertEqual(parse_sec_date("05-jan-2010"), date(2010, 1, 5))
        self.assertEqual(parse_sec_date(" 1-DEC-2025 "), date(2025, 12, 1))
        self.assertIsNone(parse_sec_date(""))
        self.assertIsNone(parse_sec_date(None))
        for bad in ("2006-03-31", "31-FOO-2006", "31-FEB-2006", "31/03/2006"):
            with self.assertRaises(SecParseError):
                parse_sec_date(bad)

    def test_numbers(self):
        self.assertEqual(parse_number("1,000.5"), 1000.5)
        self.assertIsNone(parse_number(""))
        for bad in ("abc", "nan", "inf"):
            with self.assertRaises(SecParseError):
                parse_number(bad)

    def test_accession_format(self):
        self.assertEqual(ev.accession_int("0001179110-06-007504"), 117911006007504)
        with self.assertRaises(SecParseError):
            ev.accession_int("0001179110-06-7504")


class OwnerClassificationTests(unittest.TestCase):
    def test_relationship_tokens_and_titles(self):
        o = ev.classify_owner("Director,TenPercentOwner", "", "")
        self.assertTrue(o["officer_or_director"])
        self.assertEqual(o["role_class"], "DIRECTOR")
        o = ev.classify_owner("TenPercentOwnerOther", "", "fund")
        self.assertFalse(o["officer_or_director"])
        self.assertTrue(o["is_ten_percent_owner"] and o["is_other"])
        self.assertEqual(ev.classify_owner("Officer", "EVP & CFO", "")["role_class"], "CEO_CFO")
        self.assertEqual(ev.classify_owner("Director", "CEO", "")["role_class"], "DIRECTOR")
        self.assertFalse(ev.classify_owner("Other", "Chief Executive Officer", "")
                         ["officer_or_director"])
        self.assertEqual(ev.classify_owner("Officer", "President & C.E.O.", "")["role_class"],
                         "CEO_CFO")
        self.assertEqual(ev.classify_owner("Officer", "SVP Operations", "")["role_class"],
                         "OTHER_OFFICER")


if __name__ == "__main__":
    unittest.main()
