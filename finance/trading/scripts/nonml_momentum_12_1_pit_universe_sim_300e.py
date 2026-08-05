"""Simulation — 300 EUR, momentum 12-1 univers point-in-time, ~3 derniers
mois de données disponibles. Spécification pré-enregistrée, aucun
paramètre retouché après les résultats de backtest/audit/robustesse.
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
from nonml_momentum_12_1_pit_universe_backtest import (  # noqa: E402
    load_prices, lag_one_day, LOOKBACK, SKIP, REBAL_EVERY, COST_BPS, TERCILE, REBAL_ANCHOR,
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

    weights_mom = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    first_rebal = max(LOOKBACK, int(P.index.searchsorted(pd.Timestamp(REBAL_ANCHOR))))
    rebal_dates = list(range(first_rebal, T, REBAL_EVERY))
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

    pnl_mom_full = (weights_mom * R_safe).sum(axis=1)
    pnl_bh_full = (weights_bh * R_safe).sum(axis=1)
    turn_mom = np.abs(np.diff(weights_mom, axis=0, prepend=weights_mom[:1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh, axis=0, prepend=weights_bh[:1])).sum(axis=1) / 2.0
    pnl_mom_full = pnl_mom_full - turn_mom * (COST_BPS / 1e4)
    pnl_bh_full = pnl_bh_full - turn_bh * (COST_BPS / 1e4)

    pnl_mom = pnl_mom_full[-WINDOW_DAYS:]
    pnl_bh = pnl_bh_full[-WINDOW_DAYS:]
    dates = P.index[-WINDOW_DAYS:]

    equity_mom = CAPITAL0 * np.cumprod(1.0 + pnl_mom)
    equity_bh = CAPITAL0 * np.cumprod(1.0 + pnl_bh)

    def mdd(equity):
        running_max = np.maximum.accumulate(equity)
        return (equity / running_max - 1.0).min() * 100

    me_mom, me_bh = trading_metrics(pnl_mom), trading_metrics(pnl_bh)

    lines = [
        "# Simulation — 300 EUR, momentum 12-1 univers point-in-time (~3 derniers mois)",
        "",
        f"Période : {dates[0].date()} → {dates[-1].date()} ({len(pnl_mom)} séances). "
        "Référence = Buy&Hold équipondéré (univers PIT). Spécification pré-enregistrée, "
        "aucun paramètre retouché après les résultats précédents.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers PIT) | {equity_bh[-1]:.2f} EUR | "
        f"{100*(equity_bh[-1]/CAPITAL0-1):+.1f}% | {mdd(equity_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Momentum 12-1 (univers PIT)** | **{equity_mom[-1]:.2f} EUR** | "
        f"**{100*(equity_mom[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_mom):.1f}% | {me_mom['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre de 3 mois illustrative uniquement (~3 rebalancements "
        "mensuels observés) — le verdict statistique réel reste celui du backtest complet "
        "(2015-2026, PASS Sharpe+rendement) et de la robustesse (4/5 variantes voisines OUI/OUI, "
        "seul REBAL_EVERY=27j échoue de justesse sur le Sharpe)."
    ]

    out = ROOT / "results" / "nonml_momentum_12_1_pit_universe_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
