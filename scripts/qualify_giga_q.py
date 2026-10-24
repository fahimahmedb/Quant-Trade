#!/usr/bin/env python3
"""Qualify one immutable GIGA Q revision; evidence never grants execution authority."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "ebc72b9fd14f91420c37e0b7607f9bfb584a289a"
VERTICAL = "92c4ee0a5e2d9387167f6deec24e7edec1c15b6d"
BRANCH = "builder/giga-q-final-whole-system-hardening-20261023"
NORTH_STAR = "a328b4e6d7d71dafd532938888ebf9818b1b610f"
ARCHITECTURAL_BLOCKERS = {
    "B01": "Production Multi-Source proposal-to-Discovery lineage is not established",
    "B02": "Native economic identity-to-shared wire contract binding is unresolved",
    "B03": "Full retained hostile corpus requires semantic triage and further repairs",
}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--verify-remote", action="store_true")
    args = parser.parse_args()
    if sys.flags.optimize:
        parser.error("qualification requires assertion checks enabled")
    output = args.output_dir.resolve()
    if output.is_relative_to(ROOT):
        parser.error("evidence output must be outside the qualified worktree")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("use an empty evidence directory to prevent stale receipt reuse")
    head = git("rev-parse", "HEAD")
    receipt = {"mission": "GIGA_Q", "head": head, "tree": git("rev-parse", "HEAD^{tree}"),
               "immutable_base": BASE, "north_star_blob": NORTH_STAR,
               "historical_v_sha": VERTICAL, "checks": [], "mission_qualified": False}
    env = dict(os.environ, PYTHONPATH=os.pathsep.join((str(ROOT / "src"), str(ROOT), str(ROOT / "tests"))))

    def run(name, command, *, cwd=ROOT, timeout=900):
        start = time.monotonic()
        log = output / f"{name}.log"
        with log.open("w") as handle:
            try:
                result = subprocess.run(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                        stdout=handle, stderr=subprocess.STDOUT, timeout=timeout)
                code = result.returncode
            except (OSError, subprocess.TimeoutExpired) as error:
                handle.write(f"QUALIFICATION_COMMAND_ERROR:{type(error).__name__}\n")
                code = 124
        check = {"name": name, "exit_code": code, "seconds": round(time.monotonic() - start, 3),
                 "log": log.name, "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest()}
        receipt["checks"].append(check)
        print(f"{name}: {'PASS' if code == 0 else 'FAIL'}", flush=True)

    def invariant(name, operation):
        try:
            operation()
            passed = True
        except (AssertionError, ValueError, OSError, subprocess.SubprocessError):
            passed = False
        receipt[name] = passed
        print(f"{name}: {'PASS' if passed else 'FAIL'}", flush=True)

    def initial():
        assert not git("status", "--porcelain")
        assert git("rev-parse", "HEAD:QUANT_NORTH_STAR.md") == NORTH_STAR
        assert git("branch", "--show-current") in ("", BRANCH)
        subprocess.run(["git", "merge-base", "--is-ancestor", BASE, head], cwd=ROOT, check=True)
        assert not git("rev-list", "--merges", f"{BASE}..{head}")

    def remote():
        advertised = git("ls-remote", "--heads", "origin", "refs/heads/" + BRANCH).split()
        assert advertised == [head, "refs/heads/" + BRANCH]

    invariant("initial_identity_and_clean_tree", initial)
    if args.verify_remote:
        invariant("initial_remote_match", remote)
    else:
        receipt["initial_remote_match"] = None

    python = sys.executable
    focused = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "tests").glob("test_giga_q_*.py"))
    run("focused_repairs", [python, "-m", "pytest", "-q", *focused])
    run("root_unittest", [python, "-m", "unittest", "discover", "-s", "tests", "-q"])
    run("root_pytest", [python, "-m", "pytest", "-q", "tests"])
    run("research_unittest", [python, "-m", "unittest", "discover", "-s", "research/research_os/tests", "-q"])
    run("research_pytest", [python, "-m", "pytest", "-q", "research/research_os/tests"])
    run("live_lab_js", ["node", "--test", *map(str, sorted((ROOT / "research/live_lab_ux/tests").glob("*.test.js")))])
    run("schemas", [python, "scripts/generate_schemas.py", "--check"])
    run("status_freshness", [python, "scripts/status_artifacts.py", "--check"])
    run("v1_demo", [python, "scripts/demo_quant_system.py"])

    def authority():
        sys.path[:0] = [str(ROOT), str(ROOT / "src")]
        from research.research_os.control_plane import load_control_plane
        from research.research_os.expansion.v2_core import CLOSED_AUTHORITY
        from research.research_os.expansion.scientific_adjudication import AUTHORITY_STATE as c0
        from research.research_os.expansion.economic_lifecycle import authority_state
        from research.research_os.discovery_engine import AUTHORITY as discovery
        base = ROOT / "research/research_os"
        control = load_control_plane(base)
        assert control["status"] == "PASS"
        for mapping in (CLOSED_AUTHORITY, c0, authority_state(), discovery,
                        json.loads((base / "runtime/V2_CORE_POLICY.json").read_text())["authority"],
                        json.loads((base / "runtime/RESEARCH_FRONTIER.json").read_text())["authority"]):
            assert mapping and all(value is False for value in mapping.values())
        membrane = json.loads((base / "runtime/V2_CORE_POLICY.json").read_text())["evaluation_membrane"]
        assert membrane["status"] == "SEALED"
        for key in ("research_outcome_read_capability", "research_supervisor_outcome_read_capability",
                    "evaluation_research_write_capability"):
            assert membrane[key] is False

    invariant("closed_authority_and_outcome_policy", authority)

    # Retain historical tests byte-for-byte; replay current production source,
    # never old implementation. A disposable checkout preserves fixture paths.
    replay = output / "historical-worktree"
    try:
        paths = git("ls-tree", "-r", "--name-only", VERTICAL, "tests").splitlines()
        paths = [p for p in paths if Path(p).name.startswith("test_vertical_") and p.endswith(".py")]
        assert paths
        subprocess.run(["git", "worktree", "add", "--detach", str(replay), head], cwd=ROOT,
                       check=True, stdout=subprocess.DEVNULL)
        for path in paths:
            data = subprocess.check_output(["git", "show", f"{VERTICAL}:{path}"], cwd=ROOT)
            (replay / path).write_bytes(data)
        replay_env = os.pathsep.join((str(replay / "src"), str(replay), str(replay / "tests")))
        previous = env["PYTHONPATH"]
        env["PYTHONPATH"] = replay_env
        try:
            run("historical_v", [python, "-m", "pytest", "-q", *paths,
                                 "--junitxml=" + str(output / "historical-v.xml")], cwd=replay)
        finally:
            env["PYTHONPATH"] = previous
        counts = Counter()
        cases = []
        for case in ET.parse(output / "historical-v.xml").findall(".//testcase"):
            failed = case.find("failure") is not None or case.find("error") is not None
            counts["failed" if failed else "passed"] += 1
            if failed:
                cases.append({"module": case.get("classname"), "test": case.get("name")})
        index = {"production_head": head, "fixture_sha": VERTICAL, "fixture_files": paths,
                 "case_counts": dict(counts), "failed_cases": cases,
                 "failure_count_is_independent_defect_count": False}
        (output / "historical-case-index.json").write_text(json.dumps(index, indent=2) + "\n")
        receipt["historical_case_counts"] = dict(counts)
    except (AssertionError, OSError, subprocess.SubprocessError, ET.ParseError):
        receipt["historical_replay_unavailable"] = True
    finally:
        if replay.exists():
            subprocess.run(["git", "worktree", "remove", "--force", str(replay)], cwd=ROOT,
                           check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def final():
        assert git("rev-parse", "HEAD") == head
        assert not git("status", "--porcelain")

    invariant("final_exact_head_and_clean_tree", final)
    if args.verify_remote:
        invariant("final_remote_match", remote)
    else:
        receipt["final_remote_match"] = None
    receipt["ordinary_regression_passed"] = all(c["exit_code"] == 0 for c in receipt["checks"] if c["name"] != "historical_v")
    receipt["mandatory_attack_regression_passed"] = (
        receipt.get("historical_case_counts", {}).get("failed", 0) == 0
        and receipt.get("historical_case_counts", {}).get("passed", 0) > 0
        and not receipt.get("historical_replay_unavailable", False)
    )
    # Matrices record unresolved required handoffs and external operational proof.
    # Passing a local suite cannot erase those independently recorded blockers.
    receipt["architectural_blockers"] = ARCHITECTURAL_BLOCKERS
    receipt["mission_qualified"] = (
        receipt["ordinary_regression_passed"] and receipt["mandatory_attack_regression_passed"]
        and not ARCHITECTURAL_BLOCKERS
        and all(receipt.get(key) is True for key in (
            "initial_identity_and_clean_tree", "final_exact_head_and_clean_tree",
            "initial_remote_match", "final_remote_match", "closed_authority_and_outcome_policy"))
    )
    receipt["safe_for_post_wave2_convergence"] = receipt["mission_qualified"]
    (output / "qualification.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("GIGA_Q_MISSION_QUALIFICATION=" + ("PASS" if receipt["mission_qualified"] else "BLOCKED"), flush=True)
    return 0 if receipt["mission_qualified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
