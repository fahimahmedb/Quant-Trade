"""Operator entry point for Data Plane ingestion."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.ingest import ingest_all  # noqa: E402
from quant.dataplane.registry import DatasetRegistry  # noqa: E402
from quant.events import EventLog  # noqa: E402
from quant.paths import QuantPaths  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--range", default="10y")
    parser.add_argument("--no-network", action="store_true")
    args = parser.parse_args()
    paths = QuantPaths(args.root).ensure()
    registry = DatasetRegistry(paths.dataset_registry, paths.root)
    log = EventLog(paths.events)
    outcome = ingest_all(paths, registry, log, range_=args.range, network=not args.no_network)
    outcome["registry"] = {key: record.to_dict() for key, record in registry.records.items()}
    print(json.dumps(outcome, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
