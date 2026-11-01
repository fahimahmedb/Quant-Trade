"""Exercise real replacement/rollback and the original A67 branch validator."""
import ast
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import quant_host_rebind_preflight as ops
from research.research_os.expansion.v2_core import assert_authority_closed


class HostTransactionTests(unittest.TestCase):
    def metadata(self, paths):
        return {str(p): dict(uid=p.stat().st_uid,gid=p.stat().st_gid,mode=oct(p.stat().st_mode & 0o777)) for p in paths}

    def test_only_the_single_branch_value_changes_in_exact_original_json(self):
        value = dict(branch="old/ref", repository="fahimahmedb/Quant-Trade", release_sha="a"*40,
                     model_backend={"model":"unchanged-model","budget":{"max_calls":1}},
                     private_fixture="unchanged-private-value", **{k:False for k in ops.AUTHORITY})
        raw = (json.dumps(value, indent=4)+"\n").encode()
        spec = ("/fixture",ops.digest(raw),"a"*40,"old/ref")
        updated = ops.ref_only_bytes(raw,spec)
        self.assertEqual(updated,raw.replace(b'"old/ref"',b'"code/canonical"',1))
        self.assertEqual(json.loads(updated),dict(value,branch="code/canonical"))

    def test_successful_transaction_preserves_ownership_and_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths=[Path(tmp)/n for n in ("v1.json","v2.json","status")]
            for p in paths: p.write_bytes(b"before");os.chmod(p,0o640)
            meta=self.metadata(paths)
            ops.replace_transaction({p:b"before" for p in paths},{p:b"after" for p in paths},meta)
            for p in paths:
                self.assertEqual(p.read_bytes(),b"after")
                self.assertEqual(self.metadata([p])[str(p)],meta[str(p)])

    def test_failure_after_atomic_rename_restores_every_written_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a',Path(tmp)/'b'
            for p in (a,b): p.write_bytes(b"original");os.chmod(p,0o640)
            meta=self.metadata([a,b])
            def fail_after_replace(path,raw,metadata):
                ops.atomic_file(path,raw,metadata)
                if path==b: raise OSError("simulated crash after rename before return")
            with self.assertRaisesRegex(ops.Blocked,"ROLLBACK_COMPLETED"):
                ops.replace_transaction({a:b"original",b:b"original"},{a:b"new",b:b"new"},meta,write=fail_after_replace)
            self.assertEqual((a.read_bytes(),b.read_bytes()),(b"original",b"original"))
            self.assertEqual(self.metadata([a,b]),meta)

    def test_rollback_preserves_a_concurrent_owner_edit(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a',Path(tmp)/'b'
            for p in (a,b): p.write_bytes(b"original")
            def owner_edits_then_failure(path,raw,metadata):
                if path==b:
                    a.write_bytes(b"owner-newer-edit")
                    raise OSError("intervening owner change")
                ops.atomic_file(path,raw,metadata)
            with self.assertRaisesRegex(ops.Blocked,"OWNER_EDIT_PRESERVED"):
                ops.replace_transaction({a:b"original",b:b"original"},{a:b"new",b:b"new"},
                                        self.metadata([a,b]),write=owner_edits_then_failure)
            self.assertEqual(a.read_bytes(),b"owner-newer-edit")
            self.assertEqual(b.read_bytes(),b"original")

    def test_source_drift_and_symlinks_block_before_replacement(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'config';p.write_bytes(b"owner-newer")
            with self.assertRaisesRegex(ops.Blocked,"TARGET_CHANGED_BEFORE"):
                ops.replace_transaction({p:b"old"},{p:b"new"},self.metadata([p]))
            link=Path(tmp)/'link';link.symlink_to(p)
            with self.assertRaisesRegex(ops.Blocked,"SYMLINK_DESTINATION"):
                ops.atomic_file(link,b"replace",self.metadata([p])[str(p)])
            self.assertEqual(p.read_bytes(),b"owner-newer")

    def test_newer_owner_permission_change_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'config';p.write_bytes(b'unchanged-bytes');p.chmod(0o640)
            before=self.metadata([p]);p.chmod(0o600)
            with self.assertRaisesRegex(ops.Blocked,'TARGET_CHANGED_BEFORE'):
                ops.replace_transaction({p:b'unchanged-bytes'},{p:b'new'},before)
            self.assertEqual(p.stat().st_mode & 0o777,0o600)
            self.assertEqual(p.read_bytes(),b'unchanged-bytes')

    def test_no_argument_status_control_cannot_accept_caller_options(self):
        with tempfile.TemporaryDirectory() as tmp:
            wrapper=Path(tmp)/'status';wrapper.write_bytes(ops.status_wrapper());wrapper.chmod(0o700)
            result=subprocess.run([str(wrapper),"--activate"],capture_output=True)
            self.assertEqual(result.returncode,64)
            self.assertEqual(result.stdout,b"")

    def original_validator(self):
        raw=subprocess.check_output(['git','show','a67ffec48fff895d5edc42171855e2213e49cf0d:deploy/oracle_v2_deploy.py'])
        self.assertEqual(ops.digest(raw),ops.SOURCE_HASHES['deploy/oracle_v2_deploy.py'])
        node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name=='validate_config')
        namespace=dict(validate_sha=lambda v:v,_require_v2_config=lambda c:None,
                       assert_authority_closed=assert_authority_closed,Path=Path,
                       STATE=Path('/var/lib/quant-research-v2'),BRANCH='builder/oracle-v2-core-20261020',
                       _validate_release_receipt=lambda r,s:r,json=json,backend_from_config=lambda c:object())
        exec(compile(ast.Module(body=[node],type_ignores=[]),'original-a67-validator','exec'),namespace)
        return raw,namespace['validate_config']

    def run_status_adapter(self,config):
        original_source,validator=self.original_validator()
        core=Path(ops.CORE)
        original=ModuleType('deploy.oracle_v2_deploy')
        original.BRANCH='builder/oracle-v2-core-20261020'
        original.CONFIG=Path('/fixture/worker.json')
        original.CURRENT=SimpleNamespace(resolve=lambda:core)
        original.validate_config=validator
        calls=[]
        def status(value): calls.append(copy.deepcopy(value));return {'status':'FIXTURE_READ_ONLY_STATUS'}
        original.status=status
        package=ModuleType('deploy');package.oracle_v2_deploy=original
        def read_text(path,*a,**kw):
            if path==original.CONFIG: return json.dumps(config)
            if path==core/'.quant_release_receipt.json':return json.dumps({'path':str(core)})
            raise AssertionError(str(path))
        command=shlex.split(ops.status_wrapper().decode().split('exec ',1)[1])
        python_code=command[-1]
        out=io.StringIO()
        with patch.dict(sys.modules,{'deploy':package,'deploy.oracle_v2_deploy':original}), \
                patch.object(Path,'read_text',read_text),patch.object(Path,'read_bytes',return_value=original_source), \
                patch.object(os,'geteuid',return_value=0),patch.object(os,'chdir'), \
                patch.object(sys,'argv',['-c']),patch.object(sys,'path',list(sys.path)),contextlib.redirect_stdout(out):
            exec(compile(python_code,'fixed-status-adapter','exec'),{})
        return calls,json.loads(out.getvalue())

    def config(self):
        return dict(branch='code/canonical',repository='fahimahmedb/Quant-Trade',cache='/var/lib/quant-research-v2/github.git',
                    release_sha='a67ffec48fff895d5edc42171855e2213e49cf0d',lane='auto',
                    model_backend={'implementation':'gpt_oss'},**{k:False for k in ops.AUTHORITY})

    def test_reproduces_old_control_failure_and_adapts_only_its_branch_validation(self):
        _,old=self.original_validator()
        with self.assertRaisesRegex(ValueError,'V2_CANONICAL_CONFIG_REQUIRED'):
            old(self.config())
        config=self.config();copy_before=copy.deepcopy(config)
        calls,result=self.run_status_adapter(config)
        self.assertEqual(calls,[config])
        self.assertEqual(config,copy_before)
        self.assertEqual(result['state_branch'],'code/canonical')

    def test_status_adapter_rejects_wrong_branch_release_and_open_authority(self):
        for key,value in [('branch','foreign/ref'),('release_sha','b'*40),('live_trading_authorized',True),('lane','foreign')]:
            config=self.config();config[key]=value
            with self.subTest(key=key),self.assertRaises((AssertionError,ValueError)):
                self.run_status_adapter(config)

    def test_scope_can_isolate_v2_from_an_unresolved_v1_fallback(self):
        self.assertEqual(set(ops.selected_specs('v2')),{'v2'})
        self.assertEqual(set(ops.selected_specs('v1')),{'v1'})
        with self.assertRaises(ops.Blocked):ops.selected_specs('foreign')

    def witness_fixture(self):
        timer=dict(ActiveState='active',UnitFileState='enabled',LastTriggerUSecMonotonic='2000000')
        service=dict(Result='success',ExecMainStatus='0',InvocationID='a'*32,ExecMainStartTimestampMonotonic='2000010')
        value=dict(status='NOOP_FRONTIER_EXHAUSTED',release_sha=ops.CONFIGS['v2'][2],
                   state_branch='code/canonical',input_head='b'*40,hosted_model_calls=0,writes=0,
                   authority={k:False for k in ops.AUTHORITY})
        rows=[{'_SYSTEMD_INVOCATION_ID':'a'*32,'__REALTIME_TIMESTAMP':'100000000', 'MESSAGE':json.dumps(value)}]
        receipt=dict(applied_monotonic_us=1000000,observed_automatic_wakes=[])
        return timer,service,value,rows,receipt

    def test_automatic_wake_requires_timer_service_and_journal_causal_match(self):
        timer,service,value,rows,receipt=self.witness_fixture()
        witness=ops.automatic_wake(timer,service,rows,receipt)
        self.assertEqual(witness['invocation_id'],'a'*32)
        for key,invalid in [('ExecMainStartTimestampMonotonic','12000001'),('InvocationID','c'*32),('Result','exit-code')]:
            candidate=dict(service,**{key:invalid})
            with self.subTest(key=key):
                self.assertIsNone(ops.automatic_wake(timer,candidate,rows,receipt))
        self.assertIsNone(ops.automatic_wake(dict(timer,LastTriggerUSecMonotonic='900000'),service,rows,receipt))
        self.assertIsNone(ops.automatic_wake(dict(timer,LastTriggerUSecMonotonic=''),service,rows,receipt))

    def test_old_branch_invalid_head_wrong_release_or_dryrun_never_count(self):
        timer,service,value,rows,receipt=self.witness_fixture()
        for key,invalid in [('state_branch','builder/oracle-v2-core-20261020'),('release_sha','c'*40),
                            ('input_head','unverified-head'),('status','DRY_RUN'),('hosted_model_calls',1)]:
            candidate=dict(value,**{key:invalid})
            with self.subTest(key=key):
                self.assertIsNone(ops.automatic_wake(timer,service,[dict(rows[0],MESSAGE=json.dumps(candidate))],receipt))
        candidate=copy.deepcopy(value);candidate['authority']['live_trading_authorized']=True
        self.assertIsNone(ops.automatic_wake(timer,service,[dict(rows[0],MESSAGE=json.dumps(candidate))],receipt))

    def test_duplicate_invocation_or_same_timer_trigger_cannot_be_two_wakes(self):
        timer,service,value,rows,receipt=self.witness_fixture()
        first=ops.automatic_wake(timer,service,rows,receipt)
        self.assertTrue(ops.append_automatic_witness(receipt,first))
        self.assertFalse(ops.append_automatic_witness(receipt,copy.deepcopy(first)))
        self.assertFalse(ops.append_automatic_witness(receipt,dict(first,invocation_id='c'*32)))
        self.assertTrue(ops.append_automatic_witness(receipt,dict(first,invocation_id='d'*32,timer_trigger_monotonic_us=602000000)))
        self.assertFalse(ops.append_automatic_witness(receipt,dict(first,invocation_id='e'*32,timer_trigger_monotonic_us=1202000000)))
        self.assertEqual(len(receipt['observed_automatic_wakes']),2)

    def test_post_rebind_control_failure_restores_both_configs_and_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);directory=base/'backup';directory.mkdir()
            status=base/'status';status.write_bytes(b'old-fixed-control')
            specs={}
            paths=[status]
            for flavor in ('v1','v2'):
                p=base/(flavor+'.json')
                value=dict(branch='old/'+flavor,repository='fahimahmedb/Quant-Trade',release_sha='a'*40,
                           **{k:False for k in ops.AUTHORITY})
                raw=(json.dumps(value,indent=2)+'\n').encode();p.write_bytes(raw);p.chmod(0o640)
                specs[flavor]=(str(p),ops.digest(raw),'a'*40,'old/'+flavor);paths.append(p)
            originals={p:p.read_bytes() for p in paths}
            meta=self.metadata(paths);timer={'ActiveState':'active','UnitFileState':'enabled','InvocationID':'timer-fixed'}
            pre=dict(status='PASS_BACKUP_AND_READ_ONLY_COMPATIBILITY',backup_directory=str(directory),
                     backup_file_metadata=meta,backup_sha256={str(p):ops.digest(p.read_bytes()) for p in paths},
                     timer_before=timer,v1_timer_before=timer,boot_id='boot-fixed',release_signatures={})
            failure=SimpleNamespace(returncode=1,stdout='private-output-not-to-publish',stderr='private-error-not-to-publish')
            with patch.object(os,'geteuid',return_value=0),patch.object(os,'fchown'), \
                    patch.object(ops,'worker_lock',side_effect=contextlib.nullcontext), \
                    patch.object(ops,'execute',return_value=pre),patch.object(ops,'CONFIGS',specs), \
                    patch.object(ops,'release_signatures',return_value={}), \
                    patch.object(ops,'STATUS_PATH',status), \
                    patch.object(ops,'ORIGINAL_STATUS_SHA256',ops.digest(originals[status])), \
                    patch.object(ops,'checked_bytes',side_effect=lambda p:Path(p).read_bytes()), \
                    patch.object(ops,'unit_state',return_value=timer),patch.object(subprocess,'run',return_value=failure) as process:
                result=ops.apply_binding('c'*40,'both')
            self.assertEqual(result['status'],'BLOCK_ROLLED_BACK')
            self.assertEqual({p:p.read_bytes() for p in paths},originals)
            self.assertEqual(self.metadata(paths),meta)
            self.assertNotIn('private-output',json.dumps(result))
            self.assertNotIn('private-error',json.dumps(result))
            self.assertEqual(process.call_args.args[0],[str(status)])


if __name__=='__main__':unittest.main()
