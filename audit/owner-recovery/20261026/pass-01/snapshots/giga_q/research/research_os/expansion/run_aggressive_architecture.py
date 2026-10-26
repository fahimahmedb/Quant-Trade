from __future__ import annotations

import json
from pathlib import Path

from .final_shape import run_aggressive_pipeline


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    fixture = json.loads((base / "simulations" / "aggressive_architecture_fixture.json").read_text())
    result = run_aggressive_pipeline(fixture)
    out = base / "simulations" / "aggressive_architecture_result.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"AGGRESSIVE_ARCHITECTURE={result['status']}")
    print(f"FINGERPRINT={result['deterministic_fingerprint']}")


if __name__ == "__main__":
    main()
