"""Audit adversarial — Overlay de vol-targeting estimateur EWMA.

Recalcul indépendant de la position (boucle explicite recalculant la
récursion EWMA elle-même, indépendamment de ewma_vol_ann_lagged) et test
anti-lookahead.
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
from nonml_ewma_vol_targeting_overlay_backtest import (  # noqa: E402
    ewma_vol_position, VOL_WINDOW, LAM, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION, MARKETS,
)


def independent_ewma_position(r: np.ndarray) -> np.ndarray:
    """Recalcul totalement independant : recursion EWMA recalculee par
    boucle explicite avec variance d'amorcage manuelle (sans np.var),
    sans reutiliser ewma_vol_ann_lagged."""
    n = len(r)
    mu0 = r[:VOL_WINDOW].sum() / VOL_WINDOW
    s2_seed = sum((x - mu0) ** 2 for x in r[:VOL_WINDOW]) / (VOL_WINDOW - 1)

    s2 = [None] * n
    s2[VOL_WINDOW - 1] = s2_seed
    for t in range(VOL_WINDOW, n):
        s2[t] = LAM * s2[t - 1] + (1 - LAM) * r[t - 1] ** 2

    pos = np.ones(n)
    for t in range(VOL_WINDOW, n):
        vol_ann = (s2[t] ** 0.5) * ANNUALIZATION
        if vol_ann > 0:
            pos[t] = min(max(TARGET_VOL_ANNUAL / vol_ann, 0.0), CAP)
        else:
            pos[t] = CAP
    return pos


def main():
    lines = ["# Audit adversarial — Overlay de vol-targeting estimateur EWMA", "",
             "## 1. Recalcul totalement indépendant (récursion EWMA recalculée par boucle explicite)", "",
             "| Marché | Écart position max (hors marge de fenêtre) |",
             "|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        r = np.log(close[1:] / close[:-1])
        pos_orig = ewma_vol_position(r)
        pos_indep = independent_ewma_position(r)
        start = VOL_WINDOW
        max_diff = float(np.max(np.abs(pos_orig[start:] - pos_indep[start:])))
        all_ok &= (max_diff < 1e-9)
        lines.append(f"| {name} | {max_diff:.2e} |")

    lines.append("")
    lines.append(f"**{'OK — position confirmée par recalcul totalement indépendant.' if all_ok else 'ÉCHEC.'}**")

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
        pos_before = ewma_vol_position(r)

        cut = len(r) // 2
        rng = np.random.default_rng(73)
        r_pert = r.copy()
        r_pert[cut:] = r_pert[cut:] + rng.normal(0, 0.02, len(r) - cut)
        pos_after = ewma_vol_position(r_pert)

        check_end = cut
        identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_ewma_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
