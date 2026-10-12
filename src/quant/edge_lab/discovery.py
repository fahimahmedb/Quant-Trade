"""Small V4.2 adapter: frozen exploratory contracts and single-use CAS claims."""
import copy
import hashlib
import math
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from quant.state import write_json
from .engine import budget_check, timestamp
from .store import Refused, Store, digest, event, strict_json, verify

VERDICTS = {"KILL_EXPRESSION", "KILL_MECHANISM", "PARK_DATA", "PARK_ECONOMICS",
            "PROMOTE_EXPRESSION", "PROMOTE_MECHANISM", "PROMOTE_HIGH", "INCONCLUSIVE"}
PROMOTIONS = {"PROMOTE_EXPRESSION", "PROMOTE_MECHANISM", "PROMOTE_HIGH"}


def _now(now):
    return now or datetime.now(timezone.utc)


def _cards(state):
    cards = state.get("queue", [])
    if not isinstance(cards, list) or any(not isinstance(c, dict) or not c.get("id") for c in cards):
        raise Refused("Discovery queue requires experiment identities")
    if len({c["id"] for c in cards}) != len(cards):
        raise Refused("Duplicate Discovery experiment identity")
    return cards


def _card(state, identity):
    matches = [c for c in _cards(state) if c["id"] == identity]
    if not matches:
        raise Refused("Unknown Discovery experiment")
    return matches[0]


def validate_contract(card):
    contract = card.get("contract")
    if not isinstance(contract, dict):
        raise Refused("A frozen V4.2 contract is required")
    for field in ("mechanism", "who_pays", "why_persist", "primary_signature",
                  "alternative_explanation", "negative_control"):
        if not contract.get(field):
            raise Refused("Missing contract field: " + field)
    for field in ("TEST_CAN_KILL", "TEST_CAN_SUPPORT", "TEST_CANNOT_SAY"):
        rights = contract.get(field)
        if not isinstance(rights, list) or not rights or any(not isinstance(r, str) for r in rights):
            raise Refused("Explicit asymmetric inference rights required: " + field)
    if (set(contract["TEST_CAN_KILL"]) | set(contract["TEST_CAN_SUPPORT"])) & set(contract["TEST_CANNOT_SAY"]):
        raise Refused("Conflicting inference rights")
    for field in ("BIAS_DIRECTION", "unit_economics", "adequacy", "red_team"):
        if not isinstance(contract.get(field), dict) or not contract[field]:
            raise Refused("Predeclare " + field + " before execution")
    economics = contract["unit_economics"]
    if not economics.get("unit") or not economics.get("break_even_friction"):
        raise Refused("Declare economic units and break-even friction before execution")
    for field in ("central_roundtrip_cost_points", "stress_roundtrip_cost_points"):
        value = economics.get(field)
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise Refused("A finite nonnegative friction band is required")
    if contract["adequacy"].get("failure_verdict") not in ("PARK_DATA", "INCONCLUSIVE"):
        raise Refused("Predeclare the data-adequacy failure verdict")
    minimum = contract["adequacy"].get("minimum_contracts")
    if type(minimum) is not int or minimum < 1 or contract["adequacy"].get("all_or_nothing") is not True:
        raise Refused("Predeclare positive all-or-nothing data adequacy")
    if contract["red_team"].get("required_before_promotion") is not True:
        raise Refused("One predeclared cheap adversarial test is required before promotion")
    if not contract["red_team"].get("method") or not contract["red_team"].get("pass_if"):
        raise Refused("Predeclare the one adversarial method and pass condition")
    if contract.get("claim_ceiling") not in PROMOTIONS:
        raise Refused("An explicit exploratory promotion ceiling is required")
    extension = card.get("extension_contract")
    if extension is not None and (not isinstance(extension, dict) or any(not extension.get(k) for k in
            ("new_information", "decision_impact", "additional_cost", "deadline"))):
        raise Refused("An extension requires information, decision impact, cost and deadline")
    if not card.get("mechanism_cluster"):
        raise Refused("A mechanism cluster is required; experiments are not independent discoveries")
    if card.get("selection", {}).get("economic_plausibility") not in ("HIGH", "MEDIUM", "LOW"):
        raise Refused("Declare ordinal small-capital economic plausibility")
    return contract


def load(directory):
    path = Path(directory) / "STATE.json"
    if not path.exists():
        return None
    with Store(directory).lock():
        state = strict_json(path)
        verify(state)
        _cards(state)
        return state


def save(directory, state):
    """Reuse the existing lock/atomic writer while preserving Discovery history."""
    with Store(directory).lock():
        path = Path(directory) / "STATE.json"
        current = copy.deepcopy(state)
        _cards(current)
        if path.exists():
            prior = strict_json(path)
            verify(prior)
            if current.get("events", [])[:len(prior["events"])] != prior["events"]:
                raise Refused("Discovery events cannot be removed or rewritten")
            if current.get("exposure_ledger", [])[:len(prior.get("exposure_ledger", []))] != prior.get("exposure_ledger", []):
                raise Refused("Discovery exposures cannot be removed or rewritten")
            if not set(prior.get("closed_families", [])) <= set(current.get("closed_families", [])):
                raise Refused("Closed families remain closed")
            for key in ("actual_data_test_attempts", "completed_economic_tests", "experiments_with_decision", "data_parks"):
                if current.get("metrics", {}).get(key, 0) < prior.get("metrics", {}).get(key, 0):
                    raise Refused("Discovery metrics cannot erase prior attempts or outcomes")
            mutable = {"status", "invocation_id", "claimed_at", "lease_seconds", "completed_at",
                       "result", "typed_verdict", "decision", "next", "execution_attempts", "result_sha256"}
            for old in _cards(prior):
                new = _card(current, old["id"])
                if any(new.get(k) != v for k, v in old.items() if k not in mutable):
                    raise Refused("Frozen Discovery declarations cannot change; create a linked experiment")
                if old.get("result") is not None or old["status"] in VERDICTS:
                    if new != old:
                        raise Refused("A prior Discovery result cannot be rewritten or replayed")
                if old["status"] == "RUNNING" and (new["status"] == "TEST_NOW" or any(
                        new.get(k) != old.get(k) for k in ("invocation_id", "claimed_at", "lease_seconds"))):
                    raise Refused("An unfinished economic claim cannot be reset")
        current["integrity"] = digest({k: v for k, v in current.items() if k != "integrity"})
        verify(current)
        write_json(path, current)


def project(state, control, now=None):
    now = _now(now)
    groups = {key: [] for key in ("ready", "running", "recovery", "parked", "finished")}
    active = []
    for card in _cards(state):
        item = copy.deepcopy(card)
        status = card["status"]
        group = "finished" if status in VERDICTS or status in ("KILL", "PROMOTE") else "parked"
        if status == "RUNNING":
            try:
                age = (now - timestamp(card["claimed_at"])).total_seconds()
                valid = bool(card.get("invocation_id")) and 0 <= age < int(card["lease_seconds"])
            except (KeyError, ValueError, TypeError):
                valid = False
            group = "running" if valid else "recovery"
            if valid:
                active.append(item)
        elif status in ("TEST_NOW", "PARK_UNTIL") and (not card.get("not_before") or timestamp(card["not_before"]) <= now):
            try:
                validate_contract(card)
                if card["family"] in state.get("closed_families", []):
                    raise Refused("Closed family")
                selection = card.get("selection", {})
                if selection.get("economic_plausibility") == "LOW" and not selection.get("cheap_family_falsifier"):
                    raise Refused("No plausible small-capital economics")
                group = "ready"
            except Refused as exc:
                item["blocked_reason"] = str(exc)
        groups[group].append(item)
    high = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    low = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    def rank(card):
        s = card.get("selection", {})
        return (high.get(s.get("economic_plausibility"), 3), high.get(s.get("decision_leverage"), 3), high.get(s.get("discriminating_power"), 3),
                low.get(s.get("data_friction"), 3), s.get("expected_minutes", 9999),
                high.get(s.get("mechanism_prior"), 3), high.get(s.get("capturability_plausibility"), 3), card["id"])
    groups["ready"].sort(key=rank)
    unfinished = groups["running"] or groups["recovery"]
    paused = control["paused"]
    status = "PAUSED" if paused else "RUNNING" if active else "RECOVERY_REQUIRED" if unfinished else "READY" if groups["ready"] else "IDLE_NO_ADMISSIBLE_WORK"
    return {"lane": "DISCOVERY", "status": status, "paused": paused, "groups": groups,
            "counts": {k: len(v) for k, v in groups.items()}, "active_lease": active[0] if active else None,
            "next": groups["ready"][0] if groups["ready"] and not paused and not unfinished else None,
            "economic_access_authorized": False, "edge_validated": False}


def _multiplicity(state):
    cards = _cards(state)
    ids = {c["id"] for c in cards} | {r["experiment_id"] for r in state.get("exposure_ledger", [])}
    clusters = {c.get("mechanism_cluster", c["family"]) for c in cards}
    attempts = {cluster: sum(int(c.get("execution_attempts", 0)) for c in cards
                            if c.get("mechanism_cluster", c["family"]) == cluster) for cluster in clusters}
    state["multiplicity"] = {"experiment_count": len(ids), "mechanism_cluster_count": len(clusters),
        "execution_attempts_by_experiment": {c["id"]: int(c.get("execution_attempts", 0)) for c in cards},
        "execution_attempts_by_mechanism_cluster": attempts,
        "independence_claim": "NONE; sibling expressions are not independent discoveries"}


def claim(state, experiment_id, invocation_id, now=None):
    if not isinstance(invocation_id, str) or not invocation_id or len(invocation_id) > 160:
        raise Refused("Invalid Discovery invocation identity")
    if any(c.get("invocation_id") == invocation_id for c in _cards(state)):
        raise Refused("Discovery invocation already used; never replay")
    projection = project(state, {"paused": False}, now)
    if not projection["next"] or projection["next"]["id"] != experiment_id:
        raise Refused("Only the next admissible Discovery experiment may be claimed")
    updated = copy.deepcopy(state)
    card = _card(updated, experiment_id)
    if card.get("result") is not None or card.get("execution_attempts", 0):
        raise Refused("A Discovery economic attempt cannot be repeated")
    card.update(status="RUNNING", invocation_id=invocation_id, claimed_at=_now(now).isoformat(),
                lease_seconds=int(card.get("max_time_minutes", 60)) * 60, execution_attempts=1)
    updated.setdefault("exposure_ledger", []).append({"experiment_id": experiment_id,
        "invocation_id": invocation_id, "at": card["claimed_at"],
        "source_scope": card["contract"].get("source_scope", card.get("runner")),
        "contract_sha256": card.get("contract_sha256"), "manifest_sha256": card.get("manifest_sha256")})
    metrics = updated.setdefault("metrics", {})
    metrics["actual_data_test_attempts"] = metrics.get("actual_data_test_attempts", 0) + 1
    updated["updated_at"] = card["claimed_at"]
    updated["status"] = "RUNNING"
    _multiplicity(updated)
    event(updated, "DISCOVERY_CLAIMED", {"experiment_id": experiment_id, "invocation_id": invocation_id})
    updated["integrity"] = digest({k: v for k, v in updated.items() if k != "integrity"})
    return updated


def complete(state, experiment_id, invocation_id, result, now=None):
    updated = copy.deepcopy(state)
    card = _card(updated, experiment_id)
    if card["status"] != "RUNNING" or card.get("invocation_id") != invocation_id or card.get("result") is not None:
        raise Refused("Complete the exact original unfinished Discovery claim once")
    contract = validate_contract(card)
    if not isinstance(result, dict) or result.get("experiment_id") != experiment_id:
        raise Refused("Result must identify the exact frozen experiment")
    verdict = result.get("typed_verdict")
    if verdict not in VERDICTS or not isinstance(result.get("adequacy_passed"), bool):
        raise Refused("A typed verdict and explicit data adequacy result are required")
    adequate = result["adequacy_passed"]
    if not adequate and verdict != contract["adequacy"]["failure_verdict"]:
        raise Refused("Failed adequacy must use its predeclared verdict")
    if adequate and verdict == "INCONCLUSIVE":
        raise Refused("INCONCLUSIVE is allowed only on predeclared adequacy failure")
    if verdict in contract["TEST_CANNOT_SAY"] or verdict.startswith("KILL_") and verdict not in contract["TEST_CAN_KILL"]:
        raise Refused("Verdict exceeds the frozen inference rights")
    if verdict in PROMOTIONS:
        if verdict not in contract["TEST_CAN_SUPPORT"] or result.get("red_team", {}).get("passed") is not True:
            raise Refused("Promotion requires explicit support rights and the one cheap adversarial test")
        ceilings = {"PROMOTE_EXPRESSION": 0, "PROMOTE_MECHANISM": 1, "PROMOTE_HIGH": 2}
        if ceilings[verdict] > ceilings[contract["claim_ceiling"]]:
            raise Refused("Verdict exceeds the frozen claim ceiling")
        if verdict in ("PROMOTE_MECHANISM", "PROMOTE_HIGH") and result.get("mechanism_signature_passed") is not True:
            raise Refused("Mechanism promotion requires its predeclared distinguishing signature")
    if result.get("edge_validated") or result.get("real_capital_authorized") or result.get("live_trading_authorized"):
        raise Refused("Discovery cannot validate an edge or authorize capital")
    receipt = copy.deepcopy(result)
    receipt.update(label="EXPLORATORY", edge_validated=False, real_capital_authorized=False, live_trading_authorized=False)
    card.update(status=verdict, typed_verdict=verdict, decision=verdict, completed_at=_now(now).isoformat(),
                result=receipt, result_sha256=digest(receipt), next=result.get("next"))
    metrics = updated.setdefault("metrics", {})
    metrics["experiments_with_decision"] = metrics.get("experiments_with_decision", 0) + 1
    metrics["data_parks"] = metrics.get("data_parks", 0) + int(verdict == "PARK_DATA")
    metrics["completed_economic_tests"] = metrics.get("completed_economic_tests", 0) + int(result.get("economics_computed") is True)
    metrics["last_completed_experiment"] = experiment_id
    if result.get("economics_computed") is True:
        metrics["last_completed_economic_test"] = experiment_id
    if verdict == "KILL_MECHANISM" and card["family"] not in updated.setdefault("closed_families", []):
        updated["closed_families"].append(card["family"])
    event(updated, "DISCOVERY_COMPLETED", {"experiment_id": experiment_id, "invocation_id": invocation_id,
          "typed_verdict": verdict, "result_sha256": card["result_sha256"]})
    updated["updated_at"] = _now(now).isoformat()
    updated["status"] = project(updated, {"paused": False}, now)["status"]
    _multiplicity(updated)
    updated["integrity"] = digest({k: v for k, v in updated.items() if k != "integrity"})
    return updated


def execute(directory, root, authority, experiment_id, cache_dir, invocation_id=None, runner=None):
    """Only the fixed known-prefix runner; claim is published before any data body access."""
    fresh = authority.snapshot()
    if fresh["control"]["paused"]:
        raise Refused("PAUSED: no Discovery acquisition or execution")
    budget_check(fresh["state"], fresh["control"])
    if load(directory) != fresh["discovery"]:
        raise Refused("Hydrate the exact remote Discovery state before execution")
    card = _card(fresh["discovery"], experiment_id)
    if card.get("runner") != "vix-known-prefix-v1":
        raise Refused("Unsupported Discovery runner; no generic execution")
    contract = validate_contract(card)
    pinned = []
    for field in ("contract", "manifest"):
        path = (Path(directory) / card[field + "_path"]).resolve()
        if not path.is_relative_to(Path(directory).resolve()) or hashlib.sha256(path.read_bytes()).hexdigest() != card.get(field + "_sha256"):
            raise Refused("Frozen Discovery " + field + " hash mismatch")
        pinned.append(strict_json(path))
    if pinned[0] != contract:
        raise Refused("Frozen contract differs from the inline declaration")
    versions = card.get("code_sha256", {})
    if not {"src/quant/edge_lab/vix.py", "src/quant/edge_lab/discovery.py"} <= versions.keys() or any(fresh.get("code_versions", {}).get(name) != sha or
            not (Path(root) / name).resolve().is_relative_to(Path(root).resolve()) or
            hashlib.sha256((Path(root) / name).read_bytes()).hexdigest() != sha for name, sha in versions.items()):
        raise Refused("Discovery runner code differs from the published frozen versions")
    identity = invocation_id or uuid4().hex
    claimed = claim(fresh["discovery"], experiment_id, identity)
    published = authority.claim(claimed, fresh["sha"])
    save(directory, claimed)
    current = authority.snapshot()
    if current["control"]["paused"]:
        raise Refused("PAUSED: preserve the published economic claim without executing")
    budget_check(current["state"], current["control"])
    if current["sha"] != published or current["discovery"] != claimed:
        raise Refused("Discovery authority changed before execution; preserve the claim")
    if runner is None:
        from .vix import run
        runner = run
    result = runner(pinned[1], contract, Path(cache_dir))
    current = authority.snapshot()
    if current["control"]["paused"]:
        raise Refused("PAUSED: preserve the saved result for explicit reconciliation")
    budget_check(current["state"], current["control"])
    finished = complete(current["discovery"], experiment_id, identity, result)
    completed_sha = authority.claim(finished, current["sha"])
    save(directory, finished)
    return {"status": "COMPLETED", "experiment_id": experiment_id, "invocation_id": identity,
            "claim_commit": published, "published_commit": completed_sha, "result": result}
