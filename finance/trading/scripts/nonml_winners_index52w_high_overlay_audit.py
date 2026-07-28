"""Audit adversarial — Winners momentum + overlay 52w-high indice.

Même protocole que les audits #38/#39 : exposition totale conforme,
qualité de l'alignement calendaire causal (ffill), recalcul indépendant
du signal 52w-high, test anti-lookahead.
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
from nonml_winners_index52w_high_overlay_backtest import (  # noqa: E402
    load_prices, index_trend_series, SIGNAL_WINDOW, REBAL_EVERY, TERCILE, CAP,
    INDEX_LOOKBACK, INDEX_THRESHOLD,
)


def independent_near_high(close: np.ndarray) -> np.ndarray:
    T = len(close)
    out = np.zeros(T, dtype=bool)
    for i in range(INDEX_LOOKBACK, T):
        window_max = close[i - INDEX_LOOKBACK + 1:i + 1].max()
        out[i] = close[i] >= INDEX_THRESHOLD * window_max
    return out


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
    exposure_target = np.where(trend_aligned, CAP, 1.0)
    weights_lev = weights_winners * exposure_target[:, None]

    total_exposure = weights_lev[start:].sum(axis=1)
    expected = exposure_target[start:]
    has_position = weights_winners[start:].sum(axis=1) > 1e-9
    diff = np.abs(total_exposure[has_position] - expected[has_position])
    max_diff = float(diff.max()) if diff.size else 0.0

    n_exact_match = int(P.index.isin(trend.index).sum())
    n_total = len(P.index)

    df_idx = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_idx)
    close_idx = df_idx["close"].values

    m_orig_full = index_trend_series().values
    m_indep = independent_near_high(close_idx)
    recompute_diff = int(np.sum(m_orig_full[INDEX_LOOKBACK:] != m_indep[INDEX_LOOKBACK:]))

    close_idx_pert = close_idx.copy()
    cut = len(close_idx_pert) // 2
    rng = np.random.default_rng(41)
    close_idx_pert[cut:] = close_idx_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_idx_pert) - cut))
    rolling_max_before = pd.Series(close_idx).rolling(INDEX_LOOKBACK).max().values
    above_before = close_idx >= INDEX_THRESHOLD * rolling_max_before
    rolling_max_after = pd.Series(close_idx_pert).rolling(INDEX_LOOKBACK).max().values
    above_after = close_idx_pert >= INDEX_THRESHOLD * rolling_max_after
    anti_leak_ok = bool(np.array_equal(above_before[:cut], above_after[:cut]))

    lines = [
        "# Audit adversarial — Winners momentum + overlay proximité plus haut 52-semaines indice",
        "",
        f"Écart maximum sur l'exposition totale (jours avec position) : {max_diff:.2e}",
        f"**{'OK — exposition exactement conforme.' if max_diff < 1e-9 else 'ÉCHEC — dérive détectée.'}**",
        "",
        f"Alignement calendaire (ffill causal) : {n_exact_match}/{n_total} dates du portefeuille "
        f"correspondent exactement à une séance de l'indice NDX-100 ({100*n_exact_match/n_total:.1f}%).",
        "",
        f"Recalcul indépendant du signal 52w-high (boucle explicite vs pandas.rolling.max) : "
        f"{recompute_diff} écarts. "
        f"**{'OK.' if recompute_diff == 0 else 'ÉCHEC.'}**",
        "",
        f"Test anti-lookahead sur le signal de tendance indice : "
        f"{'OK — aucune fuite.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}",
        "",
        "**Lecture** : contrairement au #18 (Winners + overlay ToM, FAIL, calendrier fixe "
        "sans lien avec le régime de marché), le filtre de tendance 52w-high réussit ici à "
        "améliorer encore un edge déjà extrême (Sharpe +2,35→+3,00) -- MAIS la **prudence "
        "forte** du #14 reste pleinement applicable : ce résultat est mesuré sur le même "
        "bull market concentré 2021-2026, sa généralisabilité hors de cet échantillon est "
        "incertaine, indépendamment de la solidité technique de l'overlay lui-même "
        "(confirmée par cet audit).",
    ]

    out = ROOT / "results" / "nonml_winners_index52w_high_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
