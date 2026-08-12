"""Backtest — Momentum de constance (#82), univers POINT-IN-TIME réel du
NDX-100 (spécification pré-enregistrée dans
PREREG_momentum_consistency_pit_universe.md, committée avant ce
script). Réutilise STRICTEMENT (Règle 7) `consistency_at` du #82
(`nonml_momentum_consistency_backtest.py`, N_BLOCKS/BLOCK_LEN/
REBAL_EVERY/TERCILE/COST_BPS inchangés) -- seul le filtre d'univers
change, à chaque date de rebalancement, aux titres RÉELLEMENT membres du
NDX-100 ce jour-là (`ndx100_membership.tickers_as_of_date`). Ancrage
2015-01-01 comme aux cycles #163/#264/#265. Complète le trio des
constructions de momentum "prix pur" testées sous PIT (#4/#38 survit,
#73 survit au #265).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402
from nonml_momentum_consistency_backtest import consistency_at, lag_one_day, LOOKBACK, REBAL_EVERY, COST_BPS, TERCILE  # noqa: E402

PRICES_PIT_DIR = ROOT / "data" / "pead" / "prices_pit"
REBAL_ANCHOR = "2015-01-01"


def load_prices():
    import json
    series = {}
    for path in sorted(PRICES_PIT_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > LOOKBACK + REBAL_EVERY:
            series[path.stem] = close
    return series


def main():
    series = load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    close = P.values
    # Rendements SIMPLES par titre : le rendement d'un panier pondere est
    # somme(w_i * r_simple_i). Voir results/nonml_portfolio_log_aggregation_audit.md.
    R = (P / P.shift(1) - 1.0).values.copy()
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)

    weights_cons = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))

    first_rebal = max(LOOKBACK, int(P.index.searchsorted(pd.Timestamp(REBAL_ANCHOR))))
    rebal_dates = list(range(first_rebal, T, REBAL_EVERY))
    membership_log = []
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        cons = consistency_at(close, t)
        elig_all = np.where(np.isfinite(cons))[0]
        members = tickers_as_of_date(P.index[t])
        eligible = np.array([j for j in elig_all if tickers[j] in members], dtype=int)
        membership_log.append((P.index[t], len(members), len(eligible)))

        n_top = max(1, int(round(len(eligible) * TERCILE)))
        n_top = min(n_top, len(eligible))
        if n_top > 0:
            top_idx = eligible[np.argsort(-cons[eligible])[:n_top]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top
            weights_cons[t:end] = w
        if len(eligible) > 0:
            weights_bh[t:end, eligible] = 1.0 / len(eligible)

    weights_cons = lag_one_day(weights_cons)
    weights_bh = lag_one_day(weights_bh)

    start = first_rebal
    pnl_cons = (weights_cons[start:] * R_safe[start:]).sum(axis=1)
    pnl_bh = (weights_bh[start:] * R_safe[start:]).sum(axis=1)
    turn_cons = np.abs(np.diff(weights_cons[start:], axis=0, prepend=weights_cons[start:start+1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    pnl_cons = pnl_cons - turn_cons * (COST_BPS / 1e4)
    pnl_bh = pnl_bh - turn_bh * (COST_BPS / 1e4)

    me_cons, me_bh = trading_metrics(np.log1p(pnl_cons)), trading_metrics(np.log1p(pnl_bh))
    ret_cons = np.cumprod(1.0 + pnl_cons)[-1] - 1.0
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    sharpe_ok = me_cons["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_cons > ret_bh
    verdict = sharpe_ok and ret_ok

    avg_coverage = np.mean([n_e / max(1, n_m) for _, n_m, n_e in membership_log])

    lines = [
        "# Résultat — Momentum de constance (#82), univers POINT-IN-TIME réel (cycle #266)",
        "",
        f"Univers PIT : {n_tickers} tickers avec prix PIT disponibles. Couverture moyenne de "
        f"l'univers investissable (éligibles/membres réels) : {100*avg_coverage:.1f}%. "
        f"{T - start} séances testables ({P.index[start].date()} → {P.index[-1].date()}). "
        "Référence = Buy&Hold équipondéré (univers PIT réel à chaque date). Construction "
        "causale (`lag_one_day`).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers PIT) | {me_bh['sharpe_ann']:+.2f} | "
        f"{100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Momentum de constance (univers PIT)** | **{me_cons['sharpe_ann']:+.2f}** | "
        f"**{100*ret_cons:+.1f}%** | {me_cons['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe > Buy&Hold : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement total > Buy&Hold : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_momentum_consistency_pit_universe_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
