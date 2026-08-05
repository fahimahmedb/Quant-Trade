"""Audit adversarial — Overlay vol-targeting gaté par la vol-de-la-vol
glissante.

Recalcul indépendant de la porte (vol_ann, vol-de-la-vol et médiane
recalculés par boucle explicite avec écart-type et médiane manuels,
indépendamment de pandas.rolling()) et test anti-lookahead.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from nonml_vol_of_vol_vol_targeting_overlay_backtest import (  # noqa: E402
    stable_vol_regime_mask, combined_position,
    VOL_WINDOW, VOV_WINDOW, MEDIAN_WINDOW, ANNUALIZATION, MARKETS,
)


def manual_std(window: np.ndarray) -> float:
    mu = window.mean()
    return float(np.sqrt(np.sum((window - mu) ** 2) / (len(window) - 1)))


def manual_median(window: np.ndarray) -> float:
    s = np.sort(window)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return float(s[mid])
    return float((s[mid - 1] + s[mid]) / 2.0)


def independent_gate(r: np.ndarray) -> np.ndarray:
    """Recalcul totalement independant : vol_ann_lagged, vol-de-la-vol
    et mediane recalcules par boucle explicite, sans pandas.rolling()."""
    n = len(r)
    vol_ann = np.full(n, np.nan)
    for t in range(VOL_WINDOW - 1, n):
        window = r[t - VOL_WINDOW + 1:t + 1]
        vol_ann[t] = manual_std(window) * ANNUALIZATION

    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan

    vol_of_vol = np.full(n, np.nan)
    for t in range(VOV_WINDOW - 1, n):
        window = vol_lagged[t - VOV_WINDOW + 1:t + 1]
        if np.any(np.isnan(window)):
            continue
        vol_of_vol[t] = manual_std(window)

    gate = np.zeros(n, dtype=bool)
    for t in range(MEDIAN_WINDOW - 1, n):
        window = vol_of_vol[t - MEDIAN_WINDOW + 1:t + 1]
        if np.any(np.isnan(window)):
            continue
        med = manual_median(window)
        gate[t] = vol_of_vol[t] <= med
    return gate


def main():
    start = VOL_WINDOW + VOV_WINDOW + MEDIAN_WINDOW
    lines = ["# Audit adversarial — Overlay vol-targeting gaté par la vol-de-la-vol glissante", "",
             "## 1. Recalcul totalement indépendant de la porte (boucle explicite, écart-type et médiane manuels)", "",
             "| Marché | Désaccords porte (hors marge de fenêtre) | Séances comparées |",
             "|---|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        r = np.log(close[1:] / close[:-1])
        if len(r) <= start:
            continue
        gate_orig = stable_vol_regime_mask(r)
        gate_indep = independent_gate(r)
        n_diff = int(np.sum(gate_orig[start:] != gate_indep[start:]))
        n_total = len(gate_orig) - start
        all_ok &= (n_diff == 0)
        lines.append(f"| {name} | {n_diff} | {n_total} |")

    lines.append("")
    lines.append(f"**{'OK — porte confirmée par recalcul totalement indépendant.' if all_ok else 'Désaccords détectés, examinés ci-dessous.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (perturbation du futur, close)")
    lines.append("")
    lines.append("| Marché | Décisions passées identiques après perturbation future |")
    lines.append("|---|---|")
    anti_leak_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        r = np.log(close[1:] / close[:-1])
        if len(r) <= start:
            continue
        gate_before = stable_vol_regime_mask(r)
        pos_before = combined_position(r, gate_before)

        cut = len(r) // 2
        rng = np.random.default_rng(73)
        r_pert = r.copy()
        r_pert[cut:] = r_pert[cut:] + rng.normal(0, 0.02, len(r) - cut)
        gate_after = stable_vol_regime_mask(r_pert)
        pos_after = combined_position(r_pert, gate_after)

        check_end = cut - start
        identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_vol_of_vol_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
