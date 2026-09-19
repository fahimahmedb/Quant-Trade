from __future__ import annotations
import json, os, signal, subprocess, sys, tempfile, textwrap, unittest, urllib.error
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from quant.dataplane.sec_form4 import (
    _sha256_bytes,acceptance_header_url_candidates,load_acceptance_checkpoint,
    resolve_acceptance_documents,validate_acceptance_cache,
)

ACC='0000000101-24-000001'
ISS={ACC:'0000000001'}
OWN={ACC:('0000000101',)}

def sgml(acc=ACC, issuer='1', owners=('101',), stamp='20240103120000'):
    ors='\n'.join(f'REPORTING-OWNER:\n OWNER DATA:\n  CENTRAL INDEX KEY: {int(c):010d}' for c in owners)
    return f'<SEC-HEADER>\n<ACCEPTANCE-DATETIME>{stamp}\nACCESSION NUMBER: {acc}\nCONFORMED SUBMISSION TYPE: 4\n{ors}\nISSUER:\n COMPANY DATA:\n  CENTRAL INDEX KEY: {int(issuer):010d}\n</SEC-HEADER>'.encode()

class Fetcher:
    def __init__(self,payload=None): self.payload=payload or sgml(); self.calls=[]
    def __call__(self,url): self.calls.append(url); return self.payload

class ResolverIntegrityTests(unittest.TestCase):
    def test_issuer_archive_candidate_precedes_owner_fallback(self):
        urls=acceptance_header_url_candidates(ACC,'1',['101']);self.assertIn('/1/',urls[0]);self.assertIn('/101/',urls[1])
    def test_legacy_cache_is_semantically_revalidated_without_network(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);cache=base/'cache';cache.mkdir();(cache/f'{ACC}.html').write_bytes(sgml());f=Fetcher()
            got,fail=resolve_acceptance_documents([ACC],ISS,cache_dir=cache,checkpoint_path=base/'cp.jsonl',fetcher=f,rate_per_second=1000,owner_ciks_of=OWN)
            self.assertFalse(fail);self.assertEqual([],f.calls);self.assertEqual('2024-01-03T12:00:00',got[ACC]['acceptance_time'])
    def test_poisoned_legacy_cache_is_refetched(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);cache=base/'cache';cache.mkdir();(cache/f'{ACC}.html').write_bytes(sgml(issuer='2'));f=Fetcher(sgml())
            got,fail=resolve_acceptance_documents([ACC],ISS,cache_dir=cache,checkpoint_path=base/'cp.jsonl',fetcher=f,rate_per_second=1000,owner_ciks_of=OWN)
            self.assertFalse(fail);self.assertEqual(1,len(f.calls));self.assertEqual(_sha256_bytes(sgml()),_sha256_bytes((cache/f'{ACC}.html').read_bytes()))
    def test_checkpoint_semantics_are_recomputed_from_raw_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);cache=base/'cache';cache.mkdir();raw=sgml();(cache/f'{ACC}.html').write_bytes(raw);cp=base/'cp.jsonl'
            cp.write_text(json.dumps({'accession':ACC,'url':'u','sha256':'x','bytes':1,'acceptance_time':'2099'})+'\n')
            good,stale=validate_acceptance_cache(load_acceptance_checkpoint(cp),cache,{ACC:{'issuer_cik':'1','owner_ciks':['101'],'form_type':'4'}})
            self.assertFalse(stale);self.assertEqual(_sha256_bytes(raw),good[ACC]['sha256']);self.assertEqual('2024-01-03T12:00:00',good[ACC]['acceptance_time'])
    def test_404_archive_candidate_falls_back(self):
        calls=[]
        def fetch(url):
            calls.append(url)
            if '/1/' in url: raise urllib.error.HTTPError(url,404,'missing',{},None)
            return sgml()
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);got,fail=resolve_acceptance_documents([ACC],ISS,cache_dir=base/'cache',checkpoint_path=base/'cp',fetcher=fetch,rate_per_second=1000,owner_ciks_of=OWN)
            self.assertFalse(fail);self.assertEqual(2,len(calls));self.assertIn(ACC,got)
    def test_torn_tail_repair_then_append_then_reload(self):
        with tempfile.TemporaryDirectory() as d:
            cp=Path(d)/'cp';cp.write_text(json.dumps({'accession':'A'})+'\n{"accession":"B"');self.assertEqual(['A'],list(load_acceptance_checkpoint(cp)))
            with cp.open('a') as h:h.write(json.dumps({'accession':'C'})+'\n')
            self.assertEqual({'A','C'},set(load_acceptance_checkpoint(cp)))

@unittest.skipUnless(hasattr(signal,'SIGKILL'),'requires SIGKILL')
class RealKillBoundaryTests(unittest.TestCase):
    def _kill_then_resume(self,phase,expect_network):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);child=base/'kill_child.py'
            child.write_text(textwrap.dedent(f'''\
                import os, signal, sys
                from pathlib import Path
                sys.path.insert(0,{str(ROOT/'src')!r})
                from quant.dataplane.sec_form4 import resolve_acceptance_documents
                ACC={ACC!r}; ISS={{ACC:'0000000001'}}; OWN={{ACC:('0000000101',)}}; PAY={sgml()!r}
                def fetch(url): return PAY
                def hook(phase,acc):
                    if phase=={phase!r}: os.kill(os.getpid(),signal.SIGKILL)
                b=Path({str(base)!r})
                resolve_acceptance_documents([ACC],ISS,cache_dir=b/'cache',checkpoint_path=b/'cp.jsonl',fetcher=fetch,rate_per_second=1000,owner_ciks_of=OWN,kill_hook=hook,batch_size=1)
            '''))
            proc=subprocess.run([sys.executable,str(child)],stdout=subprocess.PIPE,stderr=subprocess.PIPE);self.assertNotEqual(0,proc.returncode,proc.stderr.decode())
            f=Fetcher();got,fail=resolve_acceptance_documents([ACC],ISS,cache_dir=base/'cache',checkpoint_path=base/'cp.jsonl',fetcher=f,rate_per_second=1000,owner_ciks_of=OWN,batch_size=1)
            self.assertFalse(fail);self.assertIn(ACC,got);self.assertEqual(expect_network,len(f.calls));self.assertIn(ACC,load_acceptance_checkpoint(base/'cp.jsonl'))
    def test_kill_before_cache_write(self): self._kill_then_resume('before_cache_write',1)
    def test_kill_after_cache_write(self): self._kill_then_resume('after_cache_write',0)
    def test_kill_before_checkpoint_append(self): self._kill_then_resume('before_checkpoint_append',0)
    def test_kill_after_checkpoint_fsync(self): self._kill_then_resume('after_checkpoint_fsync',0)

if __name__=='__main__': unittest.main()
