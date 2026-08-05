"""Audit adversarial — Overlay vol-targeting gaté par le clustering ARCH
glissant.

Recalcul indépendant de la porte (autocorrélation recalculée par formule
directe des covariances/écarts-types, indépendamment de np.corrcoef) et
test anti-lookahead.
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
from nonml_arch_clustering_vol_targeting_overlay_backtest import (  # noqa: E402
    strong_clustering_mask, combined_position, ARCH_WINDOW, MEDIAN_WINDOW, MARKETS,
)


def independent_autocorr(a: np.ndarray, b: np.ndarray) -> float:
    """Recalcul totalement independant de l'autocorrelation a retard 1
    par formule directe (covariance/produit des ecarts-types), sans
    passer par np.corrcoef."""
    n = len(a)
    mu_a, mu_b = a.mean(), b.mean()
    cov = np.sum((a - mu_a) * (b - mu_b)) / (n - 1)
    sd_a = np.sqrt(np.sum((a - mu_a) ** 2) / (n - 1))
    sd_b = np.sqrt(np.sum((b - mu_b) ** 2) / (n - 1))
    if sd_a == 0 or sd_b == 0:
        return np.nan
    return float(cov / (sd_a * sd_b))


def independent_gate(r: np.ndarray) -> np.ndarray:
    r2 = r ** 2
    n = len(r2)
    stat = np.full(n, np.nan)
    for k in range(ARCH_WINDOW, n):
        window = r2[k - ARCH_WINDOW:k]
        stat[k] = independent_autocorr(window[:-1], window[1:])

    gate = np.zeros(n, dtype=bool)
    for k in range(MEDIAN_WINDOW - 1, n):
        window = stat[k - MEDIAN_WINDOW + 1:k + 1]
        if np.any(np.isnan(window)):
            continue
        med = float(np.median(window))
        if not np.isnan(stat[k]):
            gate[k] = stat[k] >= med
    return gate


def main():
    start = max(ARCH_WINDOW, MEDIAN_WINDOW)
    lines = ["# Audit adversarial — Overlay vol-targeting gaté par le clustering ARCH glissant", "",
             "## 1. Recalcul totalement indépendant de la porte (formule directe covariance/écarts-types)", "",
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
        gate_orig = strong_clustering_mask(r)
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
        gate_before = strong_clustering_mask(r)
        pos_before = combined_position(r, gate_before)

        cut = len(r) // 2
        rng = np.random.default_rng(73)
        r_pert = r.copy()
        r_pert[cut:] = r_pert[cut:] + rng.normal(0, 0.02, len(r) - cut)
        gate_after = strong_clustering_mask(r_pert)
        pos_after = combined_position(r_pert, gate_after)

        check_end = cut - start
        identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_arch_clustering_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
