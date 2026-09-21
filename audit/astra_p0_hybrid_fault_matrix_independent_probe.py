#!/usr/bin/env python3
"""Independent Astra probe for the bounded Gate-A hybrid fault-matrix review.

Audit-only. It does not edit the frozen production candidate. Temporary
monkeypatches are used only to falsify the claimed discriminating power.
"""

from __future__ import annotations

import copy
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = "d4d446c412258b2a9e4792cdcd9e2442ef24b615"
CODEX_DELIVERY = "686f77a383fb0e8c7ecd1b4a737585bedb544701"
CODEX_FINAL = "e5c4c720e758cd8ab3f0e04faf541b26e204be16"
CANDIDATE = "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072"
ARTIFACT = ROOT / "tools/p0_qualification/evidence/gate_a/fault_matrix.json"
OUTPUT = ROOT / "astra_p0_hybrid_fault_matrix_probe_results.json"

from tools.p0_qualification.gate_a import fault_matrix
from common.evidence import sha256_of
from quant.dataplane.sec.collector import CollectorState, SecForm4Collector
from quant.dataplane.sec.store import SecStorageFailure
from quant.state import read_json

results: dict[str, object] = {
    "candidate_sha": CANDIDATE,
    "codex_delivery_sha": CODEX_DELIVERY,
    "codex_final_sha": CODEX_FINAL,
    "checks": {},
    "findings": [],
}


def record(name: str, ok: bool, detail: object = None) -> None:
    results["checks"][name] = {"ok": bool(ok), "detail": detail}


def finding(kind: str, name: str, detail: object) -> None:
    results["findings"].append(
        {"classification": kind, "name": name, "detail": detail}
    )


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


# F1 — lineage and bounded scope.
merge_predecessor = git("merge-base", PREDECESSOR, CODEX_DELIVERY)
merge_delivery = git("merge-base", CODEX_DELIVERY, CODEX_FINAL)
codex_paths = git("diff", "--name-only", f"{PREDECESSOR}...{CODEX_FINAL}").splitlines()
record("F1_predecessor_merge_base_exact", merge_predecessor == PREDECESSOR, merge_predecessor)
record("F1_delivery_to_final_linear", merge_delivery == CODEX_DELIVERY, merge_delivery)
record(
    "F1_codex_paths_bounded",
    set(codex_paths)
    == {
        "tools/p0_qualification/gate_a/fault_matrix.py",
        "tools/p0_qualification/evidence/gate_a/fault_matrix.json",
        "handoff/BUILDER_CODEX_P0_HYBRID_FAULT_MATRIX_CHECKPOINT_2026-09-21.md",
    },
    codex_paths,
)
record(
    "F1_no_production_path_changed",
    not any(
        path.startswith(("src/", "deploy/", "scripts/", "tests/", ".github/workflows/"))
        for path in codex_paths
    ),
    codex_paths,
)

committed = json.loads(ARTIFACT.read_text(encoding="utf-8"))
rows = committed["body"]["rows"]
properties = [row["property"] for row in rows]
required = [
    "before_after_raw_write",
    "before_after_file_fsync",
    "before_after_hardlink_publication",
    "before_after_directory_fsync",
    "before_after_envelope_append",
    "before_after_attempt_completion",
    "before_after_cursor_advancement",
    "before_after_successor_scheduler_obligation",
    "before_after_cooldown_persistence",
    "supervisor_death",
    "child_death",
    "corrupt_torn_journal_tail",
    "duplicate_replay",
    "state_newer_than_journal",
    "journal_newer_than_state",
    "missing_fingerprint",
    "foreign_fingerprint",
    "missing_deployment_authority",
    "restart_burst_limit",
]
record("F2_exact_19_required_rows", properties == required, properties)
record("F2_no_duplicate_rows", len(properties) == len(set(properties)), properties)

# F3 — resolve and execute every cited repository test, de-duplicated.
cited = []
for row in rows:
    for name in row["test_or_harness_function"]:
        if name.startswith("tests.") and name not in cited:
            cited.append(name)
suite = unittest.TestSuite()
loader = unittest.TestLoader()
resolution_ok = True
for name in cited:
    loaded = list(fault_matrix._flatten_suite(loader.loadTestsFromName(name)))
    valid = bool(loaded) and all(
        type(test).__name__ != "_FailedTest" and test.id() == name for test in loaded
    )
    resolution_ok = resolution_ok and valid
    if valid:
        suite.addTests(loaded)
test_result = unittest.TextTestRunner(verbosity=1).run(suite)
record(
    "F3_all_cited_tests_resolve_and_execute",
    resolution_ok and test_result.wasSuccessful(),
    {
        "unique_cited_tests": len(cited),
        "tests_run": test_result.testsRun,
        "failures": len(test_result.failures),
        "errors": len(test_result.errors),
    },
)

# F4/F5/F6 — current green behavior of the four new discriminants.
green_file, green_file_detail = fault_matrix._file_fsync_discriminant()
green_state, green_state_detail = fault_matrix._state_journal_divergence_discriminant(
    journal_newer=False
)
green_journal, green_journal_detail = fault_matrix._state_journal_divergence_discriminant(
    journal_newer=True
)
green_burst, green_burst_detail = fault_matrix._restart_burst_limit_discriminant()
record("F4_file_fsync_current_green", green_file, green_file_detail)
record("F5_state_newer_current_green", green_state, green_state_detail)
record("F5_journal_newer_current_green", green_journal, green_journal_detail)
record("F6_restart_burst_current_green", green_burst, green_burst_detail)

# F6 — independent static-contract check: do not derive the expected good value
# from launcher.RESTART_BURST_LIMIT when constructing the systemctl fixture.
with tempfile.TemporaryDirectory(prefix="astra-burst-static-") as directory:
    root = Path(directory)
    launcher = fault_matrix.stage_isolated_root(root)
    target = root / "deploy" / "quant-sec-capture.service"

    def shown_static(value: int) -> SimpleNamespace:
        body = "\n".join(
            (
                f"FragmentPath={target}",
                "DropInPaths=",
                "ExecStart={ path=/usr/bin/python3 ; argv[]=/usr/bin/python3 -I "
                "/opt/quant/deploy/quant_sec_supervisor.py --root /opt/quant "
                "--qualifying ; }",
                "WorkingDirectory=/opt/quant",
                "Restart=on-failure",
                "RestartUSec=15s",
                "StartLimitIntervalUSec=10min",
                f"StartLimitBurst={value}",
                "KillMode=control-group",
                "KillSignal=15",
                "TimeoutStopUSec=30s",
                "EnvironmentFiles=/etc/quant/sec-capture.env (ignore_errors=no)",
            )
        ) + "\n"
        return SimpleNamespace(returncode=0, stdout=body, stderr="")

    with mock.patch.object(launcher.subprocess, "run", return_value=shown_static(5)):
        accepted_five = launcher._effective_systemd_definition(root).startswith("sha256:")
    rejected_four = False
    with mock.patch.object(launcher.subprocess, "run", return_value=shown_static(4)):
        try:
            launcher._effective_systemd_definition(root)
        except RuntimeError as exc:
            rejected_four = "STARTLIMITBURST_MISMATCH" in str(exc)
    unit_has_five = "StartLimitBurst=5" in target.read_text(encoding="utf-8")
    record(
        "F6_independent_exact_5_accepts_and_4_rejects",
        launcher.RESTART_BURST_LIMIT == 5
        and unit_has_five
        and accepted_five
        and rejected_four,
        {
            "production_constant": launcher.RESTART_BURST_LIMIT,
            "unit_declares_5": unit_has_five,
            "loaded_5_accepted": accepted_five,
            "loaded_4_rejected": rejected_four,
        },
    )

# F10 — remove regular-file fsync in an isolated monkeypatch. The Codex
# discriminant must turn red.
original_link = fault_matrix.SecCaptureStore._link_into_place


def no_regular_file_fsync(self, body: bytes, target: Path) -> None:
    staging = self.paths.sec_staging / "astra-no-file-fsync.part"
    target.parent.mkdir(parents=True, exist_ok=True)
    self._fsync_dir(target.parent.parent)
    staging.write_bytes(body)
    os.chmod(staging, 0o444)
    try:
        os.link(staging, target)
        self._fsync_dir(target.parent)
    finally:
        staging.unlink(missing_ok=True)


with mock.patch.object(fault_matrix.SecCaptureStore, "_link_into_place", no_regular_file_fsync):
    file_mutation_result, file_mutation_detail = fault_matrix._file_fsync_discriminant()
record(
    "F10_file_fsync_mutation_turns_red",
    not file_mutation_result,
    file_mutation_detail,
)
if file_mutation_result:
    finding("MISSING_PROOF", "file_fsync_discriminating_power", file_mutation_detail)

# F10 — make the production loader tolerate exactly the state/journal mismatch.
# Both divergence discriminants must turn red.
original_load_state = SecForm4Collector._load_state


def permissive_load_state(self):
    try:
        return original_load_state(self)
    except SecStorageFailure as exc:
        if "COLLECTOR_STATE_UNCOMMITTED_OR_ROLLED_BACK" not in str(exc):
            raise
        payload = read_json(self.paths.sec_collector_state)
        return CollectorState(**payload)


with mock.patch.object(SecForm4Collector, "_load_state", permissive_load_state):
    state_mutation_result, state_mutation_detail = (
        fault_matrix._state_journal_divergence_discriminant(journal_newer=False)
    )
    journal_mutation_result, journal_mutation_detail = (
        fault_matrix._state_journal_divergence_discriminant(journal_newer=True)
    )
record(
    "F10_state_newer_mutation_turns_red",
    not state_mutation_result,
    state_mutation_detail,
)
record(
    "F10_journal_newer_mutation_turns_red",
    not journal_mutation_result,
    journal_mutation_detail,
)
if state_mutation_result or journal_mutation_result:
    finding(
        "MISSING_PROOF",
        "state_journal_discriminating_power",
        {
            "state_newer_still_green": state_mutation_result,
            "journal_newer_still_green": journal_mutation_result,
        },
    )

# F10 — mutate only the frozen production constant 5 -> 4 in the isolated
# launcher. Because the Codex fixture derives its "good" loaded value from the
# same constant, this exposes whether it is a circular oracle.
original_stage = fault_matrix.stage_isolated_root


def stage_with_wrong_frozen_constant(root: Path):
    launcher = original_stage(root)
    launcher.RESTART_BURST_LIMIT = 4
    return launcher


with mock.patch.object(
    fault_matrix, "stage_isolated_root", side_effect=stage_with_wrong_frozen_constant
):
    burst_mutation_result, burst_mutation_detail = (
        fault_matrix._restart_burst_limit_discriminant()
    )
record(
    "F10_restart_constant_5_to_4_mutation_turns_red",
    not burst_mutation_result,
    burst_mutation_detail,
)
if burst_mutation_result:
    finding(
        "TEST_DEFECT",
        "restart_burst_discriminant_uses_production_constant_as_oracle",
        {
            "mutation": "RESTART_BURST_LIMIT 5 -> 4",
            "discriminant_still_green": True,
            "detail": burst_mutation_detail,
            "independent_static_5_vs_4_check": "PASS",
        },
    )

# F8/F9 — two independent generations on the same interpreter must be
# byte-identical, self-consistent, and bound to the candidate.
with tempfile.TemporaryDirectory(prefix="astra-fault-matrix-repro-") as directory:
    one_path = Path(directory) / "one.json"
    two_path = Path(directory) / "two.json"
    with mock.patch.object(fault_matrix, "ARTIFACT", one_path):
        one = fault_matrix.run()
    with mock.patch.object(fault_matrix, "ARTIFACT", two_path):
        two = fault_matrix.run()
    one_bytes = one_path.read_bytes()
    two_bytes = two_path.read_bytes()

record(
    "F8_same_environment_byte_reproducible",
    one_bytes == two_bytes and one["report_digest"] == two["report_digest"],
    {
        "report_digest_one": one["report_digest"],
        "report_digest_two": two["report_digest"],
        "python_version": one["python_version"],
    },
)
recomputed = sha256_of({k: v for k, v in committed.items() if k != "report_digest"})
record(
    "F9_committed_report_digest_self_consistent",
    recomputed == committed["report_digest"],
    {"embedded": committed["report_digest"], "recomputed": recomputed},
)
record(
    "F9_all_rows_bind_frozen_candidate",
    committed["body"]["frozen_candidate_sha"] == CANDIDATE
    and committed["exact_sha"] == CANDIDATE
    and all(row["frozen_production_candidate_sha"] == CANDIDATE for row in rows),
)
counts = committed["body"]["proof_class_counts"]
recount = {
    key: sum(row["proof_class"] == key for row in rows)
    for key in (
        "EXISTING_DISCRIMINATING_PROOF",
        "NEW_DISCRIMINATING_PROOF",
        "TARGET_HOST_ONLY",
        "MISSING_PROOF",
    )
}
record("F9_proof_counts_self_consistent", counts == recount, {"stored": counts, "recount": recount})
record(
    "F9_nonissue_count_self_consistent",
    committed["body"]["non_issues"]
    == sum(row["defect_classification"] == "NON_ISSUE" for row in rows),
)
record(
    "F9_safety_nonclaims_present",
    committed["no_t0_declared"] is True
    and committed["no_target_host_claimed"] is True
    and committed["no_p14d_amendment_claimed"] is True
    and committed["body"]["t0"] == "NOT_DECLARED"
    and committed["body"]["target_host_ready"] == "NOT_CLAIMED_BY_BUILDER"
    and committed["body"]["real_capital_authorized"] is False,
)

# The serializer hashes sys.version. This is explicit provenance, but it means
# a durable file digest is environment-bound rather than repository-only.
regenerated = one
committed_without_env = copy.deepcopy(committed)
regenerated_without_env = copy.deepcopy(regenerated)
for payload in (committed_without_env, regenerated_without_env):
    payload.pop("python_version", None)
    payload.pop("report_digest", None)
record(
    "F8_repository_payload_same_except_environment_metadata",
    committed_without_env == regenerated_without_env,
    {
        "committed_python_version": committed.get("python_version"),
        "runner_python_version": regenerated.get("python_version"),
        "committed_report_digest": committed.get("report_digest"),
        "runner_report_digest": regenerated.get("report_digest"),
    },
)
if (
    committed_without_env == regenerated_without_env
    and committed.get("python_version") != regenerated.get("python_version")
    and committed.get("report_digest") != regenerated.get("report_digest")
):
    finding(
        "TEST_DEFECT",
        "artifact_digest_is_python_build_bound",
        {
            "committed_python_version": committed["python_version"],
            "runner_python_version": regenerated["python_version"],
            "committed_report_digest": committed["report_digest"],
            "runner_report_digest": regenerated["report_digest"],
            "same_non_environment_payload": True,
        },
    )

# The named input-tree digest excludes the production paths exercised by all
# four new discriminants. Exact Git ancestry/scope above independently binds
# those bytes to the frozen candidate, so record the artifact limitation
# without silently treating the digest alone as production binding.
finding(
    "TEST_DEFECT",
    "harness_input_tree_digest_omits_exercised_production_paths",
    {
        "omitted": [
            "src/quant/dataplane/sec/store.py",
            "src/quant/dataplane/sec/collector.py",
            "deploy/quant_sec_supervisor.py",
            "deploy/quant-sec-capture.service",
        ],
        "compensating_evidence": "F1 exact Git ancestry and no-production-delta verification",
    },
)

# Audit execution succeeds when all current-code properties are green and the
# three non-restart red mutations are detected. The restart oracle defect is a
# material finding, not a probe infrastructure failure.
mandatory_current = [
    "F1_predecessor_merge_base_exact",
    "F1_delivery_to_final_linear",
    "F1_codex_paths_bounded",
    "F1_no_production_path_changed",
    "F2_exact_19_required_rows",
    "F2_no_duplicate_rows",
    "F3_all_cited_tests_resolve_and_execute",
    "F4_file_fsync_current_green",
    "F5_state_newer_current_green",
    "F5_journal_newer_current_green",
    "F6_restart_burst_current_green",
    "F6_independent_exact_5_accepts_and_4_rejects",
    "F10_file_fsync_mutation_turns_red",
    "F10_state_newer_mutation_turns_red",
    "F10_journal_newer_mutation_turns_red",
    "F8_same_environment_byte_reproducible",
    "F9_committed_report_digest_self_consistent",
    "F9_all_rows_bind_frozen_candidate",
    "F9_proof_counts_self_consistent",
    "F9_nonissue_count_self_consistent",
    "F9_safety_nonclaims_present",
]
results["probe_execution_ok"] = all(results["checks"][name]["ok"] for name in mandatory_current)
results["material_findings"] = len(results["findings"])
OUTPUT.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(results, indent=2, sort_keys=True))
raise SystemExit(0 if results["probe_execution_ok"] else 2)
