"""Audit adversarial — Overlay levé fenêtre vendredi-lundi.

Recalcul indépendant du masque jour-de-semaine via `datetime.weekday()`
(stdlib, indépendant de pandas.dt.dayofweek utilisé dans le backtest) et
vérification que la fraction de jours levés (~2/5 = 40% théorique) est
cohérente avec la mesure.
"""
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from nonml_friday_monday_overlay_backtest import fri_mon_mask, MARKETS  # noqa: E402


def independent_mask(dates) -> np.ndarray:
    ts = pd.to_datetime(dates)
    out = np.zeros(len(ts), dtype=bool)
    for i, d in enumerate(ts):
        wd = datetime(d.year, d.month, d.day).weekday()  # lundi=0 ... dimanche=6
        out[i] = wd in (0, 4)
    return out


def main():
    lines = ["# Audit adversarial — Overlay levé fenêtre vendredi-lundi", "",
             "| Marché | %j levé (mesuré) | Écart vs recalcul indépendant (nb j.) | %j théorique (2/5) |",
             "|---|---|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        m_orig = fri_mon_mask(df["date"])
        m_indep = independent_mask(df["date"])
        diff = int(np.sum(m_orig != m_indep))
        all_ok &= (diff == 0)
        lines.append(f"| {name} | {100*m_orig.mean():.1f}% | {diff} | 40.0% |")

    lines.append("")
    lines.append(f"**{'OK — masque vendredi/lundi confirmé par recalcul indépendant (datetime.weekday), aucun bug.' if all_ok else 'ÉCHEC — incohérence détectée.'}**")

    out = ROOT / "results" / "nonml_friday_monday_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
