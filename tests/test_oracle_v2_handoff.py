"""Real filesystem transaction tests with an explicit systemd/external-API double."""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

from deploy import oracle_v2_deploy as c
from deploy import oracle_v2_handoff as h
from deploy.oracle_v1_host_prepare import write_atomic as atomic

VERIFY_EFFECTIVE_UNIT = h.verify_effective_unit
QUALIFY_F3 = h.qualify_f3


class ActiveV2HandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.root = root
        self.old = root / 'releases' / ('a' * 40)
        self.new = root / 'releases' / ('b' * 40)
        self.old.mkdir(parents=True); self.new.mkdir()
        mapping = {'CONFIG':root/'etc/v2/worker.json', 'ROOT_QUALIFICATION':root/'etc/v2/proof.json',
                   'CURRENT':root/'opt/current', 'STATE':root/'state'}
        hmap = {'BACKUPS':root/'backups', 'ENV':root/'etc/v2/codex.env',
                'DROPIN':root/'systemd/service.d/90-codex-handoff.conf',
                'SHARED_ENV':root/'etc/v1/worker.env', 'V1_CONFIG':root/'etc/v1/worker.json',
                'WORKER_LOCK':root/'worker-lock', 'SYSTEMD':root/'systemd',
                'LIBEXEC':root/'libexec', 'SUDOERS':root/'sudoers',
                'ROOT_UID':os.getuid(), 'ROOT_GID':os.getgid()}
        for module, values in [(c,mapping),(h,hmap)]:
            for name,value in values.items():
                p=patch.object(module,name,value); p.start(); self.addCleanup(p.stop)
        for p in [c.CONFIG.parent,c.CURRENT.parent,c.STATE,h.BACKUPS,h.DROPIN.parent,h.SHARED_ENV.parent,h.LIBEXEC,h.WORKER_LOCK]:
            p.mkdir(parents=True,exist_ok=True)
        self.old_config={'release_sha':self.old.name,'vm_ocid':'fixture','branch':'code/canonical'}
        c.CONFIG.write_text(json.dumps(self.old_config)); c.CONFIG.chmod(0o640)
        c.ROOT_QUALIFICATION.write_bytes(b'old root proof'); c.ROOT_QUALIFICATION.chmod(0o600)
        h.SHARED_ENV.write_bytes(b'PRIVATE_FIXTURE=never-print-this\n'); h.SHARED_ENV.chmod(0o640)
        h.V1_CONFIG.write_bytes(b'unchanged-v1'); h.SUDOERS.write_bytes(b'unchanged-sudoers')
        c.CURRENT.symlink_to(self.old)
        self.legacy_dropin=h.DROPIN.parent/'50-native-live.conf'
        self.legacy_dropin.write_bytes(b'[Service]\n# original dropin\n')
        for u in [c.TIMER,c.SERVICE]: (h.SYSTEMD/u).write_bytes(b'original unit')
        for a in ['qualify','activate','status']: (h.LIBEXEC/('quant-v2-'+a)).write_bytes(b'original wrapper')
        self.states={u:dict(LoadState='loaded',ActiveState='inactive',UnitFileState='static',DropInPaths='')
                     for u in [c.TIMER,c.SERVICE,c.V1_TIMER,c.V1_SERVICE]}
        self.states[c.TIMER].update(ActiveState='active',UnitFileState='enabled')
        self.states[c.V1_TIMER]['UnitFileState']='disabled'
        self.states[c.SERVICE]['DropInPaths']=str(self.legacy_dropin)
        self.commands=[]
        self.query=patch.object(h,'query',side_effect=lambda u:deepcopy(self.states[u]));self.query.start();self.addCleanup(self.query.stop)
        def checked(argv):
            self.commands.append(argv)
            action=argv[1]
            for u in argv[2:]:
                if u not in self.states: continue
                if action=='stop': self.states[u]['ActiveState']='inactive'
                if action=='disable': self.states[u]['UnitFileState']='disabled'
                if action=='enable':
                    self.states[u]['UnitFileState']='enabled'
                    if '--now' in argv:self.states[u]['ActiveState']='active'
            return ''
        self.checked=checked
        def write(path,raw,mode=0o644,*,uid=None,gid=None):
            atomic(path,raw,mode,uid=os.getuid() if uid is None else uid,gid=os.getgid() if gid is None else gid)
        for name,side in [('checked',checked),('validate_config',lambda cfg:self.old.parent/cfg['release_sha']),
                          ('verify_ci',lambda cfg:None),('instance_identity',lambda vm:None),
                          ('backend_from_config',lambda cfg:Mock())]:
            p=patch.object(c,name,side_effect=side);p.start();self.addCleanup(p.stop)
        for name,side in [('write_atomic',write),('verify_effective_unit',lambda:None),
                          ('qualify_f3',lambda *a:dict(principal_verified=True,remote_writes=0))]:
            p=patch.object(h,name,side_effect=side);p.start();self.addCleanup(p.stop)
        self.input=root/'orchestration.json'
        values={k:'fixture' for k in h.REQUIRED}
        values.update(QUANT_REPOSITORY='fahimahmedb/Quant-Trade',QUANT_CODEX_TARGET_BRANCH='code/canonical',
                      QUANT_CODEX_EXPECTED_HEAD_SHA='c'*40,QUANT_CODEX_ISSUE_NUMBER='44',
                      QUANT_GPT_OSS_COMMAND='/fixture/local-model')
        self.input.write_text(json.dumps(values));self.input.chmod(0o600)
        self.before={str(p):h.image(p) for p in h.paths_to_save(self.states)}

    def apply(self):
        return h.handoff(self.new,self.old.name,12,34,self.input)

    def assert_restored(self):
        for p,saved in self.before.items():self.assertEqual(h.image(p),saved,p)
        self.assertEqual(c.CURRENT.resolve(),self.old)
        self.assertEqual(self.states[c.TIMER]['ActiveState'],'active')
        self.assertEqual(self.states[c.TIMER]['UnitFileState'],'enabled')
        self.assertFalse(any(c.V1_TIMER in a and a[1] in ('start','enable') for a in self.commands))

    def test_success_reuses_timer_preserves_shared_env_and_keeps_f3_unproven(self):
        result=self.apply()
        self.assertFalse(result['f3_proven']); self.assertEqual(c.CURRENT.resolve(),self.new)
        self.assertEqual(h.image(h.SHARED_ENV),self.before[str(h.SHARED_ENV)])
        self.assertEqual(self.states[c.V1_TIMER]['ActiveState'],'inactive')
        self.assertIn('--worker-version v2',h.DROPIN.read_text())
        h.rollback(Path(result['backup_directory'])); self.assert_restored()

    def test_known_managed_dropin_allows_bounded_existing_f3_upgrade(self):
        self.apply()
        self.states[c.SERVICE]['DropInPaths'] += ' ' + str(h.DROPIN)
        target=self.old.parent/('c'*40);target.mkdir()
        result=h.handoff(target,self.new.name,12,34,self.input)
        self.assertEqual(c.CURRENT.resolve(),target)
        h.rollback(Path(result['backup_directory']))
        self.assertEqual(c.CURRENT.resolve(),self.new)
        self.assertIn('QUANT_CODEX_MAX_DISPATCH_ATTEMPTS="1"',h.ENV.read_text())
        self.assertIn('QUANT_CODEX_MAX_REVIEW_ATTEMPTS="1"',h.ENV.read_text())

    def test_owner_modified_managed_dropin_is_not_silently_reused(self):
        self.apply()
        self.states[c.SERVICE]['DropInPaths'] += ' ' + str(h.DROPIN)
        h.DROPIN.write_bytes(h.DROPIN.read_bytes()+b'# Owner edit\n')
        before=h.image(h.DROPIN)
        with self.assertRaisesRegex(ValueError,'LATER_DROPIN'):
            h.handoff(self.new,self.new.name,12,34,self.input)
        self.assertEqual(h.image(h.DROPIN),before)

    def test_failure_after_rebind_restores_exact_bytes_modes_owner_and_link(self):
        def qualify(*args):
            if c.CURRENT.resolve()==self.new:
                self.assertEqual(self.states[c.TIMER]['ActiveState'],'inactive')
                raise ValueError('injected-after-rebind')
            return {'ok':True}
        with patch.object(h,'qualify_f3',side_effect=qualify),self.assertRaisesRegex(RuntimeError,'V2_RESTORED'):
            self.apply()
        self.assert_restored()

    def test_failure_during_activation_never_starts_v1(self):
        def checked(argv):
            self.checked(argv)
            if argv[1:]==['enable','--now',c.TIMER] and c.CURRENT.resolve()==self.new:
                raise RuntimeError('failed-after-enable')
        with patch.object(c,'checked',side_effect=checked),self.assertRaisesRegex(RuntimeError,'V2_RESTORED'):
            self.apply()
        self.assert_restored()

    def test_persisted_recovery_survives_loss_of_process_memory(self):
        result=self.apply();directory=Path(result['backup_directory'])
        # Recovery reads disk state, not the original Python record/exception.
        self.states[c.TIMER].update(ActiveState='inactive',UnitFileState='disabled')
        result=h.rollback(directory)
        self.assertEqual(result['status'],'V2_RESTORED');self.assert_restored()
        self.assertEqual(h.rollback(directory)['status'],'ALREADY_ROLLED_BACK')

    def test_owner_edit_blocks_overwrite_and_stops_new_runtime(self):
        result=self.apply();h.SHARED_ENV.write_bytes(b'new-owner-secret')
        with self.assertRaisesRegex(ValueError,'OWNER_OR_EXTERNAL_EDIT'):
            h.rollback(Path(result['backup_directory']))
        self.assertEqual(h.SHARED_ENV.read_bytes(),b'new-owner-secret')
        self.assertEqual(self.states[c.TIMER]['ActiveState'],'inactive')

    def test_owner_edit_to_mutated_file_is_preserved(self):
        result=self.apply();h.ENV.chmod(0o600)
        with self.assertRaisesRegex(ValueError,'OWNER_OR_EXTERNAL_EDIT'):
            h.rollback(Path(result['backup_directory']))
        self.assertEqual(h.ENV.stat().st_mode&0o777,0o600)

    def test_failed_ci_cannot_quiesce_or_mutate_host(self):
        with patch.object(c,'verify_ci',side_effect=ValueError('CI failed')),self.assertRaisesRegex(ValueError,'CI failed'):
            self.apply()
        self.assertEqual(self.commands,[]);self.assert_restored()

    def test_wrong_rollback_identity_blocks_before_downtime(self):
        with self.assertRaisesRegex(ValueError,'ROLLBACK_RELEASE_MISMATCH'):
            h.handoff(self.new,'d'*40,12,34,self.input)
        self.assertEqual(self.commands,[])

    def test_shared_env_not_changed_and_no_science_canary_is_called(self):
        with patch.object(c,'qualify',side_effect=AssertionError('science canary')),patch.object(c,'activate',side_effect=AssertionError('V1 transfer')):
            self.apply()
        self.assertEqual(h.image(h.SHARED_ENV),self.before[str(h.SHARED_ENV)])

    def test_quiescence_failure_prevents_config_writes(self):
        def checked(argv):
            self.checked(argv)
            if argv[1]=='stop':self.states[c.SERVICE]['ActiveState']='deactivating'
        with patch.object(c,'checked',side_effect=checked),self.assertRaises(RuntimeError):self.apply()
        for p,saved in self.before.items():self.assertEqual(h.image(p),saved,p)

    def test_credential_input_permissions_fail_closed(self):
        self.input.chmod(0o644)
        with self.assertRaisesRegex(ValueError,'ROOT_0600'):
            self.apply()
        self.assertEqual(self.commands,[])

    def test_legacy_activation_and_qualification_refuse_f3_mode(self):
        with self.assertRaisesRegex(ValueError,'NOT_V1_TRANSFER'):c.activate({'runtime_mode':'codex_engineering'})
        with self.assertRaisesRegex(ValueError,'NOT_SCIENTIFIC_CANARY'):c.qualify({'runtime_mode':'codex_engineering'},self.new)

    def test_effective_unit_must_bind_v2_router_env_and_writable_state(self):
        output=('ExecStart=research.research_os.host_wake --worker-version v2\n'
                'EnvironmentFiles='+str(h.ENV)+'\nReadWritePaths='+str(c.STATE)+'\n'
                'WorkingDirectory='+str(c.CURRENT)+'\n')
        with patch.object(h.subprocess,'run',return_value=Mock(returncode=0,stdout=output)):
            VERIFY_EFFECTIVE_UNIT()
        for missing in ['host_wake','codex.env',str(c.STATE),str(c.CURRENT)]:
            with self.subTest(missing=missing),patch.object(h.subprocess,'run',return_value=Mock(returncode=0,stdout=output.replace(missing,'wrong'))):
                with self.assertRaisesRegex(ValueError,'NOT_BOUND'):VERIFY_EFFECTIVE_UNIT()

    def test_control_lock_rejects_concurrent_transaction(self):
        with patch.object(h,'CONTROL_LOCK',self.root/'control-lock'):
            with h.locked():
                with self.assertRaises(BlockingIOError):
                    with h.locked():pass

    def test_snapshot_refuses_symlink_parent(self):
        link=self.root/'unsafe';link.symlink_to(c.CONFIG.parent)
        with self.assertRaisesRegex(ValueError,'SYMLINK_PARENT'):
            h.image(link/c.CONFIG.name)

    def test_local_preflight_error_does_not_echo_model_or_token(self):
        with patch.object(h.subprocess,'run',return_value=Mock(returncode=1,stdout='',stderr='PRIVATE_TOKEN')):
            with self.assertRaisesRegex(ValueError,'^F3_SERVICE_PRINCIPAL_PREFLIGHT_FAILED$'):
                QUALIFY_F3(self.old_config,{},self.new)

