from copy import deepcopy
from contextlib import nullcontext
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from deploy.oracle_h24_canary import GATES, instance_identity, release_ci
from deploy.oracle_scheduler_install import verify_qualification, activate
from deploy.oci_research_os_deploy import remote_inventory_bootstrap, state_path, parse_args
from deploy.oracle_model_inventory import inventory
from research.research_os.oracle_worker import backend_from_config
from research.research_os.worker_preflight import AUTHORITY_KEYS, canonical_hash

ROOT = Path(__file__).resolve().parents[3]


class SchedulerGateTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 19, 12, tzinfo=timezone.utc)
        self.config = {'release_sha': 'a' * 40, 'vm_ocid': 'ocid1.instance.test',
                       'qualification_ci_run_id': 123}
        self.report = {'status': 'PASS_PRE_ACTIVATION', 'evidence_scope': 'LIVE_ORACLE_VM',
                       'release_sha': self.config['release_sha'], 'config_hash': canonical_hash(self.config),
                       'instance': {'id': self.config['vm_ocid']}, 'gates': {g: True for g in GATES},
                       'completed_at': self.now.isoformat(), 'authority': {k: False for k in AUTHORITY_KEYS},
                       'hosted_model_calls': 0, 'scheduler_enabled': False}

    def test_all_live_gates_must_pass_before_any_host_command(self):
        for gate in GATES:
            report = deepcopy(self.report)
            report['gates'][gate] = False
            with self.subTest(gate=gate), patch('deploy.oracle_scheduler_install.checked') as command:
                with self.assertRaises(ValueError):
                    activate(ROOT, self.config, report)
                command.assert_not_called()

    def test_stale_foreign_or_ci_only_evidence_cannot_activate(self):
        for mutation in (
            {'release_sha': 'b' * 40}, {'config_hash': 'unknown'}, {'evidence_scope': 'CI'},
            {'instance': {'id': 'other'}}, {'hosted_model_calls': 1},
            {'completed_at': (self.now - timedelta(hours=7)).isoformat()},
            {'completed_at': (self.now + timedelta(seconds=1)).isoformat()},
            {'authority': dict(self.report['authority'], live_trading_authorized=True)},
        ):
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                verify_qualification(dict(self.report, **mutation), self.config, now=self.now)
        self.assertEqual(verify_qualification(self.report, self.config, now=self.now), self.report)

    def test_unknown_model_adapter_does_not_silently_choose_a_backend(self):
        with self.assertRaises(ValueError):
            backend_from_config({'model_backend': {'implementation': 'hosted'}})

    def test_oci_inventory_has_separate_resume_identity_and_no_installer(self):
        vm, sha = 'ocid1.instance.test', 'a' * 40
        self.assertNotEqual(state_path(vm=vm, sha=sha), state_path(vm=vm, sha=sha, operation='inventory'))
        command = remote_inventory_bootstrap(sha)
        self.assertIn('/' + sha + '/deploy/oracle_model_inventory.py', command)
        self.assertNotIn('oracle_release_install', command)
        self.assertNotIn('systemctl', command)
        self.assertTrue(parse_args(['--vm', vm, '--sha', sha, '--inventory']).inventory)

    def test_service_timer_are_valid_systemd_assets_and_no_paid_cli_dependency(self):
        directory = ROOT / 'deploy/systemd'
        p = subprocess.run(['systemd-analyze', 'verify', str(directory / 'quant-research-worker.service'),
                            str(directory / 'quant-research-worker.timer')], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        service = (directory / 'quant-research-worker.service').read_text()
        self.assertIn('User=quant-research', service)
        self.assertIn('TimeoutStartSec=8min', service)
        self.assertIn('MemoryMax=768M', service)
        self.assertIn('/usr/bin/flock --nonblock', service)
        self.assertIn('ProtectSystem=strict', service)
        self.assertNotIn('codex ', service.lower())

    def test_oci_identity_must_be_the_explicit_instance(self):
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self, *args):
                return json.dumps({'id': 'different', 'shape': 'VM.Standard.A1.Flex'}).encode()
        with patch('deploy.oracle_h24_canary.urllib.request.build_opener') as opener:
            opener.return_value.open.return_value = Response()
            with self.assertRaisesRegex(ValueError, 'INSTANCE_ID_MISMATCH'):
                instance_identity(self.config['vm_ocid'])

    def test_unreadable_model_root_is_an_explicit_gap_not_absence_or_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            denied, readable = root / 'denied', root / 'readable'
            denied.mkdir()
            (denied / 'models').mkdir()
            readable.mkdir()
            (readable / 'existing.gguf').write_bytes(b'GGUF')
            denied.chmod(0)
            try:
                # Real OS permissions reproduce the live unprivileged VM failure.
                # Retain deterministic coverage when a developer runs tests as root.
                original_is_dir = Path.is_dir
                def checked_is_dir(path):
                    if path == denied / 'models':
                        raise PermissionError(13, 'Permission denied', str(path))
                    return original_is_dir(path)
                permission_probe = patch.object(Path, 'is_dir', checked_is_dir) if os.geteuid() == 0 else nullcontext()
                with permission_probe, \
                     patch('deploy.oracle_model_inventory.local_json', return_value={}), \
                     patch('deploy.oracle_model_inventory.command', return_value={'returncode': 0, 'stdout': ''}), \
                     patch('deploy.oracle_model_inventory.processes', return_value=[]):
                    report = inventory([str(denied / 'models'), str(readable)])
            finally:
                denied.chmod(0o700)
            self.assertEqual(report['model_files'], [{'path': str(readable / 'existing.gguf'), 'size_bytes': 4}])
            self.assertEqual(report['inspection_gaps'], [{'path': str(denied / 'models'),
                             'operation': 'MODEL_ROOT_STAT', 'error': 'PermissionError'}])
            self.assertFalse(report['file_inventory_complete_for_requested_roots'])
            self.assertEqual(report['compatibility_verdict'], 'REQUIRES_REVIEW_AND_BOUNDED_INFERENCE_CANARY')
            self.assertFalse(report['mutations_performed'])


if __name__ == '__main__':
    unittest.main()
