from __future__ import annotations
import csv, io, json, os, tempfile, unittest, urllib.error, zipfile
from pathlib import Path
from unittest import mock
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT))
from quant.dataplane.sec_form4 import (CensusBuild, Form4Event, RateLimiter, SecTableSchemaError, SessionCalendar,
    _http_get,_sha256_bytes,build_census,build_mapping_ledger,parse_acceptance_timestamp,parse_edgar_header,
    resolve_event_times,validate_acceptance_cache,validate_edgar_header,load_acceptance_checkpoint)

def tsv(rows):
    keys=sorted({k for r in rows for k in r});out=io.StringIO();w=csv.DictWriter(out,fieldnames=keys,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return out.getvalue().encode()
def fixture(subs,owners,txs):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z:z.writestr('SUBMISSION.tsv',tsv(subs));z.writestr('REPORTINGOWNER.tsv',tsv(owners));z.writestr('NONDERIV_TRANS.tsv',tsv(txs))
    return b.getvalue()
def submission(a,issuer='1',symbol='AAA',form='4',filing='02-JAN-2024'):
    return {'ACCESSION_NUMBER':a,'FILING_DATE':filing,'DOCUMENT_TYPE':form,'ISSUERCIK':issuer,'ISSUERTRADINGSYMBOL':symbol}
def owner(a,cik='101',rel='Officer',name=None):return {'ACCESSION_NUMBER':a,'RPTOWNERCIK':cik,'RPTOWNERNAME':name or cik,'RPTOWNER_RELATIONSHIP':rel}
def tx(a,sk,d='02-JAN-2024',code='P',ad='A'):return {'ACCESSION_NUMBER':a,'NONDERIV_TRANS_SK':str(sk),'TRANS_DATE':d,'TRANS_CODE':code,'TRANS_ACQUIRED_DISP_CD':ad}
def sgml(a,issuer='1',owners=('101',),stamp='20240103120000',form='4',period='20240102'):
    ors='\n'.join(f'REPORTING-OWNER:\n OWNER DATA:\n  CENTRAL INDEX KEY: {int(c):010d}\n FILING VALUES:\n  FORM TYPE: {form}' for c in owners)
    return f'<SEC-HEADER>\n<ACCEPTANCE-DATETIME>{stamp}\nACCESSION NUMBER: {a}\nCONFORMED SUBMISSION TYPE: {form}\nCONFORMED PERIOD OF REPORT: {period}\n{ors}\nISSUER:\n COMPANY DATA:\n  CENTRAL INDEX KEY: {int(issuer):010d}\n</SEC-HEADER>'.encode()
SESS=['2023-12-29','2024-01-02','2024-01-03','2024-01-04','2024-01-05','2024-01-08','2024-01-09','2024-01-10','2024-01-11','2024-01-12','2024-01-16','2024-01-17','2024-01-18','2024-01-19','2024-01-22','2024-01-23']
CAL=SessionCalendar(SESS,'fixture:XNYS','1')
class Form4CensusTests(unittest.TestCase):
 def build(self,s,o,t):return build_census([('2024Q1',fixture(s,o,t))],CAL)
 def test_p_acquired_only(self):
  a='0000000001-24-000001';b=self.build([submission(a)],[owner(a)],[tx(a,1),tx(a,2,code='S'),tx(a,3,ad='D')]);self.assertEqual(1,len(b.observations))
 def test_amendment_cannot_create_event(self):
  a,b='0000000001-24-000001','0000000001-24-000002';build=self.build([submission(a),submission(b,form='4/A')],[owner(a,'101'),owner(b,'102')],[tx(a,1),tx(b,1,'03-JAN-2024')]);self.assertFalse(build.events);self.assertEqual(1,build.waterfall['form4a_filings'])
 def test_two_rows_one_insider_cannot_manufacture_cluster(self):
  a='0000000001-24-000001';build=self.build([submission(a)],[owner(a,'101')],[tx(a,1),tx(a,2,'03-JAN-2024')]);self.assertFalse(build.events)
 def test_cik_not_name_is_identity(self):
  a,b='0000000001-24-000001','0000000001-24-000002';build=self.build([submission(a),submission(b)],[owner(a,'101',name='Same'),owner(b,'102',name='Same')],[tx(a,1),tx(b,1,'03-JAN-2024')]);self.assertEqual(1,len(build.events))
 def test_same_cik_name_variation_stays_one_owner(self):
  a,b='0000000001-24-000001','0000000001-24-000002';build=self.build([submission(a),submission(b)],[owner(a,'101',name='A'),owner(b,'101',name='B')],[tx(a,1),tx(b,1,'03-JAN-2024')]);self.assertFalse(build.events)
 def test_missing_owner_cik_unresolved_not_fuzzy(self):
  a='0000000001-24-000001';build=self.build([submission(a)],[owner(a,'',name='Known')],[tx(a,1)]);self.assertFalse(build.observations);self.assertEqual(1,build.waterfall['owner_id_unresolved_rows'])
 def test_valid_owner_plus_missing_owner_cik_is_unresolved(self):
  a='0000000001-24-000001';build=self.build([submission(a)],[owner(a,'101'),owner(a,'')],[tx(a,1)]);self.assertFalse(build.observations);self.assertEqual(1,build.normalized_candidates[0].unresolved_owner_cik_rows)
 def test_joint_filing_ambiguous_excluded(self):
  a='0000000001-24-000001';build=self.build([submission(a)],[owner(a,'101'),owner(a,'102')],[tx(a,1)]);self.assertFalse(build.observations);self.assertEqual(1,build.waterfall['joint_owner_ambiguous_rows'])
 def test_ten_sessions_qualifies_eleven_does_not(self):
  a,b,c,d=[f'0000000001-24-{i:06d}' for i in range(1,5)]
  x=self.build([submission(a),submission(b)],[owner(a,'101'),owner(b,'102')],[tx(a,1,'02-JAN-2024'),tx(b,1,'16-JAN-2024')]);self.assertEqual(1,len(x.events));self.assertEqual(9,x.events[0].session_distance)
  y=self.build([submission(c),submission(d)],[owner(c,'103'),owner(d,'104')],[tx(c,1,'02-JAN-2024'),tx(d,1,'17-JAN-2024')]);self.assertEqual(1,len(y.events));self.assertEqual(10,y.events[0].session_distance)
  e,f='0000000001-24-000005','0000000001-24-000006';z=self.build([submission(e),submission(f)],[owner(e,'105'),owner(f,'106')],[tx(e,1,'02-JAN-2024'),tx(f,1,'18-JAN-2024')]);self.assertFalse(z.events)
 def test_crossing_third_and_rearm(self):
  acc=[f'0000000001-24-{i:06d}' for i in range(1,6)]
  build=self.build([submission(x) for x in acc],[owner(acc[0],'101'),owner(acc[1],'102'),owner(acc[2],'103'),owner(acc[3],'104'),owner(acc[4],'105')],[tx(acc[0],1,'02-JAN-2024'),tx(acc[1],1,'03-JAN-2024'),tx(acc[2],1,'04-JAN-2024'),tx(acc[3],1,'22-JAN-2024'),tx(acc[4],1,'23-JAN-2024')])
  self.assertEqual(2,len(build.events))
 def test_duplicate_exact_collapses(self):
  a='0000000001-24-000001';build=self.build([submission(a)],[owner(a),owner(a)],[tx(a,1),tx(a,1)]);self.assertEqual(1,len(build.observations));self.assertEqual(1,build.waterfall['duplicate_reporting_owner_row']);self.assertEqual(1,build.waterfall['duplicate_transaction_row'])
 def test_owner_conflict_order_independent_and_excluded(self):
  a='0000000001-24-000001';o1=owner(a,'101','Officer');o2=owner(a,'101','TENPERCENTOWNER');x=self.build([submission(a)],[o1,o2],[tx(a,1)]);y=self.build([submission(a)],[o2,o1],[tx(a,1)]);self.assertFalse(x.observations);self.assertEqual(x.losses,y.losses);self.assertEqual(1,x.waterfall['duplicate_reporting_owner_row_conflict'])
 def test_transaction_conflict_order_independent_and_excluded(self):
  a='0000000001-24-000001';t1=tx(a,1,'02-JAN-2024');t2=tx(a,1,'03-JAN-2024');x=self.build([submission(a)],[owner(a)],[t1,t2]);y=self.build([submission(a)],[owner(a)],[t2,t1]);self.assertFalse(x.observations);self.assertEqual(x.losses,y.losses)
 def test_submission_conflict_poisoned(self):
  a='0000000001-24-000001';s1=submission(a,issuer='1');s2=submission(a,issuer='2');b=self.build([s1,s2],[owner(a)],[tx(a,1)]);self.assertFalse(b.observations);self.assertTrue(any('DUPLICATE_ACCESSION_CONFLICT' in x.reason_codes for x in b.losses))
 def test_strict_schema_rejects_unknown_column(self):
  a='0000000001-24-000001';s=submission(a);s['SURPRISE']='x'
  with self.assertRaises(SecTableSchemaError):self.build([s],[owner(a)],[tx(a,1)])
 def test_raw_rows_reconcile_exhaustively(self):
  a='0000000001-24-000001';b=self.build([submission(a),submission(a)],[owner(a),owner(a)],[tx(a,1),tx(a,1)])
  for audit in b.diagnostics['raw_row_reconciliation'].values():self.assertEqual(audit['raw_rows'],audit['unkeyed_rows']+audit['unique_primary_keys']+audit['duplicate_rows'])
 def test_ticker_change_does_not_split_issuer(self):
  a,b='0000000001-24-000001','0000000001-24-000002';build=self.build([submission(a,symbol='AAA'),submission(b,symbol='BBB')],[owner(a,'101'),owner(b,'102')],[tx(a,1),tx(b,1,'03-JAN-2024')]);self.assertEqual(1,len(build.events));self.assertIn('TICKER_CHANGED',build_mapping_ledger(build,build.events)[0]['reason_codes'])
 def test_reused_ticker_is_mapping_ambiguity_not_census_merge(self):
  a,b,c,d=[f'000000000{i}-24-000001' for i in range(1,5)];build=self.build([submission(a,'1','AAA'),submission(b,'1','AAA'),submission(c,'2','AAA'),submission(d,'2','AAA')],[owner(a,'101'),owner(b,'102'),owner(c,'201'),owner(d,'202')],[tx(a,1),tx(b,1,'03-JAN-2024'),tx(c,1),tx(d,1,'03-JAN-2024')]);self.assertEqual(2,len(build.events));self.assertTrue(all('TICKER_REUSED_OR_AMBIGUOUS' in r['reason_codes'] for r in build_mapping_ledger(build,build.events)))
 def test_delisted_unavailable_stays_population(self):
  a,b='0000000001-24-000001','0000000001-24-000002';build=self.build([submission(a),submission(b)],[owner(a,'101'),owner(b,'102')],[tx(a,1),tx(b,1,'03-JAN-2024')]);m=build_mapping_ledger(build,build.events,{'AAA':{'status':'NO_HISTORY','covered_event_dates':[]}});self.assertEqual(1,len(build.events));self.assertIn('DELISTED_OR_NO_HISTORY',m[0]['reason_codes'])
 def test_acceptance_parser_legacy_and_sgml_validation(self):
  a='0000000001-24-000001';self.assertEqual('2024-01-03T12:00:00',parse_acceptance_timestamp(b'<ACCEPTANCE-DATETIME>20240103120000'));meta=validate_edgar_header(sgml(a),a,'1',['101']);self.assertEqual(a,meta.accession)
  with self.assertRaises(ValueError):validate_edgar_header(sgml(a),a,'2',['101'])
 def test_event_time_second_distinct_owner_public_time(self):
  a,b='0000000001-24-000001','0000000001-24-000002';build=self.build([submission(a),submission(b)],[owner(a,'101'),owner(b,'102')],[tx(a,1),tx(b,1,'03-JAN-2024')]);payload={a:sgml(a,'1',['101'],'20240104120000'),b:sgml(b,'1',['102'],'20240103160000')};events,_,_=resolve_event_times(build,fetcher=lambda u:next(v for k,v in payload.items() if k in u),rate_per_second=1000);self.assertEqual('2024-01-04T12:00:00',events[0].event_time)
 def test_unknown_relevant_owner_acceptance_blocks_event_time(self):
  a,b,c='0000000001-24-000001','0000000001-24-000002','0000000001-24-000003';build=self.build([submission(a),submission(b),submission(c)],[owner(a,'101'),owner(b,'101'),owner(c,'102')],[tx(a,1),tx(b,1),tx(c,1,'03-JAN-2024')]);payload={a:sgml(a,'1',['101']),c:sgml(c,'1',['102'],'20240103130000')}
  def fetch(u):
   for k,v in payload.items():
    if k in u:return v
   raise RuntimeError('unresolved')
  events,_,_=resolve_event_times(build,fetcher=fetch,rate_per_second=1000);self.assertEqual('UNRESOLVED',events[0].event_time_status);self.assertIsNone(events[0].event_time)
 def test_checkpoint_metadata_recomputed_from_raw(self):
  a='0000000001-24-000001'
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);cache=p/'cache';cache.mkdir();raw=sgml(a);(cache/f'{a}.html').write_bytes(raw);cp=p/'cp';cp.write_text(json.dumps({'accession':a,'url':'u','sha256':'forged','bytes':1,'acceptance_time':'2099-01-01T00:00:00'})+'\n')
   good,stale=validate_acceptance_cache(load_acceptance_checkpoint(cp),cache,{a:{'issuer_cik':'1','owner_ciks':['101'],'form_type':'4'}});self.assertFalse(stale);self.assertEqual('2024-01-03T12:00:00',good[a]['acceptance_time']);self.assertEqual(_sha256_bytes(raw),good[a]['sha256'])
 def test_torn_tail_resume_append_reload(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'cp';p.write_text(json.dumps({'accession':'A'})+'\n{"accession":"B"');self.assertEqual(['A'],list(load_acceptance_checkpoint(p)));
   with p.open('a') as h:h.write(json.dumps({'accession':'C'})+'\n')
   self.assertEqual({'A','C'},set(load_acceptance_checkpoint(p)))
 def test_http_retry_each_consumes_global_budget(self):
  class L:
   def __init__(self):self.n=0
   def acquire(self):self.n+=1
  class R:
   def read(self):return b'ok'
   def __enter__(self):return self
   def __exit__(self,*a):return False
  calls={'n':0};lim=L()
  def urlopen(req,timeout=None):calls['n']+=1;return R() if calls['n']==3 else (_ for _ in ()).throw(urllib.error.URLError('x'))
  with mock.patch.dict(os.environ,{'SEC_USER_AGENT':'Quant test@example.com'}),mock.patch('urllib.request.urlopen',urlopen),mock.patch('time.sleep',lambda _:None):self.assertEqual(b'ok',_http_get('https://www.sec.gov/x',limiter=lim))
  self.assertEqual(3,lim.n)

if __name__=='__main__':unittest.main()
