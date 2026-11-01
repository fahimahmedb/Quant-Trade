#!/usr/bin/env python3
"""One-shot repository administration / read-only host inventory. No scheduler."""
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request

REPO = "fahimahmedb/Quant-Trade"
PROJECT = "project/canonical"
CODE = "code/canonical"
OLD_DEFAULT = "blue/master-v2-2026-09-20"
RULESET = {
    "name": "canonical-history-integrity",
    "target": "branch",
    "enforcement": "active",
    "bypass_actors": [],
    "conditions": {"ref_name": {
        "include": ["refs/heads/project/canonical", "refs/heads/code/canonical"],
        "exclude": [],
    }},
    "rules": [{"type": "deletion"}, {"type": "non_fast_forward"}],
}


class Blocked(RuntimeError):
    pass


def same_ruleset(actual):
    expected = json.loads(json.dumps(RULESET))
    current = {key: actual.get(key) for key in expected}
    for value in (expected, current):
        try:
            value["conditions"]["ref_name"]["include"] = sorted(value["conditions"]["ref_name"]["include"])
            value["rules"] = sorted(value["rules"], key=lambda rule: rule["type"])
        except (KeyError, TypeError):
            return False
    return current == expected


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class GitHub:
    def __init__(self, token):
        self.token = token

    def request(self, path="", *, method="GET", payload=None):
        if not path.startswith("/") and path:
            raise Blocked("INVALID_API_PATH")
        url = "https://api.github.com/repos/" + REPO + path
        req = urllib.request.Request(url, method=method,
            data=None if payload is None else json.dumps(payload).encode(), headers={
                "Authorization": "Bearer " + self.token,
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "X-GitHub-Api-Version": "2022-11-28",
            })
        try:
            with urllib.request.build_opener(NoRedirect()).open(req, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            raise Blocked("GITHUB_HTTP_" + str(exc.code)) from None
        except (OSError, ValueError):
            raise Blocked("GITHUB_RESPONSE_UNAVAILABLE") from None

    def pages(self, path):
        result = []
        for page in range(1, 21):
            batch = self.request(path + ("&" if "?" in path else "?") +
                                 "per_page=100&page=" + str(page))
            if not isinstance(batch, list):
                raise Blocked("INVALID_PAGINATED_RESPONSE")
            result.extend(batch)
            if len(batch) < 100:
                return result
        raise Blocked("PAGINATION_BOUND_EXCEEDED")


def require(env, *keys):
    missing = [key for key in keys if not env.get(key, "").strip()]
    if missing:
        raise Blocked("SETUP_REQUIRED:" + ",".join(missing))


def workflow(api, ref):
    data = api.request("/contents/.github/workflows/data-feeds.yml?ref=" +
                       urllib.parse.quote(ref, safe=""))
    try:
        return base64.b64decode(data["content"], validate=False).decode("utf-8")
    except (KeyError, ValueError, UnicodeError):
        raise Blocked("COLLECTOR_WORKFLOW_UNREADABLE") from None


def switch_default(api):
    meta = api.request()
    before = meta["default_branch"]
    if before not in (OLD_DEFAULT, PROJECT):
        raise Blocked("UNEXPECTED_CURRENT_DEFAULT")
    for branch in (PROJECT, CODE):
        api.request("/branches/" + urllib.parse.quote(branch, safe=""))
    for pr in api.pages("/pulls?state=open"):
        if OLD_DEFAULT in (pr["base"]["ref"], pr["head"]["ref"]):
            raise Blocked("OPEN_PR_STILL_USES_OLD_DEFAULT")
    project, code, old = (workflow(api, ref) for ref in (PROJECT, CODE, OLD_DEFAULT))
    if project != code or not re.search(r"\bref:\s*code/canonical\b", project):
        raise Blocked("CANONICAL_COLLECTOR_WORKFLOWS_DIFFER")
    cron = lambda text: re.findall(r"cron:\s*['\"]([^'\"]+)['\"]", text)
    if not cron(old) or cron(old) != cron(project):
        raise Blocked("COLLECTOR_SCHEDULE_CHANGED")
    if meta.get("has_pages"):
        raise Blocked("PAGES_NEEDS_EXPLICIT_MIGRATION")
    environments = api.request("/environments?per_page=100")
    if environments.get("total_count", 0):
        raise Blocked("ENVIRONMENT_POLICIES_REQUIRE_REVIEW")
    if api.pages("/deployments"):
        raise Blocked("DEPLOYMENT_REFERENCES_REQUIRE_REVIEW")
    if api.pages("/rulesets"):
        raise Blocked("EXISTING_RULESETS_REQUIRE_REVIEW")
    if before != PROJECT:
        api.request(method="PATCH", payload={"default_branch": PROJECT})
    if api.request()["default_branch"] != PROJECT:
        raise Blocked("DEFAULT_READBACK_MISMATCH")
    return {"status": "DEFAULT_SWITCH_VERIFIED", "before": before, "after": PROJECT,
            "collector_checkout": CODE, "schedule": cron(project),
            "scheduled_execution_after_switch": "PENDING_OBSERVATION"}


def protect(api):
    names = {branch["name"] for branch in api.pages("/branches")}
    if names != {PROJECT, CODE}:
        raise Blocked("RETIRE_RESIDUAL_REFS_BEFORE_PROTECTION")
    if api.request()["default_branch"] != PROJECT:
        raise Blocked("DEFAULT_MUST_BE_PROJECT_CANONICAL")
    existing = [r for r in api.pages("/rulesets") if r["name"] == RULESET["name"]]
    if len(existing) > 1:
        raise Blocked("AMBIGUOUS_RULESET")
    if existing:
        actual = api.request("/rulesets/" + str(existing[0]["id"]))
        if not same_ruleset(actual):
            raise Blocked("EXISTING_RULESET_DIFFERS_NO_OVERWRITE")
    else:
        created = api.request("/rulesets", method="POST", payload=RULESET)
        actual = api.request("/rulesets/" + str(created["id"]))
        if not same_ruleset(actual):
            raise Blocked("RULESET_READBACK_MISMATCH")
    return {"status": "CANONICAL_HISTORY_PROTECTION_VERIFIED", "ruleset_id": actual["id"],
            "ordinary_fast_forward_writes": "ALLOWED_WITH_EXISTING_WRITE_PERMISSION",
            "required_pr_or_status_checks": False, "bypass_actors": []}


def host_inventory(env):
    require(env, "QUANT_ORACLE_HOST", "QUANT_ORACLE_USER", "QUANT_ORACLE_SSH_KEY",
            "QUANT_ORACLE_KNOWN_HOSTS")
    host, user = env["QUANT_ORACLE_HOST"], env["QUANT_ORACLE_USER"]
    if (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.:-]*", host)
            or not re.fullmatch(r"[a-z_][a-z0-9_-]*", user)):
        raise Blocked("INVALID_SSH_TARGET")
    with tempfile.TemporaryDirectory(prefix="quant-ops-") as directory:
        os.chmod(directory, 0o700)
        key, known = Path(directory) / "key", Path(directory) / "known_hosts"
        for path, value in ((key, env["QUANT_ORACLE_SSH_KEY"]),
                            (known, env["QUANT_ORACLE_KNOWN_HOSTS"])):
            path.write_text(value.rstrip() + "\n"); path.chmod(0o600)
        command = ["ssh", "-T", "-F", "/dev/null", "-oBatchMode=yes", "-oIdentitiesOnly=yes",
                   "-oStrictHostKeyChecking=yes", "-oConnectTimeout=15",
                   "-oUserKnownHostsFile=" + str(known), "-i", str(key),
                   user + "@" + host, "sudo -n python3 -"]
        source = Path(__file__).with_name("quant_host_inventory.py").read_bytes()
        try:
            result = subprocess.run(command, input=source, capture_output=True, timeout=90)
        except (OSError, subprocess.TimeoutExpired):
            raise Blocked("SSH_INVENTORY_UNAVAILABLE") from None
        if result.returncode:
            # ssh stderr may include infrastructure details; never copy it to public logs.
            raise Blocked("SSH_OR_NONINTERACTIVE_SUDO_FAILED")
        try:
            report = json.loads(result.stdout)
        except (ValueError, UnicodeError):
            raise Blocked("HOST_REPORT_INVALID") from None
        if report.get("operation") != "READ_ONLY_HOST_INVENTORY":
            raise Blocked("UNEXPECTED_HOST_REPORT")
        return report


def execute(operation, env, api=None):
    if operation == "check-access":
        return {"status": "READINESS_ONLY", "admin_token_configured": bool(env.get("QUANT_GH_ADMIN_TOKEN")),
                "ssh_configuration_present": all(bool(env.get(k)) for k in (
                    "QUANT_ORACLE_HOST", "QUANT_ORACLE_USER", "QUANT_ORACLE_SSH_KEY", "QUANT_ORACLE_KNOWN_HOSTS")),
                "permissions_verified": False, "mutations": 0}
    if operation == "host-inventory":
        return host_inventory(env)
    if operation not in ("switch-default", "protect-canonicals"):
        raise Blocked("UNKNOWN_OPERATION")
    require(env, "QUANT_GH_ADMIN_TOKEN")
    api = api or GitHub(env["QUANT_GH_ADMIN_TOKEN"])
    return switch_default(api) if operation == "switch-default" else protect(api)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["check-access", "host-inventory", "switch-default", "protect-canonicals"])
    parser.add_argument("--output", default="quant-operations-result.json")
    args = parser.parse_args()
    try:
        report = execute(args.operation, os.environ)
        code = 0
    except Blocked as exc:
        report, code = {"status": "BLOCK", "reason": str(exc)}, 2
    report.update(operation_requested=args.operation, repository=REPO,
                  code_subject_sha=os.environ.get("QUANT_CODE_SUBJECT_SHA", "UNKNOWN"))
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
