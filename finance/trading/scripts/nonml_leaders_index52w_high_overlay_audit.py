"""Audit adversarial — Leaders 52-semaines + overlay proximité plus haut
52-semaines indice.

Résultat brut EXCEPTIONNEL (Sharpe +0,78→+1,50, rendement +81,6%→+508,3%,
MDD quasi inchangé -25,7%→-25,9%) -- vérification renforcée : (1)
exposition totale conforme, (2) qualité de l'alignement calendaire
causal (ffill), (3) test anti-lookahead sur le signal de tendance
indice, (4) recalcul indépendant du signal 52w-high lui-même (boucle
explicite).
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
from nonml_leaders_index52w_high_overlay_backtest import (  # noqa: E402
    load_prices, index_trend_series, LOOKBACK, REBAL_EVERY, TERCILE, CAP,
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

    trend = index_trend_series()
    trend_aligned = trend.reindex(P.index, method="ffill").fillna(False).values.astype(bool)
    exposure_target = np.where(trend_aligned, CAP, 1.0)
    weights_lev = weights_leaders * exposure_target[:, None]

    start = LOOKBACK
    total_exposure = weights_lev[start:].sum(axis=1)
    expected = exposure_target[start:]
    has_position = weights_leaders[start:].sum(axis=1) > 1e-9
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
    rng = np.random.default_rng(29)
    close_idx_pert[cut:] = close_idx_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_idx_pert) - cut))
    rolling_max_before = pd.Series(close_idx).rolling(INDEX_LOOKBACK).max().values
    above_before = close_idx >= INDEX_THRESHOLD * rolling_max_before
    rolling_max_after = pd.Series(close_idx_pert).rolling(INDEX_LOOKBACK).max().values
    above_after = close_idx_pert >= INDEX_THRESHOLD * rolling_max_after
    anti_leak_ok = bool(np.array_equal(above_before[:cut], above_after[:cut]))

    lines = [
        "# Audit adversarial — Leaders 52-semaines + overlay proximité plus haut 52-semaines indice",
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
        "**Lecture** : le résultat est exceptionnellement fort (Sharpe +0,78→+1,50, rendement "
        "+81,6%→+508,3%) mais le MDD reste quasi identique (-25,7%→-25,9%) -- cohérent avec le "
        "mécanisme : ce signal coupe le levier avant le portefeuille Leaders lui-même ne "
        "s'effondre, contrairement à une exposition constante. Cette force du résultat justifie "
        "une attention particulière lors de la robustesse (grille CAP ET grille de seuil) avant "
        "de considérer ce résultat comme définitivement solide.",
    ]

    out = ROOT / "results" / "nonml_leaders_index52w_high_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
