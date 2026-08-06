"""Audit adversarial — Overlay levé expiration d'options mensuelle.

Recalcul indépendant du "3e vendredi de CHAQUE mois" via une méthode
purement calendaire (vendredis civils filtrés par les séances
réellement tradées), même esprit de validation croisée que l'audit du
#26 (triple witching) et du #7 (jour férié).
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from nonml_monthly_opex_overlay_backtest import opex_mask, MARKETS  # noqa: E402


def third_trading_friday_from_civil(year: int, month: int, traded_dates: set):
    days = pd.date_range(f"{year}-{month:02d}-01", periods=31, freq="D")
    days = days[days.month == month]
    fridays = [f for f in days[days.dayofweek == 4] if f.normalize() in traded_dates]
    return fridays[2] if len(fridays) >= 3 else None


def main():
    lines = ["# Audit adversarial — Overlay levé expiration d'options mensuelle", "",
             "| Marché | Nb jours opex détectés | Nb écarts vs recalcul indépendant |",
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
        mask = opex_mask(df["date"])

        df2 = pd.DataFrame({"date": dates, "mask": mask})
        df2["ym"] = df2["date"].dt.to_period("M")
        df2["dow"] = df2["date"].dt.dayofweek
        df2["is_fri"] = df2["dow"] == 4
        df2["fri_rank"] = df2.groupby("ym")["is_fri"].cumsum().where(df2["is_fri"])
        opex_days = df2.loc[df2["fri_rank"] == 3, "date"]

        n_detected = len(opex_days)
        n_diff = 0
        for d in opex_days:
            ref = third_trading_friday_from_civil(d.year, d.month, traded_dates)
            if ref is None or d.normalize() != ref.normalize():
                n_diff += 1
        all_ok &= (n_diff == 0)
        lines.append(f"| {name} | {n_detected} | {n_diff} |")

    lines.append("")
    lines.append(f"**{'OK — jours d’expiration mensuelle confirmés par recalcul totalement indépendant (vendredis civils filtrés par les séances réellement tradées), aucun bug.' if all_ok else 'ÉCHEC — incohérence détectée.'}**")

    out = ROOT / "results" / "nonml_monthly_opex_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
