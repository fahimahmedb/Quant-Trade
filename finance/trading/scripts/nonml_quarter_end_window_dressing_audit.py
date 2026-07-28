"""Audit adversarial — Window Dressing fin de trimestre.

Recalcul indépendant du masque par inspection directe des dates
(dernier jour de bourse de chaque mois de fin de trimestre), pas de
rank groupby, pour vérifier l'absence de bug (notamment aux frontières
d'année comme trouvé au cycle #6).
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
from nonml_quarter_end_window_dressing_backtest import quarter_end_mask, LAST_N_DAYS  # noqa: E402

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def mask_v2_explicit(dates):
    d = pd.to_datetime(pd.Series(dates)).reset_index(drop=True)
    mask = np.zeros(len(d), dtype=bool)
    quarters = sorted(d.dt.to_period("Q").unique())
    for q in quarters:
        idx = d[d.dt.to_period("Q") == q].sort_values().index
        tail = idx[-LAST_N_DAYS:]
        mask[tail] = True
    return mask


def main():
    lines = ["# Audit adversarial — Window Dressing fin de trimestre", "",
             "| Marché | Écart (nb jours) | Identique ? |", "|---|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        m1 = quarter_end_mask(df["date"])
        m2 = mask_v2_explicit(df["date"])
        diff = int((m1 != m2).sum())
        all_ok &= (diff == 0)
        lines.append(f"| {name} | {diff} | {'OUI' if diff == 0 else 'NON'} |")

    lines.append("")
    lines.append(f"**{'OK — deux méthodes indépendantes concordent.' if all_ok else 'ÉCHEC — divergence, bug à corriger.'}**")

    out = ROOT / "results" / "nonml_quarter_end_window_dressing_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
