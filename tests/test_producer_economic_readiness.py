from copy import deepcopy

import pytest

from research.research_os.expansion.source_qualification import (
    build_producer_test_readiness,
    qualify_producer_test_readiness,
)


def _candidate_output(family):
    return {
        "engine_family": family,
        "outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
        "candidate": {
            "hypothesis_id": f"TEST-{family}",
            "mechanism": "Documented mechanism premise; economic payoff remains untested.",
            "falsification_scope": "Reject the premise when its declared documentary preconditions fail.",
        },
    }


def _flow_detail():
    return {
        "forced_actor": {
            "status": "PARTIAL",
            "values": {
                "rule_actor": "covered broker/dealer",
                "actual_constrained_actor": "UNKNOWN",
                "forced_quantity": "UNKNOWN",
            },
        },
        "constraint_rule": {
            "status": "SUPPORTED",
            "values": {
                "rule_kind": "STANDARD_SETTLEMENT_OPERATIVE_RULE",
                "legal_basis": "OFFICIAL_CFR_2025_EDITION",
                "current_legal_status": "UNKNOWN",
            },
        },
        "implementation_clock": {
            "status": "PARTIAL",
            "values": {
                "standard_settlement_business_days": "1",
                "tradable_horizon": "UNKNOWN",
            },
        },
        "affected_universe": {
            "status": "PARTIAL",
            "values": {
                "bounded_scope": "ordinary common-equity contracts outside declared exclusions",
                "actual_eligible_quantity": "UNKNOWN",
            },
        },
    }


def _event_detail():
    return {
        "event_identity": {
            "status": "SUPPORTED",
            "values": {
                "issuer_id": "AAPL",
                "event_kind": "DECLARED_CASH_DISTRIBUTION_COMPARISON",
            },
        },
        "document_clock": {
            "status": "SUPPORTED",
            "values": {
                "publication_clock_basis": "FIRST_VERIFIED_PUBLIC_CAPTURE_NOT_HISTORICAL_PIT",
                "historical_pit": "NOT_ESTABLISHED",
            },
        },
        "eligibility_rule": {
            "status": "UNKNOWN",
            "values": {},
        },
    }


def test_flow_readiness_closes_structure_not_economic_unknowns():
    result = build_producer_test_readiness(
        _candidate_output("INSTITUTIONAL_FLOW"),
        _flow_detail(),
    )

    spec = result["specification"]
    assert result["qualification"]["status"] == "PASS"
    assert spec["universe"]["status"] == "PARTIAL"
    assert spec["clock"]["status"] == "PARTIAL"
    assert spec["expression_requirements"]["status"] == "REQUIRED"
    assert spec["data_requirements"]["status"] == "REQUIRED"
    assert spec["cost_capacity_requirements"]["status"] == "REQUIRED"
    assert spec["unsupported_economic_claims"] == {
        "payer": "UNKNOWN",
        "quantity_mechanism": "UNKNOWN",
        "directional_mechanism": "UNKNOWN",
        "empirical_return": "NOT_OBSERVED",
        "capacity_estimate": "NOT_ESTIMATED",
    }
    assert result["outcome_accessed"] is False


def test_event_readiness_does_not_infer_surprise_or_market_response():
    result = build_producer_test_readiness(
        _candidate_output("EVENT_DOCUMENT"),
        _event_detail(),
    )

    spec = result["specification"]
    assert result["qualification"]["status"] == "PASS"
    assert spec["universe"]["status"] == "PARTIAL"
    assert spec["clock"]["status"] == "PARTIAL"
    assert spec["unsupported_economic_claims"]["novelty"] == "UNKNOWN"
    assert spec["unsupported_economic_claims"]["consensus"] == "UNKNOWN"
    assert spec["unsupported_economic_claims"]["surprise"] == "UNKNOWN"
    assert spec["unsupported_economic_claims"]["market_response"] == "NOT_OBSERVED"


def test_quant_readiness_requires_implementability_without_backtest_result():
    detail = {
        "universe_definition": {
            "status": "PARTIAL",
            "values": {"instrument_class": "declared mechanism universe"},
        },
        "expression": {
            "status": "PARTIAL",
            "values": {"instrument": "declared expression", "direction": "UNKNOWN"},
        },
    }
    result = build_producer_test_readiness(
        _candidate_output("QUANT_MECHANISM"),
        detail,
    )

    spec = result["specification"]
    assert result["qualification"]["status"] == "PASS"
    assert spec["clock"]["status"] == "UNKNOWN"
    assert spec["data_requirements"]["status"] == "REQUIRED"
    assert spec["cost_capacity_requirements"]["status"] == "REQUIRED"
    assert spec["unsupported_economic_claims"]["empirical_return"] == "NOT_OBSERVED"


def test_new_claim_requires_legacy_screen_before_readiness_pass():
    base = build_producer_test_readiness(
        _candidate_output("EVENT_DOCUMENT"),
        _event_detail(),
    )["specification"]
    base["legacy_screen"] = {
        "status": "REQUIRED_BEFORE_NEW_CLAIM",
        "new_claim": True,
    }

    qualified = qualify_producer_test_readiness(base)
    assert qualified["status"] == "BLOCK"
    assert "LEGACY_SCREEN_REQUIRED_BEFORE_NEW_PRODUCER_CLAIM" in qualified["blockers"]


def test_legacy_screen_pass_allows_new_claim_contract_without_outcome_access():
    base = build_producer_test_readiness(
        _candidate_output("EVENT_DOCUMENT"),
        _event_detail(),
    )["specification"]
    base["legacy_screen"] = {
        "status": "PASS",
        "new_claim": True,
        "screen_id": "LEGACY-SCREEN-FIXTURE",
    }

    qualified = qualify_producer_test_readiness(base)
    assert qualified["status"] == "PASS"
    assert qualified["outcome_accessed"] is False
    assert qualified["economic_result"] == "NOT_OBSERVED"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("payer", "identified payer"),
        ("quantity_mechanism", "10% forced quantity"),
        ("directional_mechanism", "forced buying"),
        ("surprise", "positive surprise"),
        ("market_response", "positive response"),
        ("empirical_return", "1.2%"),
        ("capacity_estimate", "USD 1m"),
    ],
)
def test_unsupported_documentary_claims_cannot_be_promoted(field, value):
    base = build_producer_test_readiness(
        _candidate_output("INSTITUTIONAL_FLOW"),
        _flow_detail(),
    )["specification"]
    mutated = deepcopy(base)
    mutated["unsupported_economic_claims"][field] = value

    qualified = qualify_producer_test_readiness(mutated)
    assert qualified["status"] == "BLOCK"
    assert any(field.upper() in blocker for blocker in qualified["blockers"])


def test_outcome_access_or_result_is_rejected():
    base = build_producer_test_readiness(
        _candidate_output("EVENT_DOCUMENT"),
        _event_detail(),
    )["specification"]
    base["outcome_accessed"] = True
    base["economic_result"] = "OBSERVED"

    qualified = qualify_producer_test_readiness(base)
    assert qualified["status"] == "BLOCK"
    assert "OUTCOME_ACCESS_NOT_ALLOWED" in qualified["blockers"]
    assert "ECONOMIC_RESULT_NOT_ALLOWED" in qualified["blockers"]
