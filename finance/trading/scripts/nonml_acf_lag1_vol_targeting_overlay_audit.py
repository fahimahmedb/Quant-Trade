"""Audit adversarial — Overlay vol-targeting gaté par l'ACF lag-1
glissante.

Recalcul totalement indépendant (autocorrélation recalculée par boucle
explicite, médiane par tri manuel) et test anti-lookahead.
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
from nonml_acf_lag1_vol_targeting_overlay_backtest import (  # noqa: E402
    trending_acf1_mask, combined_position, ACF_WINDOW, MEDIAN_WINDOW, MARKETS,
)


def manual_median(window: np.ndarray) -> float:
    s = np.sort(window)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return float(s[mid])
    return float((s[mid - 1] + s[mid]) / 2.0)


def manual_acf1(window: np.ndarray) -> float:
    n = len(window)
    mu = sum(window) / n
    dm = [v - mu for v in window]
    num = sum(dm[i] * dm[i - 1] for i in range(1, n))
    den = sum(v * v for v in dm)
    if den <= 0:
        return float("nan")
    return num / den


def independent_gate(r: np.ndarray) -> np.ndarray:
    n = len(r)
    acf1 = np.full(n, np.nan)
    for k in range(ACF_WINDOW, n):
        window = r[k - ACF_WINDOW:k].tolist()
        acf1[k] = manual_acf1(window)

    gate = np.zeros(n, dtype=bool)
    for k in range(MEDIAN_WINDOW - 1, n):
        w = acf1[k - MEDIAN_WINDOW + 1:k + 1]
        if np.any(np.isnan(w)):
            continue
        med = manual_median(w)
        if not np.isnan(acf1[k]):
            gate[k] = acf1[k] >= med
    return gate


def main():
    lines = ["# Audit adversarial — Overlay vol-targeting gaté par l'ACF lag-1 glissante", "",
             "## 1. Recalcul totalement indépendant (autocorrélation par boucle explicite, médiane par tri manuel)", "",
             "| Marché | Désaccords porte (hors marge de fenêtre) | Séances comparées |",
             "|---|---|---|"]
    all_ok = True
    start = ACF_WINDOW + MEDIAN_WINDOW
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

        gate_orig = trending_acf1_mask(r)
        gate_indep = independent_gate(r)
        n_diff = int(np.sum(gate_orig[start:] != gate_indep[start:]))
        n_total = len(gate_orig) - start
        all_ok &= (n_diff == 0)
        lines.append(f"| {name} | {n_diff} | {n_total} |")

    lines.append("")
    lines.append(f"**{'OK — porte confirmée par recalcul totalement indépendant.' if all_ok else 'Désaccords détectés.'}**")

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
        gate_before = trending_acf1_mask(r)
        pos_before = combined_position(r, gate_before)

        cut = len(r) // 2
        rng = np.random.default_rng(73)
        r_pert = r.copy()
        r_pert[cut:] = r_pert[cut:] + rng.normal(0, 0.02, len(r) - cut)
        gate_after = trending_acf1_mask(r_pert)
        pos_after = combined_position(r_pert, gate_after)

        check_end = cut - start
        if check_end < 10:
            lines.append(f"| {name} | (fenêtre trop courte pour tester) |")
            continue
        identical = bool(np.allclose(pos_before[start:start + check_end], pos_after[start:start + check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_acf_lag1_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
