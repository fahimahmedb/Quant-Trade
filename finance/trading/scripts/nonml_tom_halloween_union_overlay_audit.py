"""Audit adversarial — Overlay levé ToM ∪ Halloween.

Recalcul indépendant de l'union via inclusion-exclusion (|A∪B| = |A|+|B|-|A∩B|)
pour vérifier la cohérence de la fraction de jours levés, et comparaison
aux fractions déjà auditées séparément aux cycles #2/#8 (~33%) et #17 (~49%).
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
from nonml_tom_halloween_union_overlay_backtest import tom_mask, halloween_mask  # noqa: E402

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def main():
    lines = ["# Audit adversarial — Overlay levé ToM ∪ Halloween", "",
             "| Marché | %ToM | %Halloween | %Union (mesurée) | %Union (inclusion-exclusion) | Écart |",
             "|---|---|---|---|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        m_tom = tom_mask(df["date"])
        m_hall = halloween_mask(df["date"])
        m_union = m_tom | m_hall
        m_inter = m_tom & m_hall

        p_tom, p_hall = m_tom.mean(), m_hall.mean()
        p_union_measured = m_union.mean()
        p_union_incl_excl = p_tom + p_hall - m_inter.mean()
        diff = abs(p_union_measured - p_union_incl_excl)
        all_ok &= (diff < 1e-9)

        lines.append(f"| {name} | {100*p_tom:.1f}% | {100*p_hall:.1f}% | {100*p_union_measured:.1f}% | "
                     f"{100*p_union_incl_excl:.1f}% | {diff:.2e} |")

    lines.append("")
    lines.append(f"**{'OK — union cohérente avec inclusion-exclusion, aucun bug de fusion des masques.' if all_ok else 'ÉCHEC — incohérence détectée.'}**")

    out = ROOT / "results" / "nonml_tom_halloween_union_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
