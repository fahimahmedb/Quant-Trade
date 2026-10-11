"""Full idea/test/decision transitions use generated receipts, never market data."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from quant.edge_lab.contracts import VERDICT_FIELDS
from quant.edge_lab.store import Refused
import tests.test_edge_lab as fixtures


class WorkflowTest(fixtures.LabTest):
    # Reuse setup/helpers, not the inherited collection of existing tests.
    def synthetic_result(self, kind):
        self.protocol.pop('purpose', None)
        code = '''import json,sys
from pathlib import Path
s=json.loads(Path('research/edge_lab/STATE.json').read_text())
p=s['protocols'][sys.argv[-3]];l=s['looks'][sys.argv[-1]]
r={'look_id':l['id'],'kind':KIND,'nature':NATURE,
 'protocol_hash':p['hash'],'data_fingerprint':l['data_fingerprint'],
 'primary':p['primary'],'benchmark':'synthetic zero','observations':{'synthetic_days':2},
 'uncertainty':'generated software fixture, no economic inference',
 'risk_exposures':{'synthetic_only':True},'capacity':'not estimated; synthetic',
 'net_after_costs':{'fixture':0},'lesson':'preserve fixture disposition',
 'next_decision':'synthetic next gate',
 'expression_results':{e:{c:{'fixture':0} for c in p['cost_paths']} for e in p['expressions']},
 'verdict':{k:'synthetic fixture' for k in FIELDS}}
print(json.dumps(r))
'''.replace('KIND', repr(kind)).replace('NATURE', repr({'SOURCE_UNUSABLE':'SOURCE_FAILURE',
    'INVALID_SOFTWARE':'SOFTWARE_FAILURE','PROSPECTIVE_OBSERVATION':'PROSPECTIVE_OBSERVATION'}.get(kind,'EXPLORATORY_BACKTEST'))).replace('FIELDS', repr(VERDICT_FIELDS))
        self.runner.write_text(code)
        self.protocol['runner_sha256'] = hashlib.sha256(self.runner.read_bytes()).hexdigest()
        self.frozen()
        self.lab.reserve('fixture-p', 'fixture-data')
        return self.lab.execute('fixture-p', self.repo, self.authority, lambda s, sha: 'b'*40)

    def test_positive_receipt_has_nine_fields_and_requires_new_validation(self):
        receipt = self.synthetic_result('POSITIVE_EXPLORATORY')
        self.assertEqual(set(receipt['result']['verdict']), set(VERDICT_FIELDS))
        identity = 'result:look:fixture-p'
        claim = self.lab.claim_decision(identity, 'synthetic-review')
        self.lab.decide(identity, 'QUALIFIED', ['look:fixture-p'], 'independent validation gate', claim)
        s, _ = self.lab.snapshot()
        self.assertEqual(s['families']['fixture']['status'], 'VALIDATION_REQUIRED')
        self.assertFalse(s['live_trading_authorized'])
        self.assertEqual(s['trial_charges']['fixture-data'], 4)

    def test_negative_receipt_closes_exact_family_and_preserves_cost_paths(self):
        self.synthetic_result('NEGATIVE')
        identity = 'result:look:fixture-p'
        claim = self.lab.claim_decision(identity, 'synthetic-review')
        with self.assertRaises(Refused):
            self.lab.decide(identity, 'QUALIFIED', ['look:fixture-p'], 'wrong promotion', claim)
        self.lab.decide(identity, 'REJECTED', ['look:fixture-p'], 'retain exact rejection', claim)
        self.assertEqual(self.lab.snapshot()[0]['families']['fixture']['status'], 'REJECTED_CLOSED')
        self.assertEqual(self.lab.snapshot()[0]['looks']['look:fixture-p']['charged_paths'], 4)

    def test_source_receipt_is_wait_and_cannot_be_economic_rejection(self):
        self.synthetic_result('SOURCE_UNUSABLE')
        identity = 'result:look:fixture-p'; claim = self.lab.claim_decision(identity, 'synthetic-review')
        with self.assertRaises(Refused):
            self.lab.decide(identity, 'REJECTED', ['look:fixture-p'], 'false rejection', claim)
        self.lab.decide(identity, 'WAIT', ['look:fixture-p'], 'wait distinct source', claim)
        self.assertEqual(self.lab.snapshot()[0]['families']['fixture']['status'], 'BLOCKED_DATA_ACCESS')

    def test_partial_print_is_saved_exactly_and_cannot_be_replayed(self):
        self.runner.write_text('import sys\nprint("partial fixture",flush=True)\nsys.exit(2)\n')
        self.protocol['runner_sha256'] = hashlib.sha256(self.runner.read_bytes()).hexdigest()
        self.frozen(); self.lab.reserve('fixture-p', 'fixture-data')
        receipt = self.lab.execute('fixture-p', self.repo, self.authority, lambda s, sha:'b'*40)
        s, _ = self.lab.snapshot(); a=s['jobs']['execute:fixture-p']['metadata']['artifacts']
        self.assertEqual(Path(a['stdout']).read_bytes(), b'partial fixture\n')
        self.assertEqual(s['looks']['look:fixture-p']['status'], 'UNKNOWN_OUTCOME')
        self.assertIsNone(receipt['result'])
        with self.assertRaises(Refused):self.lab.execute('fixture-p', self.repo, self.authority, lambda s, sha:'b'*40)

    def test_unqualified_resources_and_missing_admission_do_not_charge(self):
        self.lab.freeze(self.protocol)
        with self.assertRaises(Refused): self.lab.reserve('fixture-p', 'fixture-data')
        p=self.admission_packet();p['resources']['bound_type']='PARTIAL_BENCHMARK'
        with self.assertRaises(Refused):self.lab.admit('fixture-p',p)
        self.assertEqual(self.lab.snapshot()[0]['looks'],{})

    def test_only_one_active_experiment_and_remote_runner_must_match(self):
        self.frozen();self.lab.reserve('fixture-p','fixture-data')
        self.protocol['id']='second';self.lab.freeze(self.protocol)
        self.lab.admit('second',self.admission_packet())
        with self.assertRaises(Refused):self.lab.reserve('second','fixture-data')
        self.protocol['id']='fixture-p'
        remote=self.authority();remote['runner_versions']={}
        with self.assertRaises(Refused):self.lab.execute('fixture-p',self.repo,lambda:remote,lambda s,sha:'b'*40)

    def test_saved_partial_receipt_reconciles_after_cas_failure_without_execution_or_new_charge(self):
        from quant.edge_lab.engine import Lab, initialize
        from quant.edge_lab.store import event
        from quant.state import write_json
        self.runner.write_text('print("printed partial fixture",flush=True)\nraise RuntimeError("fixture")\n')
        self.protocol['runner_sha256']=hashlib.sha256(self.runner.read_bytes()).hexdigest()
        self.frozen();self.lab.reserve('fixture-p','fixture-data')
        saved={}
        def publish(state,sha):
            if not saved:
                saved['state']=copy.deepcopy(state)
                return 'b'*40
            raise Refused('simulated later Owner commit')
        receipt=self.lab.execute('fixture-p',self.repo,self.authority,publish)
        self.assertEqual(receipt['publication'],'PENDING_RECONCILIATION')
        original=self.lab.snapshot()[0]
        raw=Path(original['jobs']['execute:fixture-p']['metadata']['artifacts']['receipt']).parent
        freshdir=self.repo/'fresh/research/edge_lab';initialize(freshdir)
        fresh=Lab(freshdir)
        # A real caller hydrates the new remote state into a distinct checkout.
        # Here the initial file is removed only in this synthetic temporary fixture.
        fresh.store.state_path.unlink()
        s=saved['state'];s['looks']['look:fixture-p']['status']='UNKNOWN_OUTCOME'
        s['jobs']['execute:fixture-p']['status']='UNKNOWN_OUTCOME'
        event(s,'SYNTHETIC_QUARANTINE',{'look':'look:fixture-p'})
        fresh.store.save(s)
        def authority():
            state,control=fresh.snapshot()
            return {'state':state,'control':control,'sha':'c'*40,'branch':fixtures.BRANCH}
        with patch('subprocess.run',side_effect=AssertionError('reconciliation must not execute')):
            result=fresh.reconcile('fixture-p',raw,authority,lambda state,sha:'d'*40)
            again=fresh.reconcile('fixture-p',raw,authority,lambda state,sha:self.fail('no duplicate publication'))
        self.assertEqual(result['publication'],'RECONCILED')
        self.assertEqual(again['publication'],'ALREADY_RECORDED')
        final=fresh.snapshot()[0]
        self.assertEqual(final['looks']['look:fixture-p']['status'],'UNKNOWN_OUTCOME')
        self.assertEqual(final['trial_charges']['fixture-data'],4)
        self.assertTrue(final['jobs']['execute:fixture-p']['metadata']['process_stopped'])

    def test_fully_printed_result_survives_later_process_failure(self):
        self.runner.write_text('import json,sys\nprint(json.dumps({"look_id":sys.argv[-1],"kind":"SOFTWARE_CHECK"}),flush=True)\nsys.exit(2)\n')
        self.protocol['runner_sha256']=hashlib.sha256(self.runner.read_bytes()).hexdigest()
        self.frozen();self.lab.reserve('fixture-p','fixture-data')
        receipt=self.lab.execute('fixture-p',self.repo,self.authority,lambda state,sha:'b'*40)
        self.assertEqual(receipt['result']['kind'],'SOFTWARE_CHECK')
        self.assertEqual(receipt['error'],'CalledProcessError')
        self.assertEqual(self.lab.snapshot()[0]['looks']['look:fixture-p']['status'],'COMPLETED_SPENT')

    def test_disabled_scheduler_receipt_cannot_be_reenabled_by_tick_metadata(self):
        state,_=self.lab.snapshot()
        self.lab.scheduler_disabled({'id':state['scheduler']['id'],'enabled':False,
            'observed_at':'2026-10-11T00:11:00Z','evidence_id':self.packet['id']})
        with self.assertRaises(Refused):self.lab.tick(actor='synthetic',enabled_confirmed=True)
        self.assertFalse(self.lab.snapshot()[0]['scheduler']['enabled'])


# Helpers inherited from LabTest are needed; avoid rerunning its existing tests here.
for name in dir(fixtures.LabTest):
    if name.startswith('test_') and name not in WorkflowTest.__dict__:
        setattr(WorkflowTest, name, None)


if __name__ == '__main__': unittest.main()
