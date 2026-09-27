"""H-006 run: build compact committed dataset from raw, then evaluate discovery + validation.

python3 research/fast_rail/h006/run.py dataset   # raw -> data/fast_rail/h006/dataset.jsonl.gz
python3 research/fast_rail/h006/run.py evaluate  # dataset -> results.json (untouched 15% NOT scored)
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from research.fast_rail.h006 import analysis, build  # noqa: E402

DATASET = ROOT / "data" / "fast_rail" / "h006" / "dataset.jsonl.gz"
RESULTS = Path(__file__).resolve().parent / "results.json"


def make_dataset() -> None:
    lines = []
    for m in build.match(build.load_fd(), build.load_events()):
        if not build.usable(m):
            continue
        c, k = m["collection"].timestamp(), m["kickoff"].timestamp()
        prices = {}
        for o, token in m["tokens"].items():
            raw = gzip.decompress((build.RAW / f"px_{m['slug']}_{o}.json.gz").read_bytes())
            prices[o] = [p for p in json.loads(raw).get("history", []) if c - 6 * 3600 <= p["t"] <= k]
        lines.append({"slug": m["slug"], "league": m["league"], "season": m["season"],
                      "home": m["home"], "away": m["away"], "kickoff_ts": k, "collection_ts": c,
                      "PS": m["PS"], "PSC": m["PSC"], "FTR": m["FTR"], "fee_rate": m["fee_rate"],
                      "volume": m["volume"], "tokens": m["tokens"], "prices": prices})
    blob = gzip.compress("".join(json.dumps(x, sort_keys=True) + "\n" for x in lines).encode(), 9)
    DATASET.write_bytes(blob)
    print(len(lines), "matches", len(blob), "bytes", hashlib.sha256(blob).hexdigest())


def load() -> list[dict]:
    return [json.loads(x) for x in gzip.decompress(DATASET.read_bytes()).decode().splitlines()]


def evaluate() -> None:
    matches = [m for m in load() if all(m["prices"].get(o) for o in analysis.OUTCOMES)]
    disc, val, untouched = analysis.split(matches)
    out = {"expression": {"devig": "power", "edge_threshold": analysis.EDGE, "half_spread": analysis.HALF_SPREAD},
           "dataset_sha256": hashlib.sha256(DATASET.read_bytes()).hexdigest(),
           "matches_with_prices": len(matches),
           "split": {name: {"n": len(part), "from": part[0]["slug"], "to": part[-1]["slug"]}
                     for name, part in (("discovery", disc), ("validation", val), ("untouched", untouched))},
           "discovery": analysis.evaluate(disc), "validation": analysis.evaluate(val),
           "validation_2x_costs": analysis.evaluate(val, 2.0)}
    RESULTS.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("split", "validation", "validation_2x_costs")}, indent=1))


if __name__ == "__main__":
    {"dataset": make_dataset, "evaluate": evaluate}[sys.argv[1]]()
