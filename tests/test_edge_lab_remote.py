"""Real fast-forward conflicts across two clones of a temporary Git repository."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from quant.edge_lab.engine import initialize
from quant.edge_lab.remote import GitAuthority
from quant.edge_lab.seed import BRANCH
from quant.edge_lab.store import Refused, event


class RemoteTest(unittest.TestCase):
    def git(self, directory, *args):
        response = subprocess.run(["git", "-c", "user.name=fixture", "-c", "user.email=fixture@example.test", *args],
                                  cwd=directory, capture_output=True, text=True, check=True)
        return response.stdout.strip()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.bare = self.root / "origin.git"
        self.git(self.root, "init", "--bare", str(self.bare))
        self.first = self.root / "first"
        self.first.mkdir()
        self.git(self.first, "init", "-b", BRANCH)
        self.directory = self.first / "research/edge_lab"
        initialize(self.directory)
        self.git(self.first, "add", "research/edge_lab/STATE.json", "research/edge_lab/CONTROL.json")
        self.git(self.first, "commit", "-m", "synthetic initial state")
        self.git(self.first, "remote", "add", "origin", str(self.bare))
        self.git(self.first, "push", "-u", "origin", BRANCH)
        self.second = self.root / "second"
        self.git(self.root, "clone", "-b", BRANCH, str(self.bare), str(self.second))
        self.a = GitAuthority(self.first, self.directory)
        self.b = GitAuthority(self.second, self.second / "research/edge_lab")

    def tearDown(self):
        self.temp.cleanup()

    def test_only_one_host_can_publish_against_one_parent(self):
        first, second = self.a.snapshot(), self.b.snapshot()
        self.assertEqual(first["sha"], second["sha"])
        from quant.edge_lab.store import Store
        states = []
        for root in (self.directory, self.second / "research/edge_lab"):
            store = Store(root)
            with store.lock():
                state = store.read()
                event(state, "SYNTHETIC_CLAIM", {"host": str(root)})
                store.save(state)
                states.append(state)
        winner = self.a.claim(states[0], first["sha"])
        with self.assertRaises(Refused):
            self.b.claim(states[1], second["sha"])
        self.assertEqual(self.a.snapshot()["sha"], winner)

    def test_owner_pause_commit_cannot_be_overwritten(self):
        from quant.edge_lab.store import Store
        first = self.a.snapshot()
        Store(self.second / "research/edge_lab").pause(True, "fixture Owner pause")
        self.git(self.second, "add", "research/edge_lab/CONTROL.json", "research/edge_lab/STATE.json")
        self.git(self.second, "commit", "-m", "pause")
        self.git(self.second, "push", "origin", BRANCH)
        state = first["state"]
        store = Store(self.directory)
        with store.lock():
            event(state, "SYNTHETIC_STALE_CLAIM", {})
            store.save(state)
        with self.assertRaises(Refused):
            self.a.claim(state, first["sha"])
        self.assertTrue(self.a.snapshot()["control"]["paused"])

    def test_real_git_idea_to_positive_validation_gate_without_market(self):
        import hashlib
        import json
        from quant.edge_lab.engine import Lab
        from quant.edge_lab.contracts import GATES, VERDICT_FIELDS
        lab = Lab(self.directory)
        lab.evidence({'id':'synthetic-source','kind':'METHOD','url':'https://example.test/synthetic',
            'version':'v1','passage':'generated software fixture only','fact':'No market observations','limit':'No economic inference'})
        lab.family('synthetic-loop','generated software-only mechanism','synthetic-data',['synthetic-source'])
        code = '''import json,sys
from pathlib import Path
s=json.loads(Path('research/edge_lab/STATE.json').read_text())
p=s['protocols'][sys.argv[-3]];l=s['looks'][sys.argv[-1]]
Path('executed-once.txt').open('x').write('synthetic')
r={'look_id':l['id'],'kind':'POSITIVE_EXPLORATORY','nature':'EXPLORATORY_BACKTEST',
 'protocol_hash':p['hash'],'data_fingerprint':l['data_fingerprint'],'primary':p['primary'],
 'benchmark':'generated zero','observations':{'generated_days':2},'net_after_costs':{'generated':0},
 'uncertainty':'synthetic fixture','risk_exposures':'none; synthetic','capacity':'unestimated',
 'lesson':'software route only','next_decision':'independent execution/data validation, no live authority',
 'expression_results':{e:{c:{'synthetic':0} for c in p['cost_paths']} for e in p['expressions']},
 'verdict':{k:'synthetic only' for k in FIELDS}}
print(json.dumps(r))
'''.replace('FIELDS',repr(VERDICT_FIELDS))
        runner=self.first/'synthetic_runner.py';runner.write_text(code)
        protocol={'id':'synthetic-p','family':'synthetic-loop','dataset':'synthetic-data','stage':'EXPLORATION',
            'window':['2000-01-01T00:00:00Z','2000-02-01T00:00:00Z'],'expressions':['MAIN','CONTROL'],
            'cost_paths':['CENTRAL','STRESS'],'primary':'MAIN','mechanism':'generated','payer':'fixture',
            'clock':'causal generated UTC','independent_unit':'synthetic day','benchmark':'zero','costs':'generated',
            'rights':{'permitted':True,'url':'https://example.test','scope':'synthetic'},
            'decision_contract':{k:'synthetic disposition' for k in ('positive','negative','inconclusive','invalid')},
            'multiplicity_policy':'four dependent software paths','runner':'synthetic_runner.py',
            'runner_sha256':hashlib.sha256(runner.read_bytes()).hexdigest(),'evidence_ids':['synthetic-source']}
        lab.freeze(protocol)
        frozen=lab.snapshot()[0]['protocols']['synthetic-p']
        proof={'protocol_hash':frozen['hash'],'runner_sha256':protocol['runner_sha256'],'data_fingerprint':'synthetic-v1','paid_usd':0}
        for g in GATES:proof[g]={'qualified':True,'scope':'software only','evidence_ids':['synthetic-source']}
        proof['software'].update(reviewed=True,synthetic_tests_passed=True,challenge_passed=True)
        proof['resources'].update(bound_type='FULL_PROTOCOL_UPPER_BOUND',wall_seconds_upper_bound=1,
            memory_bytes_upper_bound=268435456,disk_bytes_upper_bound=1048576,input_bound_evidence='finite generated fixture')
        lab.admit('synthetic-p',proof)
        self.git(self.first,'add','research/edge_lab/STATE.json','synthetic_runner.py')
        self.git(self.first,'commit','-m','generated frozen runner and admission')
        self.git(self.first,'push','origin',BRANCH)
        parent=self.a.snapshot()['sha']
        lab.reserve('synthetic-p','synthetic-v1')
        self.a.claim(lab.snapshot()[0],parent)
        receipt=lab.execute('synthetic-p',self.first,self.a.snapshot,self.a.claim)
        self.assertEqual(receipt['result']['kind'],'POSITIVE_EXPLORATORY')
        identity='result:look:synthetic-p'
        parent=self.a.snapshot()['sha']
        claim=lab.claim_decision(identity,'synthetic-owner-review')
        self.a.claim(lab.snapshot()[0],parent)
        parent=self.a.snapshot()['sha']
        lab.decide(identity,'QUALIFIED',['look:synthetic-p'],'new independent gate only',claim)
        self.a.claim(lab.snapshot()[0],parent)
        final=self.a.snapshot()['state']
        published=self.a.snapshot()['sha']
        artifacts=final['jobs']['execute:synthetic-p']['metadata']['artifacts']
        relative=Path(artifacts['stdout']).relative_to(self.first).as_posix()
        self.assertEqual(self.git(self.first,'show',published+':'+relative),Path(artifacts['stdout']).read_text().strip())
        self.assertEqual(final['families']['synthetic-loop']['status'],'VALIDATION_REQUIRED')
        self.assertEqual(final['trial_charges']['synthetic-data'],4)
        self.assertFalse(final['live_trading_authorized'])
        with self.assertRaises(Refused):lab.execute('synthetic-p',self.first,self.a.snapshot,self.a.claim)
        self.assertEqual((self.first/'executed-once.txt').read_text(),'synthetic')


if __name__ == "__main__":
    unittest.main()
