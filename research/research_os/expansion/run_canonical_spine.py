from __future__ import annotations

import json
from pathlib import Path

from .canonical_spine import run_canonical_spine


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    fixture = json.loads((base / "simulations" / "aggressive_architecture_fixture.json").read_text())
    task = json.loads((base / "simulations" / "canonical_spine_task.json").read_text())
    legacy_path = base / "legacy" / "LEGACY_RESEARCH_LEDGER.imported.json"
    result = run_canonical_spine(
        base,
        fixture,
        task,
        legacy_ledger_path=legacy_path if legacy_path.exists() else None,
    )
    out = base / "simulations" / "canonical_spine_result.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"CANONICAL_SPINE={result['status']}")
    print(f"FINGERPRINT={result['canonical_fingerprint']}")


if __name__ == "__main__":
    main()
