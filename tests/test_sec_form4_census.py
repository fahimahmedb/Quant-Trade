from __future__ import annotations

import io
import json
import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.sec_form4 import (  # noqa: E402
    SessionCalendar,
    build_census,
    build_mapping_ledger,
    parse_acceptance_timestamp,
    resolve_event_times,
)


def zip_fixture(submissions, owners, tx):
    def tsv(rows):
        keys = sorted({k for r in rows for k in r})
        out = io.StringIO()
        import csv
        w = csv.DictWriter(out, fieldnames=keys, delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)
        return out.getvalue().encode()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("SUBMISSION.tsv", tsv(submissions))
        z.writestr("REPORTINGOWNER.tsv", tsv(owners))
        z.writestr("NONDERIV_TRANS.tsv", tsv(tx))
    return buf.getvalue()


def submission(acc, issuer="0000000001", symbol="AAA", form="4", filing_date="02-JAN-2024"):
    return {"ACCESSION_NUMBER": acc, "DOCUMENT_TYPE": form, "ISSUERCIK": issuer, "ISSUERTRADINGSYMBOL": symbol, "FILING_DATE": filing_date}


def owner(acc, cik, relationship="Officer"):
    return {"ACCESSION_NUMBER": acc, "RPTOWNERCIK": cik, "RPTOWNER_RELATIONSHIP": relationship, "RPTOWNERNAME": cik}


def tx(acc, sk, d, code="P", ad="A"):
    return {"ACCESSION_NUMBER": acc, "NONDERIV_TRANS_SK": str(sk), "TRANS_DATE": d, "TRANS_CODE": code, "TRANS_ACQUIRED_DISP_CD": ad}


class Form4CensusTests(unittest.TestCase):
    def setUp(self):
        # Weekday-only fixture is sufficient for logic tests; edge-specific holiday dates are explicit below.
        sessions = [
            "2024-01-02","2024-01-03","2024-01-04","2024-01-05","2024-01-08","2024-01-09","2024-01-10","2024-01-11","2024-01-12","2024-01-16","2024-01-17","2024-01-18","2024-01-19","2024-01-22","2024-01-23","2024-01-24","2024-01-25","2024-01-26","2024-01-29","2024-01-30",
        ]
        self.cal = SessionCalendar(sessions, "test:XNYS", "fixture")

    def build(self, subs, owners, txs):
        return build_census([("2024Q1", zip_fixture(subs, owners, txs))], self.cal)

    def test_two_rows_one_insider_cannot_manufacture_cluster(self):
        a = "0000000001-24-000001"
        b = self.build([submission(a)], [owner(a,"0000000101")], [tx(a,1,"02-JAN-2024"),tx(a,2,"02-JAN-2024")])
        self.assertEqual(1, len(b.observations)); self.assertEqual(0, len(b.events))

    def test_cik_not_name_is_identity(self):
        a,b = "0000000001-24-000001","0000000001-24-000002"
        build = self.build([submission(a),submission(b)], [owner(a,"101"),owner(b,"102")], [tx(a,1,"02-JAN-2024"),tx(b,1,"03-JAN-2024")])
        self.assertEqual(1,len(build.events)); self.assertEqual(("0000000101","0000000102"),build.events[0].owner_ciks)

    def test_same_cik_name_variation_stays_one_owner(self):
        a,b = "0000000001-24-000001","0000000001-24-000002"
        owners=[owner(a,"101"),owner(b,"101")]; owners[0]["RPTOWNERNAME"]="Jane A"; owners[1]["RPTOWNERNAME"]="J A"
        build=self.build([submission(a),submission(b)],owners,[tx(a,1,"02-JAN-2024"),tx(b,1,"03-JAN-2024")])
        self.assertEqual(0,len(build.events))

    def test_missing_owner_cik_is_unresolved_not_fuzzy_matched(self):
        a="0000000001-24-000001"; o=owner(a,"101"); o["RPTOWNERCIK"]=""
        build=self.build([submission(a)],[o],[tx(a,1,"02-JAN-2024")])
        self.assertEqual(0,len(build.observations)); self.assertTrue(any("OWNER_ID_UNRESOLVED" in x.reason_codes for x in build.losses))

    def test_joint_filing_ambiguous_excluded(self):
        a="0000000001-24-000001"
        build=self.build([submission(a)],[owner(a,"101"),owner(a,"102")],[tx(a,1,"02-JAN-2024")])
        self.assertEqual(0,len(build.observations)); self.assertTrue(any("JOINT_OWNER_AMBIGUOUS" in x.reason_codes for x in build.losses))

    def test_amendment_cannot_create_event(self):
        a,b="0000000001-24-000001","0000000001-24-000002"
        build=self.build([submission(a),submission(b,form="4/A")],[owner(a,"101"),owner(b,"102")],[tx(a,1,"02-JAN-2024"),tx(b,1,"03-JAN-2024")])
        self.assertEqual(0,len(build.events)); self.assertEqual(1,build.waterfall["form4a_filings"])

    def test_p_acquired_only(self):
        a,b,c="0000000001-24-000001","0000000001-24-000002","0000000001-24-000003"
        build=self.build([submission(a),submission(b),submission(c)],[owner(a,"101"),owner(b,"102"),owner(c,"103")],[tx(a,1,"02-JAN-2024","S","D"),tx(b,1,"03-JAN-2024","P","D"),tx(c,1,"04-JAN-2024","P","A")])
        self.assertEqual(1,len(build.observations)); self.assertEqual("0000000103",build.observations[0].owner_cik)

    def test_ten_sessions_qualifies_eleven_does_not(self):
        a,b="0000000001-24-000001","0000000001-24-000002"
        # Jan 2 -> Jan 17 crosses exactly ten regular sessions under fixture.
        build=self.build([submission(a),submission(b)],[owner(a,"101"),owner(b,"102")],[tx(a,1,"02-JAN-2024"),tx(b,1,"17-JAN-2024")])
        self.assertEqual(1,len(build.events)); self.assertEqual(10,build.events[0].session_distance)
        b2="0000000001-24-000003"
        build2=self.build([submission(a),submission(b2)],[owner(a,"101"),owner(b2,"102")],[tx(a,1,"02-JAN-2024"),tx(b2,1,"18-JAN-2024")])
        self.assertEqual(0,len(build2.events))

    def test_holiday_weekend_calendar_is_deterministic(self):
        self.assertEqual(1,self.cal.distance("2024-01-12","2024-01-16"))  # MLK weekend
        self.assertEqual(0,self.cal.distance("2024-01-13","2024-01-15"))

    def test_crossing_third_insider_and_rearm(self):
        acc=[f"0000000001-24-{i:06d}" for i in range(1,6)]
        dates=["02-JAN-2024","03-JAN-2024","04-JAN-2024","22-JAN-2024","23-JAN-2024"]
        ciks=["101","102","103","101","104"]
        build=self.build([submission(a) for a in acc],[owner(a,c) for a,c in zip(acc,ciks)],[tx(a,1,d) for a,d in zip(acc,dates)])
        self.assertEqual(2,len(build.events))

    def test_event_time_is_second_distinct_owner_public_time(self):
        a,b="0000000001-24-000001","0000000001-24-000002"
        build=self.build([submission(a),submission(b)],[owner(a,"101"),owner(b,"102")],[tx(a,1,"02-JAN-2024"),tx(b,1,"03-JAN-2024")])
        payloads={a:b"<ACCEPTANCE-DATETIME>20240104120000",b:b"<ACCEPTANCE-DATETIME>20240103160000"}
        events,losses,_=resolve_event_times(build,fetcher=lambda url: payloads[a] if a in url else payloads[b])
        self.assertEqual("2024-01-04T12:00:00",events[0].event_time)
        self.assertGreaterEqual(events[0].event_time[:10],events[0].formation_transaction_date)

    def test_same_date_three_owners_one_event_uses_earliest_two_public(self):
        acc=[f"0000000001-24-{i:06d}" for i in range(1,4)]
        build=self.build([submission(a) for a in acc],[owner(a,str(100+i)) for i,a in enumerate(acc,1)],[tx(a,1,"03-JAN-2024") for a in acc])
        self.assertEqual(1,len(build.events)); self.assertEqual(3,len(build.events[0].owner_ciks))
        times={acc[0]:b"<ACCEPTANCE-DATETIME>20240103170000",acc[1]:b"<ACCEPTANCE-DATETIME>20240103160000",acc[2]:b"<ACCEPTANCE-DATETIME>20240103180000"}
        events,_,_=resolve_event_times(build,fetcher=lambda url: next(v for k,v in times.items() if k in url))
        self.assertEqual("2024-01-03T17:00:00",events[0].event_time)

    def test_missing_acceptance_is_explicit_unresolved(self):
        a,b="0000000001-24-000001","0000000001-24-000002"
        build=self.build([submission(a),submission(b)],[owner(a,"101"),owner(b,"102")],[tx(a,1,"02-JAN-2024"),tx(b,1,"03-JAN-2024")])
        events,losses,_=resolve_event_times(build,fetcher=lambda url: (_ for _ in ()).throw(RuntimeError("no header")))
        self.assertEqual("UNRESOLVED",events[0].event_time_status); self.assertTrue(any("ACCEPTANCE_TIMESTAMP_UNRESOLVED" in x.reason_codes for x in losses))

    def test_acceptance_header_parser(self):
        self.assertEqual("2026-06-11T07:01:13",parse_acceptance_timestamp(b"x<ACCEPTANCE-DATETIME>20260611070113\ny"))

    def test_ticker_change_does_not_split_issuer(self):
        a,b="0000000001-24-000001","0000000001-24-000002"
        build=self.build([submission(a,symbol="OLD"),submission(b,symbol="NEW")],[owner(a,"101"),owner(b,"102")],[tx(a,1,"02-JAN-2024"),tx(b,1,"03-JAN-2024")])
        self.assertEqual(1,len(build.events)); mapping=build_mapping_ledger(build,build.events,None)
        self.assertEqual("UNRESOLVED",mapping[0]["mapping_status"]); self.assertIn("CIK_SYMBOL_CONFLICT",mapping[0]["reason_codes"])

    def test_reused_ticker_is_mapping_ambiguity_not_census_merge(self):
        a,b,c,d=[f"0000000001-24-{i:06d}" for i in range(1,5)]
        subs=[submission(a,"1","AAA"),submission(b,"1","AAA"),submission(c,"2","AAA"),submission(d,"2","AAA")]
        owners=[owner(a,"101"),owner(b,"102"),owner(c,"201"),owner(d,"202")]
        txs=[tx(a,1,"02-JAN-2024"),tx(b,1,"03-JAN-2024"),tx(c,1,"02-JAN-2024"),tx(d,1,"03-JAN-2024")]
        build=self.build(subs,owners,txs); self.assertEqual(2,len(build.events))
        mapping=build_mapping_ledger(build,build.events,None); self.assertTrue(all("TICKER_REUSED_OR_AMBIGUOUS" in r["reason_codes"] for r in mapping))

    def test_delisted_unavailable_stays_in_event_population(self):
        a,b="0000000001-24-000001","0000000001-24-000002"
        build=self.build([submission(a),submission(b)],[owner(a,"101"),owner(b,"102")],[tx(a,1,"02-JAN-2024"),tx(b,1,"03-JAN-2024")])
        mapping=build_mapping_ledger(build,build.events,{"AAA":{"status":"NO_HISTORY","covered_event_dates":[]}})
        self.assertEqual(1,len(build.events)); self.assertIn("DELISTED_OR_NO_HISTORY",mapping[0]["reason_codes"])

    def test_deterministic_outputs_ignore_price_coverage(self):
        a,b="0000000001-24-000001","0000000001-24-000002"
        payload=zip_fixture([submission(a),submission(b)],[owner(a,"101"),owner(b,"102")],[tx(a,1,"02-JAN-2024"),tx(b,1,"03-JAN-2024")])
        x=build_census([("2024Q1",payload)],self.cal); y=build_census([("2024Q1",payload)],self.cal)
        self.assertEqual(x.events,y.events)
        m=build_mapping_ledger(x,x.events,{"AAA":{"status":"NO_HISTORY","covered_event_dates":[]}})
        self.assertEqual(x.events,y.events); self.assertEqual(1,len(m))

    def test_source_change_changes_event_lineage(self):
        a,b="0000000001-24-000001","0000000001-24-000002"
        x=self.build([submission(a),submission(b)],[owner(a,"101"),owner(b,"102")],[tx(a,1,"02-JAN-2024"),tx(b,1,"03-JAN-2024")])
        y=self.build([submission(a),submission(b)],[owner(a,"101"),owner(b,"103")],[tx(a,1,"02-JAN-2024"),tx(b,1,"03-JAN-2024")])
        self.assertNotEqual(x.events[0].event_id,y.events[0].event_id)


if __name__ == "__main__":
    unittest.main()
