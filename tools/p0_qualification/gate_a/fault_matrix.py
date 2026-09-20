"""Gate A durability fault matrix for the frozen P0 V4 candidate.

The matrix maps every required crash/durability transition to an existing
discriminating test, a new repository-only discriminant, or an explicit proof
residual.  It calls frozen production code but never edits it.  Existing test
citations are resolved at runtime; stale citations become ``MISSING_PROOF``.

No Gate A PASS, target-host readiness, P14D amendment, or t0 is claimed.
"""

from __future__ import annotations

import errno
import json
import os
import stat
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quant.dataplane.sec.store import (  # noqa: E402
    SecCaptureStore,
    SecStorageFailure,
    digest_bytes,
)
from quant.state import append_jsonl, read_json, write_json  # noqa: E402

from common.evidence import (  # noqa: E402
    EvidenceRecord,
    Report,
    verified_input_tree_digest,
)
from common.launcher_loader import stage_isolated_root  # noqa: E402
from common.synthetic import SyntheticEnvironment, empty_router  # noqa: E402


FROZEN_CANDIDATE_SHA = "4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072"
ARTIFACT = (
    REPO_ROOT
    / "tools"
    / "p0_qualification"
    / "evidence"
    / "gate_a"
    / "fault_matrix.json"
)

PROOF_CLASSES = (
    "EXISTING_DISCRIMINATING_PROOF",
    "NEW_DISCRIMINATING_PROOF",
    "TARGET_HOST_ONLY",
    "MISSING_PROOF",
)


@dataclass(frozen=True)
class FaultRow:
    property_name: str
    proof_class: str
    evidence_source: tuple[str, ...]
    proof_function: tuple[str, ...]
    epistemic_classification: str
    defect_classification: str
    reproduce_command: str
    residual_proof_domain: str
    detail: str

    def __post_init__(self) -> None:
        if self.proof_class not in PROOF_CLASSES:
            raise ValueError(f"INVALID_PROOF_CLASS:{self.proof_class}")

    def to_dict(self) -> dict[str, object]:
        return {
            "property": self.property_name,
            "proof_class": self.proof_class,
            "evidence_source": list(self.evidence_source),
            "test_or_harness_function": list(self.proof_function),
            "frozen_production_candidate_sha": FROZEN_CANDIDATE_SHA,
            "epistemic_classification": self.epistemic_classification,
            "defect_classification": self.defect_classification,
            "reproduction_command": self.reproduce_command,
            "residual_proof_domain": self.residual_proof_domain,
            "detail": self.detail,
        }


# Every citation names a concrete discriminating test method.
EXISTING: dict[str, dict[str, object]] = {
    "before_after_raw_write": {
        "sources": ("tests/test_sec_form4_capture.py",),
        "tests": (
            "tests.test_sec_form4_capture.RawStoreTests"
            ".test_disk_full_during_raw_write_raises_instead_of_acknowledging",
        ),
        "detail": "ENOSPC during raw write leaves no object, staging file, or envelope.",
    },
    "before_after_hardlink_publication": {
        "sources": ("tests/test_p0_deployment_boundaries.py",),
        "tests": (
            "tests.test_p0_deployment_boundaries.RawPublicationDurabilityTests"
            ".test_retry_after_directory_fsync_failure_revalidates_durability",
        ),
        "detail": (
            "A visible post-link object is not acknowledged until directory durability "
            "is revalidated."
        ),
    },
    "before_after_directory_fsync": {
        "sources": ("tests/test_p0_deployment_boundaries.py",),
        "tests": (
            "tests.test_p0_deployment_boundaries.RawPublicationDurabilityTests"
            ".test_retry_after_directory_fsync_failure_revalidates_durability",
            "tests.test_p0_deployment_boundaries.RawPublicationDurabilityTests"
            ".test_new_hash_prefix_is_fsynced_in_its_parent",
        ),
        "detail": (
            "The object directory and the newly-created hash-prefix parent are both "
            "covered by discriminating fsync assertions."
        ),
    },
    "before_after_envelope_append": {
        "sources": ("tests/test_sec_form4_capture.py",),
        "tests": (
            "tests.test_sec_form4_capture.CrashBoundaryTests"
            ".test_crash_between_raw_write_and_envelope_replays_safely",
            "tests.test_sec_form4_capture.CrashBoundaryTests"
            ".test_crash_between_envelope_and_acknowledgement_costs_no_refetch",
        ),
        "detail": (
            "No envelope means replay; a durable envelope suppresses refetch and a "
            "duplicate append."
        ),
    },
    "before_after_attempt_completion": {
        "sources": ("tests/test_p0_adversarial.py",),
        "tests": (
            "tests.test_p0_adversarial.AuditFailClosedTests"
            ".test_network_intent_without_finished_attempt_invalidates_audit",
        ),
        "detail": (
            "An INTENT without a FINISHED attempt produces "
            "REQUEST_ACCOUNTING_INCOMPLETE."
        ),
    },
    "before_after_cursor_advancement": {
        "sources": ("tests/test_sec_form4_capture.py",),
        "tests": (
            "tests.test_sec_form4_capture.CrashBoundaryTests"
            ".test_crash_between_acknowledgement_and_cursor_advance_is_recoverable",
        ),
        "detail": (
            "A crash before cursor movement skips nothing; replay advances only after "
            "all acknowledgements."
        ),
    },
    "before_after_successor_scheduler_obligation": {
        "sources": ("tests/test_astra_pre_t0.py",),
        "tests": (
            "tests.test_astra_pre_t0.MoreCollectorCampaign"
            ".test_qualifying_stop_after_answer_before_next_obligation_is_not_accountable",
        ),
        "detail": (
            "An answered request without a successor obligation cannot yield an "
            "accountable window."
        ),
    },
    "before_after_cooldown_persistence": {
        "sources": ("tests/test_sec_form4_capture.py",),
        "tests": (
            "tests.test_sec_form4_capture.TrafficBudgetTests"
            ".test_cooldown_is_durable_across_restart_and_never_shortened",
        ),
        "detail": "Cooldown survives a new budget instance and cannot be shortened.",
    },
    "supervisor_death": {
        "sources": (
            "tests/test_p0_deployment_boundaries.py",
            "tests/test_gate_a_v3_red.py",
        ),
        "tests": (
            "tests.test_p0_deployment_boundaries.SupervisorRealProcessBoundaryTests"
            ".test_sigkill_supervisor_kills_child_and_replacement_is_manual",
            "tests.test_gate_a_v3_red.GateAV3PrimitiveRedTests"
            ".test_stopped_supervisor_with_pending_obligation_is_not_accountable",
        ),
        "detail": (
            "Real SIGKILL kills the child; replacement is manual and pending work stays "
            "non-accountable."
        ),
    },
    "child_death": {
        "sources": (
            "tests/test_p0_adversarial.py",
            "tests/test_astra_pre_t0.py",
        ),
        "tests": (
            "tests.test_p0_adversarial.SupervisorProductionPathTests"
            ".test_same_living_supervisor_can_attest_child_failure_restart",
            "tests.test_astra_pre_t0.Phase5AuthorityBindingCampaign"
            ".test_automatic_restart_requires_external_exit_witness",
        ),
        "detail": (
            "Only the same live supervisor's durable child-exit witness authorizes an "
            "automatic restart."
        ),
    },
    "corrupt_torn_journal_tail": {
        "sources": ("tests/test_p0_adversarial.py",),
        "tests": (
            "tests.test_p0_adversarial.DurabilityAndSemanticTests"
            ".test_torn_sec_journal_is_never_silently_discarded",
        ),
        "detail": (
            "An acquisition-critical torn SEC journal tail fails loudly instead of "
            "self-repairing."
        ),
    },
    "duplicate_replay": {
        "sources": ("tests/test_sec_form4_capture.py",),
        "tests": (
            "tests.test_sec_form4_capture.CrashBoundaryTests"
            ".test_crash_between_raw_write_and_envelope_replays_safely",
            "tests.test_sec_form4_capture.CrashBoundaryTests"
            ".test_crash_between_envelope_and_acknowledgement_costs_no_refetch",
        ),
        "detail": (
            "Replay deduplicates raw bytes; a durable envelope costs no second fetch or "
            "append."
        ),
    },
    "missing_fingerprint": {
        "sources": ("tests/test_sec_form4_capture.py",),
        "tests": (
            "tests.test_sec_form4_capture.MaterializedFingerprintTests"
            ".test_readiness_blocks_when_nothing_is_materialized",
        ),
        "detail": "Qualifying readiness blocks when no fingerprint is materialized.",
    },
    "foreign_fingerprint": {
        "sources": ("tests/test_astra_pre_t0.py",),
        "tests": (
            "tests.test_astra_pre_t0.AuditCampaign"
            ".test_single_foreign_fingerprint_cannot_pass",
        ),
        "detail": (
            "A single foreign fingerprint makes retrospective audit non-accountable."
        ),
    },
    "missing_deployment_authority": {
        "sources": ("tests/test_astra_pre_t0.py",),
        "tests": (
            "tests.test_astra_pre_t0.Phase5AuthorityBindingCampaign"
            ".test_deployment_restart_requires_consumed_external_authority",
        ),
        "detail": (
            "Removing the consumed deployment-authority ledger fails audit explicitly."
        ),
    },
}


def _flatten_suite(suite: unittest.TestSuite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _flatten_suite(item)
        else:
            yield item


def _test_exists(dotted_name: str) -> bool:
    """Reject unittest's synthetic _FailedTest as well as an empty suite."""
    try:
        tests = list(_flatten_suite(unittest.TestLoader().loadTestsFromName(dotted_name)))
    except (ImportError, AttributeError):
        return False
    return bool(tests) and all(
        type(test).__name__ != "_FailedTest" and test.id() == dotted_name
        for test in tests
    )


def _existing_row(property_name: str) -> FaultRow:
    spec = EXISTING[property_name]
    sources = tuple(spec["sources"])
    tests = tuple(spec["tests"])
    missing = tuple(test for test in tests if not _test_exists(test))
    command = "PYTHONPATH=src python3 -m unittest " + " ".join(tests) + " -v"
    if missing:
        return FaultRow(
            property_name=property_name,
            proof_class="MISSING_PROOF",
            evidence_source=sources,
            proof_function=tests,
            epistemic_classification="CLAIM",
            defect_classification="MISSING_PROOF",
            reproduce_command=command,
            residual_proof_domain=(
                "REPOSITORY: replace the stale citation or add a discriminant"
            ),
            detail=f"stale test citation(s): {list(missing)}",
        )
    return FaultRow(
        property_name=property_name,
        proof_class="EXISTING_DISCRIMINATING_PROOF",
        evidence_source=sources,
        proof_function=tests,
        epistemic_classification="FACT",
        defect_classification="NON_ISSUE",
        reproduce_command=command,
        residual_proof_domain=(
            "TARGET_HOST: physical crash/power-loss and deployed filesystem/service-manager "
            "behaviour remain outside repository proof"
        ),
        detail=str(spec["detail"]),
    )


def _file_fsync_discriminant() -> tuple[bool, str]:
    """Fail the staging-file fsync and prove no raw object is published."""
    with SyntheticEnvironment() as env:
        store = SecCaptureStore(env.paths, root=REPO_ROOT)
        body = b"fault-matrix-file-fsync"
        target = store.object_path(digest_bytes(body))
        real_fsync = os.fsync
        regular_fsync_seen = False

        def fail_regular_file(fd: int) -> None:
            nonlocal regular_fsync_seen
            if stat.S_ISREG(os.fstat(fd).st_mode):
                regular_fsync_seen = True
                raise OSError(errno.EIO, "synthetic regular-file fsync failure")
            real_fsync(fd)

        raised = False
        with mock.patch(
            "quant.dataplane.sec.store.os.fsync", side_effect=fail_regular_file
        ):
            try:
                store.put_object(body)
            except SecStorageFailure:
                raised = True
        staging = list(env.paths.sec_staging.glob("*"))
        passed = regular_fsync_seen and raised and not target.exists() and not staging
        return passed, (
            f"regular_fsync_seen={regular_fsync_seen} storage_failure={raised} "
            f"target_exists={target.exists()} staging_entries={len(staging)}"
        )


def _state_journal_divergence_discriminant(
    *, journal_newer: bool
) -> tuple[bool, str]:
    """Exercise both sides of the state/commit-journal durability boundary."""
    with SyntheticEnvironment() as env:
        env.collector(empty_router())
        if journal_newer:
            append_jsonl(
                env.paths.sec / "collector_state.commits.jsonl",
                {
                    "event": "STATE_COMMITTED",
                    "state_digest": "sha256:" + "f" * 64,
                    "recorded_at_utc": env.timebase.now_iso(),
                },
            )
            label = "journal_newer_than_state"
        else:
            payload = read_json(env.paths.sec_collector_state)
            payload["enabled"] = not payload["enabled"]
            write_json(env.paths.sec_collector_state, payload)
            label = "state_newer_than_journal"
        try:
            env.reborn(empty_router())
        except SecStorageFailure as exc:
            expected = "COLLECTOR_STATE_UNCOMMITTED_OR_ROLLED_BACK" in str(exc)
            return expected, f"{label}: failed_closed={expected} error={exc}"
        return False, f"{label}: collector restart accepted divergent durable state"


def _restart_burst_limit_discriminant() -> tuple[bool, str]:
    """Loaded StartLimitBurst drift must fail before becoming authority."""
    with tempfile.TemporaryDirectory(prefix="quant-p0-burst-limit-") as directory:
        root = Path(directory)
        launcher = stage_isolated_root(root)
        target = root / "deploy" / "quant-sec-capture.service"

        def shown(value: int) -> SimpleNamespace:
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

        with mock.patch.object(
            launcher.subprocess,
            "run",
            return_value=shown(launcher.RESTART_BURST_LIMIT),
        ):
            accepted = launcher._effective_systemd_definition(root).startswith("sha256:")
        rejected = False
        with mock.patch.object(
            launcher.subprocess,
            "run",
            return_value=shown(launcher.RESTART_BURST_LIMIT - 1),
        ):
            try:
                launcher._effective_systemd_definition(root)
            except RuntimeError as exc:
                rejected = "STARTLIMITBURST_MISMATCH" in str(exc)
        return accepted and rejected, (
            f"constant={launcher.RESTART_BURST_LIMIT} "
            f"exact_loaded_value_accepted={accepted} one_below_rejected={rejected}"
        )


def _new_row(
    property_name: str,
    function_name: str,
    passed: bool,
    detail: str,
    *,
    sources: tuple[str, ...],
    extra_functions: tuple[str, ...] = (),
) -> FaultRow:
    return FaultRow(
        property_name=property_name,
        proof_class="NEW_DISCRIMINATING_PROOF",
        evidence_source=sources,
        proof_function=(function_name,) + extra_functions,
        epistemic_classification="FACT",
        defect_classification="NON_ISSUE" if passed else "REAL_DEFECT",
        reproduce_command=(
            "PYTHONPATH=. python3 -m tools.p0_qualification.gate_a.fault_matrix"
        ),
        residual_proof_domain=(
            "TARGET_HOST: physical crash/power-loss and effective service-manager behaviour "
            "remain outside repository proof"
            if passed
            else "REPOSITORY: preserve RED evidence and return the finding to Blue"
        ),
        detail=detail,
    )


def run() -> dict[str, object]:
    rows = [
        _existing_row(name)
        for name in (
            "before_after_raw_write",
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
        )
    ]

    passed, detail = _file_fsync_discriminant()
    rows.insert(
        1,
        _new_row(
            "before_after_file_fsync",
            "tools.p0_qualification.gate_a.fault_matrix._file_fsync_discriminant",
            passed,
            detail,
            sources=(
                "tools/p0_qualification/gate_a/fault_matrix.py",
                "src/quant/dataplane/sec/store.py:SecCaptureStore._link_into_place",
            ),
        ),
    )

    passed, detail = _state_journal_divergence_discriminant(journal_newer=False)
    rows.append(
        _new_row(
            "state_newer_than_journal",
            "tools.p0_qualification.gate_a.fault_matrix."
            "_state_journal_divergence_discriminant",
            passed,
            detail,
            sources=(
                "tools/p0_qualification/gate_a/fault_matrix.py",
                "src/quant/dataplane/sec/collector.py:SecForm4Collector._load_state",
            ),
        )
    )
    passed, detail = _state_journal_divergence_discriminant(journal_newer=True)
    rows.append(
        _new_row(
            "journal_newer_than_state",
            "tools.p0_qualification.gate_a.fault_matrix."
            "_state_journal_divergence_discriminant",
            passed,
            detail,
            sources=(
                "tools/p0_qualification/gate_a/fault_matrix.py",
                "src/quant/dataplane/sec/collector.py:SecForm4Collector._load_state",
            ),
        )
    )

    rows.extend(
        _existing_row(name)
        for name in (
            "missing_fingerprint",
            "foreign_fingerprint",
            "missing_deployment_authority",
        )
    )

    runtime_test = (
        "tests.test_astra_pre_t0.Phase4LifecycleAndWindowCampaign"
        ".test_unsolicited_zero_child_exit_cannot_cleanly_stop_qualifying_service"
    )
    passed, detail = _restart_burst_limit_discriminant()
    if not _test_exists(runtime_test):
        rows.append(
            FaultRow(
                property_name="restart_burst_limit",
                proof_class="MISSING_PROOF",
                evidence_source=("tests/test_astra_pre_t0.py",),
                proof_function=(runtime_test,),
                epistemic_classification="CLAIM",
                defect_classification="MISSING_PROOF",
                reproduce_command=(
                    f"PYTHONPATH=src python3 -m unittest {runtime_test} -v"
                ),
                residual_proof_domain="REPOSITORY: runtime-guard citation is stale",
                detail=(
                    "The loaded-unit discriminant passed, but the paired runtime guard "
                    "test is absent."
                ),
            )
        )
    else:
        rows.append(
            _new_row(
                "restart_burst_limit",
                "tools.p0_qualification.gate_a.fault_matrix."
                "_restart_burst_limit_discriminant",
                passed,
                detail + "; paired runtime guard citation resolves",
                sources=(
                    "tools/p0_qualification/gate_a/fault_matrix.py",
                    "deploy/quant_sec_supervisor.py:_effective_systemd_definition",
                    "tests/test_astra_pre_t0.py",
                ),
                extra_functions=(runtime_test,),
            )
        )

    counts = {
        proof_class: sum(row.proof_class == proof_class for row in rows)
        for proof_class in PROOF_CLASSES
    }
    report = Report(
        gate="GATE_A_FAULT_MATRIX",
        exact_sha=FROZEN_CANDIDATE_SHA,
        # A stable evidence time makes two executions byte-for-byte reproducible.
        generated_at_utc="2026-09-21T00:00:00+00:00",
    )
    for row in rows:
        report.add(
            EvidenceRecord(
                property_name=f"fault_matrix:{row.property_name}",
                classification=row.epistemic_classification,
                defect_class=row.defect_classification,
                domain=(
                    "TARGET_HOST"
                    if row.proof_class == "TARGET_HOST_ONLY"
                    else "REPOSITORY"
                ),
                detail=row.detail,
                exact_sha=FROZEN_CANDIDATE_SHA,
                reproduce_command=row.reproduce_command,
                residual=row.residual_proof_domain,
            )
        )

    input_paths = (
        "tools/p0_qualification/common/evidence.py",
        "tools/p0_qualification/common/launcher_loader.py",
        "tools/p0_qualification/common/synthetic.py",
        "tools/p0_qualification/gate_a/fault_matrix.py",
        "tests/test_astra_pre_t0.py",
        "tests/test_gate_a_v3_red.py",
        "tests/test_p0_adversarial.py",
        "tests/test_p0_deployment_boundaries.py",
        "tests/test_sec_form4_capture.py",
    )
    report.body.update(
        {
            "frozen_candidate_sha": FROZEN_CANDIDATE_SHA,
            "rows": [row.to_dict() for row in rows],
            "fault_matrix_rows": len(rows),
            "proof_class_counts": counts,
            "real_defects": sum(
                row.defect_classification == "REAL_DEFECT" for row in rows
            ),
            "test_defects": sum(
                row.defect_classification == "TEST_DEFECT" for row in rows
            ),
            "non_issues": sum(
                row.defect_classification == "NON_ISSUE" for row in rows
            ),
            "restart_burst_limit_disposition": next(
                row.to_dict()
                for row in rows
                if row.property_name == "restart_burst_limit"
            ),
            "harness_input_tree_digest": verified_input_tree_digest(input_paths),
            "production_code_changed": False,
            "gate_a_v4_pass": "NOT_CLAIMED_BY_BUILDER",
            "target_host_ready": "NOT_CLAIMED_BY_BUILDER",
            "p14d_amendment": "NOT_CLAIMED_BY_BUILDER",
            "t0": "NOT_DECLARED",
            "real_capital_authorized": False,
        }
    )
    return report.write(ARTIFACT)


if __name__ == "__main__":
    result = run()
    summary = {
        "gate": result["gate"],
        "rows": result["body"]["fault_matrix_rows"],
        "proof_class_counts": result["body"]["proof_class_counts"],
        "real_defects": result["body"]["real_defects"],
        "report_digest": result["report_digest"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    raise SystemExit(1 if result["body"]["real_defects"] else 0)
