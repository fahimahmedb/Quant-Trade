"""MEGA B producer-level Discovery Engine.

Consumes a qualified Research Intelligence RUN_PRODUCER decision, enriches the
existing canonical Candidate additively, applies family-specific scientific
admission law, reuses canonical implementability, and emits a tamper-evident
Factory handoff. No scheduling, outcome access, validation, Red Team,
observation, or trading authority is owned here.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import hashlib
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .engines.protocol import validate_engine_output
from .expansion.implementability_depth import assess_implementability_depth

UNKNOWN = "UNKNOWN"
DISCOVERY_VERSION = "mega-b-discovery-v1"
DISCOVERY_BINDING_VERSION = "mega-b-discovery-binding-v1"
FACTORY_BINDING_VERSION = "mega-b-factory-handoff-binding-v1"
SUPPORTED_FAMILIES = {
    "QUANT_MECHANISM", "EVENT_DOCUMENT", "FUNDAMENTAL", "INSTITUTIONAL_FLOW",
}
AUTHORITY = {
    "economic_experiment_authorized": False,
    "prospective_observation_authorized": False,
    "real_capital_authorized": False,
    "live_trading_authorized": False,
    "outcome_accessed": False,
}
_SAFE_OUTCOME_TEXT = {
    UNKNOWN, "NOT_OBSERVED", "NOT_AUTHORIZED", "UNEXECUTED", "SEALED_BY_AUTHORITY",
}
_OUTCOME_KEYS = {
    "alpha", "observed_alpha", "pnl", "pnl_series", "realized_pnl", "unrealized_pnl",
    "profit", "profitability", "return", "returns", "return_series",
    "realized_return_series", "observed_return", "realized_return", "sharpe", "sortino",
    "performance", "effect_size", "observed_effect", "market_response", "price_response",
    "post_event_price", "price_series", "fill", "fills", "equity_curve", "drawdown",
    "win_rate", "hit_rate", "economic_result", "outcome", "outcomes",
}
_REQUIRED_EXPRESSION_FIELDS = (
    "direction_exposure_semantics", "eligibility", "position_expression",
    "cost_model_requirements", "capacity_requirements", "data_requirements",
    "execution_assumptions", "falsification_relevant_implementation_conditions",
)


def _known(value: Any) -> bool:
    if value is None or isinstance(value, bool):
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().upper() not in {
            "", UNKNOWN, "NONE", "N/A", "NA", "UNSPECIFIED", "UNAVAILABLE", "NOT_ESTIMATED", "TBD",
        }
    if isinstance(value, float):
        return value == value and value not in (float("inf"), float("-inf"))
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, (list, tuple, set, frozenset)):
        return bool(value)
    return True


def _value(mapping: Mapping[str, Any], key: str) -> Any:
    value = mapping.get(key, UNKNOWN)
    return value if _known(value) else UNKNOWN


def _clock(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _stable_key(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()


def _safe_outcome_value(value: Any) -> bool:
    return value is None or value is False or (isinstance(value, str) and value in _SAFE_OUTCOME_TEXT)


def _string_list(value: Any) -> List[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, (list, tuple, set, frozenset)):
        return [str(item) for item in value if _known(item)]
    return []


def _outcome_payload_present(value: Any) -> bool:
    """Detect outcome-bearing values recursively without treating closed sentinels as outcomes."""
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = str(key).strip().lower()
            if normalized == "outcome_accessed":
                if item is not False:
                    return True
                continue
            if normalized in _OUTCOME_KEYS and not _safe_outcome_value(item):
                return True
            if _outcome_payload_present(item):
                return True
        return False
    if isinstance(value, (list, tuple)):
        return any(_outcome_payload_present(item) for item in value)
    return False


def _source_clocks(
    producer_output: Mapping[str, Any], facts: Mapping[str, Any]
) -> Tuple[Dict[str, Any], List[str]]:
    explicit = facts.get("source_clocks") if isinstance(facts.get("source_clocks"), Mapping) else {}
    documentary = producer_output["candidate"].get("documentary_evidence")
    documentary = documentary if isinstance(documentary, Mapping) else {}
    packet = documentary.get("packet") if isinstance(documentary.get("packet"), Mapping) else {}
    clocks: Dict[str, Any] = {}
    blockers: List[str] = []

    for field in ("published_at", "available_at", "effective_at"):
        observed, declared = packet.get(field), explicit.get(field)
        if _known(observed) and _known(declared) and observed != declared:
            blockers.append(f"SOURCE_CLOCK_CONFLICT:{field}")
        chosen = observed if _known(observed) else declared
        clocks[field] = chosen if _known(chosen) else UNKNOWN

    observed_freeze, declared_freeze = documentary.get("freeze_time"), explicit.get("freeze_time")
    if _known(observed_freeze) and _known(declared_freeze) and observed_freeze != declared_freeze:
        blockers.append("SOURCE_CLOCK_CONFLICT:freeze_time")
    clocks["freeze_time"] = (
        observed_freeze if _known(observed_freeze)
        else (declared_freeze if _known(declared_freeze) else UNKNOWN)
    )
    clocks["entry_clock"] = _value(facts, "entry_clock")
    clocks["exit_clock"] = _value(facts, "exit_clock")

    required = ["published_at", "available_at", "entry_clock"]
    if producer_output.get("engine_family") in {"EVENT_DOCUMENT", "INSTITUTIONAL_FLOW"}:
        required.append("effective_at")
    for field in required:
        if not _known(clocks[field]):
            blockers.append(f"SOURCE_CLOCK_MISSING:{field}")

    parsed = {key: _clock(value) for key, value in clocks.items() if _known(value)}
    for field in required:
        if _known(clocks[field]) and parsed.get(field) is None:
            blockers.append(f"SOURCE_CLOCK_INVALID:{field}")
    if _known(clocks["exit_clock"]) and parsed.get("exit_clock") is None:
        blockers.append("SOURCE_CLOCK_INVALID:exit_clock")

    published, available = parsed.get("published_at"), parsed.get("available_at")
    effective, entry, exit_clock = (
        parsed.get("effective_at"), parsed.get("entry_clock"), parsed.get("exit_clock")
    )
    if published and available and published > available:
        blockers.append("SOURCE_TIME_LEAKAGE:PUBLISHED_AFTER_AVAILABLE")
    if available and entry and available > entry:
        blockers.append("SOURCE_TIME_LEAKAGE:ENTRY_BEFORE_AVAILABLE")
    # effective_at is a causal clock, not a generic information-availability gate.
    # A public announcement can legitimately be traded after availability but before
    # its future effective date. Family evidence must qualify the causal transfer /
    # implementation calendar; only availability is the generic anti-leakage boundary.
    if effective and entry:
        clocks["entry_effective_relation"] = (
            "BEFORE_EFFECTIVE" if entry < effective
            else "AT_EFFECTIVE" if entry == effective
            else "AFTER_EFFECTIVE"
        )
    else:
        clocks["entry_effective_relation"] = UNKNOWN
    if entry and exit_clock and entry >= exit_clock:
        blockers.append("EXECUTION_TIMING_IMPOSSIBLE")
    return clocks, sorted(set(blockers))


def _claim_ceiling(dossier: Mapping[str, Any], facts: Mapping[str, Any]) -> Tuple[Any, List[str]]:
    upstream, declared = dossier.get("claim_ceiling", UNKNOWN), facts.get("claim_ceiling", UNKNOWN)
    if _known(upstream):
        blockers = ["CLAIM_CEILING_CONFLICT_WITH_UPSTREAM"] if _known(declared) and declared != upstream else []
        return upstream, blockers
    return (declared if _known(declared) else UNKNOWN), []


def _family_blockers(family: str, facts: Mapping[str, Any], hints: Mapping[str, Any]) -> List[str]:
    evidence = facts.get("family_evidence") if isinstance(facts.get("family_evidence"), Mapping) else {}
    blockers: List[str] = []
    if family == "QUANT_MECHANISM":
        if evidence.get("statistical_signal_only") is True:
            blockers.append("STATISTICAL_SIGNAL_WITHOUT_MECHANISM")
        if evidence.get("mechanism_supported") is not True:
            blockers.append("QUANT_MECHANISM_SUPPORT_UNQUALIFIED")
        if not _known(facts.get("causal_timing")):
            blockers.append("QUANT_CAUSAL_TIMING_UNKNOWN")
        for field in ("regime_identity", "factor_exposure", "beta_exposure"):
            if not _known(hints.get(field)):
                blockers.append(f"QUANT_{field.upper()}_UNKNOWN")
        if not _known(facts.get("turnover_hypothesis")):
            blockers.append("QUANT_TURNOVER_HYPOTHESIS_UNKNOWN")
    elif family == "EVENT_DOCUMENT":
        required = (
            "actor_security_identity_qualified", "novel_information_supported",
            "causal_transfer_supported", "revision_state_qualified", "reaction_horizon_qualified",
        )
        missing = [key for key in required if evidence.get(key) is not True]
        if evidence.get("document_change_only") is True or missing:
            blockers.append("DOCUMENT_CHANGE_NOT_EDGE")
        blockers.extend(f"EVENT_{key.upper()}_MISSING" for key in missing)
    elif family == "FUNDAMENTAL":
        required = (
            "issuer_security_identity_qualified", "pit_facts_qualified",
            "realized_vs_expected_qualified", "expectation_gap_supported",
            "valuation_mispricing_basis_supported", "uncertainty_qualified",
            "restatement_state_qualified",
        )
        missing = [key for key in required if evidence.get(key) is not True]
        if evidence.get("good_fundamentals_only") is True or missing:
            blockers.append("GOOD_FUNDAMENTALS_NOT_MISPRICING")
        blockers.extend(f"FUNDAMENTAL_{key.upper()}_MISSING" for key in missing)
    elif family == "INSTITUTIONAL_FLOW":
        required = (
            "binding_rule_supported", "actual_forced_action_supported",
            "eligibility_supported", "implementation_calendar_supported",
        )
        missing = [key for key in required if evidence.get(key) is not True]
        if evidence.get("rule_exists_only") is True or missing:
            blockers.append("RULE_EXISTS_NOT_FORCED_FLOW")
        blockers.extend(f"FLOW_{key.upper()}_MISSING" for key in missing)
        if not _known(facts.get("crowding_hypothesis")):
            blockers.append("FLOW_CROWDING_HYPOTHESIS_UNKNOWN")
    return blockers


def _identity_keys(discovery: Mapping[str, Any]) -> Dict[str, Any]:
    hints = discovery.get("economic_identity_hints") if isinstance(discovery.get("economic_identity_hints"), Mapping) else {}
    actor = discovery.get("constrained_actor") if _known(discovery.get("constrained_actor")) else discovery.get("causal_actor")
    mechanism_payload = {
        "mechanism_identity": hints.get("mechanism_identity"),
        "payer": discovery.get("payer"),
        "actor": actor,
    }
    exposure_payload = {
        "economic_exposure": hints.get("economic_exposure"),
        "universe": discovery.get("universe"),
        "horizon": discovery.get("horizon"),
    }
    expression_payload = {
        **exposure_payload,
        "instrument": discovery.get("instrument"),
        "wrapper": discovery.get("wrapper"),
    }

    def key(payload: Mapping[str, Any]) -> Any:
        return _stable_key(payload) if all(_known(v) for v in payload.values()) else UNKNOWN

    return {
        "mechanism_key": key(mechanism_payload),
        "exposure_key": key(exposure_payload),
        "expression_key": key(expression_payload),
    }


def _duplicate_assessment(
    discovery: Mapping[str, Any], prior_candidates: Sequence[Mapping[str, Any]]
) -> Dict[str, Any]:
    current = _identity_keys(discovery)
    mechanism_matches: List[str] = []
    exposure_wrapper_matches: List[str] = []
    comparable = 0
    for prior in prior_candidates:
        prior_discovery = prior.get("discovery")
        if not isinstance(prior_discovery, Mapping):
            continue
        prior_keys = _identity_keys(prior_discovery)
        pid = str(prior.get("hypothesis_id") or prior.get("candidate_id") or UNKNOWN)
        if current["mechanism_key"] != UNKNOWN and prior_keys["mechanism_key"] != UNKNOWN:
            comparable += 1
            if current["mechanism_key"] == prior_keys["mechanism_key"]:
                mechanism_matches.append(pid)
        if current["exposure_key"] != UNKNOWN and prior_keys["exposure_key"] != UNKNOWN:
            comparable += 1
            if (
                current["exposure_key"] == prior_keys["exposure_key"]
                and current["expression_key"] != UNKNOWN
                and prior_keys["expression_key"] != UNKNOWN
                and current["expression_key"] != prior_keys["expression_key"]
            ):
                exposure_wrapper_matches.append(pid)
    if mechanism_matches:
        state = "DUPLICATE_MECHANISM"
    elif exposure_wrapper_matches:
        state = "SAME_EXPOSURE_DIFFERENT_WRAPPER"
    elif current["mechanism_key"] == UNKNOWN or current["exposure_key"] == UNKNOWN:
        state = UNKNOWN
    else:
        state = "NO_DUPLICATE_IN_PROVIDED_SCOPE"
    return {
        **current,
        "novelty_state": state,
        "mechanism_match_candidate_ids": sorted(set(mechanism_matches)),
        "same_exposure_different_wrapper_candidate_ids": sorted(set(exposure_wrapper_matches)),
        "comparison_scope": "PROVIDED_PRIOR_CANDIDATES_ONLY",
        "comparable_identity_checks": comparable,
        "lexical_similarity_used": False,
        "empirical_correlation_used": False,
    }


def _implementability_meta(
    discovery: Mapping[str, Any], facts: Mapping[str, Any], *, semantic_blocked: bool
) -> Dict[str, Any]:
    instrument = discovery.get("instrument") if _known(discovery.get("instrument")) else discovery.get("wrapper")
    expression = {
        "instrument": instrument,
        "universe": discovery.get("universe"),
        "entry_clock": discovery["source_clocks"].get("entry_clock"),
        "exit_clock": discovery["source_clocks"].get("exit_clock"),
        "horizon": discovery.get("horizon"),
    }
    for field in _REQUIRED_EXPRESSION_FIELDS:
        expression[field] = facts.get(field, UNKNOWN)
    documentary = discovery.get("evidence_class") == "DOCUMENTARY"
    pit = facts.get("pit_feasible", UNKNOWN)
    if documentary and pit == UNKNOWN:
        pit = True
    expression_complete = all(
        _known(expression.get(field))
        for field in ("instrument", "universe", "entry_clock", "exit_clock", *_REQUIRED_EXPRESSION_FIELDS)
    )
    explicit = facts.get("expression_feasible", UNKNOWN)
    if explicit is False:
        expression_feasible: Any = False
    elif explicit is True:
        expression_feasible = expression_complete and not semantic_blocked
    else:
        expression_feasible = True if expression_complete and not semantic_blocked else UNKNOWN
    return {
        "source_available": facts.get("source_available", UNKNOWN),
        "pit_feasible": pit,
        "expression_feasible": expression_feasible,
        "cost_model_feasible": facts.get("cost_model_feasible", UNKNOWN),
        "capacity_observable": facts.get("capacity_observable", UNKNOWN),
        "operational_complexity": facts.get("operational_complexity", UNKNOWN),
        "economic_expression": expression,
    }


def _discovery_binding(candidate_core: Mapping[str, Any], discovery: Mapping[str, Any]) -> Dict[str, Any]:
    core = deepcopy(dict(discovery))
    core.pop("binding", None)
    duplicate = core.get("duplicate_identity") if isinstance(core.get("duplicate_identity"), Mapping) else {}
    binding = {
        "schema_version": DISCOVERY_BINDING_VERSION,
        "canonical_candidate_hash": _stable_key(candidate_core),
        "discovery_core_hash": _stable_key(core),
        "producer_family": core.get("producer_family"),
        "mechanism_key": duplicate.get("mechanism_key", UNKNOWN),
        "exposure_key": duplicate.get("exposure_key", UNKNOWN),
        "expression_key": duplicate.get("expression_key", UNKNOWN),
        "evidence_refs_hash": _stable_key({"evidence_refs": core.get("evidence_refs", [])}),
        "source_clocks_hash": _stable_key(core.get("source_clocks", {})),
        "ancestry_hash": _stable_key(core.get("ancestry", {})),
        "implementability_hash": _stable_key(core.get("implementability", {})),
        "outcome_accessed": False,
    }
    binding["binding_hash"] = _stable_key(binding)
    return binding


def _factory_binding(
    candidate: Mapping[str, Any], discovery_binding: Mapping[str, Any],
    implementability_receipt: Mapping[str, Any], status: str,
) -> Dict[str, Any]:
    binding = {
        "schema_version": FACTORY_BINDING_VERSION,
        "handoff_status": status,
        "candidate_hash": _stable_key(candidate),
        "discovery_binding_hash": discovery_binding.get("binding_hash"),
        "implementability_receipt_hash": _stable_key(implementability_receipt),
        "factory_law_redefined": False,
        "validator_invoked": False,
        "red_team_invoked": False,
        "experiment_frozen": False,
        "outcome_accessed": False,
    }
    binding["binding_hash"] = _stable_key(binding)
    return binding


def validate_discovery_handoff(result: Mapping[str, Any]) -> None:
    """Recompute identity bindings and authority membranes for a Discovery result."""
    if not isinstance(result, Mapping) or result.get("version") != DISCOVERY_VERSION:
        raise ValueError("unsupported discovery handoff version")
    if result.get("status") not in {"READY_FOR_FACTORY", "BLOCKED_DISCOVERY"}:
        raise ValueError("invalid discovery handoff status")
    if result.get("scheduler_mutation") is not False or result.get("scientific_memory_mutation") is not False:
        raise ValueError("discovery handoff crossed scheduler/memory boundary")
    if result.get("control_plane_mutation") is not False or result.get("outcome_accessed") is not False:
        raise ValueError("discovery handoff crossed control/outcome boundary")
    authority = result.get("authority")
    if not isinstance(authority, Mapping) or any(value is not False for value in authority.values()):
        raise ValueError("discovery authority membrane opened")

    candidate = result.get("candidate")
    discovery = result.get("discovery")
    handoff = result.get("factory_handoff")
    if not isinstance(candidate, Mapping) or not isinstance(discovery, Mapping) or not isinstance(handoff, Mapping):
        raise ValueError("discovery handoff missing candidate/discovery/factory contract")
    if candidate.get("discovery") != discovery:
        raise ValueError("candidate.discovery diverges from discovery contract")
    if _outcome_payload_present(discovery):
        raise ValueError("discovery contract contains outcome-bearing payload")

    candidate_core = deepcopy(dict(candidate))
    candidate_core.pop("discovery", None)
    observed_binding = discovery.get("binding")
    expected_binding = _discovery_binding(candidate_core, discovery)
    if observed_binding != expected_binding:
        raise ValueError("discovery binding hash mismatch")

    expected_status = "EXPERIMENT_READY_HANDOFF" if result["status"] == "READY_FOR_FACTORY" else "NOT_READY"
    if handoff.get("status") != expected_status:
        raise ValueError("factory handoff readiness mismatch")
    if handoff.get("candidate") != candidate:
        raise ValueError("factory handoff candidate binding mismatch")
    producer_output = handoff.get("producer_output")
    if not isinstance(producer_output, Mapping) or producer_output.get("candidate") != candidate:
        raise ValueError("factory producer output candidate binding mismatch")
    for field in (
        "factory_law_redefined", "validator_invoked", "red_team_invoked",
        "experiment_frozen", "scheduler_mutation", "outcome_accessed",
    ):
        if handoff.get(field) is not False:
            raise ValueError(f"factory handoff membrane opened: {field}")
    implementability = handoff.get("implementability_receipt")
    if not isinstance(implementability, Mapping):
        raise ValueError("factory handoff missing implementability receipt")
    expected_factory_binding = _factory_binding(
        candidate, observed_binding, implementability, expected_status
    )
    if handoff.get("binding") != expected_factory_binding:
        raise ValueError("factory handoff binding hash mismatch")


def build_discovery_handoff(
    research_decision: Mapping[str, Any],
    producer_output: Mapping[str, Any],
    *,
    dossier: Mapping[str, Any],
    discovery_facts: Mapping[str, Any],
    prior_candidates: Iterable[Mapping[str, Any]] = (),
) -> Dict[str, Any]:
    """Return one deterministic, outcome-blind producer-to-Factory handoff."""
    validate_engine_output(dict(producer_output))
    output = deepcopy(dict(producer_output))
    candidate = output["candidate"]
    family = str(output.get("engine_family"))
    facts = deepcopy(dict(discovery_facts))
    prior = [deepcopy(dict(item)) for item in prior_candidates]
    blockers: List[str] = []

    if family not in SUPPORTED_FAMILIES:
        blockers.append("UNSUPPORTED_DISCOVERY_FAMILY")
    if (
        research_decision.get("action") != "RUN_PRODUCER"
        or research_decision.get("executable") is not True
        or research_decision.get("scheduler_mutation") is not False
    ):
        blockers.append("RESEARCH_INTELLIGENCE_NOT_QUALIFIED_FOR_PRODUCER")
    decision_candidate = research_decision.get("candidate_id")
    declared_origin = facts.get("research_origin_candidate_id")
    if _known(declared_origin) and _known(decision_candidate) and declared_origin != decision_candidate:
        blockers.append("RESEARCH_INTELLIGENCE_ORIGIN_BINDING_MISMATCH")

    if any(_outcome_payload_present(item) for item in (research_decision, output, dossier, facts)):
        blockers.append("OUTCOME_LEAKAGE_DETECTED")
    if dossier.get("outcome_accessed") is not False:
        blockers.append("OUTCOME_ACCESS_NOT_CLOSED")
    if dossier.get("candidate_mutated") is True:
        blockers.append("UPSTREAM_CANDIDATE_MUTATION_DETECTED")
    for field, expected in (
        ("hypothesis_id", candidate.get("hypothesis_id")),
        ("generation_id", candidate.get("generation_id")),
        ("engine_family", family),
    ):
        observed = dossier.get(field)
        if not _known(observed):
            blockers.append(f"DOSSIER_BINDING_MISSING:{field}")
        elif observed != expected:
            blockers.append(f"DOSSIER_BINDING_MISMATCH:{field}")
    if dossier.get("status") != "PASS":
        blockers.append("PRODUCER_DOSSIER_NOT_QUALIFIED")
    if output.get("synthetic_only") is False and dossier.get("factual_binding_status") != "PASS":
        blockers.append("DOCUMENTARY_SOURCE_BINDING_NOT_QUALIFIED")

    refs = list(output.get("source_refs") or [])
    if not refs:
        blockers.append("MISSING_ADMISSIBLE_SOURCE")
    declared_refs = facts.get("evidence_refs")
    if declared_refs is not None and list(declared_refs) != refs:
        blockers.append("EVIDENCE_REF_CONFLICT_WITH_PRODUCER")

    clocks, clock_blockers = _source_clocks(output, facts)
    blockers.extend(clock_blockers)
    universe, instrument, wrapper = (
        _value(facts, "universe"), _value(facts, "instrument"), _value(facts, "wrapper")
    )
    if universe == UNKNOWN:
        blockers.append("UNDEFINED_UNIVERSE")
    if instrument == UNKNOWN and wrapper == UNKNOWN:
        blockers.append("NO_TRADABLE_INSTRUMENT_OR_WRAPPER")

    payer = _value(facts, "payer")
    causal_actor, constrained_actor = _value(facts, "causal_actor"), _value(facts, "constrained_actor")
    if payer == UNKNOWN:
        blockers.append("CAUSAL_STORY_WITHOUT_PAYER")
    if causal_actor == UNKNOWN and constrained_actor == UNKNOWN:
        blockers.append("CAUSAL_OR_CONSTRAINED_ACTOR_UNKNOWN")
    if facts.get("identity_ambiguity") is True:
        blockers.append("IRREDUCIBLE_IDENTITY_AMBIGUITY")

    expected_costs = facts.get("expected_costs", UNKNOWN)
    capacity = facts.get("capacity_hypothesis", UNKNOWN)
    if not _known(expected_costs):
        blockers.append("EXPECTED_COSTS_UNBOUNDED")
        expected_costs = UNKNOWN
    if not _known(capacity):
        blockers.append("CAPACITY_HYPOTHESIS_UNBOUNDED")
        capacity = UNKNOWN

    candidate_horizon, declared_horizon = candidate.get("horizon", UNKNOWN), facts.get("horizon", UNKNOWN)
    if _known(candidate_horizon) and _known(declared_horizon) and candidate_horizon != declared_horizon:
        blockers.append("HORIZON_CONFLICT_WITH_CANONICAL_CANDIDATE")
    horizon = (
        candidate_horizon if _known(candidate_horizon)
        else (declared_horizon if _known(declared_horizon) else UNKNOWN)
    )
    if horizon == UNKNOWN:
        blockers.append("HORIZON_UNKNOWN")

    claim_ceiling, ceiling_blockers = _claim_ceiling(dossier, facts)
    blockers.extend(ceiling_blockers)
    raw_hints = facts.get("economic_identity_hints") if isinstance(facts.get("economic_identity_hints"), Mapping) else {}
    hints = {
        "mechanism_identity": _value(raw_hints, "mechanism_identity"),
        "economic_exposure": _value(raw_hints, "economic_exposure"),
        "regime_identity": _value(raw_hints, "regime_identity"),
        "factor_exposure": raw_hints.get("factor_exposure", UNKNOWN) if _known(raw_hints.get("factor_exposure")) else UNKNOWN,
        "beta_exposure": raw_hints.get("beta_exposure", UNKNOWN) if _known(raw_hints.get("beta_exposure")) else UNKNOWN,
    }
    if hints["mechanism_identity"] == UNKNOWN:
        blockers.append("MECHANISM_IDENTITY_UNKNOWN")
    if hints["economic_exposure"] == UNKNOWN:
        blockers.append("ECONOMIC_EXPOSURE_IDENTITY_UNKNOWN")
    blockers.extend(_family_blockers(family, facts, hints))

    falsifiers = _string_list(facts.get("falsifiers"))
    if not falsifiers:
        scope = candidate.get("falsification_scope")
        falsifiers = [scope] if _known(scope) else []
    if not falsifiers:
        blockers.append("FALSIFIER_MISSING")

    ancestry_raw = facts.get("ancestry") if isinstance(facts.get("ancestry"), Mapping) else {}
    ancestry = {
        "research_origin_candidate_id": decision_candidate if _known(decision_candidate) else UNKNOWN,
        "hypothesis_id": candidate.get("hypothesis_id"),
        "generation_id": candidate.get("generation_id"),
        "parent_candidate_ids": sorted(set(_string_list(ancestry_raw.get("parent_candidate_ids")))),
        "trial_refs": sorted(set(_string_list(ancestry_raw.get("trial_refs")))),
    }
    documentary = candidate.get("documentary_evidence") if isinstance(candidate.get("documentary_evidence"), Mapping) else {}
    packet = documentary.get("packet") if isinstance(documentary.get("packet"), Mapping) else {}
    evidence_identity = _value(facts, "evidence_identity")
    if evidence_identity == UNKNOWN and _known(packet.get("content_hash")):
        evidence_identity = packet["content_hash"]

    discovery: Dict[str, Any] = {
        "schema_version": DISCOVERY_VERSION,
        "producer_family": family,
        "mechanism": candidate.get("mechanism", UNKNOWN),
        "payer": payer,
        "causal_actor": causal_actor,
        "constrained_actor": constrained_actor,
        "evidence_refs": refs,
        "evidence_identity": evidence_identity,
        "source_family": _value(facts, "source_family"),
        "source_clocks": clocks,
        "universe": universe,
        "instrument": instrument,
        "wrapper": wrapper,
        "horizon": horizon,
        "expected_costs": expected_costs,
        "capacity_hypothesis": capacity,
        "turnover_hypothesis": facts.get("turnover_hypothesis", UNKNOWN) if _known(facts.get("turnover_hypothesis")) else UNKNOWN,
        "crowding_hypothesis": facts.get("crowding_hypothesis", UNKNOWN) if _known(facts.get("crowding_hypothesis")) else UNKNOWN,
        "falsifiers": deepcopy(falsifiers),
        "evidence_gaps": sorted(set(_string_list(facts.get("evidence_gaps")))),
        "claim_ceiling": claim_ceiling,
        "economic_identity_hints": hints,
        "ancestry": ancestry,
        "evidence_class": "DOCUMENTARY" if output.get("synthetic_only") is False else "SYNTHETIC",
        "outcome_accessed": False,
        "authority": deepcopy(AUTHORITY),
    }
    duplicate = _duplicate_assessment(discovery, prior)
    discovery["duplicate_identity"] = duplicate
    if duplicate["novelty_state"] == "DUPLICATE_MECHANISM":
        blockers.append("DUPLICATE_HYPOTHESIS_NOT_NOVEL")
    elif duplicate["novelty_state"] == "SAME_EXPOSURE_DIFFERENT_WRAPPER":
        blockers.append("DUPLICATE_EXPOSURE_DIFFERENT_WRAPPER")
    elif duplicate["novelty_state"] == UNKNOWN:
        discovery["evidence_gaps"] = sorted(
            set(discovery["evidence_gaps"] + ["NOVELTY_IDENTITY_INCOMPLETE"])
        )

    impl_meta = _implementability_meta(discovery, facts, semantic_blocked=bool(blockers))
    output["candidate"] = deepcopy(candidate)
    output["candidate"]["discovery"] = deepcopy(discovery)
    canonical_impl = assess_implementability_depth(output, impl_meta)
    discovery["implementability"] = {
        "status": canonical_impl["implementability_status"],
        "canonical_status": canonical_impl["status"],
        "blocking_reasons": deepcopy(canonical_impl["blocking_reasons"]),
        "source_available": canonical_impl["source_available"],
        "pit_feasible": canonical_impl["pit_feasible"],
        "expression_feasible": canonical_impl["expression_feasible"],
        "cost_model_feasible": canonical_impl["cost_model_feasible"],
        "capacity_observable": canonical_impl["capacity_observable"],
    }
    if canonical_impl["implementability_status"] != "IMPLEMENTABLE":
        blockers.append("EARLY_IMPLEMENTABILITY_NOT_READY")
        blockers.extend(f"IMPLEMENTABILITY:{reason}" for reason in canonical_impl["blocking_reasons"])

    candidate_core = deepcopy(candidate)
    discovery["binding"] = _discovery_binding(candidate_core, discovery)
    output["candidate"] = deepcopy(candidate_core)
    output["candidate"]["discovery"] = deepcopy(discovery)

    blockers = sorted(set(blockers))
    ready = not blockers
    handoff_status = "EXPERIMENT_READY_HANDOFF" if ready else "NOT_READY"
    factory_binding = _factory_binding(
        output["candidate"], discovery["binding"], canonical_impl, handoff_status
    )
    result = {
        "version": DISCOVERY_VERSION,
        "status": "READY_FOR_FACTORY" if ready else "BLOCKED_DISCOVERY",
        "producer_family": family,
        "candidate": deepcopy(output["candidate"]),
        "discovery": deepcopy(discovery),
        "blockers": blockers,
        "factory_handoff": {
            "status": handoff_status,
            "candidate": deepcopy(output["candidate"]),
            "producer_output": deepcopy(output),
            "implementability_meta": deepcopy(impl_meta),
            "implementability_receipt": deepcopy(canonical_impl),
            "binding": factory_binding,
            "factory_law_redefined": False,
            "validator_invoked": False,
            "red_team_invoked": False,
            "experiment_frozen": False,
            "scheduler_mutation": False,
            "outcome_accessed": False,
        },
        "scheduler_mutation": False,
        "scientific_memory_mutation": False,
        "control_plane_mutation": False,
        "outcome_accessed": False,
        "authority": deepcopy(AUTHORITY),
    }
    validate_discovery_handoff(result)
    return result
