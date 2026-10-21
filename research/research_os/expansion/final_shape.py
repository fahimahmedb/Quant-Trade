from __future__ import annotations

import hashlib
import json
from itertools import combinations
from typing import Any, Dict, Iterable, List
from copy import deepcopy

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext
from .archaeology import EdgeArchaeologyEngine


def _hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def assess_implementability(engine_output: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
    from .implementability_depth import assess_implementability_depth
    return assess_implementability_depth(engine_output, meta)


def freeze_experiment_envelope(
    engine_output: Dict[str, Any],
    implementability: Dict[str, Any],
    experiment_meta: Dict[str, Any],
) -> Dict[str, Any]:
    candidate = engine_output["candidate"]
    can_freeze = implementability["status"] == "PASS"
    protocol_payload = {
        "hypothesis_id": candidate["hypothesis_id"],
        "generation_id": candidate["generation_id"],
        "candidate": candidate,
        "dataset_provenance": experiment_meta.get("dataset_provenance", {}),
        "cost_model_version": experiment_meta.get("cost_model_version", "UNSPECIFIED"),
        "code_version": experiment_meta.get("code_version", "UNSPECIFIED"),
        "declared_metrics": experiment_meta.get("declared_metrics", []),
        "declared_decision_map": candidate["decision_map"],
    }
    return {
        "experiment_id": f"EXP-{candidate['hypothesis_id']}-{candidate['generation_id']}",
        "hypothesis_generation": f"{candidate['hypothesis_id']}:{candidate['generation_id']}",
        "status": "FROZEN_READY_NO_OUTCOME" if can_freeze else "NOT_FROZEN_BY_IMPLEMENTABILITY",
        "protocol_hash": _hash(protocol_payload) if can_freeze else None,
        "protocol_payload": protocol_payload if can_freeze else None,
        "dataset_provenance": protocol_payload["dataset_provenance"],
        "cost_model_version": protocol_payload["cost_model_version"],
        "code_version": protocol_payload["code_version"],
        "outcome_opened": False,
        "observed_attempts": 0,
        "effective_trials_status": "UNKNOWN",
        "estimated_effective_trials": None,
        "result": "NOT_OBSERVED",
        "immutable_generation": True,
    }


def independent_validate(
    engine_output: Dict[str, Any],
    implementability: Dict[str, Any],
    envelope: Dict[str, Any],
) -> Dict[str, Any]:
    candidate = engine_output["candidate"]
    failures: List[str] = []
    for field in ("hypothesis_id", "generation_id", "mechanism", "claim", "falsification_scope", "decision_map"):
        if not candidate.get(field):
            failures.append(f"MISSING_{field.upper()}")
    if envelope["status"] == "FROZEN_READY_NO_OUTCOME" and not envelope["protocol_hash"]:
        failures.append("MISSING_PROTOCOL_HASH")
    if envelope["outcome_opened"]:
        failures.append("UNAUTHORIZED_OUTCOME_ACCESS")
    if engine_output.get('synthetic_only') is False:
        from .engine_dossiers_v1 import build_engine_dossier
        dossier = build_engine_dossier(engine_output)
        failures.extend('DOCUMENTARY_DOSSIER_'+reason for reason in dossier['blockers'])
    return {
        "hypothesis_id": candidate["hypothesis_id"],
        "validator": "independent-validator.v1",
        "producer_engine": engine_output["engine_id"],
        "independent_from_producer": True,
        "status": "PASS" if not failures else "BLOCK",
        "failures": failures,
        "implementability_status": implementability["status"],
        "claim_mutated": False,
    }


def red_team(
    engine_output: Dict[str, Any],
    implementability: Dict[str, Any],
    validation: Dict[str, Any],
    experiment_meta: Dict[str, Any],
) -> Dict[str, Any]:
    blocks: List[str] = []
    if validation["status"] != "PASS":
        blocks.append("BLOCK_CLAIM_LEVEL")
    if not experiment_meta.get("pit_controls_declared", False):
        blocks.append("BLOCK_DATA")
    if not experiment_meta.get("leakage_controls_declared", False):
        blocks.append("BLOCK_LEAKAGE")
    if not experiment_meta.get("multiplicity_accounting_declared", False):
        blocks.append("BLOCK_MULTIPLICITY")
    if implementability["cost_model_feasible"] is False:
        blocks.append("BLOCK_COST_MODEL")
    if implementability["capacity_observable"] is False:
        blocks.append("BLOCK_CAPACITY")
    dossier = None
    if engine_output.get('synthetic_only') is False:
        from .engine_dossiers_v1 import build_engine_dossier
        dossier = build_engine_dossier(engine_output)
        if dossier.get('factual_binding_status') != 'PASS':
            blocks.append('BLOCK_DOSSIER_SOURCE')
        if dossier['status'] != 'PASS':
            blocks.append('BLOCK_DOSSIER_SUFFICIENCY')
        if dossier['dossier'].get('disconfirmation_checks', {}).get('status') != 'SUPPORTED':
            blocks.append('BLOCK_DISCONFIRMATION')
    return {
        "hypothesis_id": engine_output["candidate"]["hypothesis_id"],
        "red_team": "red-team.v1",
        "status": "PASS" if not blocks else "BLOCK",
        "negative_rights": sorted(set(blocks)),
        "repair_attempted": False,
        "claim_mutated": False,
        "dossier_hash": dossier.get('dossier_hash') if dossier else None,
    }


def economic_identity_v1(engine_output: Dict[str, Any], identity_meta: Dict[str, Any]) -> Dict[str, Any]:
    from research.research_os.scientific_store import sha256_json

    candidate = engine_output["candidate"]
    tags = sorted(set(candidate.get("economic_tags", [])))
    candidate_hash = sha256_json(candidate)
    candidate_binding = {
        "hypothesis_id": candidate["hypothesis_id"],
        "generation_id": candidate["generation_id"],
        "candidate_hash": candidate_hash,
    }
    identity = {
        "hypothesis_id": candidate["hypothesis_id"],
        "generation_id": candidate["generation_id"],
        "mechanism": candidate["mechanism"],
        "payer": identity_meta.get("payer", "UNKNOWN"),
        "asset": identity_meta.get("asset", "UNKNOWN"),
        "horizon": candidate.get("horizon", "UNKNOWN"),
        "beta": identity_meta.get("beta", "UNKNOWN"),
        "momentum": identity_meta.get("momentum", "UNKNOWN"),
        "vol": identity_meta.get("vol", "UNKNOWN"),
        "liquidity": identity_meta.get("liquidity", "UNKNOWN"),
        "capacity": identity_meta.get("capacity", "UNKNOWN"),
        "tail_exposure": identity_meta.get("tail_exposure", "UNKNOWN"),
        "economic_tags": tags,
        "capital_authority": "NOT_AUTHORIZED",
        "candidate_binding": candidate_binding,
        "candidate_snapshot": deepcopy(candidate),
        "identity_provenance": {
            "candidate_hash": candidate_hash,
            "candidate_binding": deepcopy(candidate_binding),
            "source_hash": "UNKNOWN",
            "dossier_hash": "UNKNOWN",
            "source_refs": [],
        },
    }
    if engine_output.get('synthetic_only') is False:
        from .engine_dossiers_v1 import build_engine_dossier
        dossier = build_engine_dossier(engine_output)
        bound = dossier.get('factual_binding_status') == 'PASS'
        field = {'FUNDAMENTAL':'issuer_identity', 'EVENT_DOCUMENT':'event_identity'}.get(engine_output['engine_family'])
        issuer = dossier['dossier'].get(field, {}) if field else {}
        identity['asset'] = issuer.get('values', {}).get('issuer_id', 'UNKNOWN') if bound else 'UNKNOWN'
        empirical = ('payer', 'horizon', 'beta', 'momentum', 'vol', 'liquidity', 'capacity', 'tail_exposure')
        for key in empirical:
            identity[key] = 'UNKNOWN'
        if not bound:
            identity.update(mechanism='UNKNOWN', economic_tags=[])
        support = {key:{'status':'UNKNOWN', 'support':None} for key in empirical}
        support['asset'] = {
            'status':'SUPPORTED_ISSUER_ONLY' if identity['asset'] != 'UNKNOWN' else 'UNKNOWN',
            'support':deepcopy(issuer.get('support')) if bound else None,
        }
        for key in ('mechanism', 'economic_tags'):
            support[key] = {
                'status':'CANDIDATE_THESIS_ONLY' if bound else 'UNKNOWN',
                'support':{'candidate_hash':candidate_hash, 'paths':[key]} if bound else None,
            }
        identity.update(
            evidence_class='DOCUMENTARY',
            documentary_basis=deepcopy(engine_output),
            identity_provenance={
                'candidate_hash':candidate_hash,
                'candidate_binding':deepcopy(candidate_binding),
                'source_hash':dossier['source_hash'],
                'dossier_hash':dossier['dossier_hash'],
                'source_refs':dossier['source_refs'],
                'field_support':support,
            },
            dossier_status=dossier['status'],
            dossier_blockers=list(dossier['blockers']),
            unverified_identity_metadata_ignored=True,
        )
    return identity


def _jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)


def portfolio_map_v1(identities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compatibility facade over the single canonical structural portfolio engine."""
    from .portfolio_v2 import portfolio_diagnostics_v2

    diagnostics = portfolio_diagnostics_v2(identities)
    return {
        "portfolio_engine": "portfolio-map.v1",
        "identities": identities,
        "pairwise": diagnostics["pairwise"],
        "structural_diagnostics": diagnostics,
        "portfolio_readiness": diagnostics["portfolio_readiness"],
        "empirical_correlation": diagnostics["empirical_correlation"],
        "return_series_consumed": diagnostics["return_series_consumed"],
        "capital_allocation_authorized": False,
        "position_sizing_authorized": False,
        "orders_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
        "marginal_portfolio_contribution": "NOT_ESTIMATED_WITHOUT_ADMISSIBLE_EMPIRICAL_RETURN_DATA",
    }


def forward_register(
    engine_output: Dict[str, Any],
    envelope: Dict[str, Any],
    validation: Dict[str, Any],
    red: Dict[str, Any],
) -> Dict[str, Any]:
    c = engine_output["candidate"]
    eligible = envelope["status"] == "FROZEN_READY_NO_OUTCOME" and validation["status"] == "PASS" and red["status"] == "PASS"
    return {
        "prospective_contract_id": f"PROS-{c['hypothesis_id']}-{c['generation_id']}",
        "hypothesis_id": c["hypothesis_id"],
        "generation_id": c["generation_id"],
        "protocol_hash": envelope["protocol_hash"],
        "readiness": "READY_AWAITING_OWNER_AUTHORITY" if eligible else "NOT_READY",
        "observation_authorization": "NOT_AUTHORIZED",
        "observation_started": False,
        "future_outcomes_consumed": 0,
        "material_change_requires_new_generation": True,
    }


def decay_guard(registrations: List[Dict[str, Any]]) -> Dict[str, Any]:
    assert all(r["observation_authorization"] == "NOT_AUTHORIZED" for r in registrations)
    assert all(r["future_outcomes_consumed"] == 0 for r in registrations)
    return {
        "engine": "decay-monitor.v1",
        "status": "INACTIVE_BY_AUTHORITY",
        "registrations_seen": len(registrations),
        "observations_consumed": 0,
        "decay_decisions_emitted": 0,
    }


def learning_telemetry(
    implementability: List[Dict[str, Any]],
    validations: List[Dict[str, Any]],
    red_teams: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "engine": "meta-research-telemetry.v1",
        "candidates_seen": len(implementability),
        "implementability_pass": sum(x["status"] == "PASS" for x in implementability),
        "implementability_park": sum(x["status"] != "PASS" for x in implementability),
        "validation_blocks": sum(x["status"] != "PASS" for x in validations),
        "red_team_blocks": sum(x["status"] != "PASS" for x in red_teams),
        "effective_trials_status": "UNKNOWN",
        "effective_trials": None,
        "economic_edge_inferred": False,
        "research_budget_allocator_enabled": False,
    }


def run_aggressive_pipeline(fixture: Dict[str, Any]) -> Dict[str, Any]:
    context = EngineContext(run_id=fixture["run_id"], synthetic_only=True)
    outputs: List[Dict[str, Any]] = []
    for key in ("quant", "fundamental", "event_document", "institutional_flow"):
        outputs.append(ENGINE_REGISTRY[key].run(fixture["sources"][key], context))
    outputs.append(EdgeArchaeologyEngine().run(fixture["sources"]["archaeology"], context))

    implementability: List[Dict[str, Any]] = []
    envelopes: List[Dict[str, Any]] = []
    validations: List[Dict[str, Any]] = []
    red_teams: List[Dict[str, Any]] = []
    identities: List[Dict[str, Any]] = []
    forward: List[Dict[str, Any]] = []

    for output in outputs:
        hid = output["candidate"]["hypothesis_id"]
        impl = assess_implementability(output, fixture["implementability"][hid])
        envelope = freeze_experiment_envelope(output, impl, fixture["experiments"][hid])
        validation = independent_validate(output, impl, envelope)
        red = red_team(output, impl, validation, fixture["experiments"][hid])
        identity = economic_identity_v1(output, fixture["economic_identity"][hid])
        registration = forward_register(output, envelope, validation, red)
        implementability.append(impl)
        envelopes.append(envelope)
        validations.append(validation)
        red_teams.append(red)
        identities.append(identity)
        forward.append(registration)

    portfolio = portfolio_map_v1(identities)
    decay = decay_guard(forward)
    telemetry = learning_telemetry(implementability, validations, red_teams)

    authority = {
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
    }

    deterministic_fingerprint = _hash({
        "outputs": outputs,
        "implementability": implementability,
        "envelopes": envelopes,
        "validations": validations,
        "red_teams": red_teams,
        "portfolio": portfolio,
        "forward": forward,
        "decay": decay,
        "telemetry": telemetry,
        "authority": authority,
    })

    status = "PASS"
    if any(e["outcome_opened"] for e in envelopes):
        status = "FAIL"
    if any(r["observation_started"] or r["future_outcomes_consumed"] for r in forward):
        status = "FAIL"
    if portfolio["capital_allocation_authorized"] or portfolio["orders_authorized"]:
        status = "FAIL"
    if any(v["producer_engine"] == v["validator"] for v in validations):
        status = "FAIL"

    return {
        "run_id": fixture["run_id"],
        "status": status,
        "synthetic_only": True,
        "engine_outputs": outputs,
        "implementability": implementability,
        "experiment_envelopes": envelopes,
        "validations": validations,
        "red_teams": red_teams,
        "portfolio": portfolio,
        "forward_farm": forward,
        "decay": decay,
        "learning_telemetry": telemetry,
        "authority": authority,
        "deterministic_fingerprint": deterministic_fingerprint,
    }
