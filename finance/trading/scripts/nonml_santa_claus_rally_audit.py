"""Audit adversarial — Santa Claus Rally.

Vérifie spécifiquement le cas limite propre à cette stratégie : la
continuité correcte du masque à travers la frontière d'année (5 derniers
jours de DÉCEMBRE d'une année + 2 premiers jours de JANVIER de l'année
SUIVANTE, deux groupby mensuels différents). Recalcul indépendant par
inspection directe des dates calendaires (mois/jour) plutôt que par rang
groupby, pour vérifier l'absence de bug de frontière.
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
from nonml_santa_claus_rally_backtest import santa_mask as santa_mask_v1  # noqa: E402
from nonml_santa_claus_rally_backtest import LAST_N_DEC, FIRST_N_JAN  # noqa: E402

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def santa_mask_v2_explicit(dates):
    """Methode independante : pour chaque annee presente, prend
    explicitement les N dernieres dates de decembre et les M premieres de
    janvier suivant, par tri direct des dates (pas de groupby/rank)."""
    d = pd.to_datetime(pd.Series(dates)).reset_index(drop=True)
    mask = np.zeros(len(d), dtype=bool)
    years = sorted(d.dt.year.unique())
    for y in years:
        dec_dates = d[(d.dt.year == y) & (d.dt.month == 12)].sort_values()
        tail = dec_dates.iloc[-LAST_N_DEC:] if len(dec_dates) >= 1 else dec_dates
        jan_dates = d[(d.dt.year == y + 1) & (d.dt.month == 1)].sort_values()
        head = jan_dates.iloc[:FIRST_N_JAN] if len(jan_dates) >= 1 else jan_dates
        mask[tail.index] = True
        mask[head.index] = True
    return mask


def main():
    lines = ["# Audit adversarial — Santa Claus Rally", "",
             "## Vérification de la frontière d'année (deux méthodes indépendantes)", "",
             "| Marché | Écart (nb jours) | Identique ? |", "|---|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        m1 = santa_mask_v1(df["date"])
        m2 = santa_mask_v2_explicit(df["date"])
        diff = int((m1 != m2).sum())
        all_ok &= (diff == 0)
        lines.append(f"| {name} | {diff} | {'OUI' if diff == 0 else 'NON'} |")

    lines.append("")
    lines.append(f"**{'OK — méthodes concordantes, frontière décembre/janvier correctement gérée.' if all_ok else 'ÉCHEC — divergence à la frontière d’année, bug à corriger.'}**")
    lines.append("")
    lines.append(
        "**Note méthodologique (généralisable au-delà de ce cycle)** : sous la règle "
        "renforcée (Sharpe ET rendement absolu), toute stratégie investie seulement une "
        "petite fraction de l'année (ici ~7j/252 ≈ 2,8%) est structurellement quasi "
        "incapable de battre le rendement CUMULÉ de Buy&Hold sur un historique long, "
        "simplement parce qu'elle rate presque tout le compounding — indépendamment de "
        "la qualité de l'effet de calendrier lui-même. C'est cohérent avec l'échec "
        "similaire du cycle #2 (tournant de mois, ~33% du temps investi, déjà "
        "insuffisant). Les items #8/#9 du backlog (overlay avec levier au lieu d'être "
        "flat hors fenêtre) adressent structurellement ce problème."
    )

    out = ROOT / "results" / "nonml_santa_claus_rally_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
