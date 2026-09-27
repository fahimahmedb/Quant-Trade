"""H-006 single expression: devig=power, edge_threshold=0.02. Pure functions, tested offline.

Signal uses ONLY football-data pre-match Pinnacle odds (PSH/PSD/PSA). Closing odds (PSC*) are used
ONLY to score CLV after the decision. Entry = first Polymarket hourly price at/after the
football-data collection time and strictly before kickoff.

Cost model (assumption, stated): buy = price + half_spread (0.01) + taker fee per share,
fee = rate * p * (1 - p) where rate is the market's feeSchedule.rate when feesEnabled
(sports_fees_v2 rate 0.03, exponent 1; 0 for fee-free markets). Costs x2 doubles both terms.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from quant.factory.sportsfair import devig_power  # noqa: E402

OUTCOMES = ("H", "D", "A")
EDGE = 0.02
HALF_SPREAD = 0.01


def fair(odds: list) -> dict[str, float]:
    return devig_power({o: float(x) for o, x in zip(OUTCOMES, odds)})


def entry_price(history: list[dict], collection_ts: float, kickoff_ts: float) -> dict | None:
    """First hourly point with collection_ts <= t < kickoff_ts."""
    for point in sorted(history, key=lambda p: p["t"]):
        if collection_ts <= point["t"] < kickoff_ts:
            return point
    return None


def buy_price(price: float, fee_rate: float, cost_mult: float = 1.0) -> float:
    return price + cost_mult * (HALF_SPREAD + fee_rate * price * (1.0 - price))


def decide(match: dict, cost_mult: float = 1.0) -> list[dict]:
    """Bets for one match. Reads PS (pre-match) only; never PSC."""
    pre = fair(match["PS"])
    bets = []
    for o in OUTCOMES:
        point = entry_price(match["prices"].get(o, []), match["collection_ts"], match["kickoff_ts"])
        if point is None or not 0.0 < point["p"] < 1.0:
            continue
        buy = buy_price(point["p"], match["fee_rate"], cost_mult)
        if buy < 1.0 and pre[o] - buy >= EDGE:
            bets.append({"outcome": o, "t": point["t"], "mid": point["p"], "buy": buy, "edge": pre[o] - buy})
    return bets


def score(match: dict, bets: list[dict]) -> dict | None:
    """Per-match unit stake split equally over its bets. CLV vs Pinnacle closing no-vig."""
    if not bets:
        return None
    close = fair(match["PSC"])
    clv = [close[b["outcome"]] - b["buy"] for b in bets]
    pnl = [(1.0 / b["buy"] if match["FTR"] == b["outcome"] else 0.0) - 1.0 for b in bets]
    return {"clv": sum(clv) / len(clv), "pnl": sum(pnl) / len(pnl), "bets": len(bets),
            "bet_clv": clv, "bet_pnl": pnl, "losing": sum(1 for x in pnl if x < 0)}


def split(matches: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    """Chronological 55/30/15 by kickoff over ALL matched matches (before any signal)."""
    ordered = sorted(matches, key=lambda m: (m["kickoff_ts"], m["slug"]))
    n = len(ordered)
    a, b = int(round(0.55 * n)), int(round(0.85 * n))
    return ordered[:a], ordered[a:b], ordered[b:]


def tstat(xs: list[float]) -> tuple[float, float]:
    n = len(xs)
    if n < 2:
        return (xs[0] if xs else 0.0), 0.0
    mean = sum(xs) / n
    var = sum((x - mean) ** 2 for x in xs) / (n - 1)
    return mean, (mean / math.sqrt(var / n) if var > 0 else 0.0)


def evaluate(matches: list[dict], cost_mult: float = 1.0) -> dict:
    scored = [(m, s) for m in matches if (s := score(m, decide(m, cost_mult)))]
    clv_mean, clv_t = tstat([s["clv"] for _, s in scored])
    pnl_mean, pnl_t = tstat([s["pnl"] for _, s in scored])
    bet_clv = [x for _, s in scored for x in s["bet_clv"]]
    league: dict[str, float] = {}
    for m, s in scored:
        league[m["league"]] = league.get(m["league"], 0.0) + s["clv"]
    total = sum(league.values())
    half = len(scored) // 2
    halves = [tstat([s["clv"] for _, s in part])[0] for part in (scored[:half], scored[half:])]
    return {"matches": len(matches), "bet_matches": len(scored), "bets": len(bet_clv),
            "clv_mean_match": clv_mean, "clv_t_clustered": clv_t,
            "clv_mean_bet": sum(bet_clv) / len(bet_clv) if bet_clv else 0.0,
            "pnl_mean_match": pnl_mean, "pnl_t": pnl_t,
            "losing_bets": sum(s["losing"] for _, s in scored),
            "clv_halves": halves,
            "league_clv_share": {k: (v / total if total else 0.0) for k, v in sorted(league.items())},
            "median_bet_volume": _median([m["volume"][b["outcome"]] for m, _ in scored
                                          for b in decide(m, cost_mult)])}


def _median(xs: list[float]) -> float:
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else 0.0
