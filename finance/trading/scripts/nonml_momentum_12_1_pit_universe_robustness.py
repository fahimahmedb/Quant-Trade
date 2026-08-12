"""Robustesse — Momentum 12-1, univers point-in-time (cycle #265).

Grille de plausibilité (PAS un retuning) : réutilise STRICTEMENT (Règle
7) la grille déjà publiée au #73 original (LOOKBACK {200,252,300}j,
REBAL_EVERY {15,21,27}j, SKIP=21j fixe) -- aucun nouveau paramètre
introduit par ce cycle (l'ancrage REBAL_ANCHOR=2015-01-01 est dicté par
la disponibilité des données, pas un choix arbitraire à grillé). Le
verdict PASS officiel reste celui de la spécification pré-enregistrée
(`results/nonml_momentum_12_1_pit_universe_result.md`).
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
from nonml_momentum_12_1_pit_universe_backtest import load_prices, lag_one_day, SKIP, TERCILE, REBAL_ANCHOR  # noqa: E402

LOOKBACK_GRID = [200, 252, 300]
REBAL_GRID = [15, 21, 27]


def run_one(P: pd.DataFrame, lookback: int, rebal_every: int):
    T, n_tickers = P.shape
    close = P.values
    tickers = list(P.columns)
    # Rendements SIMPLES : le rendement d'un panier pondere est somme(w_i*r_simple_i).
    # Voir results/nonml_portfolio_log_aggregation_audit.md.
    R = (P / P.shift(1) - 1.0).values.copy()
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)

    momentum = np.full((T, n_tickers), np.nan)
    for i in range(lookback, T):
        c_skip = close[i - SKIP]
        c_lookback = close[i - lookback]
        with np.errstate(all="ignore"):
            m = c_skip / c_lookback - 1.0
        valid = np.isfinite(c_skip) & np.isfinite(c_lookback)
        momentum[i, valid] = m[valid]

    weights_mom = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    first_rebal = max(lookback, int(P.index.searchsorted(pd.Timestamp(REBAL_ANCHOR))))
    rebal_dates = list(range(first_rebal, T, rebal_every))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        m = momentum[t]
        elig_all = np.where(np.isfinite(m))[0]
        members = tickers_as_of_date(P.index[t])
        eligible = np.array([j for j in elig_all if tickers[j] in members], dtype=int)
        n_top = max(1, int(round(len(eligible) * TERCILE)))
        n_top = min(n_top, len(eligible))
        if n_top > 0:
            top_idx = eligible[np.argsort(-m[eligible])[:n_top]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top
            weights_mom[t:end] = w
        if len(eligible) > 0:
            weights_bh[t:end, eligible] = 1.0 / len(eligible)

    weights_mom = lag_one_day(weights_mom)
    weights_bh = lag_one_day(weights_bh)
    start = first_rebal
    pnl_mom = (weights_mom[start:] * R_safe[start:]).sum(axis=1)
    pnl_bh = (weights_bh[start:] * R_safe[start:]).sum(axis=1)
    turn_mom = np.abs(np.diff(weights_mom[start:], axis=0, prepend=weights_mom[start:start+1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    pnl_mom = pnl_mom - turn_mom * (5.0 / 1e4)
    pnl_bh = pnl_bh - turn_bh * (5.0 / 1e4)
    me_mom, me_bh = trading_metrics(np.log1p(pnl_mom)), trading_metrics(np.log1p(pnl_bh))
    ret_mom = np.cumprod(1.0 + pnl_mom)[-1] - 1.0
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    return me_mom["sharpe_ann"] > me_bh["sharpe_ann"], ret_mom > ret_bh, me_mom["sharpe_ann"], ret_mom


def main():
    series = load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})

    lines = [
        "# Robustesse — Momentum 12-1, univers point-in-time (grille de plausibilité, PAS un retuning)",
        "",
        "Grille réutilisée telle quelle du #73 original : LOOKBACK {200,252,300}j, "
        "REBAL_EVERY {15,21,27}j, SKIP=21j fixe. Le verdict PASS officiel reste celui de la "
        "spécification pré-enregistrée (`results/nonml_momentum_12_1_pit_universe_result.md`).",
        "",
        "| LOOKBACK | REBAL_EVERY | Sharpe>BH | Rendement>BH | Sharpe momentum | Rendement total |",
        "|---|---|---|---|---|---|",
    ]
    results = []
    for lb in LOOKBACK_GRID:
        sharpe_ok, ret_ok, sharpe, ret = run_one(P, lb, 21)
        results.append((sharpe_ok, ret_ok))
        marker = " ← pré-enregistré" if lb == 252 else ""
        lines.append(f"| {lb} | 21 | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}%{marker} |")
    for rb in REBAL_GRID:
        if rb == 21:
            continue
        sharpe_ok, ret_ok, sharpe, ret = run_one(P, 252, rb)
        results.append((sharpe_ok, ret_ok))
        lines.append(f"| 252 | {rb} | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}% |")

    n_pass = sum(1 for s, r in results if s and r)
    lines.append("")
    lines.append(f"**{n_pass}/{len(results)} variantes OUI/OUI.** Lecture : si la majorité des "
                 "variantes voisines restent OUI/OUI, l'effet est un plateau plausible, pas un pic isolé.")

    out = ROOT / "results" / "nonml_momentum_12_1_pit_universe_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
