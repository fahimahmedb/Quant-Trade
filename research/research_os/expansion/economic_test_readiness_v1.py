"""Pure pre-outcome composition of the five qualified specialist interfaces.

No scheduler, task store, acquisition, observation or execution entry point is
called here. READY describes a package; it never grants execution authority.
"""
from copy import deepcopy
from math import isfinite

from research.research_os.scientific_store import sha256_json
from .experiment_runner import DryRunExperimentRunner
from .final_shape import assess_implementability, economic_identity_v1, freeze_experiment_envelope
from .portfolio_v2 import portfolio_diagnostics_v2, structural_identity
from .red_team_v2 import red_team_negative_rights_v2
from .source_qualification import build_producer_test_readiness, qualify_source_route
from .validation_v2 import validator_economic_readiness_v3


AUTHORITY = {
    "economic_experiment_authorized": False,
    "prospective_observation_authorized": False,
    "real_capital_authorized": False,
    "live_trading_authorized": False,
}
READY = "READY_FOR_AUTHORIZED_ECONOMIC_TEST"


def economic_test_readiness(package, *, legacy, frozen=None, peer_identities=(), red_team_context=None):
    """Compose supplied metadata only; optionally recheck a previous frozen receipt.

    `legacy` is a loaded LegacyKnowledgeBase. Source snapshots are content
    addresses supplied by the data contract, never fetched or opened here.
    The caller retains the returned frozen receipt for subsequent binding checks.
    """
    try:
        return _compose(package, legacy=legacy, frozen=frozen, peer_identities=peer_identities,
                        red_team_context=red_team_context)
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        return {"status": "BLOCK", "block_reasons": [f"INVALID_READINESS_PACKAGE:{type(error).__name__}:{error}"],
                "authority": dict(AUTHORITY), "outcome_accessed": False,
                "economic_result": "NOT_OBSERVED", "architecture_stop_build": False}


def _compose(package, *, legacy, frozen, peer_identities, red_team_context):
    p = deepcopy(package)
    output = p["engine_output"]
    candidate = output["candidate"]
    meta = p["runner_meta"]
    protocol = meta.get("frozen_protocol") or {}
    clock = protocol.get("clock") or {}
    expression = protocol.get("economic_expression") or {}
    reasons = []

    def require(ok, code):
        if not ok:
            reasons.append(code)

    legacy_screen = legacy.screen_candidate(candidate)
    # An unloaded ledger cannot establish absence of a legacy conflict.
    require(bool(legacy.records), "LEGACY_LEDGER_NOT_LOADED")
    require(legacy_screen["status"] == "NO_EXACT_LEGACY_CONFLICT", legacy_screen["status"])
    implementation = assess_implementability(output, p["implementability_meta"])
    reasons.extend(implementation["blocking_reasons"])
    if output.get("engine_family") == "FUNDAMENTAL" and output.get("synthetic_only") is False:
        from .engine_dossiers_v1 import build_engine_dossier
        require(build_engine_dossier(output)["status"] == "PASS", "FUNDAMENTAL_DOSSIER_NOT_QUALIFIED")
    require(expression == implementation["exact_expression_contract"], "EXPRESSION_CONTRACT_MISMATCH")
    require(output.get("outcome_accessed", False) is False, "PRODUCER_OUTCOME_ACCESS_FORBIDDEN")
    require(output.get("economic_result", "NOT_OBSERVED") == "NOT_OBSERVED", "PRODUCER_RESULT_FORBIDDEN")
    require(type(output.get("synthetic_only")) is bool, "PRODUCER_SYNTHETIC_SCOPE_INVALID")
    require(all(p.get("authority", AUTHORITY).get(k) is False for k in AUTHORITY), "AUTHORITY_MUST_REMAIN_FALSE")

    qualifications = []
    pit = []
    for source in p["sources"]:
        if (source["route"].get("source_class") == "SYNTHETIC_FIXTURE"
                or source["route"].get("permission_state") == "FIXTURE_ONLY"):
            require(output.get("synthetic_only") is True, "FIXTURE_SOURCE_REQUIRES_SYNTHETIC_SCOPE")
        q = qualify_source_route(source["route"], freeze_time=clock["freeze_time"])
        q["snapshot_hash"] = source["snapshot_hash"]
        qualifications.append(q)
        reasons.extend(q["blockers"])
        pit.append({"source_id": source["route"]["route_id"],
                    "snapshot_hash": source["snapshot_hash"],
                    "point_in_time_qualified": q["point_in_time_qualified"],
                    "available_at": source["available_at"],
                    "route_available_at": q["canonical_route"]["availability_start"],
                    "revision_policy": source["route"]["revision_policy"]})
    meta["source_pit_metadata"] = pit
    source_hashes = sorted(q["snapshot_hash"] for q in qualifications)
    manifest_hash = sha256_json(p["sources"])
    require(meta.get("dataset_manifest_hash") == manifest_hash, "DATASET_MANIFEST_BINDING_MISMATCH")

    # Declare implementation assumptions, without estimating economic capacity.
    cost = protocol.get("cost_assumptions") or {}
    capacity = protocol.get("capacity_assumptions") or {}

    def number(value):
        return type(value) in (int, float) and isfinite(value) and value >= 0

    def known(value):
        return isinstance(value, str) and bool(value.strip()) and value.strip().upper() not in (
            "UNKNOWN", "UNAVAILABLE", "UNSPECIFIED", "NOT_ESTIMATED")

    cost_valid = known(cost.get("model_id")) and all(
        number(cost.get(k)) for k in ("fees_bps", "spread_bps", "slippage_bps", "financing_bps", "borrow_bps")
    )
    cap_valid = (known(capacity.get("model_id")) and known(capacity.get("evidence_ref"))
                 and number(capacity.get("max_adv_fraction")) and 0 < capacity["max_adv_fraction"] <= 1)
    require(cost_valid, "COST_ASSUMPTIONS_INVALID")
    require(cap_valid, "CAPACITY_ASSUMPTIONS_INVALID")
    require(bool(protocol.get("multiplicity_family")) and bool(protocol.get("multiplicity_method")),
            "MULTIPLICITY_DECLARATION_MISSING")
    # B2 checks presence; the integration boundary also rejects empty test rules.
    for key in ("sample_definition", "sample_window", "missing_data_policy", "revision_policy",
                "survivorship_policy", "falsification_rule", "decision_map", "benchmark", "gross_metric", "net_metric"):
        require(bool(protocol.get(key)) and protocol[key] != "UNKNOWN", f"PROTOCOL_{key.upper()}_INCOMPLETE")
    require(protocol.get("decision_map") == candidate.get("decision_map"), "DECISION_MAP_BINDING_MISMATCH")
    require(protocol.get("entry_definition") == expression.get("entry_clock"), "ENTRY_CLOCK_BINDING_MISMATCH")
    require(protocol.get("exit_definition") == expression.get("exit_clock"), "EXIT_CLOCK_BINDING_MISMATCH")
    require(protocol.get("universe", {}).get("universe_id") == expression.get("universe"), "UNIVERSE_BINDING_MISMATCH")

    envelope = deepcopy(freeze_experiment_envelope(output, implementation, {
        "dataset_provenance": {"sources": p["sources"], "protocol": protocol},
        "implementability_declaration": implementation,
        "cost_model_version": cost.get("model_id"), "code_version": meta.get("code_sha"),
        "declared_metrics": meta.get("declared_metrics"),
    }))
    runner = DryRunExperimentRunner()
    plan = runner.plan(envelope, qualifications, meta)
    reasons.extend(plan["blockers"])
    require(plan["frozen_protocol_capability"] == "READY", "FROZEN_PROTOCOL_NOT_READY")
    replay = None
    try:
        if plan["status"] == "READY_FOR_REPRODUCIBLE_DRY_RUN":
            replay = runner.replay(plan)
        if frozen is not None:
            runner.verify_bindings(frozen["experiment_plan"], envelope, qualifications, meta)
            require(frozen["package_hash"] == sha256_json(p), "READINESS_PACKAGE_BINDING_MISMATCH")
    except (ValueError, PermissionError) as error:
        reasons.append(str(error))

    producer = build_producer_test_readiness(output, p.get("dossier_detail", {}),
        legacy_screen={"status": "PASS" if not reasons else "BLOCK", "new_claim": True})
    reasons.extend(producer["qualification"]["blockers"])
    binding = {"candidate_hash": sha256_json(candidate), "protocol_hash": envelope["protocol_hash"],
               "source_snapshot_hashes": source_hashes, "execution_plan_hash": plan["execution_plan_hash"]}
    spec = {"instrument_rule": expression.get("instrument"), "side_rule": expression.get("direction_exposure_semantics"),
            "entry_rule": expression.get("entry_clock"), "exit_rule": expression.get("exit_clock"),
            "horizon_rule": expression.get("horizon"), "sizing_rule": expression.get("position_expression")}
    effective = protocol.get("effective_trials")
    bundle = {
        "candidate": candidate, "candidate_hash": sha256_json(candidate),
        "producer_id": output["engine_id"], "validator_id": p["validator_id"],
        "legacy_screening": {"status": "PASS" if legacy_screen["status"] == "NO_EXACT_LEGACY_CONFLICT" else "BLOCK",
                             "evidence_hash": sha256_json({"screen": legacy_screen, "ledger": legacy.ledger})},
        "sources": {"manifest_hash": manifest_hash, "snapshot_hashes": source_hashes, "pit_metadata": pit},
        "clock": clock, "universe": protocol.get("universe", {}),
        "economic_expression": {"status": "COMPLETE", "spec": spec, "expression_hash": sha256_json(spec)},
        "implementability": {"status": implementation["status"], "declaration_hash": sha256_json(implementation)},
        "protocol": envelope,
        "reproducibility": {"status": "BOUND" if replay else "BLOCK", "binding_payload": binding,
                            "binding_hash": sha256_json(binding), "outcome_accessed": False},
        "multiplicity": {"declared": bool(protocol.get("multiplicity_family")), "method": protocol.get("multiplicity_method")},
        "trial_accounting": {"observed_attempt_count": protocol.get("observed_attempt_count"),
                             "effective_trials_status": "UNKNOWN" if effective == "UNKNOWN" else "KNOWN",
                             "estimated_effective_trials": None if effective == "UNKNOWN" else effective},
        "cost_model": {"status": "DECLARED" if cost_valid else "BLOCK", "model_id": cost.get("model_id"),
                       "declaration_hash": sha256_json(cost)},
        "capacity": {"status": "DECLARED" if cap_valid else "BLOCK", "model_id": capacity.get("model_id"),
                     "declaration_hash": sha256_json(capacity)},
        "outcome_access": {"opened": False, "consumed": False, "result": "NOT_OBSERVED"},
    }
    validator = validator_economic_readiness_v3(readiness_bundle=bundle)
    reasons.extend(r["code"] for r in validator["block_reasons"])
    red = red_team_negative_rights_v2(validator, context=red_team_context)
    reasons.extend(red["negative_rights"])
    identity = economic_identity_v1(output, p.get("identity_meta", {}))
    portfolio = portfolio_diagnostics_v2([identity, *deepcopy(list(peer_identities))])

    # Portfolio overlap is a pre-outcome scientific-integrity gate, never an
    # empirical-correlation claim. Besides explicit Portfolio review pairs, a
    # known-equal payer + mechanism with an unknown clock is unresolved rather
    # than distinct and must not pass independent-lineage readiness.
    blocking_pairs = []
    for pair in portfolio.get("pairwise", []):
        structure = pair.get("economic_structure") or {}
        dimensions = structure.get("dimensions") or {}
        explicit_review = bool(pair.get("same_exposure_review_required")) or (
            structure.get("classification") == "HIGH_STRUCTURAL_OVERLAP_REVIEW"
        )
        unresolved_core = (
            dimensions.get("payer") == 1.0
            and dimensions.get("mechanism") == 1.0
            and dimensions.get("timing_clock") is None
        )
        if explicit_review or unresolved_core:
            blocking_pairs.append({
                "left": pair.get("left"),
                "right": pair.get("right"),
                "classification": structure.get("classification"),
                "payer": dimensions.get("payer"),
                "mechanism": dimensions.get("mechanism"),
                "timing_clock": dimensions.get("timing_clock"),
                "basis": "EXPLICIT_REVIEW" if explicit_review else "SAME_PAYER_MECHANISM_CLOCK_UNKNOWN",
            })
    portfolio["readiness_blocking_review_pairs"] = blocking_pairs
    require(not blocking_pairs, "BLOCK_UNRESOLVED_CURRENT_EXPOSURE_OVERLAP")

    ready = not reasons
    return {
        "status": READY if ready else "BLOCK", "block_reasons": sorted(set(reasons)),
        "remaining_execution_blockers": ["OWNER_AUTHORIZATION"] if ready else sorted(set(reasons)),
        "package_hash": sha256_json(p), "legacy_screen": legacy_screen,
        "implementability": implementation, "source_qualifications": qualifications,
        "producer_readiness": producer, "experiment_plan": plan, "deterministic_replay": replay,
        "validator": validator, "red_team": red, "identity": structural_identity(identity), "portfolio": portfolio,
        "authority": dict(AUTHORITY), "outcome_accessed": False, "economic_result": "NOT_OBSERVED",
        "synthetic_only": output.get("synthetic_only"),
        "trial_accounting": bundle["trial_accounting"], "architecture_stop_build": ready,
    }
