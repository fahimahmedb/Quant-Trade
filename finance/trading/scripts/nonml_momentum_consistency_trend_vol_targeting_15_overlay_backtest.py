"""Backtest — Momentum de constance + overlay combiné tendance +
vol-targeting, CIBLE DE VOL 15% (spécification pré-enregistrée dans
PREREG_momentum_consistency_trend_vol_targeting_15_overlay.md, committée
avant ce script). Reprend le #85 à l'identique sauf TARGET_VOL_ANNUAL
(0.15 au lieu de 0.20). n_trials=1, aucune dépendance ML. Règle de
succès renforcée -- référence = momentum de constance 1.0x (cycle #82),
pas Buy&Hold.
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
from nonml_momentum_consistency_backtest import (  # noqa: E402
    load_all_prices, consistency_at, LOOKBACK, REBAL_EVERY, TERCILE,
)
from nonml_momentum_consistency_sma200_overlay_backtest import index_trend_series  # noqa: E402

COST_BPS = 5.0
CAP = 2.0
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.15
ANNUALIZATION = np.sqrt(252)


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
    R = np.nan_to_num(np.log(P / P.shift(1)).values, nan=0.0)
    R[0, :] = 0.0

    n_top = max(1, int(round(n_tickers * TERCILE)))
    weights_cons = np.zeros((T, n_tickers))
    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        cons = consistency_at(close, t)
        elig = np.where(np.isfinite(cons))[0]
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-cons[elig])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_cons[t:end] = w

    trend = index_trend_series()
    trend_aligned = trend.reindex(P.index, method="ffill").fillna(False).values.astype(bool)

    pnl_cons_raw = (weights_cons * R).sum(axis=1)
    vol_ann = pd.Series(pnl_cons_raw).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)

    exposure = np.where(trend_aligned, vt_exposure, 1.0)

    weights_base = weights_cons
    weights_lev = weights_cons * exposure[:, None]

    start = max(LOOKBACK, VOL_WINDOW)
    pnl_base = (weights_base[start:] * R[start:]).sum(axis=1)
    pnl_lev = (weights_lev[start:] * R[start:]).sum(axis=1)

    turn_base = np.abs(np.diff(weights_base[start:], axis=0, prepend=weights_base[start:start+1])).sum(axis=1) / 2.0
    turn_lev = np.abs(np.diff(weights_lev[start:], axis=0, prepend=weights_lev[start:start+1])).sum(axis=1) / 2.0
    pnl_base = pnl_base - turn_base * (COST_BPS / 1e4)
    pnl_lev = pnl_lev - turn_lev * (COST_BPS / 1e4)

    me_base = trading_metrics(pnl_base)
    me_lev = trading_metrics(pnl_lev)
    ret_base = np.cumprod(1.0 + pnl_base)[-1] - 1.0
    ret_lev = np.cumprod(1.0 + pnl_lev)[-1] - 1.0

    sharpe_ok = me_lev["sharpe_ann"] > me_base["sharpe_ann"]
    ret_ok = ret_lev > ret_base
    verdict = sharpe_ok and ret_ok

    avg_exposure = float(exposure[start:].mean())
    frac_at_floor = float((np.isclose(exposure[start:], 1.0)).mean())

    lines = [
        "# Résultat — Momentum de constance + overlay combiné tendance + vol-targeting, cible 15% (pré-enregistré, variante #85)",
        "",
        f"Référence = portefeuille momentum de constance 1.0x (cycle #82), PAS Buy&Hold. "
        f"{T - start} séances testables ({P.index[start].date()} → {P.index[-1].date()}). "
        f"Overlay actif {100*trend_aligned[start:].mean():.1f}% du temps en tendance haussière (SMA200 indice). "
        f"Exposition moyenne : {avg_exposure:.2f}x (plancher 1.0x {100*frac_at_floor:.1f}% du temps).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Momentum de constance 1.0x (référence, cycle #82) | {me_base['sharpe_ann']:+.2f} | {100*ret_base:+.1f}% | "
        f"{me_base['max_drawdown_pct']:.1f}% |",
        f"| **Momentum de constance + overlay tendance+vol-targeting (cible 15%)** | **{me_lev['sharpe_ann']:+.2f}** | "
        f"**{100*ret_lev:+.1f}%** | {me_lev['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > référence : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > référence : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_momentum_consistency_trend_vol_targeting_15_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
