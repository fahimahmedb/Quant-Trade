"""Access repair must stay instance-scoped and resume without duplicate commands."""
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("oci_installer", Path(__file__).resolve().parents[1] / "deploy/oci_one_shot.py")
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class IamFixture:
    def __init__(self, root=False):
        self.tenancy = "ocid1.tenancy.oc1.example"
        self.compartment = self.tenancy if root else "ocid1.compartment.oc1.example"
        self.groups, self.policies, self.calls = [], [], []

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        route = args[:3]
        if route == ("compute", "instance", "get"):
            data = {"lifecycle-state": "RUNNING", "compartment-id": self.compartment}
        elif route == ("instance-agent", "plugin", "list"):
            data = [{"status": "RUNNING"}]
        elif route == ("iam", "compartment", "get"):
            data = {"compartment-id": self.tenancy}
        elif route == ("iam", "region-subscription", "list"):
            data = [{"region-name": "eu-frankfurt-1", "is-home-region": True}]
        elif route == ("iam", "dynamic-group", "list"):
            data = self.groups
        elif route == ("iam", "dynamic-group", "create"):
            data = {"id": "ocid1.dynamicgroup.oc1.example", "name": args[args.index("--name") + 1],
                    "matching-rule": args[args.index("--matching-rule") + 1], "lifecycle-state": "ACTIVE"}
            self.groups.append(data)
        elif route == ("iam", "policy", "list"):
            data = self.policies
        elif route == ("iam", "policy", "create"):
            data = {"name": args[args.index("--name") + 1], "statements": json.loads(args[args.index("--statements") + 1])}
            self.policies.append(data)
        else:
            raise AssertionError("Unexpected operation: " + repr(args))
        return {"data": data}


class OciInstallerAccessTests(unittest.TestCase):
    def test_oracle_empty_list_output_is_valid_for_known_list_operations(self):
        routes = (("iam", "dynamic-group", "list"), ("iam", "policy", "list"))
        for route in routes:
            with self.subTest(route=route), patch.object(installer.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")):
                self.assertEqual(installer.oci(*route), {"data": []})

    def test_empty_get_does_not_become_empty_list(self):
        with patch.object(installer.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")):
            with self.assertRaisesRegex(RuntimeError, "OCI_EMPTY_RESPONSE: oci instance-agent command-execution get"):
                installer.oci("instance-agent", "command-execution", "get")

    def test_failed_list_preserves_authorization_error(self):
        with patch.object(installer.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "NotAuthorizedOrNotFound")):
            with self.assertRaisesRegex(RuntimeError, "oci iam dynamic-group list.*NotAuthorizedOrNotFound"):
                installer.oci("iam", "dynamic-group", "list")

    def test_query_warning_does_not_become_empty_list(self):
        with patch.object(installer.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "Query returned empty result, no output to show.")):
            with self.assertRaisesRegex(RuntimeError, "OCI_EMPTY_RESPONSE"):
                installer.oci("iam", "dynamic-group", "list")

    def test_bad_json_reports_the_exact_operation(self):
        with patch.object(installer.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "not-json", "")):
            with self.assertRaisesRegex(RuntimeError, "OCI_INVALID_JSON: oci iam policy list"):
                installer.oci("iam", "policy", "list")

    def test_cli_query_is_explicitly_unfiltered(self):
        with patch.object(installer.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, '{"data": []}', "")) as run:
            self.assertEqual(installer.oci("iam", "policy", "list"), {"data": []})
            self.assertEqual(run.call_args.args[0][-4:], ["--output", "json", "--query", "@"])

    def test_grant_is_limited_to_one_instance_and_its_own_commands(self):
        api = IamFixture()
        with patch.object(installer, "oci", api):
            installer.repair_agent_iam()
        self.assertEqual(api.groups[0]["matching-rule"], "ALL {instance.id = '" + installer.VM + "'}")
        self.assertEqual(api.policies[0]["statements"], [
            "Allow dynamic-group id ocid1.dynamicgroup.oc1.example to use instance-agent-command-execution-family in compartment id "
            + api.compartment + " where request.instance.id=target.instance.id"])
        for args, kwargs in api.calls:
            if args[:2] in (("iam", "dynamic-group"), ("iam", "policy")):
                self.assertEqual(kwargs["region"], "eu-frankfurt-1")

    def test_repair_reuses_its_existing_iam_resources(self):
        api = IamFixture()
        with patch.object(installer, "oci", api):
            installer.repair_agent_iam()
            installer.repair_agent_iam()
        creates = [a[:3] for a, _ in api.calls if "create" in a]
        self.assertEqual(creates, [("iam", "dynamic-group", "create"), ("iam", "policy", "create")])

    def test_root_compartment_retains_instance_restriction(self):
        api = IamFixture(root=True)
        with patch.object(installer, "oci", api):
            installer.repair_agent_iam()
        self.assertIn(" in tenancy where request.instance.id=target.instance.id", api.policies[0]["statements"][0])

    def test_conflicting_group_is_never_overwritten(self):
        api = IamFixture()
        api.groups = [{"name": "QuantRunCommand-" + installer.VM[-16:], "matching-rule": "ALL {instance.compartment.id = 'other'}", "lifecycle-state": "ACTIVE"}]
        with patch.object(installer, "oci", api), self.assertRaisesRegex(AssertionError, "incompatible"):
            installer.repair_agent_iam()
        self.assertFalse(any("create" in a or "update" in a for a, _ in api.calls))

    def test_conflicting_policy_is_never_overwritten(self):
        api = IamFixture()
        api.policies = [{"name": "QuantRunCommand-" + installer.VM[-16:], "statements": ["unexpected"]}]
        with patch.object(installer, "oci", api), self.assertRaisesRegex(AssertionError, "incompatible"):
            installer.repair_agent_iam()
        self.assertFalse(any(a[:2] == ("iam", "policy") and a[2] in ("update", "create") for a, _ in api.calls))

    def test_repair_without_checkpoint_never_creates_command(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(installer.Path, "home", return_value=Path(tmp)), patch.object(sys, "argv", ["installer", "--repair-agent"]), patch.object(installer, "oci") as api:
            with self.assertRaisesRegex(AssertionError, "aucune nouvelle commande"):
                installer.main()
            api.assert_not_called()

    def test_resumes_same_command_and_reports_only_confirmed_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / ".cache/quant-oci-one-shot"
            cache.mkdir(parents=True)
            (cache / "command.json").write_text(json.dumps(dict(vm=installer.VM, sha=installer.HEAD, command="existing-command")))
            replies = [{"data": {"lifecycle-state": "ACCEPTED"}}, {"data": {"lifecycle-state": "SUCCEEDED", "content": {"exit-code": 0, "text": "INSTALLED_VERIFIED"}}}]
            with patch.object(installer.Path, "home", return_value=Path(tmp)), patch.object(sys, "argv", ["installer", "--repair-agent"]), patch.object(installer, "oci", side_effect=replies) as api, patch.object(installer, "repair_agent_iam") as repair:
                self.assertEqual(installer.main(), 0)
            repair.assert_called_once()
            for call in api.call_args_list:
                self.assertEqual(call.args[:3], ("instance-agent", "command-execution", "get"))
                self.assertIn("existing-command", call.args)


if __name__ == "__main__":
    unittest.main()
