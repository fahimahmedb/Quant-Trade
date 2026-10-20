#!/usr/bin/env python3
"""Actual Oracle V2 claim/ideation crash canary and bounded state migration."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

from deploy.oracle_h24_canary import instance_identity
from deploy.oracle_v2_deploy import BRANCH, GATES, verify_ci
from research.research_os.github_state import GitHubStateStore, PREFIX, json_bytes
from research.research_os.oracle_worker import AUTHORITY, ASSERTION, backend_from_config, clock
from research.research_os.oracle_worker_v2 import build_v2_worker
from research.research_os.worker_stages import _reason
from research.research_os.expansion.v2_core import canonical_hash
from research.research_os.expansion.v2_stage_executor import v2_artifact_path
from research.research_os.expansion.v2_state import V2StateStore
from research.research_os.worker_preflight import run_worker_preflight

V1_BRANCH = "builder/oracle-economic-loop-recovery-20261019"
SCIENCE = tuple(PREFIX + name for name in ("tasks/", "events/", "receipts/", "artifacts/", "hypotheses/", "assessments/", "runtime/worker_wakes/"))


def assert_quiesced():
    for unit in ("quant-research-worker.timer", "quant-research-worker.service", "quant-research-worker-v2.timer", "quant-research-worker-v2.service"):
        state = subprocess.run(["systemctl", "is-active", unit], capture_output=True, text=True).stdout.strip()
        if state in ("active", "activating", "reloading"):
            raise ValueError("SCHEDULER_OR_WRITER_NOT_QUIESCED:" + unit)


def store(config):
    return GitHubStateStore(cache=Path(config["cache"]), repository=config["repository"], branch=config["branch"])


def migrate(config):
    assert_quiesced()
    target = store(config)
    source = GitHubStateStore(cache=Path("/var/lib/quant-research/github.git"), repository=config["repository"], branch=V1_BRANCH)
    with source.snapshot() as old, target.snapshot() as new:
        source_preflight = run_worker_preflight(old.base)
        target_preflight = run_worker_preflight(new.base)
        governed = V2StateStore(target, config["model_backend"]["model"])
        governed._preflight(new)
        epoch_binding = {k: governed.last_preflight[k] for k in ("research_epoch_id", "epoch_manifest_hash", "policy_hash")}
        for path in ("runtime/CONTROL_PLANE.json", "runtime/WORKFLOW_LANES.json", "runtime/RESEARCH_FRONTIER.json", "legacy/source_manifest.json"):
            if old.blobs.get(PREFIX + path) != new.blobs.get(PREFIX + path):
                raise ValueError("GOVERNANCE_TRANSFER_REQUIRES_EXPLICIT_RECONCILIATION:" + path)
        receipt_path = PREFIX + f"artifacts/oracle-v2-migration/{old.head}.json"
        if receipt_path in new.blobs:
            return dict(new.read(receipt_path), current_epoch_binding=epoch_binding)
        with target._locked():
            target._git("fetch", "--no-tags", target.remote, old.head)
            base = target._git("merge-base", old.head, new.head).decode().strip()
            rows = target._git("ls-tree", "-rz", base, "--", PREFIX).split(b"\0")
        original = {row.split(b"\t", 1)[1].decode(): row.split(b"\t", 1)[0].decode().split()[2]
                    for row in rows if row}
        writes = {}
        for path in old.blobs:
            if not path.startswith(SCIENCE) or old.blobs[path] == original.get(path):
                continue
            current_blob = new.blobs.get(path)
            if current_blob not in (None, original.get(path), old.blobs[path]):
                current = new.read(path)
                migration = current.get("v2_migration") or {}
                projection = {k: v for k, v in current.items() if k != "v2_migration"}
                if (not path.startswith(PREFIX + "tasks/") or not migration
                        or migration.get("projection_hash") != canonical_hash(projection)):
                    raise ValueError("CONCURRENT_SCIENTIFIC_MIGRATION_CONFLICT:" + path)
            writes[path] = old.read(path)
            if path.startswith(PREFIX + "tasks/") and current_blob:
                current = new.read(path)
                floor = current.get("lease", {}).get("generation", 0)
                incoming = writes[path].get("lease", {}).get("generation", 0)
                if incoming < floor:
                    writes[path]["lease"]["generation"] = floor
                    writes[path]["v2_migration"] = dict(
                        source_head=old.head, source_blob=old.blobs[path],
                        projection_hash=canonical_hash({k: v for k, v in writes[path].items() if k != "v2_migration"}),
                        disposition="SOURCE_STATE_IMPORTED_WITH_MONOTONE_LEASE_FENCE")
        for path in original:
            if path.startswith(SCIENCE) and path not in old.blobs:
                raise ValueError("MIGRATION_WILL_NOT_DELETE_DURABLE_EVIDENCE:" + path)
        merged_tasks = {PREFIX + f"tasks/{t['task_id']}.json": t for t in new.tasks()}
        merged_tasks.update({p: v for p, v in writes.items() if p.startswith(PREFIX + "tasks/")})
        blocked = []
        now = datetime.now(timezone.utc).isoformat()
        for path, raw in merged_tasks.items():
            stale_canary = (raw.get("task_id", "").startswith("AAA-V2-CANARY-")
                            and raw["task_id"] != "AAA-V2-CANARY-" + config["release_sha"][:16])
            if raw.get("status") not in ("READY", "CLAIMED") or (raw.get("research_contract_version") == "v2-core" and not stale_canary):
                continue
            task = deepcopy(raw)
            session = "V2-MIGRATION-" + task["task_id"] + "-" + old.head[:12]
            generation = task["lease"]["generation"] + 1
            task["status"] = "BLOCKED"
            previous_lease = deepcopy(task["lease"])
            task["lease"] = dict(generation=generation, owner="oracle-v2.migration", claimed_at=now, expires_at=now)
            projection_hash = canonical_hash({k: v for k, v in task.items() if k != "v2_migration"})
            task["v2_migration"] = dict(source_head=old.head, source_blob=old.blobs.get(path), previous_lease=previous_lease,
                                        disposition="LEGACY_CONTEXT_REQUIRES_NEW_V2_TRIAL", scientific_decision=None,
                                        projection_hash=projection_hash)
            event_path = PREFIX + f"events/{task['task_id']}/{session}.json"
            receipt = PREFIX + f"receipts/{task['task_id']}/{session}.json"
            writes[path] = task
            writes[event_path] = dict(event_id=session, session_id=session, worker_id="oracle-v2.migration",
                                      action_id=task["task_id"], event_type="ACTION_COMPLETED", event_seq=1,
                                      generation=generation, emitted_at=now,
                                      payload={"result": "CONTRACT_MIGRATION_BLOCKED", "scientific_decision": None})
            writes[receipt] = dict(receipt_id=session, task_id=task["task_id"], worker_id="oracle-v2.migration",
                                   status="BLOCKED", started_at=now, completed_at=now, input_head=new.head,
                                   summary="Execution paused for new V2 trial provenance; no scientific falsification.",
                                   authority_assertion=dict(ASSERTION), evidence_refs=[event_path])
            blocked.append(task["task_id"])
        report = dict(schema_version="v2-authoritative-state-transfer-v1", source_branch=V1_BRANCH, source_head=old.head,
                      destination_branch=BRANCH, destination_input_head=new.head, merge_base=base,
                      source_blob_bindings={p: old.blobs[p] for p in writes if p in old.blobs},
                      source_preflight=source_preflight, target_preflight=target_preflight,
                      current_epoch_binding=epoch_binding,
                      legacy_execution_blocked=blocked, v1_quiesced=True, authority=dict(AUTHORITY), outcome_accessed=False)
        writes[receipt_path] = report
        assert_quiesced()
        # Fence both the source branch and target HEAD before the canonical CAS.
        observed = source._git("ls-remote", source.remote, source.ref).decode().split()[0]
        if observed != old.head:
            raise ValueError("V1_STATE_ADVANCED_DURING_TRANSFER")
        target.commit(new, writes, create_only=[p for p in writes if p not in new.blobs], message="Research OS V2 bounded authority transfer")
        return report


def synthetic_task(task_id):
    return dict(task_id=task_id, task_type="FUNDAMENTAL_RESEARCH", required_capability="fundamental",
                research_contract_version="v2-core", priority=2147483647, status="READY",
                inputs={"canary": True, "research_contract_version": "v2-core"},
                allowed_actions=["read Legacy", "research one bounded documentary candidate"],
                forbidden_actions=["freeze_hypothesis", "economic outcome", "prospective observation", "orders", "live trading"],
                success_condition="Traceable negative structural screen, not a new freeze or economic result.",
                authority=dict(AUTHORITY, scope="V2_PRE_OUTCOME_CANARY"),
                lease=dict(generation=0, owner=None, claimed_at=None, expires_at=None),
                created_at=datetime.now(timezone.utc).isoformat())


def qualify(config, output):
    report = dict(status="IN_PROGRESS", evidence_scope="LIVE_ORACLE_V2_CORE", release_sha=config["release_sha"],
                  config_hash=canonical_hash(config), gates={gate: False for gate in GATES}, authority=dict(AUTHORITY))
    def save():
        pending = output.with_suffix(".tmp"); pending.write_bytes(json_bytes(report)); pending.replace(output)
    try:
        report["ci"] = verify_ci(config); report["gates"]["exact_release_ci"] = True
        report["instance"] = instance_identity(config["vm_ocid"]); report["gates"]["oracle_identity"] = True
        report["boot_id"] = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        readonly = output.parent / "real-readonly.json"
        subprocess.run([sys.executable, "-B", "scripts/prove_oracle_v2_dry_run.py", "--sha", config["release_sha"],
                        "--output", str(readonly), "--scope", "LIVE_ORACLE_GITHUB_READ_ONLY"], check=True, timeout=360, capture_output=True)
        report["readonly"] = json.loads(readonly.read_text()); report["gates"]["real_readonly_entrypoint"] = True
        backend = backend_from_config(config)
        governed = build_v2_worker(config).store
        with governed.snapshot():
            report["epoch_binding"] = {k: governed.last_preflight[k] for k in (
                "research_epoch_id", "epoch_manifest_hash", "policy_hash")}
        report["model_health"] = backend.healthcheck()
        report["local_reasoning"] = _reason(backend, "disconfirmation", {
            "claim": "A duplicate documentary candidate must remain blocked.", "mechanism": "Frozen research memory prevents rediscovery.",
            "falsification_scope": "Reject a claim of novelty if source and economic identity overlap."})
        report["gates"]["local_gpt_oss_reasoning"] = True
        assert_quiesced(); report["gates"]["v1_quiesced_during_writes"] = True
        report["migration"] = migrate(config); report["gates"]["canonical_migration"] = True
        task_id = "AAA-V2-CANARY-" + config["release_sha"][:16]
        report["task_id"] = task_id
        transport = store(config); task_path = PREFIX + f"tasks/{task_id}.json"
        with transport.snapshot() as snapshot:
            if task_path not in snapshot.blobs:
                transport.commit(snapshot, {task_path: synthetic_task(task_id)}, create_only=[task_path], message="Research OS V2 ideation canary")
        canary = dict(config, canary_task_id=task_id, lease_seconds=90)
        canary_path = output.parent / "canary-worker.json"; canary_path.write_bytes(json_bytes(canary)); canary_path.chmod(0o600)
        def wake():
            p = subprocess.run([sys.executable, "-B", "-s", "-m", "research.research_os.oracle_worker_v2", "--config", str(canary_path)],
                               capture_output=True, text=True, timeout=480, check=True)
            return json.loads(p.stdout.splitlines()[0])
        with transport.snapshot() as snapshot: task = snapshot.read(task_path)
        if task["status"] != "BLOCKED":
            if not task.get("execution", {}).get("completed_stages"):
                report["legacy_wake"] = wake()
            with transport.snapshot() as snapshot: task = snapshot.read(task_path)
            if task["status"] != "CLAIMED":
                crashed = subprocess.run([sys.executable, "-B", "-m", "deploy.oracle_v2_canary", "--config", str(canary_path),
                                          "--crash-after-claim"], timeout=120)
                if crashed.returncode != 75: raise ValueError("V2_ACTUAL_PROCESS_CRASH_NOT_PROVEN")
            with transport.snapshot() as snapshot:
                task = snapshot.read(task_path)
                intent = task["execution"]["v2_trial_intent"]
                if snapshot.read(intent)["state"] != "STARTED_BEFORE_IDEATION": raise ValueError("IDEATION_INTENT_NOT_DURABLE")
                expiry = clock(task["lease"]["expires_at"])
            report["gates"]["trial_before_ideation"] = True; save()
            while datetime.now(timezone.utc) <= expiry: time.sleep(2)
            report["research_wake"] = wake()
        with transport.snapshot() as snapshot:
            task = snapshot.read(task_path)
            trial = snapshot.read(v2_artifact_path(task, "research_trial.json"))
            paths = [p for p in snapshot.blobs if p.startswith(PREFIX + f"receipts/{task_id}/")]
            if task["status"] != "BLOCKED" or task["lease"]["generation"] < 3 or len(paths) != 2:
                raise ValueError("EXPECTED_DUPLICATE_SCREEN_OR_RECOVERY_NOT_PROVEN")
            if trial["proposal_count"] != 1 or len(trial["ideation_intents"]) < 2 or trial["retry_count"] < 1:
                raise ValueError("IDEATION_CRASH_ACCOUNTING_NOT_PROVEN")
            for name in ("candidate_draft.json", "leakage.json", "negative_memory.json"):
                snapshot.read(v2_artifact_path(task, name))
            if v2_artifact_path(task, "candidate_frozen.json") in snapshot.blobs: raise ValueError("CANARY_FROZE_DUPLICATE")
            for path in paths:
                if any(snapshot.read(path)["authority_assertion"].values()): raise ValueError("UNSAFE_CANARY_AUTHORITY")
            before = snapshot.head
            report.update(receipts=paths, trial=trial, sidecar_paths=[p for p in snapshot.blobs if p.startswith(PREFIX + f"artifacts/{task_id}/oracle-v2/")])
        report["terminal_replay"] = wake()
        with transport.snapshot() as snapshot:
            if snapshot.head != before: raise ValueError("TERMINAL_REPLAY_WROTE_OR_DUPLICATED_WORK")
        report["gates"].update(trial_before_ideation=True, claim_expiry_recovered=True, v2_sidecars_persisted=True,
                               no_duplicate_replay=True, authority_closed=True)
        if not all(report["gates"].values()): raise ValueError("V2_LIVE_GATE_MISSING")
        report.update(status="PASS_V2_PRE_ACTIVATION", completed_at=datetime.now(timezone.utc).isoformat(),
                      hosted_model_calls=0, outcome_accessed=False, scheduler_enabled=False)
        save()
        with transport.snapshot() as snapshot:
            path = PREFIX + f"artifacts/{task_id}/live-qualification.json"
            if path not in snapshot.blobs:
                transport.commit(snapshot, {path: report}, create_only=[path], message="Research OS V2 actual Oracle qualification")
        return report
    except Exception as exc:
        report.update(status="BLOCKED", blocker=type(exc).__name__ + ":" + str(exc)); save(); raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--migration-only", action="store_true")
    parser.add_argument("--crash-after-claim", action="store_true")
    args = parser.parse_args(); config = json.loads(args.config.read_text())
    if args.crash_after_claim:
        worker = build_v2_worker(config)
        def die(point):
            if point == "after_claim": os._exit(75)
        worker.fault = die; worker.wake(); raise ValueError("V2_CRASH_NOT_TRIGGERED")
    result = migrate(config) if args.migration_only else qualify(config, args.output)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__": main()
