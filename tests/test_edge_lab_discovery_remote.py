"""Real Git CAS for Discovery; synthetic empty queue, never market data."""
import copy
import unittest
from pathlib import Path
import test_edge_lab_remote as fixture
from quant.edge_lab.remote import DiscoveryAuthority
from quant.edge_lab.store import Refused,event
from quant.edge_lab.discovery import save,load
from quant.state import write_json
from quant.edge_lab.seed import BRANCH

class DiscoveryRemoteTest(unittest.TestCase):
    git=fixture.RemoteTest.git
    setUp=fixture.RemoteTest.setUp
    tearDown=fixture.RemoteTest.tearDown

    def prepare(self):
        self.d=self.directory/'discovery'
        save(self.d,{'schema':1,'mode':'DISCOVERY_FIRST','policy_version':'4.2','queue':[],
             'closed_families':[],'metrics':{},'events':[],'real_capital_authorized':False,'live_trading_authorized':False})
        self.git(self.first,'add','research/edge_lab/discovery/STATE.json')
        self.git(self.first,'commit','-m','synthetic Discovery')
        self.git(self.first,'push','origin',BRANCH)
        self.git(self.second,'pull','--ff-only')
        return DiscoveryAuthority(self.first,self.directory),DiscoveryAuthority(self.second,self.second/'research/edge_lab')

    def test_two_hosts_cannot_publish_the_same_parent(self):
        a,b=self.prepare();x,y=a.snapshot(),b.snapshot()
        first=copy.deepcopy(x['discovery']);event(first,'SYNTHETIC_CLAIM',{'host':'first'})
        winner=a.claim(first,x['sha'])
        second=copy.deepcopy(y['discovery']);event(second,'SYNTHETIC_CLAIM',{'host':'second'})
        with self.assertRaises(Refused):b.claim(second,y['sha'])
        self.assertEqual(a.snapshot()['sha'],winner)
        self.assertEqual(a.snapshot()['state'],x['state'])

    def test_pause_reads_no_discovery_or_runner_body(self):
        a,_=self.prepare();control=a.snapshot()['control'];control['paused']=True
        write_json(self.directory/'CONTROL.json',control)
        (self.d/'STATE.json').write_text('{corrupt discovery must not be read')
        self.git(self.first,'add','research/edge_lab/CONTROL.json','research/edge_lab/discovery/STATE.json')
        self.git(self.first,'commit','-m','synthetic Owner pause');self.git(self.first,'push','origin',BRANCH)
        snap=a.snapshot();self.assertTrue(snap['control']['paused']);self.assertIsNone(snap['discovery']);self.assertEqual(snap['code_versions'],{})

    def test_new_owner_pause_rejects_stale_claim(self):
        a,b=self.prepare();fresh=a.snapshot();control=b.snapshot()['control'];control['paused']=True
        write_json(b.directory/'CONTROL.json',control);self.git(self.second,'add','research/edge_lab/CONTROL.json')
        self.git(self.second,'commit','-m','synthetic Owner pause');self.git(self.second,'push','origin',BRANCH)
        old=copy.deepcopy(fresh['discovery']);event(old,'SYNTHETIC_CLAIM',{})
        with self.assertRaises(Refused):a.claim(old,fresh['sha'])
        self.assertTrue(a.snapshot()['control']['paused'])
