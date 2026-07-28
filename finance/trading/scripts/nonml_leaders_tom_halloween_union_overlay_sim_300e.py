"""Simulation — 300 EUR, Leaders 52-semaines + overlay union ToM∪Halloween
levé, ~3 derniers mois. Spécification pré-enregistrée (CAP=2.0x), aucun
paramètre retouché après les résultats précédents.
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
from nonml_leaders_tom_halloween_union_overlay_backtest import (  # noqa: E402
    load_prices, tom_mask, halloween_mask, LOOKBACK, REBAL_EVERY, TERCILE, COST_BPS, CAP,
)

CAPITAL0 = 300.0
WINDOW_DAYS = 63


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
    R = np.nan_to_num(np.log(P / P.shift(1)).values, nan=0.0)
    R[0, :] = 0.0

    rolling_max = np.full((T, n_tickers), np.nan)
    has_full = np.zeros((T, n_tickers), dtype=bool)
    for i in range(LOOKBACK, T):
        window = close[i - LOOKBACK + 1:i + 1]
        has_full[i] = np.isfinite(window).all(axis=0)
        with np.errstate(all="ignore"):
            rolling_max[i] = np.nanmax(window, axis=0)
    ratio = np.where(has_full, close / rolling_max, np.nan)

    n_top = max(1, int(round(n_tickers * TERCILE)))
    weights_leaders = np.zeros((T, n_tickers))
    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        r = ratio[t]
        elig = np.where(np.isfinite(r))[0]
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-r[elig])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_leaders[t:end] = w

    union = tom_mask(P.index.to_series()) | halloween_mask(P.index.to_series())
    exposure = np.where(union, CAP, 1.0)
    weights_lev = weights_leaders * exposure[:, None]

    pnl_base_full = (weights_leaders * R).sum(axis=1)
    turn_base = np.abs(np.diff(weights_leaders, axis=0, prepend=weights_leaders[:1])).sum(axis=1) / 2.0
    pnl_base_full = pnl_base_full - turn_base * (COST_BPS / 1e4)

    pnl_lev_full = (weights_lev * R).sum(axis=1)
    turn_lev = np.abs(np.diff(weights_lev, axis=0, prepend=weights_lev[:1])).sum(axis=1) / 2.0
    pnl_lev_full = pnl_lev_full - turn_lev * (COST_BPS / 1e4)

    pnl_base = pnl_base_full[-WINDOW_DAYS:]
    pnl_lev = pnl_lev_full[-WINDOW_DAYS:]
    dates = P.index[-WINDOW_DAYS:]

    equity_base = CAPITAL0 * np.cumprod(1.0 + pnl_base)
    equity_lev = CAPITAL0 * np.cumprod(1.0 + pnl_lev)

    def mdd(equity):
        running_max = np.maximum.accumulate(equity)
        return (equity / running_max - 1.0).min() * 100

    me_base, me_lev = trading_metrics(pnl_base), trading_metrics(pnl_lev)

    lines = [
        "# Simulation — 300 EUR, Leaders 52-semaines + overlay union ToM∪Halloween levé (~3 derniers mois)",
        "",
        f"Période : {dates[0].date()} → {dates[-1].date()} ({len(pnl_base)} séances). "
        "Référence = leaders 1.0x (cycle #4), pas Buy&Hold classique.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Leaders 1.0x (référence) | {equity_base[-1]:.2f} EUR | "
        f"{100*(equity_base[-1]/CAPITAL0-1):+.1f}% | {mdd(equity_base):.1f}% | {me_base['sharpe_ann']:+.2f} |",
        f"| **Leaders + overlay union ToM∪Halloween x{CAP}** | **{equity_lev[-1]:.2f} EUR** | "
        f"**{100*(equity_lev[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_lev):.1f}% | {me_lev['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre courte (~3 mois) illustrative — le verdict "
        "statistique réel reste celui du backtest complet (2022-2026, PASS) et de la "
        "robustesse (plateau stable et croissant sur CAP 1.5x-3.0x)."
    ]

    out = ROOT / "results" / "nonml_leaders_tom_halloween_union_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
