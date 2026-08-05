"""Robustesse — Tilt Amihud illiquidité.

Grille de plausibilité (PAS un retuning) autour de ILLIQ_WINDOW=126j
(seul paramètre nouveau de ce cycle — REBAL_EVERY=21j hérité de #4/#73/
#78/#82, Règle 7, non reperturbé). Le verdict PASS officiel reste celui
de la spécification pré-enregistrée
(`results/nonml_amihud_illiquidity_tilt_result.md`).
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
from nonml_amihud_illiquidity_tilt_backtest import (  # noqa: E402
    load_all_prices, load_all_volume, lag_one_day, REBAL_EVERY, COST_BPS, TERCILE,
)

ILLIQ_WINDOW_GRID = [90, 108, 126, 144, 162]  # base=126j, +-~30%


def run_one(P: pd.DataFrame, V: pd.DataFrame, illiq_window: int):
    T, n_tickers = P.shape
    exists = np.isfinite(P.values)
    R = np.log(P / P.shift(1))
    R.iloc[0, :] = 0.0
    R_safe = np.nan_to_num(R.values, nan=0.0)

    dollar_volume = P.values * V.values
    with np.errstate(divide="ignore", invalid="ignore"):
        illiq_daily = np.abs(R.values) / dollar_volume
    illiq_daily[~np.isfinite(illiq_daily)] = np.nan
    illiq_avg = pd.DataFrame(illiq_daily).rolling(illiq_window).mean().values

    weights_illiq = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    n_top = max(1, int(round(n_tickers * TERCILE)))

    rebal_dates = list(range(illiq_window, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        illiq = illiq_avg[t]
        eligible = np.where(np.isfinite(illiq) & (illiq > 0))[0]
        n_top_t = min(n_top, len(eligible))
        if n_top_t > 0:
            top_idx = eligible[np.argsort(-illiq[eligible])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_illiq[t:end] = w
        listed = exists[t]
        n_listed = listed.sum()
        if n_listed > 0:
            weights_bh[t:end] = listed.astype(float) / n_listed

    weights_illiq = lag_one_day(weights_illiq)
    weights_bh = lag_one_day(weights_bh)

    start = illiq_window
    pnl_illiq = (weights_illiq[start:] * R_safe[start:]).sum(axis=1)
    pnl_bh = (weights_bh[start:] * R_safe[start:]).sum(axis=1)
    turn_illiq = np.abs(np.diff(weights_illiq[start:], axis=0, prepend=weights_illiq[start:start+1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    pnl_illiq = pnl_illiq - turn_illiq * (COST_BPS / 1e4)
    pnl_bh = pnl_bh - turn_bh * (COST_BPS / 1e4)

    me_illiq, me_bh = trading_metrics(pnl_illiq), trading_metrics(pnl_bh)
    ret_illiq = np.cumprod(1.0 + pnl_illiq)[-1] - 1.0
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    return (me_illiq["sharpe_ann"] > me_bh["sharpe_ann"], ret_illiq > ret_bh,
            me_illiq["sharpe_ann"], ret_illiq)


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
        "# Robustesse — Tilt Amihud illiquidité (grille de plausibilité, PAS un retuning)",
        "",
        "Spécification pré-enregistrée : ILLIQ_WINDOW=126j (seul paramètre nouveau de ce "
        "cycle). REBAL_EVERY=21j hérité de #4/#73/#78/#82 (Règle 7, non reperturbé). Le "
        "verdict PASS officiel reste celui de cette spécification "
        "(`results/nonml_amihud_illiquidity_tilt_result.md`) — ceci est diagnostique "
        "uniquement.",
        "",
        "| ILLIQ_WINDOW | Sharpe>BH | Rendement>BH | Sharpe tilt | Rendement total tilt |",
        "|---|---|---|---|---|",
    ]
    results = []
    for iw in ILLIQ_WINDOW_GRID:
        sharpe_ok, ret_ok, sharpe, ret = run_one(P, V, iw)
        results.append((sharpe_ok, ret_ok))
        marker = " ← pré-enregistré" if iw == 126 else ""
        lines.append(f"| {iw}j | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}%{marker} |")

    n_pass = sum(1 for s, r in results if s and r)
    lines.append("")
    lines.append(f"**{n_pass}/{len(ILLIQ_WINDOW_GRID)} variantes OUI/OUI.** "
                 "Lecture : si la majorité des variantes voisines restent OUI/OUI, l'effet est "
                 "un plateau plausible autour de 126j, pas un pic isolé.")

    out = ROOT / "results" / "nonml_amihud_illiquidity_tilt_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
