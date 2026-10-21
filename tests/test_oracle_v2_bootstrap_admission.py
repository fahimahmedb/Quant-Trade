"""Standalone bootstrap admission; host/HTTP observations are explicit fixtures."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from deploy import oracle_v2_host_prepare as bootstrap
from deploy import oracle_v2_deploy as native


class BootstrapAdmissionTests(unittest.TestCase):
    def argv(self, source=None):
        args = ['bootstrap', '--sha', 'a'*40, '--v2-ci-run', '101', '--sec-ci-run', '102']
        return args + (['--qualification-source-branch', source] if source else [])

    def state(self, active='inactive', load='loaded', code=0):
        return SimpleNamespace(returncode=code, stdout=f'LoadState={load}\nActiveState={active}\n')

    def test_root_and_observed_inactive_states_are_required_before_network_or_publication(self):
        self.assertEqual(bootstrap.V2_UNITS, (native.TIMER, native.SERVICE))
        with patch.object(bootstrap.os, 'geteuid', return_value=1000), \
                patch.object(bootstrap.subprocess, 'run') as host:
            with self.assertRaisesRegex(ValueError, 'ROOT_REQUIRED'):
                bootstrap.assert_bootstrap_target_idle()
            host.assert_not_called()
        for state in ('active', 'activating', 'reloading', 'deactivating', 'unknown', ''):
            for index in (0, 1):
                states = [self.state(), self.state()]
                states[index] = self.state(state)
                with self.subTest(state=state, index=index), \
                        patch.object(sys, 'argv', self.argv()), \
                        patch.object(bootstrap.os, 'geteuid', return_value=0), \
                        patch.object(bootstrap.subprocess, 'run', side_effect=states), \
                        patch.object(bootstrap.urllib.request, 'urlopen') as network:
                    with self.assertRaisesRegex(ValueError, 'V2_(RUNNING_RELEASE|BOOTSTRAP_RUNTIME_STATE)'):
                        bootstrap.main()
                    network.assert_not_called()
        for state in (self.state(load='error'), self.state(code=1)):
            with patch.object(bootstrap.os, 'geteuid', return_value=0), \
                    patch.object(bootstrap.subprocess, 'run', return_value=state):
                with self.assertRaisesRegex(ValueError, 'STATE_UNAVAILABLE'):
                    bootstrap.assert_bootstrap_target_idle()
        for state in (self.state(), self.state('failed'), self.state(load='not-found'),
                      self.state(load='not-found', code=1), self.state(load='not-found', code=4)):
            with patch.object(bootstrap.os, 'geteuid', return_value=0), \
                    patch.object(bootstrap.subprocess, 'run', return_value=state) as host:
                bootstrap.assert_bootstrap_target_idle()
                self.assertEqual([call.args[0][2] for call in host.call_args_list], list(bootstrap.V2_UNITS))

    def test_unknown_source_choices_fail_before_any_network_or_child_process(self):
        self.assertEqual(bootstrap.QUALIFICATION_SOURCE_BRANCHES, native.QUALIFICATION_SOURCE_BRANCHES)
        with patch.object(sys, 'argv', self.argv('main')), \
                patch.object(bootstrap.urllib.request, 'urlopen') as network, \
                patch.object(bootstrap.subprocess, 'run') as child, \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                bootstrap.main()
            network.assert_not_called()
            child.assert_not_called()
        with patch.object(bootstrap.subprocess, 'run') as child:
            with self.assertRaisesRegex(ValueError, 'SOURCE_BRANCH_NOT_AUTHORIZED'):
                bootstrap.prepare_installed_release(Path('/synthetic'), 101, 102,
                                                     qualification_source_branch='main')
            child.assert_not_called()

    def test_cli_binds_both_ci_runs_and_rechecks_state_before_bootstrap(self):
        pinned = '4f16891393a7adaea4b9c55ff29c479860ffc08d770b82e48ec24a0211a1e44f'
        # Synthetic bootstrap body only. Digest/host/HTTP are mocked, not live evidence.
        body = b"def bootstrap(sha):\n return {'path':'/synthetic/'+sha}\n"
        for source in bootstrap.QUALIFICATION_SOURCE_BRANCHES:
            runs = [dict(head_sha='a'*40, head_branch=source, name=name,
                         status='completed', conclusion='success')
                    for name in ('Oracle V2 Core', 'SEC P0 pre-t0 gate')]
            for blocked in (False, True):
                states = [None, ValueError('V2_RUNNING_RELEASE_REQUIRES_EXPLICIT_REPAIR_HANDOFF')]
                if not blocked:
                    states = [None, None]
                with self.subTest(source=source, blocked=blocked), \
                        patch.object(sys, 'argv', self.argv(source)), \
                        patch.object(bootstrap, 'assert_bootstrap_target_idle', side_effect=states) as admission, \
                        patch.object(bootstrap.urllib.request, 'urlopen', side_effect=[
                            io.BytesIO(json.dumps(run).encode()) for run in runs] + [io.BytesIO(
                                b"def bootstrap(sha): raise AssertionError('PUBLICATION_MUST_NOT_RUN')\n"
                                if blocked else body)]), \
                        patch.object(bootstrap.hashlib, 'sha256', return_value=Mock(hexdigest=lambda: pinned)), \
                        patch.object(bootstrap, 'prepare_installed_release') as prepare:
                    if blocked:
                        with self.assertRaisesRegex(ValueError, 'EXPLICIT_REPAIR_HANDOFF'):
                            bootstrap.main()
                        prepare.assert_not_called()
                    else:
                        bootstrap.main()
                        prepare.assert_called_once_with(Path('/synthetic/'+'a'*40), 101, 102,
                                                        qualification_source_branch=source)
                    self.assertEqual(admission.call_count, 2)
            for index in (0, 1):
                bad = [dict(run) for run in runs]
                bad[index]['head_branch'] = 'main'
                with patch.object(sys, 'argv', self.argv(source)), \
                        patch.object(bootstrap, 'assert_bootstrap_target_idle'), \
                        patch.object(bootstrap.urllib.request, 'urlopen', side_effect=[
                            io.BytesIO(json.dumps(run).encode()) for run in bad]) as network:
                    with self.assertRaisesRegex(ValueError, 'BOTH_EXACT_RELEASE_CI_GATES'):
                        bootstrap.main()
                    self.assertEqual(network.call_count, index+1)

    def test_explicit_source_reaches_fresh_isolated_published_interpreter(self):
        with tempfile.TemporaryDirectory() as directory:
            release = Path(directory)
            (release/'deploy').mkdir()
            (release/'deploy/__init__.py').write_text('')
            (release/'deploy/oracle_v2_deploy.py').write_text(
                'import json\n'
                'def prepare(path,v2,sec,*,qualification_source_branch):\n'
                ' return dict(path=str(path),source=qualification_source_branch,runs=[v2,sec])\n')
            # Capture the wrapper command, then execute it against a temporary fixture.
            with patch.object(bootstrap.subprocess, 'run') as child:
                bootstrap.prepare_installed_release(release, 101, 102,
                    qualification_source_branch=bootstrap.QUALIFICATION_SOURCE_BRANCHES[1])
            command = child.call_args.args[0]
            self.assertIn('-I', command)
            self.assertIn('-B', command)
            result = subprocess.run(command, cwd='/', check=True, capture_output=True, text=True, timeout=15)
            self.assertEqual(json.loads(result.stdout), dict(path=str(release),
                source=bootstrap.QUALIFICATION_SOURCE_BRANCHES[1], runs=[101, 102]))
