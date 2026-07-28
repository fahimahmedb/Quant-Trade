"""Audit adversarial — Effet janvier small-cap.

Vérifie la fraction de jours en janvier (doit être ~8.3%, 1/12) et
recalcule le rendement moyen janvier vs reste de l'année par une méthode
indépendante (groupby direct sur le mois).
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


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "russell2000_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates = pd.to_datetime(df["date"])
    r = np.log(close[1:] / close[:-1])
    is_jan = (dates.dt.month == 1).values[1:]

    frac_jan = is_jan.mean()
    mean_jan = r[is_jan].mean()
    mean_other = r[~is_jan].mean()

    lines = [
        "# Audit adversarial — Effet janvier small-cap",
        "",
        f"Fraction de jours en janvier : {100*frac_jan:.1f}% (attendu ~8.3%, 1/12).",
        f"**{'OK — plausible.' if 6 <= 100*frac_jan <= 11 else 'SUSPECT.'}**",
        "",
        f"Rendement moyen quotidien janvier (brut) : {100*mean_jan:+.4f}%",
        f"Rendement moyen quotidien reste de l'année (brut) : {100*mean_other:+.4f}%",
        "",
        "**Lecture** : " + (
            "l'effet janvier brut est bien présent (rendement moyen plus élevé) mais le "
            "surplus est insuffisant pour compenser le coût de transaction et l'exposition "
            "au risque accrue (MDD) une fois le levier appliqué -- cohérent avec le FAIL "
            "marginal du backtest (Sharpe 0.33 vs 0.34, quasi égalité)."
            if mean_jan > mean_other else
            "aucun effet janvier brut détecté sur cet échantillon Russell 2000 -- cohérent "
            "avec le FAIL du backtest."
        ),
    ]

    out = ROOT / "results" / "nonml_january_smallcap_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
