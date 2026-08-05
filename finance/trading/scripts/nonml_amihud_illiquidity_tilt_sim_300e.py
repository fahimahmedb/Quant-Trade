"""Simulation — 300 EUR, tilt Amihud illiquidité, ~3 derniers mois de
données disponibles. Spécification pré-enregistrée (ILLIQ_WINDOW=126j),
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
from nonml_amihud_illiquidity_tilt_backtest import (  # noqa: E402
    load_all_prices, load_all_volume, lag_one_day, ILLIQ_WINDOW, REBAL_EVERY, COST_BPS, TERCILE,
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
    exists = np.isfinite(P.values)
    R = np.log(P / P.shift(1))
    R.iloc[0, :] = 0.0
    R_safe = np.nan_to_num(R.values, nan=0.0)

    dollar_volume = P.values * V.values
    with np.errstate(divide="ignore", invalid="ignore"):
        illiq_daily = np.abs(R.values) / dollar_volume
    illiq_daily[~np.isfinite(illiq_daily)] = np.nan
    illiq_avg = pd.DataFrame(illiq_daily).rolling(ILLIQ_WINDOW).mean().values

    weights_illiq = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    n_top = max(1, int(round(n_tickers * TERCILE)))

    rebal_dates = list(range(ILLIQ_WINDOW, T, REBAL_EVERY))
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

    pnl_illiq_full = (weights_illiq * R_safe).sum(axis=1)
    pnl_bh_full = (weights_bh * R_safe).sum(axis=1)
    turn_illiq = np.abs(np.diff(weights_illiq, axis=0, prepend=weights_illiq[:1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh, axis=0, prepend=weights_bh[:1])).sum(axis=1) / 2.0
    pnl_illiq_full = pnl_illiq_full - turn_illiq * (COST_BPS / 1e4)
    pnl_bh_full = pnl_bh_full - turn_bh * (COST_BPS / 1e4)

    pnl_illiq = pnl_illiq_full[-WINDOW_DAYS:]
    pnl_bh = pnl_bh_full[-WINDOW_DAYS:]
    dates = P.index[-WINDOW_DAYS:]

    equity_illiq = CAPITAL0 * np.cumprod(1.0 + pnl_illiq)
    equity_bh = CAPITAL0 * np.cumprod(1.0 + pnl_bh)

    def mdd(equity):
        running_max = np.maximum.accumulate(equity)
        return (equity / running_max - 1.0).min() * 100

    me_illiq, me_bh = trading_metrics(pnl_illiq), trading_metrics(pnl_bh)

    lines = [
        "# Simulation — 300 EUR, tilt Amihud illiquidité (NDX-100, ~3 derniers mois)",
        "",
        f"Période : {dates[0].date()} → {dates[-1].date()} ({len(pnl_illiq)} séances). "
        "Référence = Buy&Hold équipondéré (univers). Spécification pré-enregistrée "
        "(ILLIQ_WINDOW=126j), aucun paramètre retouché après les résultats précédents.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers) | {equity_bh[-1]:.2f} EUR | "
        f"{100*(equity_bh[-1]/CAPITAL0-1):+.1f}% | {mdd(equity_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Tilt Amihud illiquidité** | **{equity_illiq[-1]:.2f} EUR** | "
        f"**{100*(equity_illiq[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_illiq):.1f}% | {me_illiq['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre de 3 mois illustrative uniquement (~3 rebalancements "
        "mensuels observés) — le verdict statistique réel reste celui du backtest complet "
        "(2021-2026, PASS Sharpe+rendement) et de la robustesse (5/5 variantes voisines de "
        "ILLIQ_WINDOW restent OUI/OUI, plateau parfait)."
    ]

    out = ROOT / "results" / "nonml_amihud_illiquidity_tilt_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
