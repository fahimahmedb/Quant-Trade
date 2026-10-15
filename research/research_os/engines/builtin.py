from __future__ import annotations

from typing import Any, Dict

from .protocol import EngineContext, build_candidate


class QuantMechanismEngine:
    engine_id = "engine.quant.mechanism.v0"
    family = "QUANT_MECHANISM"

    def run(self, source: Dict[str, Any], context: EngineContext) -> Dict[str, Any]:
        return build_candidate(
            engine_id=self.engine_id,
            engine_family=self.family,
            hypothesis_id="SYN-QUANT-001",
            mechanism="Cross-sectional pressure reversal after synthetic liquidity imbalance",
            claim="Synthetic assets with extreme temporary pressure revert over the declared short horizon.",
            falsification_scope="Only the supplied synthetic cross-sectional fixture and declared horizon.",
            decision_map={"supports": "EXPLORE", "fails": "KILL_GENERATION"},
            economic_tags=["liquidity", "short_horizon", "reversal", "equity_beta"],
            source_refs=[source["source_ref"]],
            horizon="1-5d",
            context=context,
        )


class FundamentalEngine:
    engine_id = "engine.fundamental.v0"
    family = "FUNDAMENTAL"

    def run(self, source: Dict[str, Any], context: EngineContext) -> Dict[str, Any]:
        return build_candidate(
            engine_id=self.engine_id,
            engine_family=self.family,
            hypothesis_id="SYN-FUND-001",
            mechanism="Consensus underestimates synthetic margin normalization and free-cash-flow improvement",
            claim="The synthetic issuer should re-rate if declared margin and cash-flow milestones materialize.",
            falsification_scope="Only the synthetic issuer, synthetic statements and declared 2-quarter horizon.",
            decision_map={"milestones_met": "EXPLORE", "milestones_missed": "KILL_GENERATION"},
            economic_tags=["equity_beta", "quality", "margin_revision", "valuation"],
            source_refs=[source["source_ref"]],
            horizon="2q",
            context=context,
        )


class EventDocumentEngine:
    engine_id = "engine.event_document.v0"
    family = "EVENT_DOCUMENT"

    def run(self, source: Dict[str, Any], context: EngineContext) -> Dict[str, Any]:
        return build_candidate(
            engine_id=self.engine_id,
            engine_family=self.family,
            hypothesis_id="SYN-EVENT-001",
            mechanism="Synthetic guidance language implies an earnings-expectation revision not yet fully reflected",
            claim="A declared document change should precede a synthetic consensus revision over the event horizon.",
            falsification_scope="Only the supplied synthetic document pair and synthetic consensus series.",
            decision_map={"revision_materializes": "EXPLORE", "no_revision": "PARK"},
            economic_tags=["equity_beta", "earnings_revision", "event_drift", "information_processing"],
            source_refs=[source["source_ref"]],
            horizon="1-20d",
            context=context,
        )


class InstitutionalFlowEngine:
    engine_id = "engine.institutional_flow.v0"
    family = "INSTITUTIONAL_FLOW"

    def run(self, source: Dict[str, Any], context: EngineContext) -> Dict[str, Any]:
        return build_candidate(
            engine_id=self.engine_id,
            engine_family=self.family,
            hypothesis_id="SYN-FLOW-001",
            mechanism="Synthetic forced rebalancing creates temporary price pressure independent of fundamentals",
            claim="The declared synthetic rebalance produces reversible pressure around the known implementation window.",
            falsification_scope="Only the synthetic rebalance mechanism, assets and implementation window.",
            decision_map={"pressure_then_reversal": "EXPLORE", "no_pressure": "KILL_GENERATION"},
            economic_tags=["forced_flow", "liquidity", "rebalancing", "low_capacity"],
            source_refs=[source["source_ref"]],
            horizon="intraday-3d",
            context=context,
        )


ENGINE_REGISTRY = {
    "quant": QuantMechanismEngine(),
    "fundamental": FundamentalEngine(),
    "event_document": EventDocumentEngine(),
    "institutional_flow": InstitutionalFlowEngine(),
}
