"""Simulation — 300 EUR, momentum de constance univers point-in-time,
~3 derniers mois de données disponibles. Spécification pré-enregistrée,
aucun paramètre retouché après les résultats de backtest/audit/robustesse.
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
from nonml_momentum_consistency_pit_universe_backtest import load_prices, REBAL_ANCHOR  # noqa: E402

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

    weights_cons = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    first_rebal = max(LOOKBACK, int(P.index.searchsorted(pd.Timestamp(REBAL_ANCHOR))))
    rebal_dates = list(range(first_rebal, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        cons = consistency_at(close, t)
        elig_all = np.where(np.isfinite(cons))[0]
        members = tickers_as_of_date(P.index[t])
        eligible = np.array([j for j in elig_all if tickers[j] in members], dtype=int)
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

    pnl_cons_full = (weights_cons * R_safe).sum(axis=1)
    pnl_bh_full = (weights_bh * R_safe).sum(axis=1)
    turn_cons = np.abs(np.diff(weights_cons, axis=0, prepend=weights_cons[:1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh, axis=0, prepend=weights_bh[:1])).sum(axis=1) / 2.0
    pnl_cons_full = pnl_cons_full - turn_cons * (COST_BPS / 1e4)
    pnl_bh_full = pnl_bh_full - turn_bh * (COST_BPS / 1e4)

    pnl_cons = pnl_cons_full[-WINDOW_DAYS:]
    pnl_bh = pnl_bh_full[-WINDOW_DAYS:]
    dates = P.index[-WINDOW_DAYS:]

    equity_cons = CAPITAL0 * np.cumprod(1.0 + pnl_cons)
    equity_bh = CAPITAL0 * np.cumprod(1.0 + pnl_bh)

    def mdd(equity):
        running_max = np.maximum.accumulate(equity)
        return (equity / running_max - 1.0).min() * 100

    me_cons, me_bh = trading_metrics(pnl_cons), trading_metrics(pnl_bh)

    lines = [
        "# Simulation — 300 EUR, momentum de constance univers point-in-time (~3 derniers mois)",
        "",
        f"Période : {dates[0].date()} → {dates[-1].date()} ({len(pnl_cons)} séances). "
        "Référence = Buy&Hold équipondéré (univers PIT). Spécification pré-enregistrée, "
        "aucun paramètre retouché après les résultats précédents.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers PIT) | {equity_bh[-1]:.2f} EUR | "
        f"{100*(equity_bh[-1]/CAPITAL0-1):+.1f}% | {mdd(equity_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Momentum de constance (univers PIT)** | **{equity_cons[-1]:.2f} EUR** | "
        f"**{100*(equity_cons[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_cons):.1f}% | {me_cons['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre de 3 mois illustrative uniquement (~3 rebalancements "
        "mensuels observés) — le verdict statistique réel reste celui du backtest complet "
        "(2015-2026, PASS Sharpe+rendement) et de la robustesse (5/5 variantes voisines OUI/OUI, "
        "plateau parfait)."
    ]

    out = ROOT / "results" / "nonml_momentum_consistency_pit_universe_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
