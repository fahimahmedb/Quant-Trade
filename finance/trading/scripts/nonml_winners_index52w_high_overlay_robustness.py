"""Robustesse — Winners momentum + overlay proximité plus haut
52-semaines indice. Grille CAP ET grille de seuil (PAS un retuning),
autour des valeurs pré-enregistrées (CAP=2.0x, seuil=95%).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_winners_index52w_high_overlay_backtest import (  # noqa: E402
    load_prices, SIGNAL_WINDOW, REBAL_EVERY, TERCILE, COST_BPS, INDEX_LOOKBACK,
)

CAP_GRID = [1.5, 2.0, 2.5, 3.0]
THRESHOLD_GRID = [0.90, 0.93, 0.95, 0.97]


def index_trend_series_thr(threshold: float) -> pd.Series:
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    rolling_max = pd.Series(close).rolling(INDEX_LOOKBACK).max().values
    near_high = close >= threshold * rolling_max
    dates = pd.to_datetime(df["date"]).values
    return pd.Series(near_high, index=dates)


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


def evaluate(P, R_safe, weights_winners, cap, threshold):
    start = SIGNAL_WINDOW
    trend = index_trend_series_thr(threshold)
    trend_aligned = trend.reindex(P.index, method="ffill").fillna(False).values.astype(bool)

    pnl_base = (weights_winners[start:] * R_safe[start:]).sum(axis=1)
    turn_base = np.abs(np.diff(weights_winners[start:], axis=0, prepend=weights_winners[start:start+1])).sum(axis=1) / 2.0
    pnl_base = pnl_base - turn_base * (COST_BPS / 1e4)
    me_base = trading_metrics(np.log1p(pnl_base))
    ret_base = np.cumprod(1.0 + pnl_base)[-1] - 1.0

    exposure = np.where(trend_aligned, cap, 1.0)
    weights_lev = weights_winners * exposure[:, None]
    pnl_lev = (weights_lev[start:] * R_safe[start:]).sum(axis=1)
    turn_lev = np.abs(np.diff(weights_lev[start:], axis=0, prepend=weights_lev[start:start+1])).sum(axis=1) / 2.0
    pnl_lev = pnl_lev - turn_lev * (COST_BPS / 1e4)
    me_lev = trading_metrics(np.log1p(pnl_lev))
    ret_lev = np.cumprod(1.0 + pnl_lev)[-1] - 1.0

    sharpe_ok = me_lev["sharpe_ann"] > me_base["sharpe_ann"]
    ret_ok = ret_lev > ret_base
    return sharpe_ok, ret_ok, me_lev["sharpe_ann"], ret_lev, me_lev["max_drawdown_pct"]


def main():
    P, R_safe, weights_winners = build_base()

    lines = [
        "# Robustesse — Winners momentum + overlay proximité plus haut 52-semaines indice (grilles CAP et seuil, PAS un retuning)",
        "",
        "CAP pré-enregistré = 2.0x, seuil pré-enregistré = 95%. **Prudence forte héritée du #14.**",
        "",
        "## Grille CAP (seuil fixé à 95%)",
        "",
        "| CAP | Sharpe>réf | Rdt>réf | Sharpe | Rendement total | MDD |",
        "|---|---|---|---|---|---|",
    ]
    for cap in CAP_GRID:
        sharpe_ok, ret_ok, sharpe, ret, mdd = evaluate(P, R_safe, weights_winners, cap, 0.95)
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}% | {mdd:.1f}%{marker} |")

    lines.append("")
    lines.append("## Grille seuil de proximité (CAP fixé à 2.0x)")
    lines.append("")
    lines.append("| Seuil | Sharpe>réf | Rdt>réf | Sharpe | Rendement total | MDD |")
    lines.append("|---|---|---|---|---|---|")
    for thr in THRESHOLD_GRID:
        sharpe_ok, ret_ok, sharpe, ret, mdd = evaluate(P, R_safe, weights_winners, 2.0, thr)
        marker = " ← seuil pré-enregistré" if thr == 0.95 else ""
        lines.append(f"| {100*thr:.0f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}% | {mdd:.1f}%{marker} |")

    out = ROOT / "results" / "nonml_winners_index52w_high_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
