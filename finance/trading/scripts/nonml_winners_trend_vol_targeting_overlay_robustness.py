"""Robustesse — Winners + overlay combiné tendance + vol-targeting.
Grille CAP ET grille de fenêtre de vol (PAS un retuning de la cible de
vol ni du seuil de tendance), autour des valeurs pré-enregistrées
(CAP=2.0x, fenêtre vol=20j).
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
    TARGET_VOL_ANNUAL, ANNUALIZATION,
)

CAP_GRID = [1.5, 2.0, 2.5, 3.0]
WINDOW_GRID = [15, 20, 25, 30]


def build_base():
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
    # Rendements SIMPLES : le rendement d'un panier pondere est somme(w_i*r_simple_i).
    # Voir results/nonml_portfolio_log_aggregation_audit.md.
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
    return P, R_safe, weights_winners


def evaluate(P, R_safe, weights_winners, cap, window):
    trend = index_trend_series()
    trend_aligned = trend.reindex(P.index, method="ffill").fillna(False).values.astype(bool)

    pnl_raw = (weights_winners * R_safe).sum(axis=1)
    vol_ann = pd.Series(pnl_raw).rolling(window).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, cap)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)
    exposure = np.where(trend_aligned, vt_exposure, 1.0)

    start2 = max(SIGNAL_WINDOW, window)
    pnl_base = (weights_winners[start2:] * R_safe[start2:]).sum(axis=1)
    turn_base = np.abs(np.diff(weights_winners[start2:], axis=0, prepend=weights_winners[start2:start2+1])).sum(axis=1) / 2.0
    pnl_base = pnl_base - turn_base * (COST_BPS / 1e4)
    me_base = trading_metrics(np.log1p(pnl_base))
    ret_base = np.cumprod(1.0 + pnl_base)[-1] - 1.0

    weights_lev = weights_winners * exposure[:, None]
    pnl_lev = (weights_lev[start2:] * R_safe[start2:]).sum(axis=1)
    turn_lev = np.abs(np.diff(weights_lev[start2:], axis=0, prepend=weights_lev[start2:start2+1])).sum(axis=1) / 2.0
    pnl_lev = pnl_lev - turn_lev * (COST_BPS / 1e4)
    me_lev = trading_metrics(np.log1p(pnl_lev))
    ret_lev = np.cumprod(1.0 + pnl_lev)[-1] - 1.0

    sharpe_ok = me_lev["sharpe_ann"] > me_base["sharpe_ann"]
    ret_ok = ret_lev > ret_base
    return sharpe_ok, ret_ok, me_lev["sharpe_ann"], ret_lev, me_lev["max_drawdown_pct"]


def main():
    P, R_safe, weights_winners = build_base()

    lines = [
        "# Robustesse — Winners + overlay combiné tendance + vol-targeting (grilles CAP et fenêtre, PAS un retuning)",
        "",
        "CAP pré-enregistré = 2.0x, fenêtre pré-enregistrée = 20j. **Prudence forte héritée du #14.**",
        "",
        "## Grille CAP (fenêtre fixée à 20j)",
        "",
        "| CAP | Sharpe>réf | Rdt>réf | Sharpe | Rendement total | MDD |",
        "|---|---|---|---|---|---|",
    ]
    for cap in CAP_GRID:
        sharpe_ok, ret_ok, sharpe, ret, mdd = evaluate(P, R_safe, weights_winners, cap, 20)
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}% | {mdd:.1f}%{marker} |")

    lines.append("")
    lines.append("## Grille fenêtre de vol (CAP fixé à 2.0x)")
    lines.append("")
    lines.append("| Fenêtre | Sharpe>réf | Rdt>réf | Sharpe | Rendement total | MDD |")
    lines.append("|---|---|---|---|---|---|")
    for window in WINDOW_GRID:
        sharpe_ok, ret_ok, sharpe, ret, mdd = evaluate(P, R_safe, weights_winners, 2.0, window)
        marker = " ← fenêtre pré-enregistrée" if window == 20 else ""
        lines.append(f"| {window}j | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}% | {mdd:.1f}%{marker} |")

    out = ROOT / "results" / "nonml_winners_trend_vol_targeting_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
