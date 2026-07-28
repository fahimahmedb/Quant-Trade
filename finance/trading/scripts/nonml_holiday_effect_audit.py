"""Audit adversarial — Effet pré/post jour férié.

Vérifie que la détection data-driven des jours fériés fonctionne
correctement sur un cas connu (ex. Thanksgiving/Noël sur NDX) et que le
taux de jours fériés détectés par an est cohérent avec le nombre réel de
jours fériés boursiers US (~9-10/an).
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
from nonml_holiday_effect_backtest import holiday_masks  # noqa: E402


def main():
    lines = ["# Audit adversarial — Effet pré/post jour férié", ""]

    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    is_pre, is_post = holiday_masks(df["date"])
    dates = pd.to_datetime(df["date"])

    # nombre de feries detectes par an
    years = dates.dt.year
    n_years = years.nunique()
    n_detected = is_pre.sum()  # une pre-seance par ferie detecte
    lines.append("## 1. Cohérence du nombre de fériés détectés par an (NDX)")
    lines.append("")
    lines.append(f"{n_detected} jours fériés détectés sur {n_years} années "
                 f"({n_detected/n_years:.1f}/an) — le calendrier boursier US compte "
                 "typiquement 9-10 jours fériés/an (NYSE/Nasdaq).")
    plausible = 6 <= (n_detected / n_years) <= 12
    lines.append(f"**{'OK — ordre de grandeur plausible.' if plausible else 'SUSPECT — ordre de grandeur hors plage attendue, à investiguer.'}**")
    lines.append("")

    # verification sur un cas connu : Thanksgiving (4e jeudi de novembre, marche ferme)
    lines.append("## 2. Vérification sur un cas connu (Thanksgiving)")
    lines.append("")
    thanksgiving_years_checked = 0
    thanksgiving_detected = 0
    for y in sorted(years.unique()):
        if dates[(dates.dt.year == y) & (dates.dt.month == 11)].empty:
            continue
        # bug trouve et corrige : calculer le "4e jeudi" a partir du calendrier de
        # SEANCES (qui n'inclut PAS Thanksgiving, justement ferme) donnait le mauvais
        # jeudi -- il faut le calendrier CIVIL complet, independant des donnees testees.
        nov_calendar = pd.date_range(f"{y}-11-01", f"{y}-11-30", freq="D")
        thursdays = nov_calendar[nov_calendar.dayofweek == 3]
        if len(thursdays) < 4:
            continue
        fourth_thursday = thursdays[3]
        thanksgiving_years_checked += 1
        # la seance juste avant Thanksgiving (marche ferme ce jour) doit etre marquee "pre"
        idx_before = dates[dates < fourth_thursday].index
        if len(idx_before) == 0:
            continue
        i = idx_before[-1]
        if is_pre[i]:
            thanksgiving_detected += 1

    lines.append(f"Thanksgiving détecté comme jour férié (séance précédente marquée 'pré-férié') "
                 f"{thanksgiving_detected}/{thanksgiving_years_checked} années vérifiées.")
    ok2 = thanksgiving_years_checked > 0 and thanksgiving_detected / thanksgiving_years_checked > 0.9
    lines.append(f"**{'OK — détection fiable sur ce cas connu.' if ok2 else 'À vérifier manuellement.'}**")

    out = ROOT / "results" / "nonml_holiday_effect_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
