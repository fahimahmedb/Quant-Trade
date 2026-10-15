from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from research.research_os.legacy import LegacyKnowledgeBase
from .builtin import ENGINE_REGISTRY
from .cross_exam import cross_examine
from .decay import decay_monitor
from .live_bridge import worker_events
from .portfolio import build_portfolio_map, economic_identity
from .protocol import EngineContext
from .shadow import shadow_register
from .telemetry import learning_telemetry
from .validation import independent_validate, red_team


def run_pipeline(fixture: Dict[str, Any], *, legacy_ledger_path: Optional[Path] = None) -> Dict[str, Any]:
    run_id = fixture["run_id"]
    context = EngineContext(run_id=run_id, synthetic_only=True)
    base = Path(__file__).resolve().parents[1]
    legacy = LegacyKnowledgeBase.load(base, legacy_ledger_path)

    outputs: List[Dict[str, Any]] = []
    stages: List[Dict[str, str]] = []
    for engine_key in ("quant", "fundamental", "event_document", "institutional_flow"):
        engine = ENGINE_REGISTRY[engine_key]
        output = engine.run(fixture["sources"][engine_key], context)
        outputs.append(output)
        stages.append({
            "worker_id": engine.engine_id,
            "action_id": f"discover:{output['candidate']['hypothesis_id']}",
            "label": f"{output['engine_family']} discovery",
            "detail": output["candidate"]["claim"],
        })

    legacy_screen = [legacy.screen_candidate(output["candidate"]) for output in outputs]
    stages.append({
        "worker_id": "legacy-gate.v0",
        "action_id": "legacy:screen",
        "label": "Legacy anti-restart gate",
        "detail": "Screen candidates against pinned reconciled historical memory",
    })

    cross_exam = cross_examine(outputs)
    stages.append({
        "worker_id": "cross-exam.v0",
        "action_id": "cross-exam:multi-engine",
        "label": "Cross examination",
        "detail": "Challenge shared exposures without mutating frozen hypotheses",
    })

    validations = [independent_validate(output) for output in outputs]
    stages.append({
        "worker_id": "validator.v0",
        "action_id": "validate:multi-engine",
        "label": "Independent validation",
        "detail": "Validate canonical fields and authority boundaries",
    })

    red = red_team(outputs)
    stages.append({
        "worker_id": "red-team.v0",
        "action_id": "red-team:multi-engine",
        "label": "Red Team",
        "detail": "Check duplicate mechanisms and exposure overlap",
    })

    identities = [economic_identity(output) for output in outputs]
    portfolio = build_portfolio_map(identities)
    stages.append({
        "worker_id": "portfolio-map.v0",
        "action_id": "portfolio:map",
        "label": "Portfolio map",
        "detail": "Map economic identity and overlap without capital allocation",
    })

    shadow = shadow_register(outputs)
    stages.append({
        "worker_id": "shadow-registry.v0",
        "action_id": "shadow:register",
        "label": "Shadow registration",
        "detail": "Register draft-only prospective contracts; no observation starts",
    })

    decay = decay_monitor(shadow)
    telemetry = learning_telemetry(outputs=outputs, validations=validations, red_team=red)
    stages.append({
        "worker_id": "learning-telemetry.v0",
        "action_id": "telemetry:record",
        "label": "Learning telemetry",
        "detail": "Record research-process telemetry without fabricating effective trials",
    })

    events = worker_events(run_id, stages)

    no_exact_legacy_duplicates = all(item["status"] != "BLOCK_EXACT_LEGACY_DUPLICATE" for item in legacy_screen)
    passed = (
        len(outputs) == 4
        and no_exact_legacy_duplicates
        and cross_exam["mutated_hypotheses"] is False
        and cross_exam["new_hypotheses_created"] is False
        and all(v["status"] == "PASS" for v in validations)
        and red["status"] == "PASS"
        and portfolio["capital_allocation_authorized"] is False
        and shadow["prospective_observation_authorized"] is False
        and all(r["observation_started"] is False for r in shadow["registrations"])
        and decay["status"] == "INACTIVE_BY_AUTHORITY"
        and telemetry["effective_trials_status"] == "UNKNOWN"
        and all(o["synthetic_only"] is True for o in outputs)
    )

    return {
        "run_id": run_id,
        "status": "PASS" if passed else "FAIL",
        "synthetic_only": True,
        "legacy": {
            "summary": legacy.summary(),
            "screen": legacy_screen,
        },
        "engines": outputs,
        "cross_exam": cross_exam,
        "validations": validations,
        "red_team": red,
        "portfolio": portfolio,
        "shadow": shadow,
        "decay": decay,
        "learning_telemetry": telemetry,
        "worker_events": events,
        "authorities": {
            "real_capital": False,
            "live_trading": False,
            "prospective_observation": False,
            "economic_experiment": False,
        },
    }


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    fixture_path = base / "simulations" / "multi_engine_fixture.json"
    result_path = base / "simulations" / "multi_engine_result.json"
    imported = base / "legacy" / "LEGACY_RESEARCH_LEDGER.imported.json"
    fixture = json.loads(fixture_path.read_text())
    result = run_pipeline(fixture, legacy_ledger_path=imported if imported.exists() else None)
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"MULTI_ENGINE_PIPELINE={result['status']}")


if __name__ == "__main__":
    main()
