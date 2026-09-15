from __future__ import annotations
import csv, io, sys, unittest, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from quant.dataplane.sec_form4 import parse_quarter_zip

def table(header,row):
    out=io.StringIO();w=csv.DictWriter(out,fieldnames=header,delimiter="\t",lineterminator="\n");w.writeheader();w.writerow(row);return out.getvalue()

class OfficialSubmissionSchemaVariantTests(unittest.TestCase):
    def test_form3_holdings_reported_variant_is_accepted(self):
        a="0000000001-26-000001"
        sub={"ACCESSION_NUMBER":a,"FILING_DATE":"01-JUL-2026","DOCUMENT_TYPE":"4","ISSUERCIK":"1","ISSUERTRADINGSYMBOL":"AAA","FORM3_HOLDINGS_REPORTED":"0"}
        own={"ACCESSION_NUMBER":a,"RPTOWNERCIK":"101","RPTOWNERNAME":"Owner","RPTOWNER_RELATIONSHIP":"Officer"}
        tx={"ACCESSION_NUMBER":a,"NONDERIV_TRANS_SK":"1","TRANS_DATE":"30-JUN-2026","TRANS_CODE":"P","TRANS_ACQUIRED_DISP_CD":"A"}
        b=io.BytesIO()
        with zipfile.ZipFile(b,"w") as z:
            z.writestr("SUBMISSION.tsv",table(list(sub),sub));z.writestr("REPORTINGOWNER.tsv",table(list(own),own));z.writestr("NONDERIV_TRANS.tsv",table(list(tx),tx))
        subs,owners,txs=parse_quarter_zip(b.getvalue(),"2026Q2")
        self.assertEqual("0",subs[0]["FORM3_HOLDINGS_REPORTED"]);self.assertEqual(1,len(owners));self.assertEqual(1,len(txs))

if __name__=="__main__":unittest.main()
