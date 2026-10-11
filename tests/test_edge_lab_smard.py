"""Synthetic causal/calendar/source-version challenges; no market data."""
import copy
import io
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from quant.edge_lab.smard import (SourceError, WINDOW, HOUR_MS, millis, parse,
    day_spreads, calculate, mean_interval, capture, validate_manifest)
from quant.edge_lab.public_inputs import runner_environment
from quant.edge_lab.store import Refused


def calendar_quotes():
    return {t:20.0 for t in range(millis(WINDOW[0]), millis(WINDOW[1]), HOUR_MS)}


def synthetic_records(quotes):
    pairs = [[t,v] for t,v in quotes.items()]
    return [{"body":json.dumps({"series":pairs[i:i+168]})} for i in range(0,len(pairs),168)]


def synthetic_manifest():
    first = millis("2024-12-29T23:00:00Z")
    return {"series":"4169","region":"DE","resolution":"hour","planned_window":WINDOW,
        "files":[{"timestamp":t,"url":f"https://www.smard.de/app/chart_data/4169/DE/4169_DE_hour_{t}.json",
                  "status":200,"bytes":2,"etag":'"synthetic"',"encoding":None}
                 for t in [first+i*7*24*HOUR_MS for i in range(53)]]}


class SmardTest(unittest.TestCase):
    def test_full_calendar_dst_no_missing_or_double_selected_hour(self):
        q=calendar_quotes();rows=day_spreads(q)
        self.assertEqual(len(q),8760);self.assertEqual(len(rows),365)
        self.assertEqual(len({r['buy_ms'] for r in rows}),365)
        march=[r for r in rows if r['day']=='2025-03-30'][0]
        october=[r for r in rows if r['day']=='2025-10-26'][0]
        for r in (march,october):self.assertEqual(r['sell_ms']-r['buy_ms'],15*HOUR_MS)
        self.assertEqual(datetime.fromtimestamp(march['buy_ms']/1000).hour,1)
        self.assertEqual(datetime.fromtimestamp(october['buy_ms']/1000).hour,2)

    def test_price_change_cannot_select_new_hours_or_omit_negative_day(self):
        q=calendar_quotes();before=day_spreads(q)
        q[before[20]['sell_ms']]=-100000
        after=day_spreads(q)
        self.assertEqual([(r['buy_ms'],r['sell_ms']) for r in before],[(r['buy_ms'],r['sell_ms']) for r in after])
        self.assertLess(after[20]['gross_eur_per_input_mwh'],before[20]['gross_eur_per_input_mwh'])
        self.assertEqual(len(after),365)

    def test_loss_efficiency_asset_cost_and_benchmark_are_not_hidden(self):
        kind,paths,effect,_=calculate(calendar_quotes())
        self.assertEqual(kind,'NEGATIVE')
        self.assertEqual(paths['central']['mean_net_eur_per_input_mwh'],-104)
        self.assertEqual(paths['stress']['annual_net_eur_per_1mwh_device'],-154*365)
        self.assertEqual(effect['mean_gross_break_even_all_in_cost_eur_per_input_mwh'],-4)
        self.assertEqual(mean_interval([2]*365),[2,2])

    def test_fixed_stress_is_required_for_positive_not_best_cost(self):
        q=calendar_quotes()
        for r in day_spreads(q):q[r['sell_ms']]=175
        kind,paths,_,_=calculate(q)
        self.assertGreater(paths['central']['mean_net_eur_per_input_mwh'],0)
        self.assertLess(paths['stress']['mean_net_eur_per_input_mwh'],0)
        self.assertEqual(kind,'INSUFFICIENT_POWER')

    def test_complete_input_source_qa_and_identical_duplicates(self):
        q=calendar_quotes();r=synthetic_records(q)
        r.append({'body':json.dumps({'series':[[next(iter(q)),20]]})})
        parsed,qa=parse(r)
        self.assertEqual(parsed,q);self.assertEqual(qa['duplicates_identical'],1)
        self.assertEqual(qa['unique_hours_full_calendar'],8760)

    def test_null_gap_nonfinite_conflicting_revision_and_subhour_fail(self):
        base=synthetic_records(calendar_quotes())
        for replacement in (None,float('nan')):
            r=copy.deepcopy(base);data=json.loads(r[0]['body']);data['series'][0][1]=replacement;r[0]['body']=json.dumps(data)
            with self.assertRaises(SourceError):parse(r)
        r=copy.deepcopy(base);data=json.loads(r[0]['body']);data['series'].pop(0);r[0]['body']=json.dumps(data)
        with self.assertRaisesRegex(SourceError,'gaps'):parse(r)
        r=copy.deepcopy(base);r.append({'body':json.dumps({'series':[[millis(WINDOW[0]),21]]})})
        with self.assertRaisesRegex(SourceError,'Conflicting'):parse(r)
        r=copy.deepcopy(base);data=json.loads(r[0]['body']);data['series'][0][0]+=900000;r[0]['body']=json.dumps(data)
        with self.assertRaises(SourceError):parse(r)

    def test_weak_version_foreign_url_and_short_calendar_cannot_capture(self):
        for key,value in [('etag','W/"synthetic"'),('url','https://example.com/data'),('bytes',999999)]:
            m=synthetic_manifest();m['files'][0][key]=value
            with self.assertRaises(SourceError):validate_manifest(m)
        m=synthetic_manifest();m['files'].pop()
        with self.assertRaises(SourceError):validate_manifest(m)

    def test_capture_retains_raw_once_and_rejects_new_version_before_body(self):
        class Response(io.BytesIO):
            status=200
            headers={'ETag':'"synthetic"'}
            def geturl(self):return self.url
        calls=[]
        def opener(req,timeout):
            calls.append(req.get_header('If-match'))
            r=Response(b'{}');r.url=req.full_url;return r
        with tempfile.TemporaryDirectory() as tmp:
            records,hashes=capture(synthetic_manifest(),tmp,opener)
            self.assertEqual(len(records),53);self.assertEqual(calls,['"synthetic"']*53)
            with self.assertRaisesRegex(SourceError,'Prior capture'):capture(synthetic_manifest(),tmp,opener)
            self.assertEqual(len(calls),53)
        def stale(req,timeout):
            r=Response(b'{}');r.url=req.full_url;r.headers={'ETag':'"new-version"'}
            r.read=lambda *args: self.fail('Changed version body must not be read')
            return r
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(SourceError,'version changed'):capture(synthetic_manifest(),tmp,stale)

    def test_only_nonsecret_proxy_ca_enter_explicit_public_runner(self):
        e={'PATH':'/bin','API_KEY':'secret','GITHUB_TOKEN':'secret','HTTPS_PROXY':'http://proxy:8080','SSL_CERT_FILE':'/tmp/ca'}
        plain=runner_environment({},Path('/tmp'),e)
        self.assertNotIn('HTTPS_PROXY',plain)
        env=runner_environment({'public_inputs':{'hosts':['www.smard.de']}},Path('/tmp'),e)
        self.assertEqual(env['HTTPS_PROXY'],'http://proxy:8080')
        self.assertNotIn('API_KEY',env);self.assertNotIn('GITHUB_TOKEN',env)
        e['HTTPS_PROXY']='http://user:secret@proxy:8080'
        with self.assertRaises(Refused):runner_environment({'public_inputs':{'hosts':['www.smard.de']}},Path('/tmp'),e)


if __name__=='__main__':unittest.main()
