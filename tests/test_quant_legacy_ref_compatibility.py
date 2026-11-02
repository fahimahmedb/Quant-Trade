"""Frozen, offline witness: actual F394/A67 workers read canonical state.

The transport is a local bare Git fixture. This is compatibility evidence for
these exact historical bytes/snapshots, never an Oracle/runtime/E2E claim.
"""
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

from scripts import quant_host_rebind_preflight as ops

CANONICAL = "a9876c732cb88bd4383aacc433d0d2cba2feaeb5"
V2_SNAPSHOT = "71e3f28d1e162152c93931b15cef993af6199632"


class LegacyRefCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(__file__).resolve().parents[1]
        cls.temp = tempfile.TemporaryDirectory(prefix="quant-frozen-ref-proof-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.base = Path(cls.temp.name)
        cls.remote = cls.base / "remote.git"
        subprocess.run(["git","clone","--bare","--shared",str(cls.repo),str(cls.remote)],
                       check=True,capture_output=True,timeout=30)
        for branch,sha in (("code/canonical",CANONICAL),("builder/oracle-v2-core-20261020",V2_SNAPSHOT)):
            subprocess.run(["git","--git-dir="+str(cls.remote),"update-ref","refs/heads/"+branch,sha],
                           check=True,capture_output=True,timeout=10)
        for flavor,spec in ops.CONFIGS.items():
            release=cls.base/flavor; release.mkdir()
            raw=subprocess.check_output(["git","archive",spec[2],"research","deploy"],cwd=cls.repo,timeout=30)
            with tarfile.open(fileobj=io.BytesIO(raw)) as stream: stream.extractall(release,filter="data")
            config=dict(repository="fahimahmedb/Quant-Trade",branch=spec[3],cache=str(cls.base/(flavor+"-cache.git")),
                        release_sha=spec[2],lane="auto",worker_id="oracle-research-v2",research_contract_version="v2-core",
                        model_backend={"model":"gpt-oss-10.2b-q4-k-m"},**{key:False for key in ops.AUTHORITY})
            (cls.base/(flavor+".json")).write_text(json.dumps(config))

    def prove(self,flavor):
        setup='''
import sys
sys.path.insert(0,sys.argv[1])
import research.research_os.github_state as fixture
Native=fixture.GitHubStateStore
class FixtureStore(Native):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.remote=LOCAL_REMOTE
    def _git(self,*args,**kwargs):
        if args and args[0]=='push':raise AssertionError('TEST_REMOTE_PUSH_FORBIDDEN')
        if any(str(arg).startswith(('https://','http://')) for arg in args):
            raise AssertionError('TEST_NETWORK_ACCESS_FORBIDDEN')
        return super()._git(*args,**kwargs)
fixture.GitHubStateStore=FixtureStore
'''.replace('LOCAL_REMOTE',repr(self.remote.as_uri()))
        child=subprocess.run([sys.executable,"-I","-B","-c",setup+"\n"+ops.PROBE,
                              str(self.base/flavor),str(self.base/(flavor+".json")),flavor],
                             capture_output=True,text=True,timeout=90)
        self.assertEqual(child.returncode,0,child.stderr[-3000:])
        value=json.loads(child.stdout)
        ops.validate_probe(value,CANONICAL,v2=flavor=="v2")
        self.assertEqual(value['task_count'],72)
        self.assertEqual(value['model_calls'],0)
        self.assertEqual(value['writes'],0)
        return value

    def test_original_f394_fallback_can_read_frozen_canonical_queue_without_work(self):
        self.prove('v1')

    def test_original_a67_worker_preserves_72_live_task_blobs_and_v2_policy(self):
        value=self.prove('v2')
        self.assertTrue(value['same_tasks_as_live_v2'])
        self.assertEqual(value['v2_preflight'],'PASS')

    def test_real_snapshot_rollback_probe_rejects_retired_old_ref(self):
        before=self.prove('v2')
        setup='''
import sys
sys.path.insert(0,sys.argv[1])
import research.research_os.github_state as fixture
Native=fixture.GitHubStateStore
class FixtureStore(Native):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.remote=LOCAL_REMOTE
    def _git(self,*args,**kwargs):
        if args and args[0]=='push':raise AssertionError('TEST_REMOTE_PUSH_FORBIDDEN')
        if any(str(arg).startswith(('https://','http://')) for arg in args):raise AssertionError('TEST_NETWORK_ACCESS_FORBIDDEN')
        return super()._git(*args,**kwargs)
fixture.GitHubStateStore=FixtureStore
'''.replace('LOCAL_REMOTE',repr(self.remote.as_uri()))
        command=[sys.executable,'-I','-B','-c',setup+'\n'+ops.ROLLBACK_SNAPSHOT_PROBE,
                 str(self.base/'v2'),str(self.base/'v2.json'),'builder/oracle-v2-core-20261020','v2']
        result=subprocess.run(command,capture_output=True,text=True,timeout=90)
        self.assertEqual(result.returncode,0,result.stderr)
        ops.validate_rollback_surface(before,json.loads(result.stdout),v2=True)
        ref='refs/heads/builder/oracle-v2-core-20261020'
        subprocess.run(['git','--git-dir='+str(self.remote),'update-ref','-d',ref],check=True)
        try:
            result=subprocess.run(command,capture_output=True,text=True,timeout=90)
            self.assertNotEqual(result.returncode,0)
        finally:
            subprocess.run(['git','--git-dir='+str(self.remote),'update-ref',ref,V2_SNAPSHOT],check=True)


if __name__=='__main__':unittest.main()
