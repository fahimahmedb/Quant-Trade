"""Audit adversarial — Leaders 52-semaines + overlay de vol-targeting continu.

Recalcul indépendant de l'exposition (boucle explicite, ddof=1 pour
reproduire pandas.Series.std() -- bug d'audit déjà rencontré et corrigé
aux cycles #43/#44, appliqué correctement ici dès le départ), test
anti-lookahead, et vérification de l'exposition totale appliquée.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from nonml_leaders_vol_targeting_overlay_backtest import (  # noqa: E402
    load_prices, vol_target_exposure, LOOKBACK, REBAL_EVERY, TERCILE, CAP,
    VOL_WINDOW, TARGET_VOL_ANNUAL, ANNUALIZATION,
)


def independent_exposure(r: np.ndarray) -> np.ndarray:
    T = len(r)
    exp_ = np.ones(T)
    for t in range(VOL_WINDOW + 1, T):
        window = r[t - VOL_WINDOW:t]
        vol_ann = window.std(ddof=1) * ANNUALIZATION
        if vol_ann > 0:
            exp_[t] = min(max(TARGET_VOL_ANNUAL / vol_ann, 0.0), CAP)
        else:
            exp_[t] = CAP
    return exp_


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
    R = np.nan_to_num(np.log(P / P.shift(1)).values, nan=0.0)
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

    pnl_leaders_raw = (weights_leaders * R).sum(axis=1)
    exposure_orig = vol_target_exposure(pnl_leaders_raw)
    exposure_indep = independent_exposure(pnl_leaders_raw)

    start = LOOKBACK + VOL_WINDOW + 1
    max_diff = float(np.max(np.abs(exposure_orig[start:] - exposure_indep[start:])))
    recompute_ok = max_diff < 1e-9

    # exposition totale appliquee = somme des poids finaux == exposure quand une position existe
    weights_lev = weights_leaders * exposure_orig[:, None]
    has_position = weights_leaders[LOOKBACK:].sum(axis=1) > 1e-9
    applied = weights_lev[LOOKBACK:].sum(axis=1)
    expected = exposure_orig[LOOKBACK:]
    exp_diff = float(np.max(np.abs(applied[has_position] - expected[has_position])))
    exposure_ok = exp_diff < 1e-9

    cut = T // 2
    rng = np.random.default_rng(53)
    pnl_pert = pnl_leaders_raw.copy()
    pnl_pert[cut:] = pnl_pert[cut:] + rng.normal(0, 0.02, T - cut)
    exposure_after = vol_target_exposure(pnl_pert)
    check_end = cut - VOL_WINDOW
    anti_leak_ok = bool(np.allclose(exposure_orig[:check_end], exposure_after[:check_end]))

    lines = [
        "# Audit adversarial — Leaders 52-semaines + overlay de vol-targeting continu",
        "",
        f"Recalcul indépendant de l'exposition (boucle explicite, ddof=1) : écart max = {max_diff:.2e}",
        f"**{'OK.' if recompute_ok else 'ÉCHEC.'}**",
        "",
        f"Exposition totale appliquée (jours avec position) : écart max = {exp_diff:.2e}",
        f"**{'OK — exposition exactement conforme.' if exposure_ok else 'ÉCHEC — dérive détectée.'}**",
        "",
        f"Test anti-lookahead (perturbation du futur) : "
        f"{'OK — aucune fuite.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}",
        "",
        "**Lecture** : même écueil qu'au #43 -- l'exposition moyenne (0,91x) reste sous 1.0x, "
        "ce qui pénalise le rendement composé même quand la vol-targeting s'applique à un "
        "portefeuille à edge positif (Leaders) plutôt qu'à un indice neutre. Le MDD est "
        "amélioré (-21,3%→-17,7%) mais insuffisant pour compenser la perte de rendement selon "
        "la règle renforcée.",
    ]

    out = ROOT / "results" / "nonml_leaders_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
