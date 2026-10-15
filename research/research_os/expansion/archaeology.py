from __future__ import annotations

from typing import Any, Dict

from research.research_os.engines.protocol import EngineContext, build_candidate


class EdgeArchaeologyEngine:
    engine_id = "engine.edge_archaeology.v0"
    family = "EDGE_ARCHAEOLOGY"

    def run(self, source: Dict[str, Any], context: EngineContext) -> Dict[str, Any]:
        return build_candidate(
            engine_id=self.engine_id,
            engine_family=self.family,
            hypothesis_id=source.get("hypothesis_id", "SYN-ARCH-001"),
            mechanism=source.get(
                "mechanism",
                "A previously documented anomaly may persist only in a narrower operational niche after broad decay.",
            ),
            claim=source.get(
                "claim",
                "Historical negative and variant evidence can identify a bounded surviving niche without replaying spent windows.",
            ),
            falsification_scope=source.get(
                "falsification_scope",
                "Only the supplied synthetic legacy map, declared niche and non-overlapping synthetic window definition.",
            ),
            decision_map={
                "distinct_unspent_niche": "EXPLORE",
                "duplicate_or_spent": "KILL_GENERATION",
                "insufficient_provenance": "PARK",
            },
            economic_tags=source.get(
                "economic_tags",
                ["archaeology", "negative_knowledge", "low_capacity", "mechanism_reuse"],
            ),
            source_refs=[source["source_ref"]],
            horizon=source.get("horizon", "mechanism-dependent"),
            context=context,
        )
