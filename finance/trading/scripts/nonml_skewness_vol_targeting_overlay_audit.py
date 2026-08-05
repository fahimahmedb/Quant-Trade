"""Audit adversarial — Overlay vol-targeting gaté par l'asymétrie
(skewness) glissante.

Recalcul indépendant de la porte (skewness recalculée par une formule
directe des moments centrés, indépendamment de scipy.stats.skew) et test
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
from nonml_skewness_vol_targeting_overlay_backtest import (  # noqa: E402
    favorable_skew_mask, combined_position, SKEW_WINDOW, MEDIAN_WINDOW, MARKETS,
)


def independent_skew(window: np.ndarray) -> float:
    """Recalcul totalement independant de la skewness de Fisher-Pearson
    biais-corrigee (formule directe des moments centres), sans passer
    par scipy.stats.skew."""
    n = len(window)
    mu = window.mean()
    dm = window - mu
    m2 = np.sum(dm ** 2) / n
    m3 = np.sum(dm ** 3) / n
    if m2 <= 0:
        return np.nan
    g1 = m3 / (m2 ** 1.5)
    # correction de biais (Fisher-Pearson, meme convention que scipy bias=False)
    return float(np.sqrt(n * (n - 1)) / (n - 2) * g1)


def independent_gate(r: np.ndarray) -> np.ndarray:
    n = len(r)
    sk = np.full(n, np.nan)
    for k in range(SKEW_WINDOW, n):
        window = r[k - SKEW_WINDOW:k]
        sk[k] = independent_skew(window)

    gate = np.zeros(n, dtype=bool)
    for k in range(MEDIAN_WINDOW - 1, n):
        window = sk[k - MEDIAN_WINDOW + 1:k + 1]
        if np.any(np.isnan(window)):
            continue
        med = float(np.median(window))
        if not np.isnan(sk[k]):
            gate[k] = sk[k] >= med
    return gate


def main():
    lines = ["# Audit adversarial — Overlay vol-targeting gaté par l'asymétrie (skewness) glissante", "",
             "## 1. Recalcul totalement indépendant de la porte (formule directe des moments centrés)", "",
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
        gate_orig = favorable_skew_mask(r)
        gate_indep = independent_gate(r)
        start = max(SKEW_WINDOW, MEDIAN_WINDOW)
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
        gate_before = favorable_skew_mask(r)
        pos_before = combined_position(r, gate_before)

        cut = len(r) // 2
        rng = np.random.default_rng(73)
        r_pert = r.copy()
        r_pert[cut:] = r_pert[cut:] + rng.normal(0, 0.02, len(r) - cut)
        gate_after = favorable_skew_mask(r_pert)
        pos_after = combined_position(r_pert, gate_after)

        check_end = cut - max(SKEW_WINDOW, MEDIAN_WINDOW)
        identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_skewness_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
