"""Consequential operation gates, using fake APIs and a fake SSH process only."""
import base64
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import quant_operational_job as ops


class API:
    def __init__(self):
        self.default = ops.OLD_DEFAULT
        self.changes = []
        self.rules = []
        self.refs = [ops.PROJECT, ops.CODE]
        self.prs = []
        self.env_count = 0
        self.collector = "on:\n  schedule:\n    - cron: '47 * * * *'\nwith:\n  ref: code/canonical\n"

    def request(self, path="", *, method="GET", payload=None):
        if method != "GET":
            self.changes.append((method, path, payload))
            if method == "PATCH":
                self.default = payload["default_branch"]
                return {}
            self.rules = [dict(copy.deepcopy(payload), id=91)]
            return self.rules[0]
        if not path:
            return {"default_branch": self.default, "has_pages": False}
        if path.startswith("/branches/"):
            return {"commit": {"sha": "a" * 40}}
        if path.startswith("/contents/"):
            return {"content": base64.b64encode(self.collector.encode()).decode()}
        if path.startswith("/environments"):
            return {"total_count": self.env_count}
        if path.startswith("/rulesets/"):
            return self.rules[0]
        raise AssertionError(path)

    def pages(self, path):
        return {"/pulls?state=open": self.prs, "/deployments": [],
                "/rulesets": self.rules, "/branches": [{"name": ref} for ref in self.refs]}[path]


class OperationalJobTests(unittest.TestCase):
    def test_readiness_without_credentials_does_not_access_api(self):
        result = ops.execute("check-access", {}, api=object())
        self.assertFalse(result["admin_token_configured"])
        self.assertEqual(result["mutations"], 0)

    def test_missing_admin_credential_blocks_before_mutation(self):
        api = API()
        with self.assertRaisesRegex(ops.Blocked, "QUANT_GH_ADMIN_TOKEN"):
            ops.execute("switch-default", {}, api)
        self.assertEqual(api.changes, [])

    def test_default_changes_only_after_preflight_and_readback(self):
        api = API()
        self.assertEqual(ops.switch_default(api)["after"], ops.PROJECT)
        self.assertEqual(api.changes, [("PATCH", "", {"default_branch": ops.PROJECT})])
        ops.switch_default(api)
        self.assertEqual(len(api.changes), 1)

    def test_unexpected_default_or_open_old_pr_does_not_mutate(self):
        for variant in ("foreign_default", "open_pr", "environment"):
            api = API()
            if variant == "foreign_default": api.default = "foreign"
            if variant == "open_pr": api.prs = [{"base": {"ref": ops.OLD_DEFAULT}, "head": {"ref": ops.CODE}}]
            if variant == "environment": api.env_count = 1
            with self.subTest(variant=variant), self.assertRaises(ops.Blocked):
                ops.switch_default(api)
            self.assertEqual(api.changes, [])

    def test_missing_or_changed_schedule_blocks_switch(self):
        api = API(); api.collector = "with:\n  ref: code/canonical\n"
        with self.assertRaisesRegex(ops.Blocked, "SCHEDULE_CHANGED"):
            ops.switch_default(api)
        self.assertEqual(api.changes, [])

    def test_canonical_workflow_mismatch_blocks_switch(self):
        api = API(); original = api.request
        def request(path="", **kw):
            if "ref=project%2Fcanonical" in path:
                return {"content": base64.b64encode(b"mismatched workflow").decode()}
            return original(path, **kw)
        api.request = request
        with self.assertRaisesRegex(ops.Blocked, "WORKFLOWS_DIFFER"):
            ops.switch_default(api)
        self.assertEqual(api.changes, [])

    def test_protection_is_deferred_until_two_branches(self):
        api = API(); api.refs.append(ops.OLD_DEFAULT)
        with self.assertRaisesRegex(ops.Blocked, "RETIRE_RESIDUAL"):
            ops.protect(api)
        self.assertEqual(api.changes, [])

    def test_rules_protect_history_without_blocking_worker_ff_writes(self):
        api = API(); api.default = ops.PROJECT
        ops.protect(api)
        self.assertEqual({r["type"] for r in api.changes[0][2]["rules"]}, {"deletion", "non_fast_forward"})
        self.assertEqual(api.changes[0][2]["bypass_actors"], [])
        ops.protect(api)
        self.assertEqual(len(api.changes), 1)

    def test_different_existing_protection_is_not_overwritten(self):
        api = API(); api.default = ops.PROJECT
        api.rules = [dict(copy.deepcopy(ops.RULESET), id=91)]
        api.rules[0]["bypass_actors"] = [{"actor_id": 5, "actor_type": "User", "bypass_mode": "always"}]
        with self.assertRaisesRegex(ops.Blocked, "NO_OVERWRITE"):
            ops.protect(api)
        self.assertEqual(api.changes, [])

    def test_ssh_target_is_validated_and_host_key_checking_is_mandatory(self):
        env = {"QUANT_ORACLE_HOST": "-proxycommand", "QUANT_ORACLE_USER": "ubuntu",
               "QUANT_ORACLE_SSH_KEY": "synthetic-key", "QUANT_ORACLE_KNOWN_HOSTS": "synthetic-host-key"}
        with patch.object(ops.subprocess, "run") as child:
            with self.assertRaisesRegex(ops.Blocked, "INVALID_SSH_TARGET"):
                ops.host_inventory(env)
            child.assert_not_called()
        env["QUANT_ORACLE_HOST"] = "oracle.invalid"
        with patch.object(ops.subprocess, "run", return_value=SimpleNamespace(
                returncode=0, stdout=json.dumps({"operation": "READ_ONLY_HOST_INVENTORY"}).encode())) as child:
            ops.host_inventory(env)
            command = child.call_args.args[0]
            self.assertIn("-oStrictHostKeyChecking=yes", command)
            self.assertIn("-F", command)
            self.assertEqual(command[-1], "sudo -n python3 -")
            key = Path(command[command.index("-i") + 1])
        self.assertFalse(key.exists())

    def test_ssh_failure_does_not_leak_stderr_or_keys(self):
        env = {"QUANT_ORACLE_HOST": "oracle.invalid", "QUANT_ORACLE_USER": "ubuntu",
               "QUANT_ORACLE_SSH_KEY": "synthetic-private-key", "QUANT_ORACLE_KNOWN_HOSTS": "synthetic-host-key"}
        with patch.object(ops.subprocess, "run", return_value=SimpleNamespace(
                returncode=1, stderr=b"synthetic-private-key")):
            with self.assertRaisesRegex(ops.Blocked, "^SSH_OR_NONINTERACTIVE_SUDO_FAILED$"):
                ops.host_inventory(env)


if __name__ == "__main__":
    unittest.main()
