"""Robustesse — Leaders + overlay vol-targeting cible 20%. Grille CAP ET
grille de fenêtre de vol (PAS un retuning de la cible), autour des
valeurs pré-enregistrées (CAP=2.0x, fenêtre=20j).
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
from nonml_leaders_vol_targeting_20_overlay_backtest import (  # noqa: E402
    load_prices, LOOKBACK, REBAL_EVERY, TERCILE, COST_BPS, TARGET_VOL_ANNUAL, ANNUALIZATION,
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
    R = np.nan_to_num((P / P.shift(1) - 1.0).values, nan=0.0)
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
    return P, R, weights_leaders


def evaluate(P, R, weights_leaders, cap, window):
    pnl_leaders_raw = (weights_leaders * R).sum(axis=1)
    vol_ann = pd.Series(pnl_leaders_raw).rolling(window).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        exposure = TARGET_VOL_ANNUAL / vol_lagged
    exposure = np.clip(exposure, 0.0, cap)
    exposure = np.nan_to_num(exposure, nan=1.0)

    start = LOOKBACK + window
    pnl_base = (weights_leaders[start:] * R[start:]).sum(axis=1)
    turn_base = np.abs(np.diff(weights_leaders[start:], axis=0, prepend=weights_leaders[start:start+1])).sum(axis=1) / 2.0
    pnl_base = pnl_base - turn_base * (COST_BPS / 1e4)
    me_base = trading_metrics(np.log1p(pnl_base))
    ret_base = np.cumprod(1.0 + pnl_base)[-1] - 1.0

    weights_lev = weights_leaders * exposure[:, None]
    pnl_lev = (weights_lev[start:] * R[start:]).sum(axis=1)
    turn_lev = np.abs(np.diff(weights_lev[start:], axis=0, prepend=weights_lev[start:start+1])).sum(axis=1) / 2.0
    pnl_lev = pnl_lev - turn_lev * (COST_BPS / 1e4)
    me_lev = trading_metrics(np.log1p(pnl_lev))
    ret_lev = np.cumprod(1.0 + pnl_lev)[-1] - 1.0

    sharpe_ok = me_lev["sharpe_ann"] > me_base["sharpe_ann"]
    ret_ok = ret_lev > ret_base
    return sharpe_ok, ret_ok, me_lev["sharpe_ann"], ret_lev


def main():
    P, R, weights_leaders = build_base()

    lines = [
        "# Robustesse — Leaders + overlay vol-targeting cible 20% (grilles CAP et fenêtre, PAS un retuning)",
        "",
        "CAP pré-enregistré = 2.0x, fenêtre pré-enregistrée = 20j.",
        "",
        "## Grille CAP (fenêtre fixée à 20j)",
        "",
        "| CAP | Sharpe>réf | Rdt>réf | Sharpe | Rendement total |",
        "|---|---|---|---|---|",
    ]
    for cap in CAP_GRID:
        sharpe_ok, ret_ok, sharpe, ret = evaluate(P, R, weights_leaders, cap, 20)
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}%{marker} |")

    lines.append("")
    lines.append("## Grille fenêtre de vol (CAP fixé à 2.0x)")
    lines.append("")
    lines.append("| Fenêtre | Sharpe>réf | Rdt>réf | Sharpe | Rendement total |")
    lines.append("|---|---|---|---|---|")
    for window in WINDOW_GRID:
        sharpe_ok, ret_ok, sharpe, ret = evaluate(P, R, weights_leaders, 2.0, window)
        marker = " ← fenêtre pré-enregistrée" if window == 20 else ""
        lines.append(f"| {window}j | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{sharpe:+.2f} | {100*ret:+.1f}%{marker} |")

    out = ROOT / "results" / "nonml_leaders_vol_targeting_20_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
