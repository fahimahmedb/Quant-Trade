"""Simulation — 300 EUR, Winners momentum + overlay combiné tendance +
vol-targeting, ~3 derniers mois. Spécification pré-enregistrée, aucun
paramètre retouché après les résultats précédents. **Prudence forte
héritée du #14.**
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
from nonml_winners_trend_vol_targeting_overlay_backtest import (  # noqa: E402
    load_prices, index_trend_series, SIGNAL_WINDOW, REBAL_EVERY, TERCILE, COST_BPS,
    CAP, VOL_WINDOW, TARGET_VOL_ANNUAL, ANNUALIZATION,
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
    exists = np.isfinite(close)
    # Rendements SIMPLES par titre : le rendement d'un panier pondere est
    # somme(w_i * r_simple_i). Voir results/nonml_portfolio_log_aggregation_audit.md.
    R = (P / P.shift(1) - 1.0).values.copy()
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)

    signal = np.full((T, n_tickers), np.nan)
    for i in range(SIGNAL_WINDOW, T):
        with np.errstate(all="ignore", invalid="ignore"):
            signal[i] = close[i] / close[i - SIGNAL_WINDOW] - 1.0
        signal[i, ~(exists[i] & exists[i - SIGNAL_WINDOW])] = np.nan

    n_top = max(1, int(round(n_tickers * TERCILE)))
    weights_winners = np.zeros((T, n_tickers))
    start = SIGNAL_WINDOW
    rebal_dates = list(range(start, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        s = signal[t]
        elig = np.where(np.isfinite(s))[0]
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-s[elig])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_winners[t:end] = w

    trend = index_trend_series()
    trend_aligned = trend.reindex(P.index, method="ffill").fillna(False).values.astype(bool)

    pnl_raw = (weights_winners * R_safe).sum(axis=1)
    vol_ann = pd.Series(pnl_raw).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)
    exposure = np.where(trend_aligned, vt_exposure, 1.0)
    weights_lev = weights_winners * exposure[:, None]

    pnl_base_full = (weights_winners * R_safe).sum(axis=1)
    turn_base = np.abs(np.diff(weights_winners, axis=0, prepend=weights_winners[:1])).sum(axis=1) / 2.0
    pnl_base_full = pnl_base_full - turn_base * (COST_BPS / 1e4)

    pnl_lev_full = (weights_lev * R_safe).sum(axis=1)
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

    me_base, me_lev = trading_metrics(np.log1p(pnl_base)), trading_metrics(np.log1p(pnl_lev))

    lines = [
        "# Simulation — 300 EUR, Winners + overlay combiné tendance + vol-targeting (~3 derniers mois)",
        "",
        f"Période : {dates[0].date()} → {dates[-1].date()} ({len(pnl_base)} séances). "
        "Référence = Winners 1.0x (cycle #14), pas Buy&Hold classique.",
        "",
        "**Prudence forte héritée du #14.**",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Winners 1.0x (référence) | {equity_base[-1]:.2f} EUR | "
        f"{100*(equity_base[-1]/CAPITAL0-1):+.1f}% | {mdd(equity_base):.1f}% | {me_base['sharpe_ann']:+.2f} |",
        f"| **Winners + overlay tendance+vol-targeting** | **{equity_lev[-1]:.2f} EUR** | "
        f"**{100*(equity_lev[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_lev):.1f}% | {me_lev['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre courte (~3 mois) illustrative — le verdict "
        "statistique réel reste celui du backtest complet (2021-2026, PASS) et de la "
        "robustesse (plateau parfait sur les deux grilles CAP 1.5x-3.0x et fenêtre "
        "15j-30j, MDD constant -22,4% partout). Généralisabilité incertaine hors du bull "
        "market échantillonné (même mise en garde que le #14/#42)."
    ]

    out = ROOT / "results" / "nonml_winners_trend_vol_targeting_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
