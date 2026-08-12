"""Robustesse — "January effect" (proxy prix bas) en overlay. Grille CAP
(PAS un retuning), autour du CAP pré-enregistré (2.0x). Le mois
calendaire (janvier) et la fenêtre de rebalancement (21j) ne sont PAS
perturbés (au cœur de l'hypothèse testée).
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
from nonml_january_effect_lowprice_overlay_backtest import (  # noqa: E402
    load_all_prices, REBAL_EVERY, TERCILE, COST_BPS,
)

CAP_GRID = [1.5, 2.0, 2.5, 3.0]


def main():
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    close = P.values
    exists = np.isfinite(close)
    R = np.nan_to_num((P / P.shift(1) - 1.0).values, nan=0.0)
    R[0, :] = 0.0

    n_low = max(1, int(round(n_tickers * TERCILE)))
    weights_lowprice = np.zeros((T, n_tickers))
    start = REBAL_EVERY
    rebal_dates = list(range(start, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        c = close[t]
        elig = np.where(np.isfinite(c) & exists[t])[0]
        n_low_t = min(n_low, len(elig))
        if n_low_t > 0:
            low_idx = elig[np.argsort(c[elig])[:n_low_t]]
            w = np.zeros(n_tickers)
            w[low_idx] = 1.0 / n_low_t
            weights_lowprice[t:end] = w

    is_january = np.array([d.month == 1 for d in P.index])

    pnl_base = (weights_lowprice[start:] * R[start:]).sum(axis=1)
    turn_base = np.abs(np.diff(weights_lowprice[start:], axis=0, prepend=weights_lowprice[start:start+1])).sum(axis=1) / 2.0
    pnl_base = pnl_base - turn_base * (COST_BPS / 1e4)
    me_base = trading_metrics(np.log1p(pnl_base))
    ret_base = np.cumprod(1.0 + pnl_base)[-1] - 1.0

    lines = [
        "# Robustesse — \"January effect\" (proxy prix bas) en overlay (grille CAP, PAS un retuning)",
        "",
        "CAP pré-enregistré = 2.0x.",
        "",
        "| CAP | Sharpe>réf | Rendement>réf | Sharpe | Rendement total |",
        "|---|---|---|---|---|",
    ]
    for cap in CAP_GRID:
        exposure = np.where(is_january, cap, 1.0)
        weights_lev = weights_lowprice * exposure[:, None]
        pnl_lev = (weights_lev[start:] * R[start:]).sum(axis=1)
        turn_lev = np.abs(np.diff(weights_lev[start:], axis=0, prepend=weights_lev[start:start+1])).sum(axis=1) / 2.0
        pnl_lev = pnl_lev - turn_lev * (COST_BPS / 1e4)
        me_lev = trading_metrics(np.log1p(pnl_lev))
        ret_lev = np.cumprod(1.0 + pnl_lev)[-1] - 1.0
        sharpe_ok = me_lev["sharpe_ann"] > me_base["sharpe_ann"]
        ret_ok = ret_lev > ret_base
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{me_lev['sharpe_ann']:+.2f} | {100*ret_lev:+.1f}%{marker} |")

    out = ROOT / "results" / "nonml_january_effect_lowprice_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
