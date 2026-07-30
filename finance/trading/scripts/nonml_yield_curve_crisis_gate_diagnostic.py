"""Diagnostic — pourquoi le #126 (S&P 500) échoue le stress de crise là
où le #114 (NDX) réussit (cycle #127, pré-enregistré dans
PREREG_yield_curve_crisis_gate_diagnostic.md). PAS un nouveau backtest.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

CRISIS_WINDOWS = [
    ("Dot-com crash", "2000-01-01", "2002-12-31"),
    ("Crise financière 2008", "2007-10-01", "2009-03-31"),
]

CANDIDATES = {
    "NDX (#114)": "nonml_yield_curve_slope_vol_targeting_overlay_pnl.npz",
    "S&P 500 (#126)": "nonml_yield_curve_slope_sp500_vol_targeting_overlay_pnl.npz",
}


def main():
    lines = ["# Diagnostic — activation de la porte pente-des-taux pendant les crises (NDX vs S&P 500)", "",
             "PAS un nouveau backtest -- recalcul sur les artefacts déjà committés des #114/#126.", ""]

    data = {}
    for name, fname in CANDIDATES.items():
        d = np.load(ROOT / "results" / fname, allow_pickle=True)
        dates = pd.to_datetime(d["dates"])
        pos = d["pos"]
        r = d["r_asset"]
        data[name] = (dates, pos, r)

    for label, d0, d1 in CRISIS_WINDOWS:
        lines.append(f"## {label} ({d0} → {d1})")
        lines.append("")
        lines.append("| Marché | Séances | %activation porte | %activation (pire décile de rendement) |")
        lines.append("|---|---|---|---|")
        for name, (dates, pos, r) in data.items():
            mask = (dates >= pd.Timestamp(d0)) & (dates <= pd.Timestamp(d1))
            n = int(mask.sum())
            if n < 20:
                lines.append(f"| {name} | {n} | hors couverture | -- |")
                continue
            pos_w = pos[mask]
            r_w = r[mask]
            active = pos_w > 1.0
            pct_active = 100 * active.mean()

            thresh = np.percentile(r_w, 10)
            worst_mask = r_w <= thresh
            pct_active_worst = 100 * active[worst_mask].mean() if worst_mask.sum() > 0 else float("nan")

            lines.append(f"| {name} | {n} | {pct_active:.1f}% | {pct_active_worst:.1f}% |")
        lines.append("")

    lines.append("## Interprétation")
    lines.append("")
    lines.append(
        "Si %activation (pire décile) est nettement PLUS ÉLEVÉ sur S&P 500 que sur NDX pendant "
        "ces deux fenêtres, cela confirme mécaniquement que le levier a été appliqué plus souvent "
        "précisément pendant les pires séances sur S&P 500 -- expliquant le MDD dégradé (#126) "
        "malgré un mécanisme et un signal identiques à ceux qui fonctionnent sur NDX (#114). "
        "Ceci documente une explication plausible, pas une preuve de causalité unique -- aucune "
        "correction n'est proposée ici (nécessiterait un nouveau pré-enregistrement séparé)."
    )

    out = ROOT / "results" / "nonml_yield_curve_crisis_gate_diagnostic.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
