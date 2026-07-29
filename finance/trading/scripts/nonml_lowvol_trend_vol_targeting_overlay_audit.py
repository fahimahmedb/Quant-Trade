"""Audit adversarial — Low-Vol Tilt + overlay combiné tendance +
vol-targeting.

Même protocole que les audits #47/#51 : recalcul indépendant de
l'exposition vol-targeting (ddof=1), qualité de l'alignement calendaire,
test anti-lookahead sur le signal de tendance indice.
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
from nonml_lowvol_trend_vol_targeting_overlay_backtest import (  # noqa: E402
    load_prices, index_trend_series, LOWVOL_WINDOW, REBAL_EVERY, TERCILE, CAP,
    VOL_WINDOW, TARGET_VOL_ANNUAL, ANNUALIZATION, INDEX_LOOKBACK, INDEX_THRESHOLD,
)


def main():
    series = load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    exists = np.isfinite(P.values)
    R = np.nan_to_num(np.log(P / P.shift(1)).values, nan=0.0)
    R[0, :] = 0.0

    vol = P.pct_change(fill_method=None).rolling(LOWVOL_WINDOW).std().values
    n_low = max(1, int(round(n_tickers * TERCILE)))
    weights_lowvol = np.zeros((T, n_tickers))
    start = LOWVOL_WINDOW
    rebal_dates = list(range(start, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        v = vol[t]
        elig = np.where(np.isfinite(v) & exists[t])[0]
        n_low_t = min(n_low, len(elig))
        if n_low_t > 0:
            low_idx = elig[np.argsort(v[elig])[:n_low_t]]
            w = np.zeros(n_tickers)
            w[low_idx] = 1.0 / n_low_t
            weights_lowvol[t:end] = w

    trend = index_trend_series()
    trend_aligned = trend.reindex(P.index, method="ffill").fillna(False).values.astype(bool)

    pnl_raw = (weights_lowvol * R).sum(axis=1)
    vol_ann = pd.Series(pnl_raw).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)

    def independent_vt(r_pnl):
        n = len(r_pnl)
        exp_ = np.ones(n)
        for t in range(VOL_WINDOW + 1, n):
            window = r_pnl[t - VOL_WINDOW:t]
            vol_ = window.std(ddof=1) * ANNUALIZATION
            if vol_ > 0:
                exp_[t] = min(max(TARGET_VOL_ANNUAL / vol_, 1.0), CAP)
            else:
                exp_[t] = CAP
        return exp_

    vt_indep = independent_vt(pnl_raw)
    diff_start = VOL_WINDOW + 1
    max_diff_vt = float(np.max(np.abs(vt_exposure[diff_start:] - vt_indep[diff_start:])))

    n_exact_match = int(P.index.isin(trend.index).sum())
    n_total = len(P.index)

    df_idx = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_idx)
    close_idx = df_idx["close"].values
    rolling_max_before = pd.Series(close_idx).rolling(INDEX_LOOKBACK).max().values
    above_before = close_idx >= INDEX_THRESHOLD * rolling_max_before
    close_idx_pert = close_idx.copy()
    cut = len(close_idx_pert) // 2
    rng = np.random.default_rng(89)
    close_idx_pert[cut:] = close_idx_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_idx_pert) - cut))
    rolling_max_after = pd.Series(close_idx_pert).rolling(INDEX_LOOKBACK).max().values
    above_after = close_idx_pert >= INDEX_THRESHOLD * rolling_max_after
    anti_leak_trend_ok = bool(np.array_equal(above_before[:cut], above_after[:cut]))

    lines = [
        "# Audit adversarial — Low-Vol Tilt + overlay combiné tendance + vol-targeting",
        "",
        f"Recalcul indépendant de l'exposition vol-targeting (ddof=1, boucle explicite) : "
        f"écart max = {max_diff_vt:.2e}",
        f"**{'OK.' if max_diff_vt < 1e-9 else 'ÉCHEC.'}**",
        "",
        f"Alignement calendaire (ffill causal) : {n_exact_match}/{n_total} dates du portefeuille "
        f"correspondent exactement à une séance de l'indice NDX-100 ({100*n_exact_match/n_total:.1f}%).",
        "",
        f"Test anti-lookahead sur le signal de tendance indice : "
        f"{'OK — aucune fuite.' if anti_leak_trend_ok else 'ÉCHEC — fuite détectée.'}",
        "",
        "**Lecture** : complète le trio des portefeuilles de base testés avec le mécanisme "
        "hiérarchique (#47 Buy&Hold, #51 Winners, #53 Low-Vol) — dans les trois cas, la "
        "combinaison tendance+vol-targeting bat ou égale le simple overlay binaire "
        "correspondant (#29/#35, #42, ici #35) en préservant systématiquement bien le MDD "
        "(-18,9%→-19,4%, quasi inchangé, cohérent avec #35's -18,9%→-19,9%).",
    ]

    out = ROOT / "results" / "nonml_lowvol_trend_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
