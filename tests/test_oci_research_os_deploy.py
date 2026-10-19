from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "oci_research_os_deploy",
    ROOT / "deploy" / "oci_research_os_deploy.py",
)
deploy = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(deploy)


class OciResearchOsDeployTests(unittest.TestCase):
    def test_vm_and_sha_are_explicit_and_strict(self):
        vm = "ocid1.instance.oc1.eu-paris-1.example"
        sha = "A" * 40
        self.assertEqual(
            deploy.validate_inputs(vm, sha, "eu-paris-1"),
            (vm, "a" * 40, "eu-paris-1"),
        )
        for bad_sha in ("main", "1" * 39, "g" * 40):
            with self.subTest(bad_sha=bad_sha), self.assertRaisesRegex(
                deploy.DeployBlock, "INVALID_DEPLOY_SHA"
            ):
                deploy.validate_inputs(vm, bad_sha, "eu-paris-1")
        with self.assertRaisesRegex(deploy.DeployBlock, "INVALID_VM_OCID"):
            deploy.validate_inputs("instance-123", "1" * 40, "eu-paris-1")

    def test_remote_bootstrap_is_small_and_pinned_to_exact_sha(self):
        sha = "1" * 40
        command = deploy.remote_bootstrap(sha)
        self.assertLess(len(command.encode()), 4096)
        self.assertIn("python3 -c", command)
        # Mutable branch names are never accepted by validate_inputs and therefore
        # cannot be deployment identities.
        with self.assertRaisesRegex(deploy.DeployBlock, "INVALID_DEPLOY_SHA"):
            deploy.validate_inputs(
                "ocid1.instance.oc1.eu-paris-1.example", "main", "eu-paris-1"
            )

    def test_failed_oci_request_is_never_interpreted_as_empty_collection(self):
        failure = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="NotAuthorizedOrNotFound"
        )
        with patch.object(deploy.subprocess, "run", return_value=failure):
            with self.assertRaisesRegex(deploy.DeployBlock, "NotAuthorizedOrNotFound"):
                deploy.oci("iam", "dynamic-group", "list", region="eu-paris-1")

    def test_known_empty_list_is_allowed_but_empty_get_is_blocked(self):
        empty = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with patch.object(deploy.subprocess, "run", return_value=empty):
            self.assertEqual(
                deploy.oci("iam", "policy", "list", region="eu-paris-1"),
                {"data": []},
            )
            with self.assertRaisesRegex(deploy.DeployBlock, "OCI_EMPTY_RESPONSE"):
                deploy.oci(
                    "instance-agent", "command-execution", "get", region="eu-paris-1"
                )

    def test_invalid_json_and_missing_data_fail_closed(self):
        invalid = subprocess.CompletedProcess(args=[], returncode=0, stdout="nope", stderr="")
        with patch.object(deploy.subprocess, "run", return_value=invalid):
            with self.assertRaisesRegex(deploy.DeployBlock, "OCI_INVALID_JSON"):
                deploy.oci("compute", "instance", "get", region="eu-paris-1")
        missing = subprocess.CompletedProcess(args=[], returncode=0, stdout='{"x": 1}', stderr="")
        with patch.object(deploy.subprocess, "run", return_value=missing):
            with self.assertRaisesRegex(deploy.DeployBlock, "OCI_DATA_MISSING"):
                deploy.oci("compute", "instance", "get", region="eu-paris-1")

    def test_state_identity_is_keyed_by_vm_and_sha(self):
        vm1 = "ocid1.instance.oc1.eu-paris-1.one"
        vm2 = "ocid1.instance.oc1.eu-paris-1.two"
        sha1 = "1" * 40
        sha2 = "2" * 40
        self.assertNotEqual(
            deploy.state_path(vm=vm1, sha=sha1), deploy.state_path(vm=vm2, sha=sha1)
        )
        self.assertNotEqual(
            deploy.state_path(vm=vm1, sha=sha1), deploy.state_path(vm=vm1, sha=sha2)
        )


if __name__ == "__main__":
    unittest.main()
