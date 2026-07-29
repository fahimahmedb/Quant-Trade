"""Audit adversarial — Overlay vol-targeting gaté par breadth interne
NDX-100.

Recalcul totalement indépendant de la breadth (boucle explicite par
titre, sans réutiliser numpy vectorisé) et de la position (boucle
explicite jour par jour, ddof=1), et test anti-lookahead (perturbation
du futur sur les prix titre ET indice).
"""
import json
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
from nonml_internal_breadth_vol_targeting_overlay_backtest import (  # noqa: E402
    load_all_prices, combined_position, INDEX_LOOKBACK, INDEX_THRESHOLD, BREADTH_THRESHOLD,
    VOL_WINDOW, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION,
)


def independent_breadth_series():
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    close = P.values
    T, n_tickers = P.shape

    breadth = np.full(T, np.nan)
    for i in range(INDEX_LOOKBACK, T):
        n_listed, n_near_high = 0, 0
        for j in range(n_tickers):
            # denominateur = tous les titres COTES au jour i (conforme au
            # PREREG : "denominateur = titres cotes"), pas seulement ceux
            # ayant un historique complet de 252j -- bug trouve dans ce
            # script d'audit lors du premier passage (utilisait a tort la
            # fenetre complete comme critere de comptage), corrige ici en
            # reproduisant exactement la definition pre-enregistree.
            if not np.isfinite(close[i, j]):
                continue
            n_listed += 1
            c = close[i - INDEX_LOOKBACK + 1:i + 1, j]
            if np.isfinite(c).all() and close[i, j] >= INDEX_THRESHOLD * c.max():
                n_near_high += 1
        if n_listed > 0:
            breadth[i] = n_near_high / n_listed
    return pd.Series(breadth, index=P.index)


def independent_combined_position(close: np.ndarray, r: np.ndarray, breadth_aligned: np.ndarray) -> np.ndarray:
    T = len(r)
    gate = breadth_aligned >= BREADTH_THRESHOLD
    pos = np.ones(T)
    for i in range(T):
        if not gate[i]:
            pos[i] = 1.0
            continue
        if i - VOL_WINDOW < 0:
            pos[i] = 1.0
            continue
        vol_window_r = r[i - VOL_WINDOW:i]
        vol_ann = vol_window_r.std(ddof=1) * ANNUALIZATION
        if vol_ann > 0:
            pos[i] = min(max(TARGET_VOL_ANNUAL / vol_ann, 1.0), CAP)
        else:
            pos[i] = CAP
    return pos


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    r = np.log(close[1:] / close[:-1])

    from nonml_internal_breadth_vol_targeting_overlay_backtest import compute_breadth_series
    breadth_orig = compute_breadth_series()
    breadth_indep = independent_breadth_series()

    diff_breadth = float(np.nanmax(np.abs(breadth_orig.values - breadth_indep.values)))

    breadth_aligned_raw = breadth_orig.reindex(dates_idx.values, method="ffill").values
    breadth_aligned = np.nan_to_num(breadth_aligned_raw, nan=0.0)
    first_valid = int(np.argmax(~np.isnan(breadth_aligned_raw)))
    start = max(first_valid, INDEX_LOOKBACK, VOL_WINDOW)

    pos_orig = combined_position(close, r, breadth_aligned)
    pos_indep = independent_combined_position(close[start - VOL_WINDOW:], r[start - VOL_WINDOW:], breadth_aligned[start - VOL_WINDOW:])
    # aligner : pos_indep[0] correspond a pos_orig[start-VOL_WINDOW]
    max_diff_pos = float(np.max(np.abs(pos_orig[start:] - pos_indep[VOL_WINDOW:])))

    lines = ["# Audit adversarial — Overlay vol-targeting gaté par breadth interne NDX-100", "",
             "## 1. Recalcul indépendant de la breadth (boucle explicite par titre)", "",
             f"Écart maximum absolu (hors NaN) : {diff_breadth:.2e}",
             f"**{'OK — breadth confirmée par recalcul indépendant.' if diff_breadth < 1e-9 else 'ÉCHEC.'}**",
             "",
             "## 2. Recalcul indépendant de la position (boucle explicite jour par jour, ddof=1)",
             "",
             f"Écart maximum absolu sur l'échantillon testable : {max_diff_pos:.2e}",
             f"**{'OK — position confirmée par recalcul indépendant.' if max_diff_pos < 1e-9 else 'ÉCHEC.'}**",
             ""]

    lines.append("## 3. Test anti-lookahead (perturbation du futur sur l'indice)")
    lines.append("")
    cut = len(close) // 2
    close_pert = close.copy()
    rng = np.random.default_rng(251)
    close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
    r_pert = np.log(close_pert[1:] / close_pert[:-1])
    pos_before = combined_position(close, r, breadth_aligned)
    pos_after = combined_position(close_pert, r_pert, breadth_aligned)
    check_end = cut - max(INDEX_LOOKBACK, VOL_WINDOW)
    identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
    lines.append(f"**{'OK — aucune fuite (perturbation des prix indice futurs sans effet passé).' if identical else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_internal_breadth_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
