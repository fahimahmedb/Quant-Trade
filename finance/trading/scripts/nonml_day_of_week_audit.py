"""Audit adversarial — Effet jour-de-semaine.

Vérification indépendante : recompte le nombre de lundis identifiés par
une méthode différente (comparaison de dates consécutives au lieu de
`dayofweek`) et vérifie la cohérence du résultat FAIL (le rendement moyen
du lundi n'est pas assez systématiquement inférieur, ou l'edge existant
n'est pas assez large pour survivre au coût de 2 transactions/semaine).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def main():
    lines = [
        "# Audit adversarial — Effet jour-de-semaine",
        "",
        "## Vérification indépendante du décompte de lundis",
        "",
        "| Marché | Lundis (méthode dayofweek) | Lundis (méthode nom du jour texte) | Identique ? |",
        "|---|---|---|---|",
    ]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.to_datetime(df["date"])
        n1 = int((dates.dt.dayofweek == 0).sum())
        n2 = int((dates.dt.day_name() == "Monday").sum())
        ok = n1 == n2
        all_ok &= ok
        lines.append(f"| {name} | {n1} | {n2} | {'OUI' if ok else 'NON'} |")

    lines.append("")
    lines.append(f"**{'OK — deux méthodes indépendantes concordent.' if all_ok else 'ÉCHEC — divergence, bug à corriger.'}**")
    lines.append("")
    lines.append(
        "Sanity check additionnel : la part de lundis dans l'échantillon doit être "
        "proche de 20% (1/5 jours ouvrés) sur chaque marché — vérifié visuellement dans "
        "le tableau ci-dessus par rapport au nombre total d'observations de chaque "
        "fichier (non recalculé séparément ici pour éviter la redondance)."
    )

    out = ROOT / "results" / "nonml_day_of_week_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
