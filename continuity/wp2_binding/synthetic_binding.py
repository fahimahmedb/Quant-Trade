"""WP2-only synthetic join from the native worker to the existing dry-run runner.

This module is qualification apparatus, not a runtime registration.  It adds no
CLI, scheduler, queue, authority, outcome access, or production sink.
"""
from __future__ import annotations

from copy import deepcopy

from research.research_os.expansion.experiment_runner import DryRunExperimentRunner, NOT_OBSERVED
from research.research_os.scientific_store import sha256_json
from research.research_os.worker_preflight import AUTHORITY_KEYS
from research.research_os.worker_stages import StageBlocked


TASK_ID = "WP2-SYNTHETIC-LINEAGE-001"
SINK = f"research/research_os/artifacts/{TASK_ID}/wp2/causality.json"
RUNNER_ID = "DryRunExperimentRunner:dry-run-experiment-runner.v1"
EVALUATOR_ID = "DryRunExperimentRunner.verify_bindings"


class SyntheticWP2Binding:
    """Narrow executor seam used only by the disposable WP2 qualification."""

    def __init__(self, envelope, qualifications, runner_meta, *, expected_sink=SINK):
        self.envelope = deepcopy(envelope)
        self.qualifications = deepcopy(qualifications)
        self.runner_meta = deepcopy(runner_meta)
        self.expected_sink = expected_sink
        self.runner = DryRunExperimentRunner()
        self.fixture_id = "sha256:" + sha256_json({
            "envelope": self.envelope,
            "qualifications": self.qualifications,
            "runner_meta": self.runner_meta,
        })

    def execute(self, snapshot, task, lane, stage, now, worker_id):
        if task.get("task_id") != TASK_ID:
            raise StageBlocked("WP2_TASK_IDENTITY_MISMATCH")
        if lane != "evidence_data" or stage != "recover_or_qualify":
            raise StageBlocked("WP2_ROUTE_MISMATCH")
        if self.expected_sink != SINK:
            raise StageBlocked("WP2_SINK_IDENTITY_MISMATCH")
        lease = task.get("lease") or {}
        execution = task.get("execution") or {}
        if (type(lease.get("generation")) is not int or lease["generation"] < 1
                or lease.get("owner") != worker_id or not execution.get("session_id")):
            raise StageBlocked("WP2_LEASE_OR_SESSION_IDENTITY_MISMATCH")
        authority = task.get("authority") or {}
        if any(authority.get(key) is not False for key in AUTHORITY_KEYS):
            raise StageBlocked("WP2_AUTHORITY_MEMBRANE_VIOLATION")

        plan = self.runner.plan(self.envelope, self.qualifications, self.runner_meta)
        evaluation = self.runner.verify_bindings(
            plan, self.envelope, self.qualifications, self.runner_meta
        )
        subject = plan["execution_plan_hash"]
        if evaluation["execution_plan_hash"] != subject:
            raise StageBlocked("WP2_RUNNER_EVALUATOR_SUBJECT_MISMATCH")

        receipt = {
            "schema": "wp2-causality-receipt.v1",
            "task_id": task["task_id"],
            "materialization_head": snapshot.head,
            "lease_generation": lease["generation"],
            "lease_owner": lease["owner"],
            "execution_session": execution["session_id"],
            "runner": RUNNER_ID,
            "runner_subject": subject,
            "evaluator": EVALUATOR_ID,
            "evaluator_subject": evaluation["execution_plan_hash"],
            "sink": SINK,
            "fixture_id": self.fixture_id,
            "release_sha": execution.get("release_sha"),
            "synthetic": True,
            "production_science": False,
            "counts_toward_trial_denominator": False,
            "counts_toward_exposure": False,
            "counts_toward_production_memory": False,
            "outcome_access": False,
            "economic_result": NOT_OBSERVED,
            "live_source_access": False,
            "real_capital": False,
            "live_trading": False,
            "deployment": False,
            "owner_promotion": False,
        }
        receipt["receipt_hash"] = sha256_json(receipt)
        return deepcopy(receipt), {SINK: receipt}, "COMPLETE"
