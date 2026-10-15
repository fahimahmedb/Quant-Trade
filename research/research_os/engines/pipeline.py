from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from research.research_os.control_plane import load_control_plane
from research.research_os.legacy import LegacyKnowledgeBase
from research.research_os.scientific_store import build_scientific_ledgers
from .builtin import ENGINE_REGISTRY
from .cross_exam import cross_examine
from .decay import decay_monitor
from .live_bridge import worker_events
from .portfolio import build_portfolio_map, economic_identity
from .protocol import EngineContext
from .shadow import shadow_register
from .telemetry import learning_telemetry
from .validation import independent_validate, red_team


ENGINE_ACTIVITY = {
    "QUANT_MECHANISM": "data-qualification",
    "FUNDAMENTAL": "document-reading",
    "EVENT_DOCUMENT": "document-reading",
    "INSTITUTIONAL_FLOW": "source-research",
}


def run_pipeline(fixture: Dict[str, Any], *, legacy_ledger_path: Optional[Path] = None) -> Dict[str, Any]:
    run_id = fixture["run_id"]
    base_time = fixture["base_time"]
    context = EngineContext(run_id=run_id, synthetic_only=True)
    base = Path(__file__).resolve().parents[1]

    control_plane = load_control_plane(base)
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
            "ui_activity": ENGINE_ACTIVITY[output["engine_family"]],
        })

    ledger_bundle = build_scientific_ledgers(
        run_id=run_id,
        outputs=outputs,
        timestamp=base_time,
    )
    scientific_ledger = ledger_bundle["scientific_ledger"]
    trial_records = ledger_bundle["trial_records"]
    scientific_ledger.append("LEGACY_REFERENCE", legacy.summary())
    scientific_ledger.append("CONTROL_PLANE_SNAPSHOT", {
        "status": control_plane["status"],
        "capabilities": control_plane["capabilities"],
        "global_authority": control_plane["global_authority"],
    })

    legacy_screen = [legacy.screen_candidate(output["candidate"]) for output in outputs]
    stages.append({
        "worker_id": "legacy-gate.v0",
        "action_id": "legacy:screen",
        "label": "Legacy anti-restart gate",
        "detail": "Screen candidates against pinned reconciled historical memory",
        "ui_activity": "document-reading",
    })

    cross_exam = cross_examine(outputs)
    stages.append({
        "worker_id": "cross-exam.v0",
        "action_id": "cross-exam:multi-engine",
        "label": "Cross examination",
        "detail": "Challenge shared exposures without mutating frozen hypotheses",
        "ui_activity": "audit-red-team",
    })

    validations = [independent_validate(output) for output in outputs]
    stages.append({
        "worker_id": "validator.v0",
        "action_id": "validate:multi-engine",
        "label": "Independent validation",
        "detail": "Validate canonical fields and authority boundaries",
        "ui_activity": "audit-red-team",
    })

    red = red_team(outputs)
    stages.append({
        "worker_id": "red-team.v0",
        "action_id": "red-team:multi-engine",
        "label": "Red Team",
        "detail": "Check duplicate mechanisms and exposure overlap",
        "ui_activity": "audit-red-team",
    })

    identities = [economic_identity(output) for output in outputs]
    portfolio = build_portfolio_map(identities)
    stages.append({
        "worker_id": "portfolio-map.v0",
        "action_id": "portfolio:map",
        "label": "Portfolio map",
        "detail": "Map economic identity and overlap without capital allocation",
        "ui_activity": "data-qualification",
    })

    shadow = shadow_register(outputs)
    stages.append({
        "worker_id": "shadow-registry.v0",
        "action_id": "shadow:register",
        "label": "Shadow registration",
        "detail": "Register draft-only prospective contracts; no observation starts",
        "ui_activity": "commit-persistence",
    })

    decay = decay_monitor(shadow)
    telemetry = learning_telemetry(outputs=outputs, validations=validations, red_team=red)
    stages.append({
        "worker_id": "learning-telemetry.v0",
        "action_id": "telemetry:record",
        "label": "Learning telemetry",
        "detail": "Record research-process telemetry without fabricating effective trials",
        "ui_activity": "commit-persistence",
    })

    events = worker_events(run_id, stages, base_time=base_time)

    no_exact_legacy_duplicates = all(item["status"] != "BLOCK_EXACT_LEGACY_DUPLICATE" for item in legacy_screen)
    passed = (
        control_plane["status"] == "PASS"
        and len(outputs) == 4
        and scientific_ledger.verify()
        and len(trial_records) == 4
        and all(t["effective_trials_status"] == "UNKNOWN" for t in trial_records)
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
        "control_plane": control_plane,
        "legacy": {
            "summary": legacy.summary(),
            "screen": legacy_screen,
        },
        "scientific_ledger": {
            "verified": scientific_ledger.verify(),
            "entry_count": len(scientific_ledger.entries),
            "entries": scientific_ledger.entries,
        },
        "trial_ledger": trial_records,
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
            "production_workers": False,
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
    ledger_path = base / "simulations" / "scientific_ledger.jsonl"
    trials_path = base / "simulations" / "trial_ledger.json"
    imported = base / "legacy" / "LEGACY_RESEARCH_LEDGER.imported.json"
    fixture = json.loads(fixture_path.read_text())
    result = run_pipeline(fixture, legacy_ledger_path=imported if imported.exists() else None)
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    ledger_path.write_text("".join(json.dumps(e, sort_keys=True, separators=(",", ":")) + "\n" for e in result["scientific_ledger"]["entries"]))
    trials_path.write_text(json.dumps(result["trial_ledger"], indent=2, sort_keys=True) + "\n")
    print(f"MULTI_ENGINE_PIPELINE={result['status']}")


if __name__ == "__main__":
    main()
