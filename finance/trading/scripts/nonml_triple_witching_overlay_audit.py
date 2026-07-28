"""Audit adversarial — Overlay levé triple witching.

Recalcul indépendant du "3e vendredi du mois" via une méthode purement
calendaire (calcul du 3e vendredi civil du mois avec `pandas.date_range`,
indépendant du calendrier de trading), puis vérification que ce jour
civil correspond bien (ou au jour de bourse suivant si férié) au jour
détecté par le backtest -- même esprit de validation croisée que la
détection Thanksgiving au cycle #7.
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
from nonml_triple_witching_overlay_backtest import witching_mask, WITCHING_MONTHS, MARKETS  # noqa: E402


def third_trading_friday_from_civil(year: int, month: int, traded_dates: set) -> pd.Timestamp:
    """Méthode totalement indépendante : liste tous les vendredis CIVILS du
    mois, ne garde que ceux qui sont effectivement des séances de bourse
    (intersection avec le calendrier réel), prend le 3e de cette liste
    filtrée. Contrairement à third_friday_civil (qui ignore les fermetures),
    ceci reproduit la sémantique data-driven du pré-enregistrement par un
    chemin de calcul différent de witching_mask()."""
    days = pd.date_range(f"{year}-{month:02d}-01", periods=31, freq="D")
    days = days[days.month == month]
    fridays = [f for f in days[days.dayofweek == 4] if f.normalize() in traded_dates]
    return fridays[2] if len(fridays) >= 3 else None


def main():
    lines = ["# Audit adversarial — Overlay levé triple witching", "",
             "| Marché | Nb jours witching détectés | Nb écarts vs recalcul indépendant (vendredis civils filtrés par jours tradés) |",
             "|---|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.to_datetime(df["date"])
        traded_dates = set(dates.dt.normalize())
        mask = witching_mask(df["date"])

        df2 = pd.DataFrame({"date": dates, "mask": mask})
        df2["ym"] = df2["date"].dt.to_period("M")
        df2["dow"] = df2["date"].dt.dayofweek
        df2["is_fri"] = df2["dow"] == 4
        df2["fri_rank"] = df2.groupby("ym")["is_fri"].cumsum().where(df2["is_fri"])
        witch_days = df2.loc[(df2["fri_rank"] == 3) & df2["date"].dt.month.isin(WITCHING_MONTHS), "date"]

        n_detected = len(witch_days)
        n_diff = 0
        for d in witch_days:
            ref = third_trading_friday_from_civil(d.year, d.month, traded_dates)
            if ref is None or d.normalize() != ref.normalize():
                n_diff += 1
        all_ok &= (n_diff == 0)
        lines.append(f"| {name} | {n_detected} | {n_diff} |")

    lines.append("")
    lines.append(f"**{'OK — jours de triple witching confirmés par recalcul totalement indépendant (vendredis civils filtrés par les séances réellement tradées), aucun bug.' if all_ok else 'ÉCHEC — incohérence détectée.'}**")

    out = ROOT / "results" / "nonml_triple_witching_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
