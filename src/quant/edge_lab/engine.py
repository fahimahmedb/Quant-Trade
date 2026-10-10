"""Decision events first. Market outcomes require a durable, single-use look."""
from __future__ import annotations

import copy
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .compat import ResearchTask
from quant.state import utc_now, write_json
from .seed import BRANCH, initial_control, initial_state
from .store import Refused, Store, digest, event, strict_json, verify


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise Refused("Timezone is required")
    return parsed.astimezone(timezone.utc)


def overlap(left, right):
    def boundary(value):
        return timestamp(value + "T00:00:00Z" if len(value) == 10 else value)
    return boundary(left[0]) < boundary(right[1]) and boundary(right[0]) < boundary(left[1])


def initialize(directory):
    store = Store(directory)
    with store.lock():
        if store.state_path.exists():
            store.read()
            store.control()
            return store
        if store.control_path.exists():
            raise Refused("State missing with existing controls; restore, do not reset")
        write_json(store.control_path, initial_control())
        store.save(initial_state())
    return store


def budget_check(state, control):
    if control["paused"]:
        raise Refused("PAUSED: " + str(control["pause_reason"]))
    for limit, meter in (("paid_usd_total", "paid_usd"), ("tokens_total", "tokens"),
                         ("cpu_seconds_total", "cpu_seconds")):
        cap, used = control["limits"][limit], state["usage"][meter]
        if cap is not None and used is None:
            raise Refused(f"BUDGET_UNMEASURED: {meter}")
        if cap is not None and (used > cap or (meter != "paid_usd" and used >= cap)):
            raise Refused(f"BUDGET_EXHAUSTED: {meter}")


class Lab:
    def __init__(self, directory):
        self.store = Store(directory)

    def snapshot(self):
        with self.store.lock():
            return self.store.read(), self.store.control()

    def tick(self, observations=None, actor="manual", enabled_confirmed=False):
        """No outcome worker is called by startup, heartbeat, CI, or a changed SHA."""
        cpu_start, wall_start = time.process_time(), time.monotonic()
        with self.store.lock():
            state, control = self.store.read(), self.store.control()
            try:
                budget_check(state, control)
            except Refused as exc:
                state["scheduler"]["last_tick"] = {"at": utc_now(), "actor": actor, "status": str(exc), "new_events": 0}
                self.store.save(state)
                return state
            changes = 0
            for identity, observation in (observations or {}).items():
                # Only allowlisted branch-head metadata, never arbitrary URLs or files.
                if identity not in state["families"] or observation["ref"] != state["families"][identity]["ref"]:
                    raise Refused("Unregistered source")
                if not re.fullmatch(r"[0-9a-f]{40}", observation["sha"]):
                    raise Refused("Invalid source SHA")
                prior = state["sources"].get(identity)
                baseline = state["families"][identity]["sha"]
                state["sources"][identity] = {**observation, "observed_at": utc_now()}
                if observation["sha"] != (prior["sha"] if prior else baseline):
                    decision_id = f"delta:{identity}:{observation['sha']}"
                    if decision_id not in state["decisions"]:
                        state["decisions"][decision_id] = {
                            "status": "OPEN", "family": identity, "priority": state["families"][identity]["priority"],
                            "question": "Lire le delta utile, rapprocher verdict/droits/réservations ; ne pas relancer un test.",
                            "created_at": utc_now(), "evidence": [], "reason": "REMOTE_HEAD_CHANGED"}
                        event(state, "SOURCE_CHANGED", {"id": identity, "old": prior["sha"] if prior else baseline,
                                                        "new": observation["sha"]})
                        changes += 1
            now = datetime.now(timezone.utc)
            for job in state["jobs"].values():
                if job["status"] == "RUNNING" and (now - timestamp(job["started_at"])).total_seconds() > job["lease_seconds"]:
                    job["status"] = "UNKNOWN_OUTCOME"
                    job["blocked_reason"] = "Lease expired: preserve spent look, never auto-retry"
                    look = state["looks"][job["metadata"]["look_id"]]
                    look["status"] = "UNKNOWN_OUTCOME"
                    event(state, "LOOK_QUARANTINED", {"job": job["task_id"], "look": look["id"]})
            for identity, decision in state["decisions"].items():
                if (decision["status"] == "RESEARCHING"
                        and (now - timestamp(decision["claimed_at"])).total_seconds() > decision["lease_seconds"]):
                    decision["status"] = "RECOVERY_NEEDED"
                    event(state, "QUESTION_LEASE_EXPIRED", {"id": identity,
                                                           "next": "Reconcile cached sources/partial receipt; no blind repeated review"})
            if enabled_confirmed:
                state["scheduler"]["enabled_confirmed_at"] = utc_now()
            state["scheduler"]["last_tick"] = {"at": utc_now(), "actor": actor, "status": "IDLE" if not changes else "DECISION_PENDING",
                                                "new_events": changes}
            state["usage"]["cpu_seconds"] += time.process_time() - cpu_start
            state["usage"]["wall_seconds"] += time.monotonic() - wall_start
            self.store.save(state)
            return state

    def evidence(self, packet):
        """Cache versioned source passages; outcome packets must name a charged look."""
        required = ("id", "url", "version", "passage", "fact", "limit", "kind")
        if any(not packet.get(k) for k in required):
            raise Refused("Evidence requires primary URL, version, passage, fact and limit")
        if packet["kind"] not in ("ACCESS", "METHOD", "CONTRADICTION", "OUTCOME", "DATA_EXPOSURE"):
            raise Refused("Unknown evidence kind")
        with self.store.lock():
            state, control = self.store.read(), self.store.control()
            budget_check(state, control)
            identity = packet["id"]
            if identity in state["evidence"]:
                if state["evidence"][identity] != packet:
                    raise Refused("New evidence version needs a new ID")
                return identity
            if packet["kind"] in ("OUTCOME", "DATA_EXPOSURE"):
                look = state["looks"].get(packet.get("look_id"))
                if not look:
                    raise Refused("Exposure must be reserved BEFORE outcomes are read")
            state["evidence"][identity] = copy.deepcopy(packet)
            event(state, "EVIDENCE_ADDED", {"id": identity, "digest": digest(packet), "kind": packet["kind"]})
            self.store.save(state)
        return identity

    def claim_decision(self, identity, actor):
        """Publish this claim with remote CAS BEFORE expensive external reasoning."""
        if not actor:
            raise Refused("Research actor required")
        with self.store.lock():
            state, control = self.store.read(), self.store.control()
            budget_check(state, control)
            decision = state["decisions"][identity]
            if decision["status"] != "OPEN":
                raise Refused("Question already claimed/resolved; do not duplicate reasoning")
            claim_id = digest({"id": identity, "actor": actor, "at": utc_now()})
            decision.update(status="RESEARCHING", claim_id=claim_id, actor=actor,
                            claimed_at=utc_now(), lease_seconds=600)
            event(state, "QUESTION_CLAIMED", {"id": identity, "actor": actor, "claim_id": claim_id})
            self.store.save(state)
            return claim_id

    def decide(self, identity, verdict, evidence_ids, next_action, claim_id=None):
        if verdict not in ("WAIT", "CLOSED", "QUALIFIED", "REJECTED", "INSUFFICIENT_POWER", "INVALID_SOFTWARE"):
            raise Refused("Decision type must distinguish economic, software and power outcomes")
        with self.store.lock():
            state, control = self.store.read(), self.store.control()
            budget_check(state, control)
            decision = state["decisions"][identity]
            if decision["status"] not in ("OPEN", "RESEARCHING", "RECOVERY_NEEDED"):
                raise Refused("Resolved question requires a new event, not another review")
            if decision.get("claim_id") and decision["claim_id"] != claim_id:
                raise Refused("Only the recorded claim may finish/reconcile this question")
            if not evidence_ids or any(x not in state["evidence"] for x in evidence_ids):
                raise Refused("Decision requires cached evidence")
            if verdict in ("REJECTED", "INSUFFICIENT_POWER", "INVALID_SOFTWARE") and not any(
                    state["evidence"][x]["kind"] == "OUTCOME" for x in evidence_ids):
                raise Refused("Missing access/source is not an economic rejection")
            decision.update(status=verdict, evidence=list(evidence_ids), next_action=next_action, resolved_at=utc_now())
            event(state, "DECISION", {"id": identity, "verdict": verdict, "evidence": evidence_ids, "next": next_action})
            self.store.save(state)

    def family(self, identity, mechanism, dataset, evidence_ids):
        """A novel mechanism needs provenance; variants keep the same family."""
        with self.store.lock():
            state, control = self.store.read(), self.store.control()
            budget_check(state, control)
            if identity in state["families"] or not evidence_ids or any(e not in state["evidence"] for e in evidence_ids):
                raise Refused("Existing family or missing provenance")
            mechanism_hash = digest(" ".join(mechanism.lower().split()))
            if any(f.get("mechanism_hash") == mechanism_hash for f in state["families"].values()):
                raise Refused("Same mechanism: add a variant, do not reset trial history")
            state["families"][identity] = {"label": mechanism, "mechanism_hash": mechanism_hash, "dataset": dataset,
                "priority": 10, "status": "HYPOTHESIS", "next": "Choisir un test discriminant accessible.",
                "wake": "Accès/horloge/coûts et protocole admissibles.", "evidence": evidence_ids}
            event(state, "FAMILY_REGISTERED", {"id": identity, "mechanism_hash": mechanism_hash, "dataset": dataset})
            self.store.save(state)

    def freeze(self, protocol):
        required = ("id", "family", "dataset", "stage", "window", "expressions", "cost_paths", "primary",
                    "mechanism", "payer", "clock", "independent_unit", "benchmark", "costs", "rights",
                    "decision_contract", "multiplicity_policy", "runner", "runner_sha256", "evidence_ids")
        if any(not protocol.get(k) for k in required):
            raise Refused("Incomplete economic protocol; no generic Sharpe target substitutes for a decision")
        if protocol["stage"] not in ("EXPLORATION", "VALIDATION", "PROSPECTIVE"):
            raise Refused("Capital decisions are not executable")
        window = protocol["window"]
        if len(window) != 2 or window[0] >= window[1]:
            raise Refused("Invalid half-open window")
        start, end = timestamp(window[0]), timestamp(window[1])
        expressions, paths = protocol["expressions"], protocol["cost_paths"]
        if (len(set(expressions)) != len(expressions) or len(set(paths)) != len(paths)
                or protocol["primary"] not in expressions):
            raise Refused("Duplicate variants or undeclared primary")
        if not re.fullmatch("[0-9a-f]{64}", protocol["runner_sha256"]):
            raise Refused("Runner content must be pinned")
        contract = protocol["decision_contract"]
        if not all(contract.get(x) for x in ("positive", "negative", "inconclusive", "invalid")):
            raise Refused("Every outcome needs a decision, including uncertainty")
        with self.store.lock():
            state, control = self.store.read(), self.store.control()
            budget_check(state, control)
            identity, family = protocol["id"], state["families"].get(protocol["family"])
            if not family or family["status"] == "REJECTED_CLOSED":
                raise Refused("Unknown or terminal family; no renamed restart")
            if family["dataset"] != protocol["dataset"]:
                raise Refused("Dataset identity cannot be changed by a new vendor")
            # Legacy freezes are references, not editable templates. Adoption needs an exact reviewed adapter.
            if family.get("sha"):
                raise Refused("Legacy frozen protocol: use the upstream adapter; do not recreate or alter it")
            if not protocol["evidence_ids"] or any(e not in state["evidence"] for e in protocol["evidence_ids"]):
                raise Refused("Protocol needs primary evidence")
            history = state["baseline"].get(protocol["dataset"], {})
            if protocol["stage"] == "VALIDATION" and not history.get("history_complete"):
                raise Refused("Historical exposure is UNKNOWN; cannot label this a pristine confirmation")
            if protocol["stage"] == "PROSPECTIVE" and start <= datetime.now(timezone.utc):
                raise Refused("Prospective observations must start AFTER the freeze")
            protected = history.get("protected", [])
            if any(overlap(window, w) for w in protected):
                raise Refused("Reserved/closed holdout; neither exploration nor a new vendor clears it")
            if protocol["stage"] == "VALIDATION" and any(overlap(window, w)
                                                          for w in history.get("spent", [])):
                raise Refused("Consumed validation window")
            frozen = copy.deepcopy(protocol)
            frozen.update(frozen_at=utc_now(), hash=digest(protocol))
            if identity in state["protocols"]:
                if state["protocols"][identity]["hash"] != frozen["hash"]:
                    raise Refused("Frozen protocol cannot change")
                return identity
            state["protocols"][identity] = frozen
            event(state, "PROTOCOL_FROZEN", {"id": identity, "hash": frozen["hash"], "stage": protocol["stage"]})
            self.store.save(state)
            return identity

    def reserve(self, protocol_id, data_fingerprint):
        """Charge all paths conservatively; dependent paths are NOT independent N."""
        if not data_fingerprint:
            raise Refused("A specific acquired data version is required")
        with self.store.lock():
            state, control = self.store.read(), self.store.control()
            budget_check(state, control)
            protocol = state["protocols"][protocol_id]
            # The protocol is single-use even when files, vendor or fingerprint change.
            look_id = "look:" + protocol_id
            if look_id in state["looks"]:
                raise Refused("Look already spent/reserved; no opportunistic rerun")
            dataset, window = protocol["dataset"], protocol["window"]
            if protocol["stage"] != "EXPLORATION" and any(
                    x["dataset"] == dataset and overlap(window, x["window"]) for x in state["looks"].values()):
                raise Refused("This outcome window has already been exposed")
            rights = protocol["rights"]
            if not rights.get("permitted") or not rights.get("url") or not rights.get("scope"):
                raise Refused("BLOCKED_PERMISSION: rights are not qualified")
            if protocol.get("paid_usd", 0) != 0:
                raise Refused("Paid access is not authorized")
            charge = len(protocol["expressions"]) * len(protocol["cost_paths"])
            look = {"id": look_id, "protocol": protocol_id, "protocol_hash": protocol["hash"],
                    "dataset": dataset, "window": window, "stage": protocol["stage"],
                    "expressions": protocol["expressions"], "cost_paths": protocol["cost_paths"],
                    "charged_paths": charge, "data_fingerprint": data_fingerprint,
                    "reserved_at": utc_now(), "status": "RESERVED_SPENT"}
            state["looks"][look_id] = look
            state["trial_charges"][dataset] = state["trial_charges"].get(dataset, 0) + charge
            task = ResearchTask(task_id="execute:" + protocol_id, lane=protocol["family"], priority=1,
                                reason="Execute exactly one frozen protocol", worker="pinned_local_runner",
                                data_fingerprint=data_fingerprint, status="RESERVED",
                                metadata={"look_id": look_id, "protocol": protocol_id})
            state["jobs"][task.task_id] = asdict(task)
            event(state, "LOOK_RESERVED_SPENT", look)
            self.store.save(state)
            return look_id

    def execute(self, protocol_id, repository, remote_snapshot, remote_claim):
        """remote_snapshot() must freshly verify GitHub HEAD + controls + state.

        Reservation is published BEFORE this call; remote_claim uses Git CAS to
        publish RUNNING before launching the process. Only that winner executes.
        A local state file or a claimed commit SHA is not a remote durability receipt.
        """
        authority = remote_snapshot()
        verify(authority["state"])
        look_id = "look:" + protocol_id
        with self.store.lock():
            state, control = self.store.read(), self.store.control()
            budget_check(state, control)
            budget_check(authority["state"], authority["control"])
            if (authority["control"].get("schema") != 1
                    or authority["control"].get("real_capital_authorized") is not False
                    or authority["control"].get("live_trading_authorized") is not False):
                raise Refused("Remote controls are not qualified")
            if authority["branch"] != BRANCH or not re.fullmatch("[0-9a-f]{40}", authority["sha"]):
                raise Refused("Wrong remote authority")
            look, remote_look = state["looks"][look_id], authority["state"]["looks"].get(look_id)
            job = state["jobs"]["execute:" + protocol_id]
            if (remote_look != look or look["status"] != "RESERVED_SPENT" or job["status"] != "RESERVED"):
                raise Refused("Reservation not durable, already executing, or outcome uncertain")
            protocol = state["protocols"][protocol_id]
            if authority["state"]["protocols"].get(protocol_id) != protocol:
                raise Refused("Remote protocol mismatch")
            if protocol["stage"] == "PROSPECTIVE" and datetime.now(timezone.utc) < timestamp(protocol["window"][1]):
                raise Refused("WAIT_OBSERVATIONS: do not inspect partial prospective outcomes")
            root = Path(repository).resolve()
            runner = (root / protocol["runner"]).resolve()
            if root not in runner.parents or runner.suffix != ".py" or not runner.is_file():
                raise Refused("Only a pinned Python runner inside this checkout is executable")
            import hashlib
            if hashlib.sha256(runner.read_bytes()).hexdigest() != protocol["runner_sha256"]:
                raise Refused("Runner changed after freeze")
            job.update(status="RUNNING", started_at=utc_now(), lease_seconds=control["limits"]["job_wall_seconds"] + 30)
            look["status"] = "RUNNING_SPENT"
            event(state, "EXECUTION_STARTED", {"look": look_id, "durable_commit": authority["sha"]})
            self.store.save(state)
            # This happens under the stable local lock. Another host wins or loses
            # against the same remote parent; a loser never reads outcomes.
            try:
                claim_sha = remote_claim(state, authority["sha"])
            except Exception as exc:
                job.update(status="UNKNOWN_OUTCOME", last_error="REMOTE_CLAIM_FAILED")
                look["status"] = "UNKNOWN_OUTCOME"
                event(state, "CLAIM_FAILED_NO_EXECUTION", {"look": look_id, "error": type(exc).__name__})
                self.store.save(state)
                raise Refused("Remote claim rejected: do not execute or retry this look") from exc
        # No secrets inherited, no shell, no old QuantSystem boot. Admission trusts pinned reviewed code.
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONPATH": str(root / "src"),
               "TZ": "UTC", "PYTHONNOUSERSITE": "1", "REAL_CAPITAL_AUTHORIZED": "FALSE", "LIVE_TRADING_AUTHORIZED": "FALSE"}
        started = time.monotonic()
        import resource
        child_before = resource.getrusage(resource.RUSAGE_CHILDREN)
        try:
            completed = subprocess.run([sys.executable, str(runner), "--protocol", protocol_id, "--look", look_id],
                                       cwd=root, env=env, capture_output=True, text=True,
                                       timeout=control["limits"]["job_wall_seconds"], check=True)
            if len(completed.stdout.encode()) > 1048576:
                raise Refused("Oversized outcome; keep charged look and inspect diagnostic")
            result = json.loads(completed.stdout, parse_constant=lambda x: (_ for _ in ()).throw(Refused(x)))
            if result.get("look_id") != look_id or result.get("kind") not in (
                    "NEGATIVE", "POSITIVE_EXPLORATORY", "INSUFFICIENT_POWER", "INVALID_SOFTWARE",
                    "SOURCE_UNUSABLE", "PROSPECTIVE_OBSERVATION", "SOFTWARE_CHECK"):
                raise Refused("Invalid outcome contract; no automatic proven-alpha label")
            if result["kind"] != "SOFTWARE_CHECK":
                required = ("nature", "benchmark", "observations", "uncertainty", "risk_exposures", "capacity",
                            "lesson", "next_decision", "protocol_hash", "data_fingerprint")
                if any(not result.get(x) for x in required) or "net_after_costs" not in result:
                    raise Refused("Economic receipt must state net costs, benchmark, information unit, risk and uncertainty")
                if result["protocol_hash"] != protocol["hash"] or result["data_fingerprint"] != look["data_fingerprint"]:
                    raise Refused("Outcome is not bound to its frozen protocol/data")
                if result["nature"] not in ("EXPLORATORY_BACKTEST", "PROSPECTIVE_OBSERVATION", "SOFTWARE_FAILURE", "SOURCE_FAILURE"):
                    raise Refused("Do not relabel realized return or risk premium as residual alpha")
            error = None
        except Exception as exc:
            result, error = None, type(exc).__name__
        with self.store.lock():
            state = self.store.read()
            job = state["jobs"]["execute:" + protocol_id]
            state["looks"][look_id]["status"] = "COMPLETED_SPENT" if result else "UNKNOWN_OUTCOME"
            job.update(status="COMPLETED" if result else "UNKNOWN_OUTCOME", last_error=error,
                       updated_at=utc_now(), metadata={**job["metadata"], "result": result})
            state["usage"]["wall_seconds"] += time.monotonic() - started
            child_after = resource.getrusage(resource.RUSAGE_CHILDREN)
            state["usage"]["cpu_seconds"] += (child_after.ru_utime + child_after.ru_stime
                                              - child_before.ru_utime - child_before.ru_stime)
            event(state, "EXECUTION_RECEIPT", {"look": look_id, "result": result, "error": error,
                                               "wall_seconds": time.monotonic() - started})
            if result and result["kind"] != "SOFTWARE_CHECK":
                family = state["families"][protocol["family"]]
                family["next"] = result["next_decision"]
                family["latest_lesson"] = result["lesson"]
                state["decisions"]["result:" + look_id] = {"status": "OPEN", "family": protocol["family"],
                    "priority": family["priority"], "question": result["next_decision"], "reason": "ECONOMIC_RESULT_REQUIRES_DECISION",
                    "created_at": utc_now(), "evidence": [look_id]}
            self.store.save(state)
            try:
                remote_claim(state, claim_sha)
            except Exception as exc:
                # Durable remote RUNNING stays spent; preserve local receipt/artifact.
                # A newer Owner control or another commit is never overwritten.
                return {"look_id": look_id, "result": result, "error": error,
                        "publication": "PENDING_RECONCILIATION", "reason": type(exc).__name__}
        return {"look_id": look_id, "result": result, "error": error}

    def next_decision(self):
        state, control = self.snapshot()
        if control["paused"]:
            return None
        due = [(k, v) for k, v in state["decisions"].items() if v["status"] == "OPEN"]
        return min(due, key=lambda x: (x[1]["priority"], x[1]["created_at"], x[0]), default=None)
