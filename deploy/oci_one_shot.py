#!/usr/bin/env python3
"""CloudShell installer for the qualified, pre-outcome release. No scheduler starts."""
import base64
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time
import zlib

VM = "ocid1.instance.oc1.eu-paris-1.anrwiljrtoradqacmugziwzu3sls2orieua6i7vkjveiq7q5wsiypa3mejpa"
REGION = "eu-paris-1"
HEAD = "e980d201d3c84d16d7d91fde0d27a06c9a2c3121"
REMOTE = r'''
import fcntl, io, json, os, platform, subprocess, sys, tarfile, tempfile, urllib.request
from pathlib import Path
sha = "e980d201d3c84d16d7d91fde0d27a06c9a2c3121"
assert sys.version_info >= (3, 12), "Python 3.12+ requis"
base = Path.home() / "Quant-Trade-qualified"
base.mkdir(mode=0o700, exist_ok=True)
lock = (base / "install.lock").open("a")
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
release = base / sha
receipt = base / "installed.json"
if release.exists():
    assert receipt.exists() and json.loads(receipt.read_text())["sha"] == sha, "Installation existante inconnue: aucune modification"
else:
    url = "https://codeload.github.com/fahimahmedb/Quant-Trade/tar.gz/" + sha
    with tempfile.TemporaryDirectory(prefix=".install-", dir=base) as tmp:
        with urllib.request.urlopen(url, timeout=60) as response:
            archive = response.read(64 * 1024 * 1024 + 1)
        assert len(archive) <= 64 * 1024 * 1024, "Archive trop grande"
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
            tar.extractall(tmp, filter="data")
        source = Path(tmp) / ("Quant-Trade-" + sha)
        assert source.is_dir(), "Archive inattendue"
        # Publish only after verification below; preserve all other installations.
        release = source
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        modules = ["implementability_depth", "experiment_runner_frozen_protocol", "economic_readiness_validation", "economic_identity_portfolio_readiness", "producer_economic_readiness", "economic_readiness_integration"]
        with (base / "verification.log").open("w") as log:
            check = subprocess.run([sys.executable, "-m", "unittest"] + ["research.research_os.tests.test_" + m for m in modules], cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT)
        if check.returncode:
            print((base / "verification.log").read_text()[-1800:])
            raise SystemExit("BLOCK_VERIFICATION")
        release = base / sha
        source.rename(release)
os.chdir(release)
sys.path.insert(0, str(release))
sys.dont_write_bytecode = True
from research.research_os.tests.test_economic_readiness_integration import fixture, legacy
from research.research_os.expansion.economic_test_readiness_v1 import economic_test_readiness, AUTHORITY, READY
r = economic_test_readiness(fixture(), legacy=legacy())
assert r["status"] == READY and r["authority"] == AUTHORITY
assert r["outcome_accessed"] is False and r["economic_result"] == "NOT_OBSERVED"
result = dict(status="INSTALLED_VERIFIED", sha=sha, path=str(release), python=platform.python_version(), architecture=platform.machine(), synthetic_readiness=r["status"], outcome_accessed=False, scheduler_started=False, authority=AUTHORITY)
pending = base / "installed.json.tmp"
pending.write_text(json.dumps(result, indent=2) + "\n")
pending.replace(receipt)
print(json.dumps(result))
'''


def oci(*args, region=REGION):
    # Oracle's renderer prints nothing for some successful, empty list responses.
    # Never interpret an empty GET or a failed request as an empty collection.
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
        capture_output=True, text=True)
    if process.returncode:
        raise RuntimeError(operation + " a echoue (code " + str(process.returncode) + "): "
                           + (process.stderr.strip() or "aucun detail stderr"))
    raw = process.stdout.strip()
    if not raw:
        if args[:3] in list_operations and not process.stderr.strip():
            return {"data": []}
        raise RuntimeError("OCI_EMPTY_RESPONSE: " + operation + "; "
                           + (process.stderr.strip() or "code 0 mais aucune reponse exploitable"))
    try:
        response = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("OCI_INVALID_JSON: " + operation + "; " + str(exc)) from exc
    if not isinstance(response, dict):
        raise RuntimeError("OCI_UNEXPECTED_RESPONSE: " + operation)
    if "data" not in response:
        if args[:3] in list_operations and set(response) <= {"etag", "opc-request-id"}:
            return dict(response, data=[])
        raise RuntimeError("OCI_DATA_MISSING: " + operation)
    return response


def repair_agent_iam():
    """Add only the documented right for this instance to consume its commands."""
    instance = oci("compute", "instance", "get", "--instance-id", VM)["data"]
    assert instance["lifecycle-state"] == "RUNNING", "VM non RUNNING"
    compartment = instance["compartment-id"]
    plugins = oci("instance-agent", "plugin", "list", "--compartment-id", compartment,
                  "--instanceagent-id", VM, "--name", "Compute Instance Run Command")["data"]
    assert any(p["status"] == "RUNNING" for p in plugins), "Plugin Run Command non RUNNING"
    tenancy = compartment
    seen = set()
    while not tenancy.startswith("ocid1.tenancy."):
        assert tenancy not in seen, "Hierarchie IAM invalide"
        seen.add(tenancy)
        tenancy = oci("iam", "compartment", "get", "--compartment-id", tenancy)["data"]["compartment-id"]
    subscriptions = oci("iam", "region-subscription", "list", "--tenancy-id", tenancy, "--all")["data"]
    home_regions = [r["region-name"] for r in subscriptions if r["is-home-region"]]
    assert len(home_regions) == 1, "Region IAM principale introuvable"
    home_region = home_regions[0]
    name = "QuantRunCommand-" + VM[-16:]
    rule = "ALL {instance.id = '" + VM + "'}"
    groups = oci("iam", "dynamic-group", "list", "--compartment-id", tenancy, "--all", region=home_region)["data"]
    group = next((g for g in groups if g["name"] == name), None)
    if group is None:
        print("Creation du groupe IAM limite a cette VM…", flush=True)
        group = oci("iam", "dynamic-group", "create", "--compartment-id", tenancy,
                    "--name", name, "--description", "Quant: this VM may consume only its own Run Commands",
                    "--matching-rule", rule, "--wait-for-state", "ACTIVE", "--max-wait-seconds", "60",
                    "--wait-interval-seconds", "3", region=home_region)["data"]
    assert group["matching-rule"] == rule and group["lifecycle-state"] == "ACTIVE", "Groupe IAM existant incompatible; aucun remplacement"
    scope = "tenancy" if compartment == tenancy else "compartment id " + compartment
    statement = ("Allow dynamic-group id " + group["id"] + " to use instance-agent-command-execution-family in "
                 + scope + " where request.instance.id=target.instance.id")
    policies = oci("iam", "policy", "list", "--compartment-id", compartment, "--all", region=home_region)["data"]
    policy = next((p for p in policies if p["name"] == name), None)
    if policy is None:
        print("Ajout du droit de recuperer uniquement ses propres commandes…", flush=True)
        policy = oci("iam", "policy", "create", "--compartment-id", compartment, "--name", name,
                     "--description", "Quant: instance-bound Run Command execution only",
                     "--statements", json.dumps([statement]), region=home_region)["data"]
    assert policy["statements"] == [statement], "Politique IAM existante incompatible; aucun remplacement"
    print("Prerequis IAM configure. Propagation Oracle: jusqu'a 30 min. Suivi de la meme commande…", flush=True)


def main():
    repair = "--repair-agent" in sys.argv[1:]
    cache = Path.home() / ".cache" / "quant-oci-one-shot"
    cache.mkdir(parents=True, mode=0o700, exist_ok=True)
    state = cache / "command.json"
    assert not repair or state.exists(), "Etat de reprise absent; aucune nouvelle commande creee"
    if state.exists():
        saved = json.loads(state.read_text())
        assert saved["vm"] == VM and saved["sha"] == HEAD, "Etat de reprise incompatible"
        command = saved["command"]
        print("Reprise de la commande existante.", flush=True)
        execution = oci("instance-agent", "command-execution", "get", "--command-id", command, "--instance-id", VM)["data"]
        if repair and execution["lifecycle-state"] == "ACCEPTED":
            repair_agent_iam()
    else:
        instance = oci("compute", "instance", "get", "--instance-id", VM)["data"]
        vnics = oci("compute", "instance", "list-vnics", "--instance-id", VM)["data"]
        ips = [v["public-ip"] for v in vnics if v.get("public-ip")]
        # No password prompt, no key generation, no firewall/IAM changes.
        keys = [None] + [str(p.with_suffix("")) for p in (Path.home() / ".ssh").glob("*.pub") if p.with_suffix("").is_file()]
        for ip in ips[:1]:
            for key in keys:
                ssh = ["ssh", "-oBatchMode=yes", "-oConnectTimeout=6", "-oConnectionAttempts=1", "-oStrictHostKeyChecking=accept-new"]
                if key:
                    ssh += ["-oIdentitiesOnly=yes", "-i", key]
                ssh += ["ubuntu@" + ip]
                try:
                    probe = subprocess.run(ssh + ["python3 -c 'print(81273)'"], capture_output=True, text=True, timeout=9)
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
                if probe.returncode == 0 and probe.stdout.strip() == "81273":
                    print("Installation par SSH…", flush=True)
                    return subprocess.run(ssh + ["python3 -"], input=REMOTE, text=True).returncode
        print("SSH indisponible ; installation par l'agent OCI…", flush=True)
        packed = base64.b64encode(zlib.compress(REMOTE.encode())).decode()
        payload = "python3 -c " + shlex.quote("import zlib,base64;exec(zlib.decompress(base64.b64decode(" + repr(packed) + ")))" )
        assert len(payload.encode()) < 4096, "Limite OCI depassee"
        content = {"source": {"sourceType": "TEXT", "text": payload}, "output": {"outputType": "TEXT"}}
        target = {"instanceId": VM}
        created = oci("instance-agent", "command", "create", "--compartment-id", instance["compartment-id"], "--target", json.dumps(target), "--content", json.dumps(content), "--timeout-in-seconds", "900", "--display-name", "Quant qualified code installation; no worker execution")
        command = created["data"]["id"]
        state.write_text(json.dumps(dict(vm=VM, sha=HEAD, command=command)))
        state.chmod(0o600)
    print("Commande : " + command, flush=True)
    for n in range(211 if repair else 91):
        execution = oci("instance-agent", "command-execution", "get", "--command-id", command, "--instance-id", VM)["data"]
        status = execution["lifecycle-state"]
        if n % 6 == 0:
            print(status, flush=True)
        if status in {"SUCCEEDED", "FAILED", "TIMED_OUT", "CANCELED"}:
            output = execution.get("content") or {}
            print(output.get("text") or output.get("message") or status)
            return 0 if status == "SUCCEEDED" and output.get("exit-code") == 0 else 1
        if not repair and n == 12 and status == "ACCEPTED":
            print("BLOCK_AGENT_DELIVERY: aucune execution confirmee. Un plugin RUNNING ne prouve pas ses droits IAM. Diagnostic/correction: python3 ~/qt-install.py --repair-agent")
            return 2
        time.sleep(10)
    print("BLOCK_AGENT_DELIVERY: execution non confirmee apres attente. Commande conservee; la cause doit etre verifiee dans les journaux de l'agent. Aucun succes d'installation declare.")
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, AssertionError, RuntimeError, subprocess.CalledProcessError) as exc:
        raise SystemExit("BLOCK_INSTALLATION: " + str(exc))
