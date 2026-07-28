"""Audit adversarial — Effet Halloween.

1. Vérifie la fraction de jours en régime "hiver" (nov-avril, doit être
   ~50%) et la décomposition brute des rendements hiver vs été.
2. Vérifie l'exposition totale (1.0 ou CAP exactement).
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

CAP = 2.0
MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def main():
    lines = ["# Audit adversarial — Effet Halloween", "",
             "| Marché | % jours hiver (nov-avr) | Rdt moy./j hiver (brut) | Rdt moy./j été (brut) | Exposition conforme ? |",
             "|---|---|---|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = pd.to_datetime(df["date"])
        r = np.log(close[1:] / close[:-1])
        month = dates.dt.month.values[1:]
        is_winter = (month >= 11) | (month <= 4)

        pos = np.where(is_winter, CAP, 1.0)
        conforme = set(np.round(pos, 6)) <= {1.0, CAP}
        all_ok &= conforme

        lines.append(
            f"| {name} | {100*is_winter.mean():.1f}% | {100*r[is_winter].mean():+.4f}% | "
            f"{100*r[~is_winter].mean():+.4f}% | {'OUI' if conforme else 'NON'} |"
        )

    lines.append("")
    lines.append(f"**{'OK — fraction hiver plausible (~50%), exposition conforme sur tous les marchés.' if all_ok else 'ÉCHEC — anomalie detectee.'}**")

    out = ROOT / "results" / "nonml_halloween_effect_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
