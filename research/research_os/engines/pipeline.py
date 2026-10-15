from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .builtin import ENGINE_REGISTRY
from .live_bridge import worker_events
from .portfolio import build_portfolio_map, economic_identity
from .protocol import EngineContext
from .shadow import shadow_register
from .validation import independent_validate, red_team


def run_pipeline(fixture: Dict[str, Any]) -> Dict[str, Any]:
    run_id = fixture["run_id"]
    context = EngineContext(run_id=run_id, synthetic_only=True)

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

    events = worker_events(run_id, stages)

    passed = (
        len(outputs) == 4
        and all(v["status"] == "PASS" for v in validations)
        and red["status"] == "PASS"
        and portfolio["capital_allocation_authorized"] is False
        and shadow["prospective_observation_authorized"] is False
        and all(r["observation_started"] is False for r in shadow["registrations"])
        and all(o["synthetic_only"] is True for o in outputs)
    )

    return {
        "run_id": run_id,
        "status": "PASS" if passed else "FAIL",
        "synthetic_only": True,
        "engines": outputs,
        "validations": validations,
        "red_team": red,
        "portfolio": portfolio,
        "shadow": shadow,
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
    fixture = json.loads(fixture_path.read_text())
    result = run_pipeline(fixture)
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"MULTI_ENGINE_PIPELINE={result['status']}")


if __name__ == "__main__":
    main()
