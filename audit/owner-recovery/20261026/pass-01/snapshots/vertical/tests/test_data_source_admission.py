"""Source admission fixtures are entirely synthetic; no provider access."""
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from quant.dataplane.adapters import DataUnavailable, YAHOO_CAVEATS, fetch_yahoo_daily
from quant.dataplane import ingest
from quant.dataplane.registry import DatasetRegistry
from quant.events import EventLog
from quant.paths import QuantPaths


class DailySourceAdmissionTests(unittest.TestCase):
    def payload(self):
        return {'chart': {'error': None, 'result': [{'timestamp': [1704153600, 1704240000, 1704326400],
            'indicators': {'quote': [{'open': [10, 10, 10], 'high': [11, 11, 11],
                'low': [9, 9, 9], 'close': [10, 10, 10], 'volume': [1, 1, 0]}],
                'adjclose': [{'adjclose': [10, 10, 10]}]}}]}}

    def fetch(self, payload):
        with patch('quant.dataplane.adapters.urllib.request.urlopen',
                   return_value=io.BytesIO(json.dumps(payload).encode())):
            return fetch_yahoo_daily(['SYNTHETIC'])

    def test_only_explicit_null_error_admits_a_successful_envelope(self):
        for error in ('', {}, [], False, 0, 'provider error', {'code': 'NOT_FOUND'}):
            payload = self.payload()
            payload['chart']['error'] = error
            with self.subTest(error=error), self.assertRaises(DataUnavailable):
                self.fetch(payload)
        payload = self.payload()
        del payload['chart']['error']
        with self.assertRaises(DataUnavailable):
            self.fetch(payload)

    def test_malformed_provider_envelopes_and_series_are_dependency_blocks(self):
        bad = [None, [], {}, {'chart': None}, {'chart': {}}, {'chart': {'error': None, 'result': []}}]
        for key, value in [('result', None), ('result', [None]), ('result', [{}, {}])]:
            payload = self.payload()
            payload['chart'][key] = value
            bad.append(payload)
        for key, value in [('indicators', None), ('indicators', []), ('timestamp', None),
                           ('timestamp', []), ('timestamp', [True, 1704240000, 1704326400]),
                           ('timestamp', [10**100, 1704240000, 1704326400]),
                           ('timestamp', [1704153600]*3)]:
            payload = self.payload()
            payload['chart']['result'][0][key] = value
            bad.append(payload)
        for field, value in [('open', []), ('close', [True, 10, 10]), ('volume', [1, 'unknown', 0]),
                             ('low', [9, float('nan'), 9]), ('high', [11, float('inf'), 11])]:
            payload = self.payload()
            payload['chart']['result'][0]['indicators']['quote'][0][field] = value
            bad.append(payload)
        payload = self.payload()
        del payload['chart']['result'][0]['indicators']['adjclose']
        bad.append(payload)
        for payload in bad:
            with self.subTest(payload=payload), self.assertRaises(DataUnavailable):
                self.fetch(payload)

    def test_complete_bars_real_zero_volume_and_pit_caveats_are_preserved(self):
        payload = self.payload()
        before = deepcopy(payload)
        panel, provenance = self.fetch(payload)
        self.assertEqual(panel.dates, ['2024-01-02', '2024-01-03', '2024-01-04'])
        for date in panel.dates:
            self.assertEqual([panel.price(date, 'SYNTHETIC', k) for k in
                              ('open', 'high', 'low', 'close', 'adj_close')], [10, 11, 9, 10, 10])
        self.assertEqual(panel.price('2024-01-04', 'SYNTHETIC', 'volume'), 0)
        self.assertEqual(provenance['bars_per_symbol'], {'SYNTHETIC': 3})
        self.assertEqual(provenance['caveats'], YAHOO_CAVEATS)
        self.assertEqual(payload, before)

    def test_missing_price_or_volume_drops_the_bar_without_interpolation(self):
        for field in ('open', 'volume'):
            payload = self.payload()
            payload['chart']['result'][0]['indicators']['quote'][0][field][1] = None
            panel, provenance = self.fetch(payload)
            self.assertFalse(panel.has('2024-01-03', 'SYNTHETIC'))
            self.assertEqual(provenance['bars_per_symbol'], {'SYNTHETIC': 2})
        payload['chart']['result'][0]['indicators']['quote'][0]['volume'] = [None]*3
        with self.assertRaises(DataUnavailable):
            self.fetch(payload)

    def test_actual_ingestion_records_block_and_continues_snapshot_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = QuantPaths(Path(directory)).ensure()
            registry = DatasetRegistry(paths.dataset_registry, paths.root)
            log = EventLog(paths.events)
            with patch('quant.dataplane.adapters.urllib.request.urlopen', return_value=io.BytesIO(b'{"chart":{}}')), \
                    patch.object(ingest, 'ingest_index', side_effect=DataUnavailable('synthetic absent index')), \
                    patch.object(ingest, 'register_committed_snapshots', return_value=[]) as fallback:
                outcome = ingest.ingest_all(paths, registry, log)
            self.assertEqual(outcome['ingested'], [])
            self.assertEqual({row['dataset_id'] for row in outcome['blocked']},
                             {ingest.SECTOR_DATASET, ingest.INDEX_DATASET})
            self.assertEqual([row['kind'] for row in log.all()], ['dataset_blocked', 'dataset_blocked'])
            self.assertTrue(all(row['severity'] == 'WARN' for row in log.all()))
            self.assertFalse(log.faults())
            self.assertFalse((paths.datasets/(ingest.SECTOR_DATASET+'.csv')).exists())
            fallback.assert_called_once_with(paths, registry, log)
            # The dependency state is resumable from the ordinary persistent event log.
            self.assertEqual(EventLog(paths.events).all(), log.all())
