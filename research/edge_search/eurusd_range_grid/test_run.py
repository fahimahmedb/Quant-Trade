"""Synthetic ZIPs and temporary result files only; no requests or market files."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from engine import (Engine,Indicators,Bar,BarBuilder,BAR_MS,START,END,at,
                    Quote,CENTRAL,STRESS)
from run import (ArchiveReader,SourceError,atomic_json,begin_attempt,verify_claim,
                 REF,failure_result,digest,validate_result,verify_freeze,HERE)
from test_engine import book


def make_zip(root,month,rows,member=None):
    name='HISTDATA_COM_ASCII_EURUSD_T_'+month+'.zip'
    with zipfile.ZipFile(Path(root)/name,'w') as z:
        z.writestr(member or 'DAT_ASCII_EURUSD_T_'+month+'.csv',rows)
    return {'source_local_month':month[:4]+'-'+month[4:],
            'expected_archive_name':name}


class ReaderTests(unittest.TestCase):
    def test_equal_time_duplicate_rows_group_once_with_adverse_envelope(self):
        rows='20250131 190000123,1.10,1.1001,0\n'*2
        rows+='20250131 190000123,1.09,1.0901,0\n20250131 190001123,1.1,1.1001,0\n'
        with tempfile.TemporaryDirectory() as root:
            reader=ArchiveReader(root,[make_zip(root,'202501',rows)])
            groups=list(reader.groups())
        self.assertEqual(len(groups),2)
        self.assertEqual((groups[0].bid,groups[0].ask),(1.09,1.1001))
        self.assertEqual(groups[0].time_ms,START+123)
        self.assertEqual(reader.qa['duplicates'],1)
        self.assertEqual(reader.qa['multirow_groups'],1)

    def test_source_local_january_utc_outcome_prefix_is_retained(self):
        with tempfile.TemporaryDirectory() as root:
            job=make_zip(root,'202501','20250131 190000000,1,1.0001,0\n')
            q=list(ArchiveReader(root,[job]).groups())[0]
        self.assertEqual(q.time_ms,START)

    def test_after_outcome_utc_prices_not_parsed_and_cannot_close(self):
        with tempfile.TemporaryDirectory() as root:
            job=make_zip(root,'202609','20260930 185959999,1,1.0001,0\n20260930 190000000,not_a_price,invalid,0\n')
            reader=ArchiveReader(root,[job]);qs=list(reader.groups())
        self.assertEqual(len(qs),1);self.assertEqual(qs[0].time_ms,END-1)
        self.assertEqual(reader.qa['outside_utc_rows_not_price_parsed'],1)

    def test_nonmonotone_source_never_sorted(self):
        with tempfile.TemporaryDirectory() as root:
            job=make_zip(root,'202501','20250102 000001000,1,1.0001,0\n20250102 000000000,1,1.0001,0\n')
            with self.assertRaisesRegex(SourceError,'nonmonotone'):
                list(ArchiveReader(root,[job]).groups())

    def test_wrong_month_asset_columns_and_invalid_quotes_fail_closed(self):
        for row,member in [('20250202 000000000,1,1.0001,0\n',None),
            ('20250102 000000000,1,1.0001\n',None),
            ('20250102 000000000,1.1,1,0\n',None),
            ('20250102 000000000,NaN,1,0\n',None),
            ('20250102 000000000,1,1.0001,0\n','DAT_ASCII_GBPUSD_T_202501.csv')]:
            with tempfile.TemporaryDirectory() as root:
                job=make_zip(root,'202501',row,member)
                with self.assertRaises(SourceError):list(ArchiveReader(root,[job]).groups())

    def test_no_future_prices_used_in_previous_bar_signal_or_seed(self):
        start=at('2025-02-03',7)
        def prefix():
            i=Indicators(previous=Bar(start,1.1,1.1,1.1),count=30,gain=.00029,loss=.00071,
                         tr=.001,plus=.0005,minus=.0005,dx_count=30,adx=10,rsi=29)
            e=Engine(indicators=i,reference=.001,variance=.000001,warmup_done=True,
                     builder=BarBuilder(start))
            for t in range(start,start+BAR_MS,60000):e.feed(book(t,1.1002))
            e.feed(book(start+BAR_MS-1000,1.1002))
            return e
        a,b=prefix(),prefix()
        a.feed(book(start+BAR_MS,1.5));b.feed(book(start+BAR_MS,.8))
        self.assertEqual(a.opportunities,b.opportunities)
        self.assertEqual(len(a.opportunities),1)
        self.assertAlmostEqual(a.opportunities[0][2],1.1002)
        self.assertEqual(a.reference,b.reference)
        self.assertEqual(a.variance,b.variance)
        self.assertEqual(len(a.paths),6)

    def test_warmup_state_is_saved_before_first_outcome_quote_reaches_engine(self):
        b=BarBuilder(START-BAR_MS)
        for t in range(START-BAR_MS,START,60000):b.add(book(t,1.1))
        b.add(book(START-1000,1.1))
        e=Engine(builder=b,last=book(START-1000,1.1),
                 warmup_returns=[.001]*1000,last_group_ms=START-1000)
        seen=[]
        def sink(state):
            self.assertLess(e.last.time_ms,START)
            self.assertLess(state['last_source_group']['fields']['time_ms'],START)
            self.assertTrue(all(p.basket is None for p in e.paths))
            seen.append(state)
        e.feed(book(START,2),warmup_sink=sink)
        self.assertEqual(len(seen),1)
        self.assertEqual(e.last.time_ms,START)


class OnceOnlyTests(unittest.TestCase):
    def test_freeze_rejects_mutated_code_and_runtime_identity(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root);(p/'code.py').write_text('synthetic');(p/'timezone').write_text('fixed')
            freeze={'schema':1,'proxy_harness_frozen':True,
                'files':{'code.py':digest(p/'code.py')},'runtime_data':{str(p/'timezone'):digest(p/'timezone')}}
            verify_freeze(p,freeze)
            (p/'code.py').write_text('changed')
            with self.assertRaises(ValueError):verify_freeze(p,freeze)
            (p/'code.py').write_text('synthetic');(p/'timezone').write_text('changed')
            with self.assertRaises(ValueError):verify_freeze(p,freeze)

    def test_full_frozen_schema_preserves_all_paths_and_comparators(self):
        schema=json.loads((HERE/'result_schema.json').read_text())
        r=failure_result(Engine(),'synthetic',{});r['integrity']={}
        validate_result(r,schema)
        r['paths'].pop('STATIC_GRID_STRESS')
        with self.assertRaises(ValueError):validate_result(r,schema)

    def test_result_never_overwritten_and_partial_candidate_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/'result.json'
            atomic_json(p,{'exact':'first'})
            with self.assertRaises(FileExistsError):atomic_json(p,{'exact':'second'})
            self.assertEqual(json.loads(p.read_text()),{'exact':'first'})
            self.assertEqual(len(list(Path(root).glob('result*.tmp'))),1)

    def test_partial_saved_result_blocks_even_first_attempt(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root)/'result-crash.tmp').write_text('{"partial_pnl":')
            with self.assertRaises(FileExistsError):begin_attempt(root,{'frozen_commit':'a'*40})

    def test_second_attempt_requires_evidence_not_elapsed_time(self):
        with tempfile.TemporaryDirectory() as root:
            begin_attempt(root,{'frozen_commit':'a'*40})
            with self.assertRaises(FileExistsError):begin_attempt(root,{'frozen_commit':'a'*40})

    def test_resume_does_not_bypass_saved_result(self):
        with tempfile.TemporaryDirectory() as root:
            atomic_json(Path(root)/'result.json',{'verdict':'source_failed'})
            with self.assertRaises(FileExistsError):begin_attempt(root,{'frozen_commit':'a'*40},
                {'no_printed_or_saved_outcome':True})

    def test_claim_requires_exact_original_ref_freeze_and_commit(self):
        c={'schema':1,'ref':REF,'atomic_create_receipt':True,
           'freeze_sha256':'b'*64,'frozen_commit':'a'*40}
        remote={'ref':REF,'object':{'sha':'a'*40}}
        verify_claim(c,'b'*64,remote)
        for key,value in [('ref','refs/heads/f1/crypto-carry-001-stage-b-look'),
                          ('atomic_create_receipt',False),('frozen_commit','c'*40)]:
            changed=dict(c);changed[key]=value
            with self.assertRaises(ValueError):verify_claim(changed,'b'*64,remote)

    def test_source_failure_preserves_partial_book_and_all_nine_fields(self):
        e=Engine()
        r=failure_result(e,'synthetic_missing_archive',{})
        self.assertEqual(r['verdict']['RESULT'],'SOURCE_GATE_FAILED')
        self.assertEqual(len(r['verdict']),9)
        self.assertEqual(len(r['partial_marked_equity']),6)
        self.assertIn('partial_exposure',r)


if __name__=='__main__':unittest.main()
