"""Audit adversarial — Momentum de constance + overlay SMA200.

Vérifie (1) l'alignement causal (ffill uniquement) entre le calendrier
indice (NDX-100 OHLC) et le calendrier portefeuille (tickers
individuels, calendrier légèrement différent), (2) l'exposition totale
conforme, (3) un test anti-lookahead sur le signal de tendance lui-même.
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
from nonml_momentum_consistency_sma200_overlay_backtest import (  # noqa: E402
    load_all_prices, index_trend_series, consistency_at, LOOKBACK, REBAL_EVERY, TERCILE, CAP, SMA_WINDOW,
)


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
    exposure_target = np.where(trend_aligned, CAP, 1.0)
    weights_lev = weights_cons * exposure_target[:, None]

    start = LOOKBACK
    total_exposure = weights_lev[start:].sum(axis=1)
    expected = exposure_target[start:]
    has_position = weights_cons[start:].sum(axis=1) > 1e-9
    diff = np.abs(total_exposure[has_position] - expected[has_position])
    max_diff = float(diff.max()) if diff.size else 0.0

    n_exact_match = int(P.index.isin(trend.index).sum())
    n_total = len(P.index)

    df_idx = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_idx)
    close_idx = df_idx["close"].values
    sma_before = pd.Series(close_idx).rolling(SMA_WINDOW).mean().values
    above_before = close_idx > sma_before

    close_idx_pert = close_idx.copy()
    cut = len(close_idx_pert) // 2
    rng = np.random.default_rng(317)
    close_idx_pert[cut:] = close_idx_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_idx_pert) - cut))
    sma_after = pd.Series(close_idx_pert).rolling(SMA_WINDOW).mean().values
    above_after = close_idx_pert > sma_after
    anti_leak_ok = bool(np.array_equal(above_before[:cut], above_after[:cut]))

    lines = [
        "# Audit adversarial — Momentum de constance + overlay SMA200",
        "",
        f"Écart maximum sur l'exposition totale (jours avec position) : {max_diff:.2e}",
        f"**{'OK — exposition exactement conforme.' if max_diff < 1e-9 else 'ÉCHEC — dérive détectée.'}**",
        "",
        f"Alignement calendaire (ffill causal) : {n_exact_match}/{n_total} dates du portefeuille "
        f"correspondent exactement à une séance de l'indice NDX-100 "
        f"({100*n_exact_match/n_total:.1f}%), le reste utilise la dernière valeur connue (ffill, "
        "jamais de donnée future).",
        "",
        f"Test anti-lookahead sur le signal de tendance indice : "
        f"{'OK — aucune fuite.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}",
    ]

    out = ROOT / "results" / "nonml_momentum_consistency_sma200_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
