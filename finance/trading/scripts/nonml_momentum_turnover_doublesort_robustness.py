"""Robustesse — Momentum 12-1 + double-tri turnover/volume-dollars.

Grille de plausibilité (PAS un retuning) autour de TURNOVER_WINDOW=126j
(seul paramètre réellement NOUVEAU introduit par ce cycle — LOOKBACK,
SKIP, REBAL_EVERY, TERCILE sont hérités tels quels de #73/#79, Règle 7,
et ne sont pas reperturbés ici). Le verdict PASS officiel reste celui de
la spécification pré-enregistrée
(`results/nonml_momentum_turnover_doublesort_result.md`).
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
from nonml_momentum_turnover_doublesort_backtest import (  # noqa: E402
    load_all_prices, load_all_volume, lag_one_day,
    LOOKBACK, SKIP, REBAL_EVERY, COST_BPS, TERCILE,
)

TURNOVER_WINDOW_GRID = [90, 108, 126, 144, 162]  # base=126j, +-~30%


def run_one(P: pd.DataFrame, V: pd.DataFrame, turnover_window: int):
    T, n_tickers = P.shape
    close = P.values
    R = np.log(P / P.shift(1)).values
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)

    momentum = np.full((T, n_tickers), np.nan)
    for i in range(LOOKBACK, T):
        c_skip = close[i - SKIP]
        c_lookback = close[i - LOOKBACK]
        with np.errstate(all="ignore"):
            m = c_skip / c_lookback - 1.0
        valid = np.isfinite(c_skip) & np.isfinite(c_lookback)
        momentum[i, valid] = m[valid]

    dollar_volume = P.values * V.values
    turnover_avg = pd.DataFrame(dollar_volume).rolling(turnover_window).mean().values

    weights_double = np.zeros((T, n_tickers))
    weights_momentum_only = np.zeros((T, n_tickers))
    n_top_mom_full = max(1, int(round(n_tickers * TERCILE)))

    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        m = momentum[t]
        tv = turnover_avg[t]
        eligible = np.where(np.isfinite(m) & np.isfinite(tv) & (tv > 0))[0]
        n_top_mom = min(n_top_mom_full, len(eligible))
        if n_top_mom > 0:
            top_mom_idx = eligible[np.argsort(-m[eligible])[:n_top_mom]]
            w = np.zeros(n_tickers)
            w[top_mom_idx] = 1.0 / n_top_mom
            weights_momentum_only[t:end] = w

            n_top_double = max(1, int(round(len(top_mom_idx) * TERCILE)))
            n_top_double = min(n_top_double, len(top_mom_idx))
            if n_top_double > 0:
                low_turnover_idx = top_mom_idx[np.argsort(tv[top_mom_idx])[:n_top_double]]
                w2 = np.zeros(n_tickers)
                w2[low_turnover_idx] = 1.0 / n_top_double
                weights_double[t:end] = w2

    weights_double = lag_one_day(weights_double)
    weights_momentum_only = lag_one_day(weights_momentum_only)

    start = LOOKBACK
    pnl_double = (weights_double[start:] * R_safe[start:]).sum(axis=1)
    pnl_mom = (weights_momentum_only[start:] * R_safe[start:]).sum(axis=1)
    turn_double = np.abs(np.diff(weights_double[start:], axis=0, prepend=weights_double[start:start+1])).sum(axis=1) / 2.0
    turn_mom = np.abs(np.diff(weights_momentum_only[start:], axis=0, prepend=weights_momentum_only[start:start+1])).sum(axis=1) / 2.0
    pnl_double = pnl_double - turn_double * (COST_BPS / 1e4)
    pnl_mom = pnl_mom - turn_mom * (COST_BPS / 1e4)

    me_double, me_mom = trading_metrics(pnl_double), trading_metrics(pnl_mom)
    ret_double = np.cumprod(1.0 + pnl_double)[-1] - 1.0
    ret_mom = np.cumprod(1.0 + pnl_mom)[-1] - 1.0
    return (me_double["sharpe_ann"] > me_mom["sharpe_ann"], ret_double > ret_mom,
            me_double["sharpe_ann"], ret_double)


def main():
    close_series = load_all_prices()
    vol_series = load_all_volume()
    tickers = sorted(set(close_series.keys()) & set(vol_series.keys()))
    ref_idx = None
    for t in tickers:
        ref_idx = close_series[t].index if ref_idx is None else ref_idx.union(close_series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: close_series[t].reindex(ref_idx) for t in tickers})
    V = pd.DataFrame({t: vol_series[t].reindex(ref_idx) for t in tickers})

    lines = [
        "# Robustesse — Momentum 12-1 + double-tri turnover/volume-dollars (grille de plausibilité, PAS un retuning)",
        "",
        "Spécification pré-enregistrée : TURNOVER_WINDOW=126j (seul paramètre nouveau de ce "
        "cycle). LOOKBACK=252j, SKIP=21j, REBAL_EVERY=21j, TERCILE=1/3 hérités de #73/#79 "
        "(Règle 7, non reperturbés). Le verdict PASS officiel reste celui de cette spécification "
        "(`results/nonml_momentum_turnover_doublesort_result.md`) — ceci est diagnostique "
        "uniquement.",
        "",
        "| TURNOVER_WINDOW | Sharpe>référence | Rendement>référence | Sharpe double-tri | Rendement total double-tri |",
        "|---|---|---|---|---|",
    ]
    for tw in TURNOVER_WINDOW_GRID:
        sharpe_ok, ret_ok, sharpe, ret = run_one(P, V, tw)
        marker = " ← pré-enregistré" if tw == 126 else ""
        lines.append(f"| {tw}j | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}%{marker} |")

    n_pass = sum(1 for tw in TURNOVER_WINDOW_GRID
                 for sharpe_ok, ret_ok, _, _ in [run_one(P, V, tw)] if sharpe_ok and ret_ok)
    lines.append("")
    lines.append(f"**{n_pass}/{len(TURNOVER_WINDOW_GRID)} variantes OUI/OUI.** "
                 "Lecture : si la majorité des variantes voisines restent OUI/OUI, l'effet est "
                 "un plateau plausible autour de 126j, pas un pic isolé.")

    out = ROOT / "results" / "nonml_momentum_turnover_doublesort_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
