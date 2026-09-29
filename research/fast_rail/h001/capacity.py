"""H-001 capacity measurement (Blue prerequisite to order 12). NO verdict, no parameter change.

Over the stored streams: matched events per venue, qualified opportunities (net edge
>= 0.02 after the declared fees vs the latest Pinnacle snapshot at or before the quote),
depth at the ask, and the monthly economic ceiling = sum(edge x depth) scaled to 30 days
(one opportunity per (event, outcome, venue): its best edge x depth).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from quant.dataplane.h001_relay import parse_time  # noqa: E402
from quant.factory.sportsfair import devig_power  # noqa: E402
from clv import load  # noqa: E402
from forward import MIN_NET_EDGE, fee_per_contract  # noqa: E402


def measure(out: Path, since: str | None = None) -> dict:
    pinnacle, quotes = load(out)
    if since:
        quotes = [q for q in quotes if q["observed_at"] >= since]
    snaps: dict[str, list] = {}
    for row in pinnacle:
        snaps.setdefault(row["event_id"], []).append(row)
    matched: dict[str, set] = {}
    best: dict[tuple, dict] = {}
    for q in quotes:
        matched.setdefault(q["venue"], set()).add(q["odds_event_id"])
        ask = q.get("best_ask")
        prior = [p for p in snaps.get(q["odds_event_id"], []) if p["observed_at"] <= q["observed_at"]]
        if ask is None or not 0 < ask < 1 or not prior:
            continue
        p = max(prior, key=lambda r: r["observed_at"])
        if parse_time(q["observed_at"]) >= parse_time(p["commence_time"]):
            continue
        fair = devig_power(p["prices"]).get(q["outcome"])
        if fair is None:
            continue
        edge = fair - ask - fee_per_contract(q["venue"], ask)
        if edge < MIN_NET_EDGE:
            continue
        depth = sum(s for pr, s in (q.get("asks") or []) if pr <= ask + 1e-9)
        age_h = (parse_time(q["observed_at"]) - parse_time(p["observed_at"])).total_seconds() / 3600
        slot = (q["odds_event_id"], q["outcome"], q["venue"])
        value = edge * depth
        if slot not in best or value > best[slot]["value_usd"]:
            best[slot] = {"edge": edge, "depth": depth, "value_usd": value, "pinnacle_age_h": age_h}
    stamps = sorted(q["observed_at"] for q in quotes)
    days = ((parse_time(stamps[-1]) - parse_time(stamps[0])).total_seconds() / 86400) if len(stamps) > 1 else 0
    total = sum(b["value_usd"] for b in best.values())
    return {"window": [stamps[0], stamps[-1]] if stamps else None, "days": round(days, 2),
            "quote_rows": len(quotes), "matched_events": {v: len(e) for v, e in matched.items()},
            "qualified_opportunities": len(best),
            "qualified_with_depth": sum(1 for b in best.values() if b["depth"] > 0),
            "median_depth": sorted(b["depth"] for b in best.values())[len(best) // 2] if best else None,
            "ceiling_usd_window": round(total, 2),
            "ceiling_usd_per_month": round(total * 30 / days, 2) if days else None}


if __name__ == "__main__":
    print(json.dumps(measure(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else None), indent=1))
