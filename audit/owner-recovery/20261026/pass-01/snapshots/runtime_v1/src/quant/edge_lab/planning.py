"""Finite, evidence-bound source investigations; no source I/O or outcome access."""
import copy
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from quant.state import utc_now
from .engine import budget_check, question_due, timestamp
from .store import Refused, digest, event, strict_json


def register(lab, packet):
    required = ("id", "source_id", "source_version", "parent_decision", "question_id",
                "question", "decision_use", "unresolved_fact", "primary_urls", "evidence_ids",
                "trigger_evidence_id", "bounds")
    if any(not packet.get(k) for k in required):
        raise Refused("A research option needs a source version, novel fact, decision use and bounds")
    with lab.store.lock():
        state, control = lab.store.read(), lab.store.control()
        budget_check(state, control)
        parent = state["decisions"].get(packet["parent_decision"])
        if not parent or parent["status"] not in ("WAIT", "QUALIFIED"):
            raise Refused("An option requires a resolved source/construction parent")
        family = state["families"][parent["family"]]
        if family["status"] == "REJECTED_CLOSED":
            raise Refused("Closed economic families cannot return through the planner")
        if not re.fullmatch(r"build:" + re.escape(parent["family"]) + r":[a-z0-9][a-z0-9-]{0,79}", packet["question_id"]):
            raise Refused("Question must retain its parent family")
        if any(e not in parent["evidence"] for e in packet["evidence_ids"]):
            raise Refused("Reuse the parent's cached primary evidence")
        trigger = state["evidence"].get(packet["trigger_evidence_id"], {})
        if trigger.get("kind") not in ("METHOD", "ACCESS", "CONTRADICTION"):
            raise Refused("Explicit non-outcome provenance is required")
        inventory = strict_json(lab.store.root / "sources/SOURCE_INVENTORY.json")
        row = next((r for r in inventory["sources"] if r["id"] == packet["source_id"]), None)
        if not row or digest(row) != packet["source_version"]:
            raise Refused("Option must bind the exact cached catalogue entry")
        if row["qualification"] not in ("SEARCH_IDENTIFIED", "DOCS_VERIFIED", "METADATA_ACCESS_VERIFIED", "DOCS_ACCESS_VERIFIED"):
            raise Refused("Known closed/blocked/qualified sources need distinct primary evidence, not a new option")
        if not isinstance(packet["primary_urls"], list) or any(
                urlparse(u).scheme != "https" or urlparse(u).username or urlparse(u).password
                for u in packet["primary_urls"]):
            raise Refused("Explicit HTTPS primary document paths required")
        if type(packet.get("priority", 10)) is not int:
            raise Refused("A fixed priority is required; no outcome ranking")
        _bounds(packet["bounds"], control)
        identity = packet["id"]
        options = state.setdefault("research_options", {})
        if identity in options:
            if {k: v for k, v in options[identity].items() if k != "registered_at"} == packet:
                return identity
            raise Refused("Registered research options are immutable")
        if packet["question_id"] in state["decisions"] or any(
                o["question_id"] == packet["question_id"] or
                (o["source_id"], o["source_version"]) == (packet["source_id"], packet["source_version"])
                for o in options.values()):
            raise Refused("Source version/question already considered; no renamed repetition")
        options[identity] = {**copy.deepcopy(packet), "registered_at": utc_now()}
        event(state, "RESEARCH_OPTION_REGISTERED", {"id": identity, "source": packet["source_id"],
              "version": packet["source_version"], "question": packet["question_id"], "access": "DOCS_METADATA_ONLY"})
        lab.store.save(state)
        return identity


def _bounds(bounds, control):
    for key in ("max_requests", "max_payload_bytes", "timeout_seconds"):
        if type(bounds.get(key)) is not int or bounds[key] <= 0:
            raise Refused("Finite measured request/byte/time bounds are required")
    if (bounds.get("retries") != 0 or bounds.get("outcome_access") is not False
            or bounds["max_requests"] * bounds["max_payload_bytes"] > control["limits"]["metadata_bytes_per_tick"]
            or bounds["max_requests"] * bounds["timeout_seconds"] > control["limits"]["job_wall_seconds"]):
        raise Refused("Metadata-only option must respect current control ceilings and zero retries")


def project(state, control, now=None):
    now = now or datetime.now(timezone.utc)
    decisions = state["decisions"]
    pending, consumed, blocked = [], [], []
    for option in state.get("research_options", {}).values():
        if option["question_id"] in decisions:
            consumed.append(option["id"])
            continue
        parent = decisions[option["parent_decision"]]
        siblings = [d for d in decisions.values() if d.get("parent_decision") == option["parent_decision"]
                    and d["status"] in ("OPEN", "RESEARCHING", "RECOVERY_NEEDED")]
        try:
            _bounds(option["bounds"], control)
            bounds_ok = True
        except Refused:
            bounds_ok = False
        if parent["status"] not in ("WAIT", "QUALIFIED") or siblings or not bounds_ok or state["families"][parent["family"]]["status"] == "REJECTED_CLOSED":
            blocked.append(option["id"])
        else:
            pending.append(option)
    pending.sort(key=lambda o: (o.get("priority", 10), o["registered_at"], o["id"]))
    recovery = any(d["status"] == "RECOVERY_NEEDED" or (d["status"] == "RESEARCHING" and
                   (now-timestamp(d["claimed_at"])).total_seconds() >= d["lease_seconds"]) for d in decisions.values())
    busy = any(d["status"] == "RESEARCHING" for d in decisions.values()) or any(
        s["status"] == "STARTED" for s in state.get("worker_sessions", {}).values())
    due = any(question_due(d, now) for d in decisions.values())
    dates = sorted(d["not_before"] for d in decisions.values() if d["status"] == "OPEN"
                   and d.get("not_before") and not question_due(d, now))
    status = ("PAUSED" if control["paused"] else "RECOVERY_NEEDED" if recovery else "BUSY" if busy else
              "DUE_QUESTION" if due else "READY_TO_QUALIFY" if pending else "WAIT_FOR_DATE" if dates else "NO_ACCESSIBLE_QUESTION")
    return {"status": status, "pending": pending, "consumed": consumed, "blocked": blocked,
            "next_option": pending[0] if status == "READY_TO_QUALIFY" else None,
            "next_due_at": dates[0] if dates else None,
            "scope": "Finite cached source questions only; no automatic economic test or external access"}


def promote(lab):
    state, control = lab.snapshot()
    budget_check(state, control)
    plan = project(state, control)
    option = plan["next_option"]
    if option is None:
        return plan
    inventory = strict_json(lab.store.root / "sources/SOURCE_INVENTORY.json")
    row = next((r for r in inventory["sources"] if r["id"] == option["source_id"]), None)
    if row is None or digest(row) != option["source_version"]:
        raise Refused("Cached source changed; qualify the delta before promotion")
    lab.build_question(option["question_id"], option["parent_decision"], option["question"],
                       option["decision_use"], option["evidence_ids"])
    # Presence of question_id is the durable consumption marker, including WAIT/CLOSED.
    # The caller publishes this question and its claim together before any reasoning.
    return plan


def reconcile_software(lab, identity, completed_by, evidence_ids, remaining_question, summary):
    with lab.store.lock():
        state, control = lab.store.read(), lab.store.control()
        budget_check(state, control)
        old, done, remaining = (state["decisions"].get(i, {}) for i in (identity, completed_by, remaining_question))
        if (not identity.startswith("build:") or old.get("status") != "WAIT"
                or done.get("status") != "QUALIFIED" or not completed_by.startswith("build:")
                or remaining.get("status") != "WAIT" or not remaining_question.startswith("qualify:")
                or not old.get("family") == done.get("family") == remaining.get("family")):
            raise Refused("Only completed construction can be reconciled; retain the economic WAIT")
        ancestor = done.get("parent_decision")
        visited = set()
        while ancestor and ancestor != identity and ancestor not in visited:
            visited.add(ancestor)
            ancestor = state["decisions"].get(ancestor, {}).get("parent_decision")
        if ancestor != identity or not evidence_ids or any(e not in done["evidence"] for e in evidence_ids) or not summary:
            raise Refused("Exact descendant completion evidence and scope required")
        record = {"completed_by": completed_by, "evidence_ids": evidence_ids,
                  "remaining_question": remaining_question, "summary": summary}
        prior = state.setdefault("decision_reconciliations", {}).get(identity)
        if prior:
            if prior == record:
                return
            raise Refused("A reconciliation cannot be rewritten")
        state["decision_reconciliations"][identity] = record
        event(state, "CONSTRUCTION_RECONCILED", {"id": identity, **record})
        lab.store.save(state)
