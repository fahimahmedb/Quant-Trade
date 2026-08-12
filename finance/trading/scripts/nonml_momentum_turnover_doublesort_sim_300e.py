"""Simulation — 300 EUR, momentum 12-1 + double-tri turnover, ~3 derniers
mois de données disponibles. Spécification pré-enregistrée
(TURNOVER_WINDOW=126j), aucun paramètre retouché après les résultats de
backtest/audit/robustesse.
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
    LOOKBACK, SKIP, TURNOVER_WINDOW, REBAL_EVERY, COST_BPS, TERCILE,
)

CAPITAL0 = 300.0
WINDOW_DAYS = 63


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
    T, n_tickers = P.shape
    close = P.values
    # Rendements SIMPLES par titre : le rendement d'un panier pondere est
    # somme(w_i * r_simple_i). Voir results/nonml_portfolio_log_aggregation_audit.md.
    R = (P / P.shift(1) - 1.0).values.copy()
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
    turnover_avg = pd.DataFrame(dollar_volume).rolling(TURNOVER_WINDOW).mean().values

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

    pnl_double_full = (weights_double * R_safe).sum(axis=1)
    pnl_mom_full = (weights_momentum_only * R_safe).sum(axis=1)
    turn_double = np.abs(np.diff(weights_double, axis=0, prepend=weights_double[:1])).sum(axis=1) / 2.0
    turn_mom = np.abs(np.diff(weights_momentum_only, axis=0, prepend=weights_momentum_only[:1])).sum(axis=1) / 2.0
    pnl_double_full = pnl_double_full - turn_double * (COST_BPS / 1e4)
    pnl_mom_full = pnl_mom_full - turn_mom * (COST_BPS / 1e4)

    pnl_double = pnl_double_full[-WINDOW_DAYS:]
    pnl_mom = pnl_mom_full[-WINDOW_DAYS:]
    dates = P.index[-WINDOW_DAYS:]

    equity_double = CAPITAL0 * np.cumprod(1.0 + pnl_double)
    equity_mom = CAPITAL0 * np.cumprod(1.0 + pnl_mom)

    def mdd(equity):
        running_max = np.maximum.accumulate(equity)
        return (equity / running_max - 1.0).min() * 100

    me_double, me_mom = trading_metrics(np.log1p(pnl_double)), trading_metrics(np.log1p(pnl_mom))

    lines = [
        "# Simulation — 300 EUR, momentum 12-1 + double-tri turnover (NDX-100, ~3 derniers mois)",
        "",
        f"Période : {dates[0].date()} → {dates[-1].date()} ({len(pnl_double)} séances). "
        "Référence = momentum 12-1 seul (cycle #73), PAS Buy&Hold — cohérent avec le critère "
        "renforcé du backtest. Spécification pré-enregistrée (TURNOVER_WINDOW=126j), aucun "
        "paramètre retouché après les résultats précédents.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Momentum 12-1 seul (référence) | {equity_mom[-1]:.2f} EUR | "
        f"{100*(equity_mom[-1]/CAPITAL0-1):+.1f}% | {mdd(equity_mom):.1f}% | {me_mom['sharpe_ann']:+.2f} |",
        f"| **Momentum 12-1 + double-tri turnover faible** | **{equity_double[-1]:.2f} EUR** | "
        f"**{100*(equity_double[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_double):.1f}% | {me_double['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre de 3 mois illustrative uniquement (~3 rebalancements "
        "mensuels observés) — le verdict statistique réel reste celui du backtest complet "
        "(2022-2026, PASS Sharpe+rendement) et de la robustesse (5/5 variantes voisines de "
        "TURNOVER_WINDOW restent OUI/OUI, plateau parfait)."
    ]

    out = ROOT / "results" / "nonml_momentum_turnover_doublesort_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
