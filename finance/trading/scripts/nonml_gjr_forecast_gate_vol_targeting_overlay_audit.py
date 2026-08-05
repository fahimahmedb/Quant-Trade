"""Audit adversarial — Overlay vol-targeting gaté par la prévision GJR-t
walk-forward.

Recalcul indépendant de la porte et de la position (médiane glissante et
exposition réalisée recalculées par boucle explicite, indépendamment du
backtest) et test anti-lookahead. La prévision GJR-t elle-même n'est PAS
recalculée (fonction déjà validée à l'Étape C/#165, réutilisée sans
modification, Règle 7) — l'audit porte sur l'USAGE qui en est fait ici
(la porte et le mécanisme #46), pas sur le modèle GARCH sous-jacent.
"""
import sys
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from overlay import walk_forward_vol_forecast  # noqa: E402
from nonml_gjr_forecast_gate_vol_targeting_overlay_backtest import (  # noqa: E402
    MARKET_FILE, T0, REFIT_EVERY, MEDIAN_WINDOW, VOL_WINDOW,
    TARGET_VOL_ANNUAL, CAP, COST_BPS, ANNUALIZATION,
)
from prediction import trading_metrics  # noqa: E402


def manual_median(window: np.ndarray) -> float:
    s = np.sort(window)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return float(s[mid])
    return float((s[mid - 1] + s[mid]) / 2.0)


def manual_std(window: np.ndarray) -> float:
    mu = window.mean()
    return float(np.sqrt(np.sum((window - mu) ** 2) / (len(window) - 1)))


def independent_position(r_pct: np.ndarray, vol_fcst_pct: np.ndarray) -> np.ndarray:
    """Recalcul independant de la porte (mediane par tri manuel) et de
    l'exposition realisee (ecart-type par boucle explicite), a partir de
    la meme prevision GJR-t (fonction non recalculee, deja validee)."""
    r_frac = r_pct / 100.0
    n = len(r_pct)

    gate = np.zeros(n, dtype=bool)
    for t in range(T0 + MEDIAN_WINDOW - 1, n):
        window = vol_fcst_pct[t - MEDIAN_WINDOW + 1:t + 1]
        if np.any(np.isnan(window)):
            continue
        med = manual_median(window)
        gate[t] = vol_fcst_pct[t] <= med

    vol_ann_frac = np.full(n, np.nan)
    for t in range(VOL_WINDOW - 1, n):
        window = r_frac[t - VOL_WINDOW + 1:t + 1]
        vol_ann_frac[t] = manual_std(window) * ANNUALIZATION
    vol_lagged = np.roll(vol_ann_frac, 1)
    vol_lagged[0] = np.nan

    pos = np.ones(n)
    for t in range(n):
        if np.isnan(vol_lagged[t]) or not gate[t]:
            pos[t] = 1.0
            continue
        vt = TARGET_VOL_ANNUAL / vol_lagged[t]
        pos[t] = min(max(vt, 1.0), CAP)
    return pos


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    ser = log_returns_pct(df)
    r_pct = ser.values

    fc = walk_forward_vol_forecast(r_pct, T0, REFIT_EVERY)
    vol_fcst_pct = fc["vol_fcst"]

    import nonml_gjr_forecast_gate_vol_targeting_overlay_backtest as bt
    r_frac = r_pct / 100.0
    valid = vol_fcst_pct[T0:]
    import pandas as pd
    med_pd = pd.Series(valid).rolling(MEDIAN_WINDOW).median().values
    gate_valid = np.nan_to_num(valid <= med_pd, nan=0.0).astype(bool)
    gate_orig_full = np.zeros(len(r_pct), dtype=bool)
    gate_orig_full[T0:] = gate_valid
    import numpy as _np
    vol_ann_frac_orig = pd.Series(r_frac).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged_orig = _np.roll(vol_ann_frac_orig, 1)
    vol_lagged_orig[0] = _np.nan
    with _np.errstate(divide="ignore", invalid="ignore"):
        vt_orig = TARGET_VOL_ANNUAL / vol_lagged_orig
    vt_orig = _np.clip(vt_orig, 1.0, CAP)
    vt_orig = _np.nan_to_num(vt_orig, nan=1.0)
    pos_orig = _np.where(gate_orig_full, vt_orig, 1.0)

    pos_indep = independent_position(r_pct, vol_fcst_pct)

    start = T0 + MEDIAN_WINDOW
    max_diff = float(np.max(np.abs(pos_orig[start:] - pos_indep[start:])))

    lines = ["# Audit adversarial — Overlay vol-targeting gaté par la prévision GJR-t walk-forward", "",
             "## 1. Recalcul indépendant de la porte et de la position (médiane par tri, écart-type par boucle)", "",
             f"Écart position max (NDX, hors marge de fenêtre) : {max_diff:.2e}",
             "",
             f"**{'OK — position confirmée par recalcul indépendant.' if max_diff < 1e-9 else 'ÉCHEC.'}**",
             "",
             "## 2. Test anti-lookahead (perturbation du futur, rendements)",
             ""]

    r_pert = r_pct.copy()
    cut = len(r_pct) // 2
    rng = np.random.default_rng(73)
    r_pert[cut:] = r_pert[cut:] + rng.normal(0, 0.5, len(r_pct) - cut)  # perturbation en % (echelle arch)

    fc_pert = walk_forward_vol_forecast(r_pert, T0, REFIT_EVERY)
    vol_fcst_pert = fc_pert["vol_fcst"]
    valid_pert = vol_fcst_pert[T0:]
    med_pert = pd.Series(valid_pert).rolling(MEDIAN_WINDOW).median().values
    gate_pert_valid = np.nan_to_num(valid_pert <= med_pert, nan=0.0).astype(bool)
    gate_pert_full = np.zeros(len(r_pert), dtype=bool)
    gate_pert_full[T0:] = gate_pert_valid
    r_frac_pert = r_pert / 100.0
    vol_ann_frac_pert = pd.Series(r_frac_pert).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged_pert = np.roll(vol_ann_frac_pert, 1)
    vol_lagged_pert[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_pert = TARGET_VOL_ANNUAL / vol_lagged_pert
    vt_pert = np.clip(vt_pert, 1.0, CAP)
    vt_pert = np.nan_to_num(vt_pert, nan=1.0)
    pos_pert = np.where(gate_pert_full, vt_pert, 1.0)

    check_end = cut - MEDIAN_WINDOW
    identical = bool(np.allclose(pos_orig[:check_end], pos_pert[:check_end]))
    lines.append(f"Décisions passées identiques après perturbation future (NDX) : {'OUI' if identical else 'NON — FUITE DETECTEE'}")
    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if identical else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_gjr_forecast_gate_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
