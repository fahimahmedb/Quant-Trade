"""Host preflight must never turn a branch migration into scientific work."""
import contextlib
import copy
import json
import os
from pathlib import Path
from types import ModuleType, SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import quant_host_rebind_preflight as preflight


class HostPreflightTests(unittest.TestCase):
    def probe(self):
        return dict(status="DRY_RUN", writes=0, input_head="a" * 40,
                    state_branch="code/canonical", selected_task=None, claimed_tasks=0,
                    hosted_model_calls=0, model_calls=0, same_tasks_as_live_v2=True,
                    v2_preflight="PASS", authority={k: False for k in preflight.AUTHORITY})

    def test_changed_head_work_or_model_calls_prevent_qualification(self):
        cases = dict(input_head="b" * 40, state_branch="old/ref", status="RUN",
                     writes=1, model_calls=1, hosted_model_calls=1,
                     selected_task="new-task", claimed_tasks=1)
        preflight.validate_probe(self.probe(), "a" * 40, v2=True)
        for key, value in cases.items():
            candidate = self.probe(); candidate[key] = value
            with self.subTest(key=key), self.assertRaises(preflight.Blocked):
                preflight.validate_probe(candidate, "a" * 40, v2=True)

    def test_active_runtime_requires_identical_tasks_and_v2_policy(self):
        for key, value in (("same_tasks_as_live_v2", False), ("v2_preflight", None)):
            candidate = self.probe(); candidate[key] = value
            with self.subTest(key=key), self.assertRaises(preflight.Blocked):
                preflight.validate_probe(candidate, "a" * 40, v2=True)

    def test_every_authority_must_be_explicitly_closed(self):
        for key in preflight.AUTHORITY:
            candidate = self.probe(); del candidate["authority"][key]
            with self.subTest(key=key), self.assertRaises(preflight.Blocked):
                preflight.validate_probe(candidate, "a" * 40)

    def test_config_drift_and_wrong_binding_block_without_secret_output(self):
        value = dict(branch="old/ref", release_sha="a" * 40, repository="fahimahmedb/Quant-Trade",
                     private_fixture_value="must-not-appear-in-errors")
        raw = json.dumps(value).encode()
        spec = ("/fixture/worker.json", preflight.digest(raw), "a" * 40, "old/ref")
        self.assertEqual(preflight.validate_config(raw, spec), value)
        for candidate in (raw + b" ", json.dumps(dict(value, branch="foreign/ref")).encode()):
            with self.assertRaises(preflight.Blocked) as caught:
                preflight.validate_config(candidate, spec)
            self.assertNotIn(value["private_fixture_value"], str(caught.exception))

    def test_backups_are_private_exact_and_cannot_overwrite_prior_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "worker.json"; source.write_bytes(b'{"branch":"old/ref"}\n')
            os.chmod(source, 0o640)
            target = Path(tmp) / "rollback"
            with patch.object(preflight, "checked_bytes", side_effect=lambda p: Path(p).read_bytes()):
                hashes = preflight.backup_files([source], target)
                with self.assertRaises(FileExistsError):
                    preflight.backup_files([source], target)
            saved = target / str(source).lstrip("/")
            self.assertEqual(saved.read_bytes(), source.read_bytes())
            self.assertEqual(hashes[str(source)], preflight.digest(source.read_bytes()))
            self.assertEqual(target.stat().st_mode & 0o777, 0o700)
            self.assertEqual(saved.stat().st_mode & 0o777, 0o600)
            self.assertEqual(source.stat().st_mode & 0o777, 0o640)

    def test_even_a_worker_that_attempts_publication_cannot_write(self):
        writes = []
        class Store:
            def __init__(self, **kwargs): pass
            def commit(self, *args, **kwargs): writes.append("REMOTE_WRITE")
            @contextlib.contextmanager
            def snapshot(self):
                yield SimpleNamespace(tasks=lambda: [], blobs={}, head="a" * 40)
        class Worker:
            def __init__(self, store, **kwargs): self.store = store
            def wake(self, **kwargs): self.store.commit("unexpected-publication")
        state = ModuleType("research.research_os.github_state"); state.GitHubStateStore = Store
        worker = ModuleType("research.research_os.oracle_worker"); worker.ResearchOSWorker = Worker
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "worker.json"
            config.write_text(json.dumps(dict(branch="old/ref", cache=tmp,
                              repository="fahimahmedb/Quant-Trade", worker_id="worker", release_sha="a" * 40)))
            with patch.dict(sys.modules, {state.__name__: state, worker.__name__: worker}), \
                    patch.object(sys, "argv", ["probe", tmp, str(config), "v1"]), \
                    patch.object(sys, "path", list(sys.path)), \
                    self.assertRaisesRegex(RuntimeError, "PREFLIGHT_REMOTE_WRITE_FORBIDDEN"):
                exec(compile(preflight.PROBE, "readonly-probe", "exec"), {})
        self.assertEqual(writes, [])

    def test_missing_root_blocks_before_any_file_read_or_backup(self):
        with patch.object(os, "geteuid", return_value=1000), \
                patch.object(preflight, "checked_bytes") as read, \
                patch.object(preflight, "backup_files") as backup, \
                self.assertRaisesRegex(preflight.Blocked, "ROOT_AND_EXACT"):
            preflight.execute("a" * 40)
        read.assert_not_called(); backup.assert_not_called()


if __name__ == "__main__":
    unittest.main()
