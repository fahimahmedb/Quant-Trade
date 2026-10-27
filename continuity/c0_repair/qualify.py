"""Exact-HEAD C0 repair qualification; all run artifacts stay outside the checkout."""
from __future__ import annotations

import argparse
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = "d19b1237636d2311cd42f97f0b02feb55168347b"
W2_SHA = "ebc72b9fd14f91420c37e0b7607f9bfb584a289a"
SOURCE_BRANCH = "codex/verified-autonomous-continuity-oneshot-20261027"
REPAIR_BRANCH = "codex/c0-confirmation-repair-20261027"
STATE_PATHS = ["research/research_os/" + name for name in (
    "runtime", "tasks", "hypotheses", "assessments", "sources", "artifacts",
    "events", "receipts", "legacy",
)] + ["research/edge_lab"]
FROZEN_PATHS = ["src", "research", "deploy", "scripts", "tests", ".github/workflows",
                "STATE.md", "CHIEF_BRIEF.md", "continuity/c0_repair/qualify.py", "continuity/c0_repair/probes"]
ALLOWED_CHANGED = {
    "research/research_os/expansion/scientific_adjudication.py",
    "tests/test_c0_confirmation_count_repair.py",
    "tests/test_research_os_canonical_identity.py",
    "tests/test_research_os_v2_pipeline.py", "STATE.md", "CHIEF_BRIEF.md",
    ".github/workflows/c0-repair-qualification.yml",
}


def utc():
    return datetime.now(timezone.utc).isoformat()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--freeze-file", type=Path,
                        default=ROOT / "continuity/c0_repair/evidence/PRODUCT_FREEZE.json")
    parser.add_argument("--check-source-remote", action="store_true")
    args = parser.parse_args()
    out = args.output_dir.resolve()
    require(not out.is_relative_to(ROOT), "qualification output must be outside checkout")
    out.mkdir(parents=True, exist_ok=True)
    started, head = utc(), git("rev-parse", "HEAD")
    runs, guards = [], []
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src") + os.pathsep + str(ROOT),
           "PYTHONDONTWRITEBYTECODE": "1"}
    freeze_sha = None

    def guard(name, check):
        start = utc()
        try:
            detail = check()
            result, failures = "PASS", []
        except Exception as exc:
            detail, result, failures = None, "FAIL", [str(exc)]
        guards.append({"NAME": name, "HEAD_SHA": head, "START_TIME": start,
                       "END_TIME": utc(), "RESULT": result,
                       "FAILURES": failures, "DETAIL": detail})

    def frozen_product():
        nonlocal freeze_sha
        freeze = json.loads(args.freeze_file.read_text())
        freeze_sha = freeze.get("PRODUCT_FREEZE_SHA") or freeze.get("product_freeze_sha")
        require(isinstance(freeze_sha, str) and len(freeze_sha) == 40, "missing full product freeze SHA")
        subprocess.run(["git", "merge-base", "--is-ancestor", freeze_sha, head], cwd=ROOT, check=True)
        require(not git("diff", "--name-only", freeze_sha, head, "--", *FROZEN_PATHS),
                "product/test/CI/helper changed after freeze")
        return {"PRODUCT_FREEZE_SHA": freeze_sha, "PATHS": FROZEN_PATHS}

    def evidence_manifest():
        path = ROOT / "continuity/c0_repair/evidence/MANIFEST_SHA256.json"
        manifest = json.loads(path.read_text())
        require(manifest.get("SELF_HASHED") is False, "manifest must explicitly exclude itself")
        entries = manifest.get("FILES")
        require(isinstance(entries, list) and bool(entries), "manifest FILES must enumerate its hash domain")
        seen = set()
        for entry in entries:
            relative = Path(entry["PATH"])
            target = (ROOT / relative).resolve()
            require(not relative.is_absolute() and target.is_relative_to(ROOT), "manifest path escapes checkout")
            require(target != path.resolve(), "manifest must not hash itself")
            require(str(relative) not in seen, "duplicate manifest path")
            seen.add(str(relative))
            raw = target.read_bytes()
            require(len(raw) == entry["SIZE"], "manifest size mismatch: " + str(relative))
            require(hashlib.sha256(raw).hexdigest() == entry["SHA256"],
                    "manifest hash mismatch: " + str(relative))
        return {"MANIFEST": str(path.relative_to(ROOT)), "VERIFIED_FILES": len(entries),
                "SELF_HASHED": False}

    def permitted_delta():
        changed = git("diff", "--name-only", SOURCE_SHA, head).splitlines()
        unexpected = [p for p in changed if p not in ALLOWED_CHANGED
                      and not p.startswith("continuity/c0_repair/")
                      and p not in {"continuity/CURRENT_STATE.md", "continuity/EXECUTION_LEDGER.md",
                                    "continuity/evidence/EXECUTION_EVENTS.jsonl", "continuity/DECISION_REGISTER.csv",
                                    "continuity/FOLLOWUP_MISSION_REGISTER.csv", "continuity/PARALLEL_WORK_REGISTER.csv",
                                    "continuity/FINAL_HANDOFF.md"}]
        require(not unexpected, "unexpected source-relative mutation: " + repr(unexpected))
        return changed

    def immutable_source():
        paths = STATE_PATHS + ["continuity/one_shot", "QUANT_NORTH_STAR.md",
                               "research/research_os/expansion/_scientific_adjudication_c0.py"]
        require(not git("diff", "--name-only", SOURCE_SHA, head, "--", *paths),
                "production inputs, prior mission evidence or historical C0 changed")
        return {"SOURCE_SHA": SOURCE_SHA, "PATHS": paths}

    def exact_head():
        require(git("rev-parse", "HEAD") == head, "HEAD changed during qualification")
        require(not git("status", "--porcelain"), "worktree is not clean")
        if os.environ.get("GITHUB_ACTIONS") == "true":
            require(os.environ.get("GITHUB_SHA") == head, "hosted HEAD != GITHUB_SHA")
            require(os.environ.get("GITHUB_REF") == "refs/heads/" + REPAIR_BRANCH,
                    "hosted run is not exact repair branch push")
            require(os.environ.get("GITHUB_EVENT_NAME") == "push", "unexpected hosted event")
        return {"HEAD_SHA": head, "WORKTREE_CLEAN": True}

    def remote_source():
        lines = git("ls-remote", "origin", "refs/heads/" + SOURCE_BRANCH).splitlines()
        require(len(lines) == 1 and lines[0].split()[0] == SOURCE_SHA, "frozen source remote HEAD moved")
        return {"SOURCE_BRANCH": SOURCE_BRANCH, "REMOTE_SOURCE_HEAD": SOURCE_SHA}

    guard("initial_exact_head_clean", exact_head)
    for label, ancestor in (("source_ancestry", SOURCE_SHA), ("w2_ancestry", W2_SHA)):
        guard(label, lambda sha=ancestor: subprocess.run(
            ["git", "merge-base", "--is-ancestor", sha, head], cwd=ROOT, check=True).returncode)
    guard("permitted_source_delta", permitted_delta)
    guard("immutable_source_state", immutable_source)
    guard("product_freeze", frozen_product)
    guard("evidence_manifest", evidence_manifest)
    if args.check_source_remote:
        guard("initial_source_remote", remote_source)

    python = sys.executable
    commands = {
        "targeted_c0": [python, "-m", "unittest", "-v", "tests.test_wave2_c2_scientific_adjudication",
                        "tests.test_c0_confirmation_count_repair"],
        "preserved_current_c0_attack": [python, "continuity/one_shot/oneshot_c0_current_attack.py"],
        "residual_outcome_ref_invariant": [python, "continuity/c0_repair/probes/outcome_ref_current_probe.py"],
        "retained_integrity": [python, "-m", "unittest", "-v",
            "tests.test_research_os_trial_proposal_export_binding",
            "tests.test_research_os_epoch_model_admission", "tests.test_research_os_trial_epoch_window",
            "tests.test_research_os_serializable_outcome_membrane", "tests.test_research_os_native_trial_lineage",
            "tests.test_research_os_epoch_blinding_admission", "tests.test_research_os_evaluation_membrane_admission",
            "tests.test_research_os_source_pit_clocks"],
        "ordinary_regression": [python, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        "research_os_regression": [python, "-m", "unittest", "discover", "-s", "research/research_os/tests", "-p", "test_*.py"],
        "historical_replay": [python, "continuity/one_shot/replay_historical_tests.py"],
        "source_shadow": [python, "continuity/one_shot/oneshot_e1_probe.py"],
        "schema_check": [python, "scripts/generate_schemas.py", "--check"],
        "status_check": [python, "scripts/status_artifacts.py", "--check"],
        "selected_q_attacks": [python, "-m", "pytest", "-q",
            "continuity/one_shot/evidence/regression_classification/q-source/test_giga_q_core_identity.py",
            "-k", "export_guard_covers_nested_json_serializable_sequences or pipeline_cannot_accept_tuple_hidden_outcome or authority_never_coerces_false_like_values"],
    }

    def run(item):
        name, command = item
        start, log = utc(), out / (name + ".log")
        try:
            with log.open("w") as stream:
                completed = subprocess.run(command, cwd=ROOT, env=env, stdout=stream,
                                           stderr=subprocess.STDOUT, timeout=1200)
            code, failures = completed.returncode, []
            if code:
                failures = [line for line in log.read_text(errors="replace").splitlines()
                            if line.startswith(("FAIL:", "ERROR:", "FAILED ", "AssertionError", "ValueError"))]
                failures = failures or ["nonzero exit; see complete preserved log"]
        except Exception as exc:
            code, failures = -1, [str(exc)]
        record = {"NAME": name, "COMMAND": command,
            "ENVIRONMENT": {"cwd": str(ROOT), "python": platform.python_version(),
                            "PYTHONPATH": env["PYTHONPATH"], "PYTHONDONTWRITEBYTECODE": "1",
                            "state": "isolated fixtures and read-only registered source"},
            "HEAD_SHA": head, "START_TIME": start, "END_TIME": utc(),
            "RESULT": "PASS" if code == 0 else "FAIL", "EXIT_CODE": code,
            "FAILURES": failures, "LOG_REF": log.name}
        (out / (name + ".json")).write_text(json.dumps(record, indent=2) + "\n")
        return record

    if all(g["RESULT"] == "PASS" for g in guards):
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            runs = list(pool.map(run, commands.items()))
    guard("final_exact_head_clean", exact_head)
    guard("final_immutable_source_state", immutable_source)
    guard("final_product_freeze", frozen_product)
    guard("final_evidence_manifest", evidence_manifest)
    if args.check_source_remote:
        guard("final_source_remote", remote_source)
    passed = len(runs) == len(commands) and all(r["RESULT"] == "PASS" for r in runs + guards)
    result = {"MISSION": "C0_CONFIRMATION_REPAIR", "HEAD_SHA": head, "SOURCE_SHA": SOURCE_SHA,
              "PRODUCT_FREEZE_SHA": freeze_sha, "START_TIME": started, "END_TIME": utc(),
              "ENVIRONMENT": {"python": platform.python_version(), "cwd": str(ROOT)},
              "HOSTED_RUN_ID": os.environ.get("GITHUB_RUN_ID"),
              "HOSTED_RUN_ATTEMPT": os.environ.get("GITHUB_RUN_ATTEMPT"),
              "HOSTED_EVENT": os.environ.get("GITHUB_EVENT_NAME"),
              "GUARDS": guards, "RUNS": runs, "REQUIRED_RUN_COUNT": len(commands),
              "RESULT": "PASS" if passed else "FAIL", "QUALIFICATION_SCOPE": "C0_REPAIR_ENGINEERING_ONLY",
              "PRODUCTION_INPUTS_EQUAL_SOURCE": all(g["RESULT"] == "PASS" for g in guards
                  if g["NAME"] in {"immutable_source_state", "final_immutable_source_state"}),
              "PRODUCTION_RESEARCH_STATE_MUTATED": False if all(
                  g["RESULT"] == "PASS" for g in guards if g["NAME"] in {
                      "immutable_source_state", "final_immutable_source_state", "initial_exact_head_clean",
                      "final_exact_head_clean"}) else "UNKNOWN_GUARD_FAILURE",
              "AUTHORITY_CHANGED": False if all(g["RESULT"] == "PASS" for g in guards
                  if g["NAME"] in {"immutable_source_state", "final_immutable_source_state"}) else "UNKNOWN_GUARD_FAILURE",
              "OUTCOME_ACCESSED": False, "ECONOMIC_READINESS": "NOT_EVALUATED_IN_THIS_MISSION"}
    (out / "QUALIFICATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
