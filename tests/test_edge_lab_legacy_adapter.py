"""Exact legacy authority and result routing use synthetic metadata only."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quant.edge_lab import legacy_adapter as adapter
from quant.edge_lab.contracts import VERDICT_FIELDS, outcome
from quant.edge_lab.engine import initialize, Lab
from quant.edge_lab.store import Refused


class LegacyAdapterTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.capture, self.output = self.root / 'capture', self.root / 'output'
        self.capture.mkdir(); self.output.mkdir()
        self.claim = {'schema':1,'ref':adapter.REF,'atomic_create_receipt':True,
            'freeze_sha256':adapter.FREEZE_SHA256,'frozen_commit':adapter.FROZEN_COMMIT}
        self.remote = {'ref':adapter.REF,'object':{'sha':adapter.FROZEN_COMMIT}}
        self.certificate = {'status':'COMPLETE_NO_ROWS_OPENED','price_rows_opened':0,
            'manifest_sha256':'a'*64,'archives':[{'name':str(i)} for i in range(21)]}
        (self.capture/'reservation.json').write_text(json.dumps(self.claim))
        (self.capture/'capture.json').write_text(json.dumps(self.certificate))
        self.protocol = {'id':adapter.PROTOCOL,'hash':'b'*64,'primary':'MAIN',
            'expressions':['MAIN','NO_ADDS','STATIC_GRID'],'cost_paths':['CENTRAL','STRESS'],
            'benchmark':'frozen comparators','legacy':{'freeze_sha256':adapter.FREEZE_SHA256,'manifest_sha256':'a'*64}}
        self.proof = {'data_fingerprint':hashlib.sha256((self.capture/'capture.json').read_bytes()).hexdigest()}
        self.look = {'id':'look:'+adapter.PROTOCOL,'data_fingerprint':self.proof['data_fingerprint']}

    def tearDown(self): self.temp.cleanup()

    def result(self, tags):
        return {'verdict':{**{k:'synthetic only' for k in VERDICT_FIELDS},'RESULT':tags},
            'paths':{e+'_'+c:{'synthetic_net':-1} for e in self.protocol['expressions'] for c in self.protocol['cost_paths']},
            'qa':{'fixture':True},'opportunities':0,'integrity':{'fixture':True},'paired_central':{'synthetic_only':True}}

    def test_existing_original_ref_and_no_prior_attempt_required_without_price_read(self):
        with patch('zipfile.ZipFile',side_effect=AssertionError('no archives')):
            adapter.check_inputs(self.protocol,self.proof,self.remote,capture=self.capture,output=self.output)
        wrong=copy.deepcopy(self.remote);wrong['object']['sha']='c'*40
        with self.assertRaises(Refused):adapter.check_inputs(self.protocol,self.proof,wrong,capture=self.capture,output=self.output)
        (self.output/'result-partial.tmp').write_text('do not read')
        with patch('pathlib.Path.read_bytes',side_effect=AssertionError('stop before outcome read')):
            with self.assertRaises(Refused):adapter.check_inputs(self.protocol,self.proof,self.remote,capture=self.capture,output=self.output)

    def test_blind_complete_capture_hash_cannot_be_substituted(self):
        bad=copy.deepcopy(self.proof);bad['data_fingerprint']='wrong'
        with self.assertRaises(Refused):adapter.check_inputs(self.protocol,bad,self.remote,capture=self.capture,output=self.output)
        cert=copy.deepcopy(self.certificate);cert['price_rows_opened']=1
        (self.capture/'capture.json').write_text(json.dumps(cert))
        with self.assertRaises(Refused):adapter.check_inputs(self.protocol,self.proof,self.remote,capture=self.capture,output=self.output)

    def test_mapping_keeps_all_six_paths_nine_fields_and_original_increment_label(self):
        r=self.result('PROXY_POSITIVE_NEEDS_EXECUTION_VALIDATION;GRID_OR_ADAPTATION_INCREMENT_UNSUPPORTED')
        receipt=adapter.translate(r,'d'*64,self.protocol,self.look)
        self.assertEqual(receipt['kind'],'POSITIVE_EXPLORATORY')
        self.assertEqual(receipt['verdict'],r['verdict'])
        self.assertEqual(receipt['original_result']['sha256'],'d'*64)
        for e in self.protocol['expressions']:
            for c in self.protocol['cost_paths']:
                self.assertEqual(receipt['expression_results'][e][c],r['paths'][e+'_'+c])
        outcome(receipt,self.protocol,self.look)

    def test_source_failure_is_not_an_economic_rejection_and_uncertainty_stays_wait(self):
        for tags,kind in [('SOURCE_GATE_FAILED;PROXY_COST_REJECT_THIS_RULE','SOURCE_UNUSABLE'),
                          ('PROXY_INCONCLUSIVE;GRID_OR_ADAPTATION_INCREMENT_UNSUPPORTED','INSUFFICIENT_POWER'),
                          ('PROXY_RISK_REJECT_THIS_RULE','NEGATIVE')]:
            r=adapter.translate(self.result(tags),'d'*64,self.protocol,self.look)
            self.assertEqual(r['kind'],kind);outcome(r,self.protocol,self.look)
        with self.assertRaises(Refused):adapter.translate(self.result('INVENTED_ALPHA'),'d'*64,self.protocol,self.look)

    def test_missing_admission_stops_adoption_before_original_ref_or_capture(self):
        lab=Lab(self.root/'research/edge_lab');initialize(lab.store.root)
        p={**self.protocol,'family':'eurusd-technical-grid','runner_sha256':'f'*64,
           'rights':{'permitted':True,'url':'https://example.test','scope':'synthetic'}}
        with patch.object(adapter,'plan',return_value=p):
            with self.assertRaises(Refused):
                adapter.adopt(lab,self.root,{},ref_reader=lambda: self.fail('no network before gates'))
        self.assertEqual(lab.snapshot()[0]['protocols'],{})

    def test_conditional_adoption_mirrors_original_six_paths_without_rewriting_history(self):
        from quant.edge_lab.contracts import GATES
        lab=Lab(self.root/'research/edge_lab');initialize(lab.store.root)
        packet={'id':'synthetic-gate','kind':'METHOD','url':'https://example.test','version':'v1',
            'passage':'generated software permission fixture','fact':'No market input','limit':'synthetic only'}
        lab.evidence(packet)
        before=copy.deepcopy(lab.snapshot()[0]['baseline'])
        family=lab.snapshot()[0]['families']['eurusd-technical-grid']
        p={**self.protocol,'family':'eurusd-technical-grid','dataset':family['dataset'],'stage':'EXPLORATION',
           'window':['2025-02-01T00:00:00Z','2026-10-01T00:00:00Z'],'runner_sha256':'f'*64,
           'rights':{'permitted':True,'url':'https://example.test','scope':'synthetic'},
           'legacy':{**self.protocol['legacy'],'original_charge_alias':adapter.REF}}
        proof={'protocol_hash':p['hash'],'runner_sha256':p['runner_sha256'],'data_fingerprint':'synthetic-v1','paid_usd':0}
        for gate in GATES:proof[gate]={'qualified':True,'scope':'generated only','evidence_ids':['synthetic-gate']}
        proof['software'].update(reviewed=True,synthetic_tests_passed=True,challenge_passed=True)
        proof['resources'].update(bound_type='FULL_PROTOCOL_UPPER_BOUND',wall_seconds_upper_bound=1,
            memory_bytes_upper_bound=268435456,disk_bytes_upper_bound=1048576,input_bound_evidence='finite synthetic')
        with patch.object(adapter,'plan',return_value=p),patch.object(adapter,'check_inputs',return_value=self.claim):
            execution={'reservation_ref':adapter.REF,'frozen_commit':adapter.FROZEN_COMMIT,
                'reserved_look_never_executed':True,'no_printed_or_saved_outcome':True,
                'artifact_scopes_checked':['local','public_logs','remote_artifacts'],'evidence_ids':['synthetic-gate']}
            packet={'admission':proof,'original_execution':execution}
            with self.assertRaises(Refused):adapter.adopt(lab,self.root,{'admission':proof},ref_reader=lambda:self.fail('before source'))
            adapter.adopt(lab,self.root,packet,ref_reader=lambda:self.remote)
            with self.assertRaises(Refused):adapter.adopt(lab,self.root,packet,ref_reader=lambda:self.remote)
        lab.reserve(adapter.PROTOCOL,'synthetic-v1')
        s=lab.snapshot()[0]
        self.assertEqual(s['baseline'],before)
        self.assertEqual(s['looks']['look:'+adapter.PROTOCOL]['charged_paths'],6)
        self.assertEqual(s['protocols'][adapter.PROTOCOL]['legacy']['original_charge_alias'],adapter.REF)
        with self.assertRaises(Refused):lab.reserve(adapter.PROTOCOL,'other-vendor-data')


if __name__ == '__main__':unittest.main()
