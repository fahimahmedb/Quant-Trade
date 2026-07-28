"""Audit adversarial — Effet tournant de mois.

Recalcul indépendant du masque ToM par une méthode différente (offsets de
jours de bourse via pandas, pas un groupby+slicing) pour vérifier
l'absence de bug d'indexation (ex. décalage de 1 jour, mauvaise gestion
du premier/dernier mois de l'échantillon).
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

LAST_N_DAYS = 4
FIRST_N_DAYS = 3

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def tom_mask_v1(dates: pd.Series) -> np.ndarray:
    """Copie exacte de la methode du backtest principal (groupby + slicing)."""
    df = pd.DataFrame({"date": pd.to_datetime(dates)})
    df["ym"] = df["date"].dt.to_period("M")
    mask = np.zeros(len(df), dtype=bool)
    for _, idx in df.groupby("ym").groups.items():
        idx = list(idx)
        for i in idx[-LAST_N_DAYS:]:
            mask[i] = True
        for i in idx[:FIRST_N_DAYS]:
            mask[i] = True
    return mask


def tom_mask_v2_independent(dates: pd.Series) -> np.ndarray:
    """Methode INDEPENDANTE : pour chaque jour, compte son rang depuis la
    fin du mois (calcule via un groupby DIFFERENT : rank descendant) et son
    rang depuis le debut du mois (rank ascendant), sans slicing de liste."""
    df = pd.DataFrame({"date": pd.to_datetime(dates)})
    df["ym"] = df["date"].dt.to_period("M")
    df["rank_asc"] = df.groupby("ym").cumcount() + 1
    df["rank_desc"] = df.groupby("ym")["date"].transform(lambda s: len(s)) - df["rank_asc"] + 1
    mask = (df["rank_asc"] <= FIRST_N_DAYS) | (df["rank_desc"] <= LAST_N_DAYS)
    return mask.values


def main():
    lines = [
        "# Audit adversarial — Effet tournant de mois",
        "",
        "## Vérification de cohérence (deux méthodes indépendantes de calcul du masque ToM)",
        "",
        "| Marché | Écart (nb jours différents) | Identique ? |",
        "|---|---|---|",
    ]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        m1 = tom_mask_v1(df["date"])
        m2 = tom_mask_v2_independent(df["date"])
        diff = int((m1 != m2).sum())
        all_ok &= (diff == 0)
        lines.append(f"| {name} | {diff} | {'OUI' if diff == 0 else 'NON'} |")

    lines.append("")
    lines.append(f"**{'OK — deux méthodes indépendantes concordent parfaitement (aucun bug d’indexation détecté).' if all_ok else 'ÉCHEC — les deux méthodes divergent, bug à corriger avant toute conclusion.'}**")

    out = ROOT / "results" / "nonml_turn_of_month_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
