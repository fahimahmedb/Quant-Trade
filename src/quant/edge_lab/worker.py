"""Bounded agent handoff, recovery and receipts. This module never calls a model or a backtest.

The existing cloud task supplies the reasoning. A published session is evidence
of an agent's CLI declaration, not platform delivery telemetry or a daemon host.
V3 may renew an expired reasoning lease on the exact original claim; it never
creates a second claim, retries an economic look or authorizes outcomes.
"""
from datetime import datetime, timezone
from uuid import uuid4

from quant.state import utc_now
from .engine import budget_check, question_due, timestamp
from .store import Refused, event


def _session_for(state, decision_id, claim_id=None):
    matches = [s for s in state.get("worker_sessions", {}).values()
               if s.get("status") == "STARTED" and s.get("question_id") == decision_id
               and (claim_id is None or s.get("claim_id") == claim_id)]
    return matches[0] if len(matches) == 1 else None


def _activity_at(state, identity, decision):
    base = timestamp(decision["claimed_at"])
    session = _session_for(state, identity, decision.get("claim_id"))
    if session and session.get("heartbeat_at"):
        beat = timestamp(session["heartbeat_at"])
        if beat > base:
            base = beat
    return base


def queue(state, control, now=None):
    now = now or datetime.now(timezone.utc)
    groups = {key: [] for key in ("ready", "scheduled", "in_progress", "recovery", "waiting", "finished")}
    for identity, decision in state["decisions"].items():
        reconciliation = state.get("decision_reconciliations", {}).get(identity)
        status = "SOFTWARE_RECONCILED" if reconciliation else decision["status"]
        group = ("ready" if question_due(decision, now) else "scheduled") if status == "OPEN" else {
            "RESEARCHING": "in_progress", "RECOVERY_NEEDED": "recovery", "WAIT": "waiting"}.get(status, "finished")
        if status == "RESEARCHING" and (now - _activity_at(state, identity, decision)).total_seconds() >= decision["lease_seconds"]:
            group = "recovery"
        groups[group].append({"id": identity, "family": decision["family"],
            "status": status, "priority": decision.get("priority", 99),
            "question": decision.get("question"), "next": decision.get("next_action"),
            "decision_use": decision.get("decision_use"), "reconciliation": reconciliation,
            "original_status": decision["status"],
            "not_before": decision.get("not_before"), "claim_id": decision.get("claim_id"),
            "created_at": decision.get("created_at", ""),
            "outcome_access_authorized": False})
    for items in groups.values():
        items.sort(key=lambda item: (item["priority"], item["created_at"], item["id"]))
    return {"paused": control["paused"], "counts": {key: len(items) for key, items in groups.items()},
            "groups": groups, "next": None if control["paused"] else next(iter(groups["recovery"] or groups["ready"]), None),
            "scope": "Decision queue only; a queue item never admits an outcome or resets a look"}


def _validate_context(remote, context, actor):
    if context not in ("interactive", "scheduled-automation") or not actor or len(actor) > 120:
        raise Refused("Explicit agent actor and execution context required")
    if context == "scheduled-automation" and (actor != "scheduled-automation" or not remote["scheduler"].get("enabled")):
        raise Refused("Owner-disabled or mismatched scheduled worker")


def start(lab, authority, actor, context="interactive", invocation_id=None):
    # Fresh remote control is read before remote STATE by the authority.
    fresh = authority.snapshot()
    if fresh["control"]["paused"]:
        raise Refused("PAUSED: no new session or metadata access")
    remote = fresh["state"]
    _validate_context(remote, context, actor)
    budget_check(remote, fresh["control"])
    local, control = lab.snapshot()
    if local != remote or control != fresh["control"]:
        raise Refused("Hydrate the exact remote state before starting an agent session")
    now = datetime.now(timezone.utc)
    # Discovery is a separate economic lane: a V3 reasoning session or recovery
    # cannot consume its ready work, nor does this metadata handoff execute it.
    from .discovery import load as load_discovery, project as project_discovery
    discovery = load_discovery(lab.store.root / "discovery")
    if discovery is not None:
        frontier = project_discovery(discovery, control, now)
        if frontier["next"] is not None:
            return {"status": "DISCOVERY_READY", "lane": "DISCOVERY", "next": frontier["next"],
                    "context": context, "economic_access_authorized": False,
                    "outcome_access_authorized": False,
                    "scope": "Run discovery-execute for this frozen experiment; this handoff creates no session or economic claim."}
        # Discovery remains the primary lane between economic tests, too.
        # A documentary handoff is not an economic reservation or active process.
        return {"status": "DISCOVERY_RESEARCH_READY" if frontier.get("next_work") else frontier["status"],
                "lane": "DISCOVERY", "next": frontier.get("next_work"), "context": context,
                "authority_parent": fresh["sha"], "economic_access_authorized": False,
                "outcome_access_authorized": False,
                "scope": "Documents/metadata qualification only. V3 recovery is independent; price/outcome access still requires a frozen Discovery economic CAS claim."}
    sessions = remote.get("worker_sessions", {})
    work = queue(remote, control, now)
    started = [s for s in sessions.values() if s["status"] == "STARTED"]
    if started:
        if work["counts"]["recovery"]:
            target = work["groups"]["recovery"][0]
            original = _session_for(remote, target["id"], target.get("claim_id"))
            if original:
                return {"status": "RECOVERY_NEEDED", "session_id": original["id"],
                    "claim_id": original["claim_id"], "next": target, "context": context,
                    "scope": "Expired original reasoning lease; renew the same claim with worker-recover. No retry or new claim.",
                    "outcome_access_authorized": False}
        raise Refused("Existing agent session needs completion/recovery; do not start a second worker")
    if work["counts"]["in_progress"]:
        raise Refused("A question is already in progress; preserve its claim")
    if work["counts"]["recovery"]:
        return {"status": "RECOVERY_NEEDED", "next": work["groups"]["recovery"][0],
                "scope": "Reconcile saved evidence; no automatic retry or fresh claim"}
    identity = invocation_id or uuid4().hex
    if not isinstance(identity, str) or not identity or len(identity) > 160:
        raise Refused("Invalid invocation id")
    if identity in sessions:
        raise Refused("Agent invocation already recorded; never replay it")
    from .planning import project, promote
    planning = project(remote, control, now)
    if work["next"] is None:
        planning = promote(lab)
        work = queue(*lab.snapshot(), now=now)
    pending = work["next"]
    claim_id = lab.claim_decision(pending["id"], actor) if pending else None
    with lab.store.lock():
        state = lab.store.read()
        record = {"id": identity, "actor": actor, "context": context,
            "status": "STARTED" if pending else "IDLE", "started_at": utc_now(),
            "heartbeat_at": utc_now(), "lease_seconds": 600,
            "authority_parent": fresh["sha"], "question_id": pending["id"] if pending else None,
            "claim_id": claim_id, "delivery_verified": False,
            "idle_reason": planning["status"] if not pending else None,
            "next_due_at": planning["next_due_at"],
            "planning_option": planning["next_option"]["id"] if planning["next_option"] else None,
            "scope": "Published CLI session declaration; not a signed scheduler receipt or process telemetry"}
        state.setdefault("worker_sessions", {})[identity] = record
        event(state, "AGENT_SESSION_STARTED" if pending else "AGENT_SESSION_IDLE", record)
        lab.store.save(state)
    # Losing CAS stops here: the caller receives no work authorization.
    published = authority.claim(state, fresh["sha"])
    if pending:
        pending = {**pending, "status": "RESEARCHING", "claim_id": claim_id}
    return {"session_id": identity, "status": record["status"], "published_commit": published,
        "claim_id": claim_id, "next": pending, "context": context, "planning": planning,
        "scope": record["scope"], "outcome_access_authorized": False}


def recover(lab, authority, actor, context="scheduled-automation", invocation_id=None):
    """Renew one expired reasoning lease on its exact original claim via CAS."""
    fresh = authority.snapshot()
    if fresh["control"]["paused"]:
        raise Refused("PAUSED: preserve the expired session without new access")
    remote = fresh["state"]
    _validate_context(remote, context, actor)
    budget_check(remote, fresh["control"])
    local, control = lab.snapshot()
    if local != remote or control != fresh["control"]:
        raise Refused("Hydrate the exact remote state before recovering an agent session")
    work = queue(remote, control)
    if not work["groups"]["recovery"]:
        raise Refused("No expired reasoning lease is recoverable")
    target = work["groups"]["recovery"][0]
    original = _session_for(remote, target["id"], target.get("claim_id"))
    if not original:
        raise Refused("Recovery requires the original STARTED session and claim")
    identity = invocation_id or uuid4().hex
    if not isinstance(identity, str) or not identity or len(identity) > 160:
        raise Refused("Invalid recovery invocation id")
    with lab.store.lock():
        state = lab.store.read()
        session = state["worker_sessions"].get(original["id"])
        decision = state["decisions"].get(target["id"])
        if (not session or session["status"] != "STARTED" or not decision
                or decision.get("claim_id") != session.get("claim_id")
                or decision["status"] not in ("RESEARCHING", "RECOVERY_NEEDED")):
            raise Refused("Original claim changed while preparing recovery")
        if session.get("recovery_invocation_id") == identity:
            raise Refused("Recovery invocation already recorded; never replay it")
        now = utc_now()
        session.update(heartbeat_at=now, recovered_at=now, recovery_actor=actor,
            recovery_context=context, recovery_invocation_id=identity,
            recovery_count=int(session.get("recovery_count", 0)) + 1)
        event(state, "AGENT_SESSION_RECOVERED", {"id": session["id"], "question_id": target["id"],
            "claim_id": session["claim_id"], "actor": actor, "context": context,
            "recovery_count": session["recovery_count"], "invocation_id": identity})
        lab.store.save(state)
    published = authority.claim(state, fresh["sha"])
    pending = {**target, "status": "RESEARCHING", "claim_id": original["claim_id"]}
    return {"session_id": original["id"], "status": "RECOVERED", "published_commit": published,
        "claim_id": original["claim_id"], "next": pending, "context": context,
        "recovery_count": state["worker_sessions"][original["id"]]["recovery_count"],
        "scope": "Same original claim renewed after lease expiry; no new claim, outcome access or economic retry.",
        "outcome_access_authorized": False}


def finish(lab, authority, session_id, evidence_ids, summary):
    fresh = authority.snapshot()
    if fresh["control"]["paused"]:
        raise Refused("PAUSED: preserve the partial session without new accesses")
    budget_check(fresh["state"], fresh["control"])
    local, control = lab.snapshot()
    if local != fresh["state"] or control != fresh["control"]:
        raise Refused("Hydrate fresh authority before publishing the agent receipt")
    with lab.store.lock():
        state = lab.store.read()
        session = state.get("worker_sessions", {}).get(session_id)
        if not session or session["status"] != "STARTED":
            raise Refused("Only an existing, unfinished session may be completed")
        decision = state["decisions"][session["question_id"]]
        if decision.get("claim_id") != session["claim_id"] or decision["status"] in ("OPEN", "RESEARCHING", "RECOVERY_NEEDED"):
            raise Refused("Resolve/reconcile the original question first; never retry it")
        if (not evidence_ids or any(i not in decision["evidence"] for i in evidence_ids)
                or not isinstance(summary, str) or not summary.strip() or len(summary) > 1600):
            raise Refused("Receipt needs the resolved question's evidence and a bounded summary")
        session.update(status="COMPLETED", finished_at=utc_now(),
            evidence_ids=list(evidence_ids), summary=summary, decision_status=decision["status"])
        event(state, "AGENT_SESSION_COMPLETED", session)
        lab.store.save(state)
    published = authority.claim(state, fresh["sha"])
    return {"session_id": session_id, "status": "COMPLETED", "published_commit": published,
            "delivery_verified": False, "scope": session["scope"]}
