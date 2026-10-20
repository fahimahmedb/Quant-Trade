"""Release provenance can name an authorized source without redirecting state."""
from copy import deepcopy
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from deploy import oracle_v2_deploy as deploy
from tests import test_research_os_v2_worker_integration as fixtures


class ReleaseProvenanceTests(unittest.TestCase):
    def config(self):
        config = fixtures.V2WorkerIntegrationTests().worker_config()
        config.update(repository="fahimahmedb/Quant-Trade", branch=deploy.BRANCH,
                      cache=str(deploy.STATE / "github.git"), qualification_ci_runs={"v2_core": 101, "sec_p0": 102})
        return config

    def runs(self, branch):
        return [dict(id=run, head_sha=self.config()["release_sha"], head_branch=branch, name=name,
                     status="completed", conclusion="success", html_url=f"https://github.com/actions/runs/{run}")
                for run, name in ((101, "Oracle V2 Core"), (102, "SEC P0 pre-t0 gate"))]

    def test_both_exact_workflows_bind_the_same_explicit_source_or_legacy_default(self):
        for source in (None, *deploy.QUALIFICATION_SOURCE_BRANCHES):
            config = self.config()
            if source is not None:
                config["qualification_source_branch"] = source
            branch = source or deploy.BRANCH
            with self.subTest(source=source), patch.object(deploy.urllib.request, "urlopen",
                    side_effect=[io.BytesIO(json.dumps(run).encode()) for run in self.runs(branch)]):
                result = deploy.verify_ci(config)
                self.assertEqual({entry["head_branch"] for entry in result.values()}, {branch})
                self.assertEqual({entry["head_sha"] for entry in result.values()}, {config["release_sha"]})
            self.assertEqual(config["branch"], deploy.BRANCH)

    def test_unknown_or_ambiguous_source_is_rejected_before_network_access(self):
        for source in (None, "", "main", deploy.BRANCH + "-lookalike", True, [], {}):
            config = self.config()
            config["qualification_source_branch"] = source
            with self.subTest(source=source), patch.object(deploy.urllib.request, "urlopen") as network:
                with self.assertRaisesRegex(ValueError, "SOURCE_BRANCH_NOT_AUTHORIZED"):
                    deploy.verify_ci(config)
                network.assert_not_called()

    def test_foreign_mixed_or_unsuccessful_ci_cannot_qualify_a_release(self):
        branch = "builder/v2-forward-20261020"
        config = dict(self.config(), qualification_source_branch=branch)
        for index in (0, 1):
            for key, value in (("head_sha", "a" * 40), ("head_branch", deploy.BRANCH),
                               ("head_branch", "main"), ("name", "Other workflow"),
                               ("status", "in_progress"), ("conclusion", "failure")):
                runs = self.runs(branch)
                runs[index][key] = value
                with self.subTest(index=index, field=key, value=value), patch.object(deploy.urllib.request, "urlopen",
                        side_effect=[io.BytesIO(json.dumps(run).encode()) for run in runs]):
                    with self.assertRaisesRegex(ValueError, "EXACT_RELEASE_CI_NOT_SUCCESSFUL"):
                        deploy.verify_ci(config)

    def test_source_branch_permission_never_redirects_canonical_scientific_state(self):
        config = dict(self.config(), qualification_source_branch="builder/v2-forward-20261020",
                      branch="builder/v2-forward-20261020")
        with patch.object(Path, "read_text") as read:
            with self.assertRaisesRegex(ValueError, "V2_CANONICAL_CONFIG_REQUIRED"):
                deploy.validate_config(config)
            read.assert_not_called()

    def test_explicit_preparation_keeps_active_v2_handoff_gate_and_closed_authorities(self):
        source = "builder/v2-forward-20261020"
        old = self.config()
        old["vm_ocid"] = "synthetic-vm-identity"
        account = SimpleNamespace(pw_uid=123, pw_gid=123, pw_dir="/var/lib/quant-research")
        backend = Mock()
        with patch.object(deploy.os, "geteuid", return_value=0), \
             patch.object(Path, "read_text", return_value=json.dumps(old)), \
             patch.object(deploy.pwd, "getpwnam", return_value=account), \
             patch.object(deploy, "validate_config") as validate, \
             patch.object(deploy, "verify_ci"), patch.object(deploy, "instance_identity"), \
             patch.object(deploy, "backend_from_config", return_value=backend), \
             patch.object(deploy, "active", return_value="active"), \
             patch.object(deploy, "write_atomic") as write:
            with self.assertRaisesRegex(ValueError, "V2_RUNNING_RELEASE_REQUIRES_EXPLICIT_REPAIR_HANDOFF"):
                deploy.prepare(Path("/synthetic/" + "f" * 40), 101, 102, qualification_source_branch=source)
            proposed = deepcopy(validate.call_args.args[0])
            self.assertEqual(proposed["qualification_source_branch"], source)
            self.assertEqual(proposed["branch"], deploy.BRANCH)
            for key in ("economic_experiment_authorized", "prospective_observation_authorized",
                        "real_capital_authorized", "live_trading_authorized"):
                self.assertIs(proposed[key], False)
            write.assert_not_called()
