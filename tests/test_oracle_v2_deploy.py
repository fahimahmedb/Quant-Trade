"""Local contract/real-Git tests, never substitutes for Oracle qualification."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import subprocess

from deploy import oracle_v2_canary as canary
from deploy.oracle_v2_deploy import CONFIG, ROOT_QUALIFICATION, GATES, verify_qualification
from research.research_os.expansion.v2_core import CLOSED_AUTHORITY, canonical_hash
from research.research_os.github_state import GitHubStateStore, PREFIX


class V2DeploymentTests(unittest.TestCase):
    def test_activation_rejects_missing_stale_foreign_and_unsafe_proofs(self):
        self.assertEqual(ROOT_QUALIFICATION.parent, CONFIG.parent)
        from deploy.oracle_v2_deploy import run_as_worker
        process = unittest.mock.Mock(pid=999)
        process.communicate.side_effect = [subprocess.TimeoutExpired("fixture", 1), ("", "")]
        with patch("deploy.oracle_v2_deploy.subprocess.Popen", return_value=process) as spawn, \
                patch("deploy.oracle_v2_deploy.os.killpg") as kill:
            with self.assertRaisesRegex(RuntimeError, "PROCESS_GROUP_KILLED"):
                run_as_worker(["-m", "fixture"], timeout=1)
            self.assertTrue(spawn.call_args.kwargs["start_new_session"])
            self.assertIn("/usr/bin/flock", spawn.call_args.args[0])
            self.assertIn("/var/lib/quant-research", spawn.call_args.args[0])
            kill.assert_called_once()
        now = datetime(2026, 10, 20, 3, tzinfo=timezone.utc)
        config = dict(release_sha="a" * 40, vm_ocid="fixture-vm")
        valid = dict(status="PASS_V2_PRE_ACTIVATION", evidence_scope="LIVE_ORACLE_V2_CORE",
                     release_sha=config["release_sha"], config_hash=canonical_hash(config),
                     instance={"id": config["vm_ocid"]}, gates=dict.fromkeys(GATES, True),
                     completed_at=now.isoformat(), authority=dict(CLOSED_AUTHORITY), hosted_model_calls=0,
                     scheduler_enabled=False, outcome_accessed=False)
        self.assertEqual(verify_qualification(valid, config, now), valid)
        for gate in GATES:
            invalid = deepcopy(valid); invalid["gates"][gate] = False
            with self.subTest(gate=gate), self.assertRaises(ValueError):
                verify_qualification(invalid, config, now)
        for key, value in (("release_sha", "b" * 40), ("scheduler_enabled", True),
                           ("outcome_accessed", True), ("hosted_model_calls", 1),
                           ("completed_at", (now - timedelta(hours=7)).isoformat())):
            invalid = deepcopy(valid); invalid[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify_qualification(invalid, config, now)
        invalid = deepcopy(valid); invalid["authority"]["real_capital_authorized"] = True
        with self.assertRaises(ValueError): verify_qualification(invalid, config, now)

    def migration_fixture(self):
        from research.research_os.tests import test_oracle_worker as fixture
        harness = fixture.WorkerTests(); harness.setUp(); self.addCleanup(harness.tearDown)
        harness.store._git("fetch", harness.store.remote, "refs/heads/recovery")
        head = harness.store._git("rev-parse", "FETCH_HEAD").decode().strip()
        harness.store._git("push", harness.store.remote, head + ":refs/heads/v2")
        target = GitHubStateStore(cache=harness.root / "v2-cache", repository="fixture/repo", branch="v2")
        target.remote = str(harness.remote)
        config = dict(repository="fixture/repo", branch=canary.BRANCH, cache=str(target.cache),
                      model_backend={"model": "DETERMINISTIC_ENGINE"}, release_sha="a" * 40)
        patches = (patch.object(canary, "assert_quiesced"), patch.object(canary, "store", return_value=target),
                   patch.object(canary, "GitHubStateStore", return_value=harness.store))
        for item in patches: item.start(); self.addCleanup(item.stop)
        return harness, target, config

    def test_real_git_transfer_replays_preserves_destination_and_fences_generations(self):
        harness, target, config = self.migration_fixture()
        report = canary.migrate(config)
        with target.snapshot() as snapshot:
            head = snapshot.head
            task = snapshot.read(PREFIX + "tasks/RECOVER-TEST-001.json")
            self.assertEqual(task["status"], "BLOCKED")
            self.assertEqual(task["lease"]["generation"], 1)
        self.assertEqual(canary.migrate(config), report)
        with target.snapshot() as snapshot:
            self.assertEqual(snapshot.head, head)
            target.commit(snapshot, {PREFIX + "artifacts/v2-only.json": {"immutable": True}},
                          create_only=[PREFIX + "artifacts/v2-only.json"], message="fixture destination evidence")
        with harness.store.snapshot() as source:
            task = source.read(PREFIX + "tasks/RECOVER-TEST-001.json")
            task["status"] = "COMPLETE"
            harness.store.commit(source, {PREFIX + "tasks/RECOVER-TEST-001.json": task}, message="fixture source completion")
        canary.migrate(config)
        with target.snapshot() as snapshot:
            task = snapshot.read(PREFIX + "tasks/RECOVER-TEST-001.json")
            self.assertEqual(task["status"], "COMPLETE")
            self.assertEqual(task["lease"]["generation"], 1)
            self.assertTrue(snapshot.read(PREFIX + "artifacts/v2-only.json")["immutable"])

    def test_real_git_transfer_rejects_concurrent_scientific_changes(self):
        harness, target, config = self.migration_fixture()
        path = PREFIX + "tasks/RECOVER-TEST-001.json"
        for state, marker in ((harness.store, "source"), (target, "destination")):
            with state.snapshot() as snapshot:
                task = snapshot.read(path); task["fixture_mutation"] = marker
                state.commit(snapshot, {path: task}, message="fixture concurrent mutation")
        with target.snapshot() as snapshot: head = snapshot.head
        with self.assertRaisesRegex(ValueError, "CONCURRENT_SCIENTIFIC_MIGRATION_CONFLICT"):
            canary.migrate(config)
        with target.snapshot() as snapshot: self.assertEqual(snapshot.head, head)

    def test_v2_units_and_bootstrap_keep_explicit_release_and_shared_v1_lock(self):
        root = Path(__file__).resolve().parents[1] / "deploy/systemd"
        v1 = (root / "quant-research-worker.service").read_text()
        v2 = (root / "quant-research-worker-v2.service").read_text()
        self.assertNotIn("oracle_worker_v2", v1)
        self.assertIn("research.research_os.oracle_worker_v2", v2)
        self.assertIn("--conflict-exit-code=0 /var/lib/quant-research ", v1)
        self.assertIn("--conflict-exit-code=0 /var/lib/quant-research ", v2)
        self.assertIn("Conflicts=quant-research-worker.timer quant-research-worker.service", v2)
        self.assertIn("MemoryMax=768M", v2)
        # Reproduce CP1 importing a package from staging, then publishing it
        # by rename. A sys.path insertion cannot repair cached __path__ values.
        import tempfile, sys
        with tempfile.TemporaryDirectory() as directory:
            stage, release = Path(directory) / "staging", Path(directory) / "release"
            for package in ("deploy", "research", "research/research_os", "research/research_os/expansion"):
                folder = stage / package; folder.mkdir(parents=True, exist_ok=True)
                (folder / "__init__.py").write_text("")
            (stage / "research/research_os/expansion/v2_core.py").write_text("SENTINEL = 'published-package'\n")
            (stage / "deploy/oracle_v2_deploy.py").write_text(
                "from research.research_os.expansion.v2_core import SENTINEL\n"
                "def prepare(release, v2, sec): return dict(sentinel=SENTINEL,path=str(release),runs=[v2,sec])\n")
            bootstrap = root.parent / "oracle_v2_host_prepare.py"
            code = '''
import importlib.util,json,sys
from pathlib import Path
stage,release,bootstrap=sys.argv[1:]
sys.path.insert(0,stage)
import research.research_os.expansion
Path(stage).rename(release)
sys.path.insert(0,release)
try:
    import research.research_os.expansion.v2_core
except ModuleNotFoundError:
    pass
else:
    raise AssertionError("fixture did not reproduce the stale package path")
spec=importlib.util.spec_from_file_location("fixed_bootstrap",bootstrap)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.prepare_installed_release(Path(release),12,34)
'''
            process = subprocess.run([sys.executable, "-I", "-c", code, str(stage), str(release), str(bootstrap)],
                                     capture_output=True, text=True, check=True, timeout=30)
            value = json.loads(process.stdout)
            self.assertEqual(value, dict(sentinel="published-package", path=str(release), runs=[12, 34]))


if __name__ == "__main__": unittest.main()
