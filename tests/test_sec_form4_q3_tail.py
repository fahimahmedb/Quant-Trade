from __future__ import annotations
import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'src'))
from scripts import sec_form4_census as census
from quant.dataplane.sec_form4 import SessionCalendar, build_census

ACC='0000000101-26-000001'
def header(period='20260630'):
    return f'''<SEC-HEADER>\n<ACCEPTANCE-DATETIME>20260701120000\nACCESSION NUMBER: {ACC}\nCONFORMED SUBMISSION TYPE: 4\nCONFORMED PERIOD OF REPORT: {period}\nREPORTING-OWNER:\n OWNER DATA:\n  CENTRAL INDEX KEY: 0000000101\nISSUER:\n COMPANY DATA:\n  CENTRAL INDEX KEY: 0000000001\n</SEC-HEADER>'''.encode()
def full(date='2026-06-30'):
    return f'''<SEC-DOCUMENT><ownershipDocument><documentType>4</documentType><periodOfReport>{date}</periodOfReport><issuer><issuerCik>0000000001</issuerCik><issuerName>X</issuerName><issuerTradingSymbol>AAA</issuerTradingSymbol></issuer><reportingOwner><reportingOwnerId><rptOwnerCik>0000000101</rptOwnerCik><rptOwnerName>A</rptOwnerName></reportingOwnerId><reportingOwnerRelationship><isDirector>0</isDirector><isOfficer>1</isOfficer><isTenPercentOwner>0</isTenPercentOwner><isOther>0</isOther></reportingOwnerRelationship></reportingOwner><nonDerivativeTable><nonDerivativeTransaction><securityTitle><value>Common</value></securityTitle><transactionDate><value>{date}</value></transactionDate><transactionCoding><transactionFormType>4</transactionFormType><transactionCode>P</transactionCode></transactionCoding><transactionAmounts><transactionAcquiredDisposedCode><value>A</value></transactionAcquiredDisposedCode></transactionAmounts><ownershipNature><directOrIndirectOwnership><value>D</value></directOrIndirectOwnership></ownershipNature></nonDerivativeTransaction></nonDerivativeTable></ownershipDocument></SEC-DOCUMENT>'''.encode()

class Q3TailTests(unittest.TestCase):
    def test_master_keeps_original_form4_only(self):
        data=("Description\n-----\n0000000101|Owner|4|2026-07-01|edgar/data/101/0000000101-26-000001.txt\n"
              "0000000101|Owner|4/A|2026-07-02|edgar/data/101/0000000101-26-000002.txt\n").encode()
        rows=census._q3_master_rows(data);self.assertEqual(1,len(rows));self.assertEqual(ACC,rows[0]['accession'])
    def test_period_of_report_is_extracted_for_h1_gate(self):
        self.assertEqual('2026-06-30',census._period_from_header(header('20260630')));self.assertEqual('2026-07-01',census._period_from_header(header('20260701')))
    def test_q3_xml_is_cross_checked_against_sgml_and_normalizes(self):
        row={'accession':ACC,'filed_date':'2026-07-01'};sub,owners,txs=census._synthetic_tail_rows(row,header(),full())
        self.assertEqual('0000000001',sub['ISSUERCIK']);self.assertEqual('0000000101',owners[0]['RPTOWNERCIK']);self.assertEqual(('P','A','2026-06-30'),(txs[0]['TRANS_CODE'],txs[0]['TRANS_ACQUIRED_DISP_CD'],txs[0]['TRANS_DATE']))
    def test_q3_tail_uses_same_frozen_transaction_cutoff(self):
        row={'accession':ACC,'filed_date':'2026-07-01'};sub,owners,txs=census._synthetic_tail_rows(row,header(),full());payload=census._zip_tail([sub],owners,txs)
        cal=SessionCalendar(['2026-06-29','2026-06-30','2026-07-01'],'fixture','1');build=build_census([('2026Q3_TAIL',payload)],cal)
        self.assertEqual(1,len(build.observations));self.assertEqual('2026-06-30',build.observations[0].transaction_date)
        sub2,owners2,txs2=census._synthetic_tail_rows({'accession':ACC,'filed_date':'2026-07-02'},header('20260701'),full('2026-07-01'));build2=build_census([('2026Q3_TAIL',census._zip_tail([sub2],owners2,txs2))],cal)
        self.assertFalse(build2.observations);self.assertEqual(1,build2.waterfall['p_acquired_rows_date_out_of_scope'])
    def test_sgml_xml_identity_mismatch_is_fatal(self):
        with self.assertRaises(ValueError):census._synthetic_tail_rows({'accession':ACC,'filed_date':'2026-07-01'},header(),full().replace(b'<issuerCik>0000000001',b'<issuerCik>0000000002'))

if __name__=='__main__':unittest.main()
