"""Synthetic pinned quarterly CSVs only; no market payloads or real HTTP."""
import copy
import hashlib
import io
import json
import tempfile
import time
import unittest
import urllib.error
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from quant.edge_lab import vix

ROOT = Path(__file__).resolve().parents[1]
# Calendar/URLs are metadata from the parked attempt, never its market bodies.
BASE_FILES = json.loads((ROOT/'research/edge_lab/discovery/experiments/disc-cfe-vix-term-premium-l1-v0.manifest.json').read_text())['files'][:36]
CONTRACT = {'claim_ceiling':'PROMOTE_EXPRESSION', 'design':vix.DESIGN.copy()}


def fixture(gross=None):
    values = [Decimal(str(v)) for v in (gross if gross is not None else ['1']*36)]
    manifest = {'experiment_id':vix.EXPERIMENT, 'files':copy.deepcopy(BASE_FILES)}
    raw = {}
    for f, value in zip(manifest['files'], values):
        body = f'Trade Date,Settle\n{f["entry_target"]},{Decimal("20")+value}\n{f["exit_target"]},20\n'.encode()
        raw[f['contract']] = body
        repin(f, body)
    return manifest, raw


def repin(item, body):
    item.update(sha256=hashlib.sha256(body).hexdigest(), payload_bytes=len(body), prior_status=200)


def changed_rows(manifest, raw, rows, index=0):
    f = manifest['files'][index]
    body = ('Trade Date,Settle\n'+''.join(f'{d},{v}\n' for d,v in rows)).encode()
    raw[f['contract']] = body
    repin(f, body)


class Response(io.BytesIO):
    status = 200
    headers = {}
    def __init__(self, body, url):
        super().__init__(body)
        self.url = url
    def geturl(self):
        return self.url


class Opener:
    def __init__(self, manifest, raw, fail=None, changed=None):
        self.by_url = {f['url']:(f['contract'], raw[f['contract']]) for f in manifest['files']}
        self.calls, self.fail, self.changed = [], fail, changed
    def open(self, request, timeout):
        name, body = self.by_url[request.full_url]
        self.calls.append((name, timeout, request.full_url))
        if name == self.fail:
            raise OSError('synthetic transport failure')
        return Response(body if name != self.changed else body+b'changed', request.full_url)


class VixTest(unittest.TestCase):
    def test_complete_short_pnl_costs_units_and_no_quote_redistribution(self):
        m, raw = fixture()
        result = vix.calculate(m, raw, CONTRACT)
        self.assertEqual(result['decision'], 'PROMOTE_EXPRESSION')
        self.assertEqual(result['observations'], {'trades':36, 'calendar_year_clusters':9})
        for name, value in [('gross',1), ('central',.9), ('stress',.75)]:
            self.assertEqual(result['summary'][name]['mean_points'], value)
            self.assertEqual(result['summary'][name]['mean_usd'], value*1000)
            self.assertEqual(result['summary'][name]['year_totals_points']['2013'], value*4)
        self.assertEqual(result['unit_economics']['break_even_friction_usd'], 1000)
        self.assertEqual(result['unit_economics']['frequency_per_year'], 4)
        self.assertEqual(result['limits']['current_2022_2026'], 'UNKNOWN')
        self.assertEqual(result['adversary']['remaining_trades'], 32)
        self.assertEqual(result['adversary']['removed_year'], 2013)
        self.assertEqual(result['trades'][0]['gross_points'], 1)
        self.assertNotIn('Settle', json.dumps(result))
        self.assertNotIn('entry_price', json.dumps(result))

    def test_decimal_threshold_and_kill_boundaries(self):
        for gross, expected in [('.35','PROMOTE_EXPRESSION'), ('.25','KILL_EXPRESSION'),
                                ('0','KILL_EXPRESSION'), ('.30','PARK_ECONOMICS')]:
            with self.subTest(gross=gross):
                m, raw = fixture([gross]*36)
                result = vix.calculate(m, raw, CONTRACT)
                self.assertEqual(result['decision'], expected)
                self.assertEqual(result['adversary']['executed'], expected == 'PROMOTE_EXPRESSION')
        self.assertEqual(vix.calculate(*fixture(['.35']*36), CONTRACT)['summary']['central']['mean_points'], .25)

    def test_fixed_block_must_be_strictly_positive_and_cannot_filter_losses(self):
        m, raw = fixture(['.10']*24+['2']*12)
        result = vix.calculate(m, raw, CONTRACT)
        self.assertEqual(result['decision'], 'PARK_ECONOMICS')
        self.assertEqual(result['fixed_block_central_mean_points']['2013-2018'], 0)
        self.assertFalse(result['adversary']['executed'])
        self.assertEqual(len(result['trades']),36)

    def test_one_adversary_stress_zero_parks_and_best_year_tie_is_earliest(self):
        m, raw = fixture(['2']*4+['.25']*32)
        result = vix.calculate(m, raw, CONTRACT)
        self.assertEqual(result['primary_decision'], 'PROMOTE_EXPRESSION')
        self.assertEqual(result['decision'], 'PARK_ECONOMICS')
        self.assertEqual(result['adversary']['removed_year'], 2013)
        self.assertEqual(result['adversary']['remaining_mean_net_points']['stress'], 0)
        m, raw = fixture(['1']*8+['.5']*28)
        result = vix.calculate(m, raw, CONTRACT)
        self.assertEqual(result['adversary']['removed_year'],2013)
        self.assertTrue(result['adversary']['passed'])

    def test_endpoint_drawdown_starts_at_zero_and_bootstrap_is_whole_year(self):
        m, raw = fixture(['-1','2','-3','4']*9)
        result = vix.calculate(m, raw, CONTRACT)
        self.assertEqual(result['summary']['gross']['endpoint_drawdown_points'], -3)
        self.assertEqual(result['summary']['gross']['worst_trade_points'], -3)
        self.assertEqual(result['uncertainty']['gross_mean_points_interval'], [.5,.5])
        self.assertFalse(result['uncertainty']['statistical_confirmation'])
        self.assertEqual(result['uncertainty']['draws'],2000)
        self.assertEqual(result['uncertainty']['seed'],41011)
        self.assertEqual(result, vix.calculate(m, raw, CONTRACT))
        m, raw = fixture([str(y) for y in range(9) for _ in range(4)])
        result = vix.calculate(m, raw, CONTRACT)
        interval = result['uncertainty']['gross_mean_points_interval']
        self.assertLess(interval[0],4)
        self.assertGreater(interval[1],4)

    def test_first_positive_after_target_inclusive_four_days_no_best_price_choice(self):
        m, raw = fixture()
        entry = date.fromisoformat(m['files'][0]['entry_target'])
        exit_ = date.fromisoformat(m['files'][0]['exit_target'])
        changed_rows(m, raw, [(entry-timedelta(days=1),1000), (entry,0),
                              (entry+timedelta(days=2),21), (entry+timedelta(days=3),1000),
                              (exit_+timedelta(days=4),20)])
        result = vix.calculate(m, raw, CONTRACT)
        self.assertEqual(result['trades'][0]['entry_date'],(entry+timedelta(days=2)).isoformat())
        self.assertEqual(result['trades'][0]['exit_date'],(exit_+timedelta(days=4)).isoformat())
        self.assertEqual(result['trades'][0]['gross_points'],1)
        self.assertEqual(m['files'][-1]['expiry'],'2021-12-22')

    def test_csv_missing_duplicate_order_nonfinite_and_fifth_day_fail_without_economics(self):
        for case in ('missing','duplicate','order','nan','negative','blank','late'):
            with self.subTest(case=case):
                m, raw = fixture()
                entry, exit_ = m['files'][0]['entry_target'],m['files'][0]['exit_target']
                rows = [(entry,21),(exit_,20)]
                if case == 'missing': rows = [(entry,21)]
                if case == 'duplicate': rows.insert(1,(entry,21))
                if case == 'order': rows.append(((date.fromisoformat(entry)+timedelta(days=1)).isoformat(),22))
                if case == 'nan': rows[0] = (entry,'NaN')
                if case == 'negative': rows[0] = (entry,-1)
                if case == 'blank': rows[0] = ('',21)
                if case == 'late': rows[0] = ((date.fromisoformat(entry)+timedelta(days=5)).isoformat(),21)
                changed_rows(m, raw, rows)
                result = vix.calculate(m, raw, CONTRACT)
                self.assertEqual(result['decision'],'PARK_DATA')
                self.assertFalse(result['economics_computed'])
                self.assertNotIn('summary',result)
                self.assertNotIn('trades',result)

    def test_strictly_descending_csv_has_same_chronological_first_positive_endpoints(self):
        m, raw = fixture()
        ascending = vix.calculate(m,raw,CONTRACT)
        for i,f in enumerate(m['files']):
            changed_rows(m,raw,[(f['exit_target'],20),(f['entry_target'],21)],i)
        self.assertEqual(vix.calculate(m,raw,CONTRACT),ascending)

    def test_all36_exact_versions_and_frozen_population_rule_rights_are_required(self):
        for case in ('missing_raw','extra_raw','sha','size','missing_file','duplicate','reorder','failed_url','calendar','rights','design'):
            with self.subTest(case=case):
                m, raw = fixture()
                contract = copy.deepcopy(CONTRACT)
                if case == 'missing_raw': raw.pop('H2013')
                if case == 'extra_raw': raw['H2022'] = b'not allowed'
                if case == 'sha': raw['H2013'] += b'changed'
                if case == 'size': m['files'][0]['payload_bytes'] += 1
                if case == 'missing_file': m['files'].pop()
                if case == 'duplicate': m['files'][1] = m['files'][0]
                if case == 'reorder': m['files'][0],m['files'][1] = m['files'][1],m['files'][0]
                if case == 'failed_url': m['files'][0]['url'] = 'https://cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/VX_2022-03-16.csv'
                if case == 'calendar': m['files'][-1]['expiry'] = '2021-12-15'
                if case == 'rights': contract['claim_ceiling'] = 'PROMOTE_MECHANISM'
                if case == 'design': contract['design']['entry_days'] = 44
                result = vix.calculate(m, raw, contract)
                self.assertEqual(result['decision'],'PARK_DATA')
                self.assertFalse(result['economics_computed'])

    def test_manifest_rejected_before_any_body_or_network_access(self):
        m, raw = fixture()
        m['files'][0]['url'] = 'https://example.com/private'
        with tempfile.TemporaryDirectory() as tmp, patch.object(vix.urllib.request,'build_opener') as opener:
            result = vix.run(m, CONTRACT, tmp)
        opener.assert_not_called()
        self.assertEqual(result['decision'],'PARK_DATA')

    def test_run_sequential36_pinned_once_private_cache_reused_without_http(self):
        m, raw = fixture()
        opener = Opener(m, raw)
        with tempfile.TemporaryDirectory() as tmp, patch.object(vix.urllib.request,'build_opener',return_value=opener):
            first = vix.run(m, CONTRACT, tmp)
            self.assertEqual(first['decision'],'PROMOTE_EXPRESSION')
            self.assertEqual([c[0] for c in opener.calls], [f['contract'] for f in m['files']])
            self.assertTrue(all(0 < c[1] <= 15 for c in opener.calls))
            self.assertEqual(first['acquisition']['payload_bytes'],sum(map(len,raw.values())))
            self.assertEqual(len(first['acquisition']['receipts']),36)
            self.assertEqual((Path(tmp)/'H2013.csv').stat().st_mode & 0o777, 0o600)
            self.assertEqual(Path(tmp).stat().st_mode & 0o777,0o700)
            second = vix.run(m, CONTRACT, tmp)
            self.assertEqual(len(opener.calls),36)
            self.assertEqual(second,first)
            self.assertEqual(json.loads((Path(tmp)/(vix.EXPERIMENT+'.result.json')).read_text()),first)
            self.assertNotIn('H2022',json.dumps(first))

    def test_failure_preserves_partial_and_never_retries_or_publishes_early_economics(self):
        m, raw = fixture()
        opener = Opener(m, raw, fail='U2013')
        with tempfile.TemporaryDirectory() as tmp, patch.object(vix.urllib.request,'build_opener',return_value=opener), patch('sys.stdout',new_callable=io.StringIO) as stdout:
            first = vix.run(m, CONTRACT, tmp)
            self.assertEqual([c[0] for c in opener.calls],['H2013','M2013','U2013'])
            self.assertEqual(first['decision'],'PARK_DATA')
            self.assertFalse(first['economics_computed'])
            self.assertEqual((Path(tmp)/'U2013.csv').read_bytes(),b'')
            self.assertTrue((Path(tmp)/'U2013.intent.json').exists())
            self.assertTrue((Path(tmp)/'U2013.receipt.json').exists())
            second = vix.run(m, CONTRACT, tmp)
            self.assertEqual(second['decision'],'PARK_DATA')
            self.assertEqual(len(opener.calls),3)
            self.assertEqual(stdout.getvalue(),'')
            self.assertNotIn('summary',first)

    def test_hash_mismatch_preserved_bytes_counted_and_not_replaced(self):
        m, raw = fixture()
        opener = Opener(m, raw, changed='M2013')
        with tempfile.TemporaryDirectory() as tmp, patch.object(vix.urllib.request,'build_opener',return_value=opener):
            result = vix.run(m, CONTRACT, tmp)
            self.assertEqual(result['decision'],'PARK_DATA')
            self.assertEqual([c[0] for c in opener.calls],['H2013','M2013'])
            self.assertEqual((Path(tmp)/'M2013.csv').read_bytes(),raw['M2013']+b'c')
            self.assertEqual(result['acquisition']['payload_bytes'],len(raw['H2013'])+len(raw['M2013'])+1)
            again = vix.run(m, CONTRACT, tmp)
            self.assertEqual(again['decision'],'PARK_DATA')
            self.assertEqual(len(opener.calls),2)

    def test_missing_body_after_intent_never_requests_again(self):
        m, raw = fixture()
        with tempfile.TemporaryDirectory() as tmp, patch.object(vix.urllib.request,'build_opener') as opener:
            (Path(tmp)/'H2013.intent.json').write_text('{}')
            result = vix.run(m, CONTRACT, tmp)
        self.assertEqual(result['decision'],'PARK_DATA')
        opener.return_value.open.assert_not_called()

    def test_invalid_first_csv_stops_before_second_request_and_error_has_no_values(self):
        m, raw = fixture()
        sentinel = 'SECRET_SYNTHETIC_QUOTE'
        changed_rows(m, raw, [(m['files'][0]['entry_target'],sentinel),(m['files'][0]['exit_target'],20)])
        opener = Opener(m, raw)
        with tempfile.TemporaryDirectory() as tmp, patch.object(vix.urllib.request,'build_opener',return_value=opener):
            result = vix.run(m, CONTRACT, tmp)
        self.assertEqual(result['decision'],'PARK_DATA')
        self.assertEqual(len(opener.calls),1)
        self.assertNotIn(sentinel,json.dumps(result))

    def test_partial_transport_read_receipt_has_exact_retained_bytes(self):
        m, raw = fixture()
        class Partial(Response):
            def read(self, count):
                if self.tell():
                    raise TimeoutError('synthetic timeout')
                return super().read(8)
        opener = Opener(m, raw)
        opener.open = lambda request, timeout: Partial(raw['H2013'],request.full_url)
        with tempfile.TemporaryDirectory() as tmp, patch.object(vix.urllib.request,'build_opener',return_value=opener):
            result = vix.run(m, CONTRACT, tmp)
            self.assertEqual((Path(tmp)/'H2013.csv').read_bytes(),raw['H2013'][:8])
            self.assertEqual(result['acquisition']['payload_bytes'],8)
        self.assertEqual(result['decision'],'PARK_DATA')

    def test_existing_prior_raw36_reuses_hashes_without_http(self):
        m, raw = fixture()
        with tempfile.TemporaryDirectory() as tmp, patch.object(vix.urllib.request,'build_opener') as opener:
            for name, body in raw.items():
                (Path(tmp)/(name+'.csv')).write_bytes(body)
            result = vix.run(m,CONTRACT,tmp)
        opener.return_value.open.assert_not_called()
        self.assertEqual(result['decision'],'PROMOTE_EXPRESSION')
        self.assertTrue(all(r['reused'] for r in result['acquisition']['receipts']))

    def test_derived_usd_overflow_and_strict_csv_quote_fail_closed(self):
        m, raw = fixture()
        changed_rows(m,raw,[(m['files'][0]['entry_target'],'1e308'),(m['files'][0]['exit_target'],20)])
        result = vix.calculate(m,raw,CONTRACT)
        self.assertEqual(result['decision'],'PARK_DATA')
        self.assertFalse(result['economics_computed'])
        m, raw = fixture()
        raw['H2013'] = b'Trade Date,Settle\n"'
        repin(m['files'][0],raw['H2013'])
        opener = Opener(m,raw)
        with tempfile.TemporaryDirectory() as tmp, patch.object(vix.urllib.request,'build_opener',return_value=opener):
            result = vix.run(m,CONTRACT,tmp)
        self.assertEqual(result['decision'],'PARK_DATA')
        self.assertEqual(len(opener.calls),1)

    def test_full_body_then_timeout_never_reuses_failed_provenance(self):
        m, raw = fixture()
        class FullThenTimeout(Response):
            def read(self, count):
                if self.tell():
                    raise TimeoutError('synthetic after full body')
                return super().read(count)
        calls = []
        class FailingOpener:
            def open(self,request,timeout):
                calls.append(request.full_url)
                return FullThenTimeout(raw['H2013'],request.full_url)
        with tempfile.TemporaryDirectory() as tmp, patch.object(vix.urllib.request,'build_opener',return_value=FailingOpener()):
            first = vix.run(m,CONTRACT,tmp)
            self.assertEqual(first['decision'],'PARK_DATA')
            self.assertEqual((Path(tmp)/'H2013.csv').read_bytes(),raw['H2013'])
            # Even without the durable result, failed receipt provenance cannot resume.
            (Path(tmp)/(vix.EXPERIMENT+'.result.json')).unlink()
            second = vix.run(m,CONTRACT,tmp)
        self.assertEqual(second['decision'],'PARK_DATA')
        self.assertEqual(len(calls),1)

    def test_real_http_error_code_retained_without_response_body(self):
        m, raw = fixture()
        def denied(request,timeout):
            raise urllib.error.HTTPError(request.full_url,403,'synthetic denial',{},None)
        opener = Opener(m,raw)
        opener.open = denied
        with tempfile.TemporaryDirectory() as tmp, patch.object(vix.urllib.request,'build_opener',return_value=opener):
            result = vix.run(m,CONTRACT,tmp)
            receipt = json.loads((Path(tmp)/'H2013.receipt.json').read_text())
        self.assertEqual(result['decision'],'PARK_DATA')
        self.assertEqual(receipt['status'],403)
        self.assertEqual(receipt['payload_bytes'],0)

    def test_metadata_reserve_refuses_total_cap_before_any_requests(self):
        m, raw = fixture()
        for f in m['files']:
            f['payload_bytes'] = vix.MAX_TOTAL//36
        with tempfile.TemporaryDirectory() as tmp, patch.object(vix.urllib.request,'build_opener') as opener:
            result = vix.run(m,CONTRACT,tmp)
        self.assertEqual(result['decision'],'PARK_DATA')
        opener.assert_not_called()

    def test_redirect_status_encoding_and_payload_overflow_do_not_continue(self):
        for case in ('redirect','status','encoding','overflow'):
            with self.subTest(case=case):
                m, raw = fixture()
                opener = Opener(m,raw)
                response = Response(raw['H2013'],m['files'][0]['url'])
                if case == 'redirect': response.url = 'https://example.com/not-permitted'
                if case == 'status': response.status = 403
                if case == 'encoding': response.headers = {'Content-Encoding':'gzip'}
                if case == 'overflow': response = Response(b'x'*(vix.MAX_FILE+100),m['files'][0]['url'])
                calls = []
                def open_response(request,timeout):
                    calls.append(request.full_url)
                    return response
                opener.open = open_response
                with tempfile.TemporaryDirectory() as tmp, patch.object(vix.urllib.request,'build_opener',return_value=opener):
                    result = vix.run(m,CONTRACT,tmp)
                    self.assertLessEqual((Path(tmp)/'H2013.csv').stat().st_size,vix.MAX_FILE)
                self.assertEqual(result['decision'],'PARK_DATA')
                self.assertEqual(len(calls),1)

    def test_whole_job_deadline_stops_sequential_fetches_without_result(self):
        m, raw = fixture()
        opener = Opener(m,raw)
        elapsed = iter(range(0,1000,4))
        with tempfile.TemporaryDirectory() as tmp, patch.object(vix.urllib.request,'build_opener',return_value=opener), patch.object(vix.time,'monotonic',side_effect=lambda:next(elapsed)):
            result = vix.run(m,CONTRACT,tmp)
        self.assertEqual(result['decision'],'PARK_DATA')
        self.assertLess(len(opener.calls),36)
        self.assertFalse(result['economics_computed'])
        self.assertTrue(all(0 < c[1] <= 15 for c in opener.calls))

    def test_hard_job_deadline_bypasses_post_expiry_persistence(self):
        m, raw = fixture()
        opener = Opener(m,raw)
        real_endpoints = vix._endpoints
        def slow_source_qa(*args):
            time.sleep(.20)
            return real_endpoints(*args)
        started = time.monotonic()
        with tempfile.TemporaryDirectory() as tmp, patch.object(vix.urllib.request,'build_opener',return_value=opener), patch.object(vix,'MAX_JOB',.02), patch.object(vix,'_endpoints',side_effect=slow_source_qa):
            result = vix.run(m,CONTRACT,tmp)
            self.assertEqual((Path(tmp)/'H2013.csv').read_bytes(),raw['H2013'])
            self.assertTrue((Path(tmp)/'H2013.intent.json').exists())
            self.assertFalse((Path(tmp)/(vix.EXPERIMENT+'.result.json')).exists())
            self.assertFalse((Path(tmp)/'H2013.receipt.json').exists())
        self.assertLess(time.monotonic()-started,.15)
        self.assertEqual(result['decision'],'PARK_DATA')
        self.assertFalse(result['economics_computed'])


if __name__ == '__main__':
    unittest.main()
