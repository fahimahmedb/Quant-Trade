#!/usr/bin/env python3
"""Deploy one exact verified Research OS release to an Oracle VM.

CloudShell-side orchestrator. It does not start or install any scheduler. The VM
and Git SHA are explicit inputs; no instance identifier or mutable branch name is
embedded in this file.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time
import zlib

REPOSITORY = "fahimahmedb/Quant-Trade"
DEFAULT_REGION = "eu-paris-1"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
VM_RE = re.compile(r"^ocid1\.instance\.[A-Za-z0-9._-]+$")


class DeployBlock(RuntimeError):
    """Fail-closed deployment error."""


def validate_inputs(vm: str, sha: str, region: str) -> tuple[str, str, str]:
    sha = (sha or "").strip().lower()
    vm = (vm or "").strip()
    region = (region or "").strip()
    if not SHA_RE.fullmatch(sha):
        raise DeployBlock("INVALID_DEPLOY_SHA")
    if not VM_RE.fullmatch(vm):
        raise DeployBlock("INVALID_VM_OCID")
    if not region or any(ch.isspace() for ch in region):
        raise DeployBlock("INVALID_REGION")
    return vm, sha, region


def oci(*args: str, region: str) -> dict:
    list_operations = {
        ("compute", "instance", "list-vnics"),
        ("instance-agent", "plugin", "list"),
        ("iam", "region-subscription", "list"),
        ("iam", "dynamic-group", "list"),
        ("iam", "policy", "list"),
    }
    operation = "oci " + " ".join(args[:3])
    process = subprocess.run(
        ["oci", "--region", region, *args, "--output", "json", "--query", "@"],
        capture_output=True,
        text=True,
        check=False,
    )
    if process.returncode:
        raise DeployBlock(
            operation
            + f" failed (code {process.returncode}): "
            + (process.stderr.strip() or "no stderr detail")
        )
    raw = process.stdout.strip()
    if not raw:
        if args[:3] in list_operations and not process.stderr.strip():
            return {"data": []}
        raise DeployBlock(
            "OCI_EMPTY_RESPONSE:"
            + operation
            + ":"
            + (process.stderr.strip() or "code 0 with no usable response")
        )
    try:
        response = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DeployBlock(f"OCI_INVALID_JSON:{operation}:{exc}") from exc
    if not isinstance(response, dict):
        raise DeployBlock(f"OCI_UNEXPECTED_RESPONSE:{operation}")
    if "data" not in response:
        if args[:3] in list_operations and set(response) <= {"etag", "opc-request-id"}:
            return dict(response, data=[])
        raise DeployBlock(f"OCI_DATA_MISSING:{operation}")
    return response


def repair_agent_iam(*, vm: str, region: str) -> None:
    """Grant only this instance permission to consume its own Run Commands."""
    instance = oci("compute", "instance", "get", "--instance-id", vm, region=region)["data"]
    if instance.get("lifecycle-state") != "RUNNING":
        raise DeployBlock("VM_NOT_RUNNING")
    compartment = instance["compartment-id"]
    plugins = oci(
        "instance-agent",
        "plugin",
        "list",
        "--compartment-id",
        compartment,
        "--instanceagent-id",
        vm,
        "--name",
        "Compute Instance Run Command",
        region=region,
    )["data"]
    if not any(plugin.get("status") == "RUNNING" for plugin in plugins):
        raise DeployBlock("RUN_COMMAND_PLUGIN_NOT_RUNNING")

    tenancy = compartment
    seen = set()
    while not tenancy.startswith("ocid1.tenancy."):
        if tenancy in seen:
            raise DeployBlock("IAM_HIERARCHY_LOOP")
        seen.add(tenancy)
        tenancy = oci(
            "iam", "compartment", "get", "--compartment-id", tenancy, region=region
        )["data"]["compartment-id"]

    subscriptions = oci(
        "iam", "region-subscription", "list", "--tenancy-id", tenancy, "--all", region=region
    )["data"]
    home_regions = [item["region-name"] for item in subscriptions if item.get("is-home-region")]
    if len(home_regions) != 1:
        raise DeployBlock("IAM_HOME_REGION_NOT_UNIQUE")
    home_region = home_regions[0]

    name = "QuantRunCommand-" + vm[-16:]
    rule = "ALL {instance.id = '" + vm + "'}"
    groups = oci(
        "iam", "dynamic-group", "list", "--compartment-id", tenancy, "--all", region=home_region
    )["data"]
    group = next((item for item in groups if item.get("name") == name), None)
    if group is None:
        group = oci(
            "iam",
            "dynamic-group",
            "create",
            "--compartment-id",
            tenancy,
            "--name",
            name,
            "--description",
            "Quant-Trade: this VM may consume only its own Run Commands",
            "--matching-rule",
            rule,
            "--wait-for-state",
            "ACTIVE",
            "--max-wait-seconds",
            "60",
            "--wait-interval-seconds",
            "3",
            region=home_region,
        )["data"]
    if group.get("matching-rule") != rule or group.get("lifecycle-state") != "ACTIVE":
        raise DeployBlock("EXISTING_DYNAMIC_GROUP_INCOMPATIBLE")

    scope = "tenancy" if compartment == tenancy else "compartment id " + compartment
    statement = (
        "Allow dynamic-group id "
        + group["id"]
        + " to use instance-agent-command-execution-family in "
        + scope
        + " where request.instance.id=target.instance.id"
    )
    policies = oci(
        "iam", "policy", "list", "--compartment-id", compartment, "--all", region=home_region
    )["data"]
    policy = next((item for item in policies if item.get("name") == name), None)
    if policy is None:
        policy = oci(
            "iam",
            "policy",
            "create",
            "--compartment-id",
            compartment,
            "--name",
            name,
            "--description",
            "Quant-Trade: instance-bound Run Command execution only",
            "--statements",
            json.dumps([statement]),
            region=home_region,
        )["data"]
    if policy.get("statements") != [statement]:
        raise DeployBlock("EXISTING_IAM_POLICY_INCOMPATIBLE")


def remote_bootstrap(sha: str) -> str:
    """Small remote bootstrap; installer logic remains versioned at the target SHA."""
    raw_url = (
        f"https://raw.githubusercontent.com/{REPOSITORY}/{sha}/"
        "deploy/oracle_release_install.py"
    )
    program = (
        "import sys,urllib.request;"
        f"u={raw_url!r};"
        "d=urllib.request.urlopen(u,timeout=60).read(262144);"
        "assert d, 'EMPTY_INSTALLER';"
        "c=compile(d,u,'exec');"
        "g={'__name__':'__main__','__file__':u};"
        "sys.argv=['oracle_release_install.py','--sha',"
        + repr(sha)
        + "];exec(c,g,g)"
    )
    packed = base64.b64encode(zlib.compress(program.encode())).decode()
    command = "python3 -c " + shlex.quote(
        "import base64,zlib;exec(zlib.decompress(base64.b64decode(" + repr(packed) + ")))"
    )
    if len(command.encode()) >= 4096:
        raise DeployBlock("OCI_RUN_COMMAND_PAYLOAD_TOO_LARGE")
    return command


def remote_inventory_bootstrap(sha: str) -> str:
    """Run only the versioned read-only probe; no release/model installation."""
    sha = validate_inputs('ocid1.instance.inventory', sha, DEFAULT_REGION)[1]
    raw_url = f'https://raw.githubusercontent.com/{REPOSITORY}/{sha}/deploy/oracle_model_inventory.py'
    program = (
        "import sys,urllib.request;"
        f"u={raw_url!r};"
        "d=urllib.request.urlopen(u,timeout=30).read(262144);"
        "assert d, 'EMPTY_INVENTORY_PROBE';"
        "sys.argv=['oracle_model_inventory.py'];"
        "exec(compile(d,u,'exec'),{'__name__':'__main__','__file__':u})"
    )
    return 'python3 -c ' + shlex.quote(program)


def state_path(*, vm: str, sha: str, operation: str = 'install') -> Path:
    identity_text = vm + '\0' + sha + ('' if operation == 'install' else '\0' + operation)
    identity = hashlib.sha256(identity_text.encode()).hexdigest()[:20]
    return Path.home() / ".cache" / "quant-oci-research-os" / f"{identity}.json"


def try_ssh(*, vm: str, sha: str, region: str, command: str) -> int | None:
    instance = oci("compute", "instance", "get", "--instance-id", vm, region=region)["data"]
    if instance.get("lifecycle-state") != "RUNNING":
        raise DeployBlock("VM_NOT_RUNNING")
    vnics = oci("compute", "instance", "list-vnics", "--instance-id", vm, region=region)["data"]
    ips = [item.get("public-ip") for item in vnics if item.get("public-ip")]
    keys = [None] + [
        str(path.with_suffix(""))
        for path in (Path.home() / ".ssh").glob("*.pub")
        if path.with_suffix("").is_file()
    ]
    for ip in ips[:1]:
        for key in keys:
            ssh = [
                "ssh",
                "-oBatchMode=yes",
                "-oConnectTimeout=6",
                "-oConnectionAttempts=1",
                "-oStrictHostKeyChecking=accept-new",
            ]
            if key:
                ssh += ["-oIdentitiesOnly=yes", "-i", key]
            ssh += ["ubuntu@" + ip]
            try:
                probe = subprocess.run(
                    ssh + ["python3 -c 'print(81273)'"],
                    capture_output=True,
                    text=True,
                    timeout=9,
                    check=False,
                )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
            if probe.returncode == 0 and probe.stdout.strip() == "81273":
                return subprocess.run(ssh + [command], check=False).returncode
    return None


def get_or_create_command(*, vm: str, sha: str, region: str, command: str, operation: str = 'install') -> str:
    if operation not in ('install', 'inventory'):
        raise DeployBlock('UNKNOWN_OCI_OPERATION')
    path = state_path(vm=vm, sha=sha) if operation == 'install' else state_path(vm=vm, sha=sha, operation=operation)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.exists():
        state = json.loads(path.read_text())
        if state.get("vm") != vm or state.get("sha") != sha or state.get("region") != region or state.get('operation', 'install') != operation:
            raise DeployBlock("DEPLOY_STATE_IDENTITY_MISMATCH")
        return state["command_id"]

    instance = oci("compute", "instance", "get", "--instance-id", vm, region=region)["data"]
    if instance.get("lifecycle-state") != "RUNNING":
        raise DeployBlock("VM_NOT_RUNNING")
    content = {
        "source": {"sourceType": "TEXT", "text": command},
        "output": {"outputType": "TEXT"},
    }
    target = {"instanceId": vm}
    created = oci(
        "instance-agent",
        "command",
        "create",
        "--compartment-id",
        instance["compartment-id"],
        "--target",
        json.dumps(target),
        "--content",
        json.dumps(content),
        "--timeout-in-seconds",
        "1200",
        "--display-name",
        "Quant-Trade read-only model inventory" if operation == 'inventory' else "Quant-Trade verified Research OS installation; scheduler disabled",
        region=region,
    )
    command_id = created["data"]["id"]
    pending = path.with_suffix(".tmp")
    pending.write_text(
        json.dumps(
            {"vm": vm, "sha": sha, "region": region, "command_id": command_id, 'operation': operation},
            sort_keys=True,
        )
        + "\n"
    )
    pending.chmod(0o600)
    pending.replace(path)
    return command_id


def wait_for_command(*, vm: str, command_id: str, region: str, attempts: int) -> int:
    for index in range(attempts):
        execution = oci(
            "instance-agent",
            "command-execution",
            "get",
            "--command-id",
            command_id,
            "--instance-id",
            vm,
            region=region,
        )["data"]
        status = execution.get("lifecycle-state")
        if index % 6 == 0:
            print(status, flush=True)
        if status in {"SUCCEEDED", "FAILED", "TIMED_OUT", "CANCELED"}:
            output = execution.get("content") or {}
            print(output.get("text") or output.get("message") or status)
            return 0 if status == "SUCCEEDED" and output.get("exit-code") == 0 else 1
        time.sleep(10)
    print("BLOCK_AGENT_DELIVERY: no terminal execution state confirmed; command retained")
    return 2


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--vm", required=True, help="Oracle Compute instance OCID")
    parser.add_argument("--sha", required=True, help="Exact 40-hex Git commit to deploy")
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--repair-agent", action="store_true")
    parser.add_argument("--skip-ssh", action="store_true")
    parser.add_argument('--inventory', action='store_true', help='Read-only model/host inventory; no installation')
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    vm, sha, region = validate_inputs(args.vm, args.sha, args.region)
    command = remote_inventory_bootstrap(sha) if args.inventory else remote_bootstrap(sha)

    if not args.skip_ssh:
        ssh_result = try_ssh(vm=vm, sha=sha, region=region, command=command)
        if ssh_result is not None:
            return ssh_result

    kwargs = {'operation': 'inventory'} if args.inventory else {}
    command_id = get_or_create_command(vm=vm, sha=sha, region=region, command=command, **kwargs)
    print("Oracle command: " + command_id, flush=True)
    if args.repair_agent:
        execution = oci(
            "instance-agent",
            "command-execution",
            "get",
            "--command-id",
            command_id,
            "--instance-id",
            vm,
            region=region,
        )["data"]
        if execution.get("lifecycle-state") == "ACCEPTED":
            repair_agent_iam(vm=vm, region=region)
    return wait_for_command(
        vm=vm,
        command_id=command_id,
        region=region,
        attempts=210 if args.repair_agent else 90,
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (DeployBlock, OSError, ValueError, KeyError, AssertionError) as exc:
        raise SystemExit("BLOCK_DEPLOYMENT: " + str(exc))
