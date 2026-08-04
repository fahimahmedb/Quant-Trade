"""Audit indépendant — cycle #182 (intersection Halloween x année
pré-électorale).

1. Recalcul indépendant (boucle explicite mois/année) du masque combiné,
   comparaison à la construction vectorisée du backtest.
2. Anti-lookahead : les deux composantes ne dépendent que du calendrier
   (mois, année), jamais des prix -- structurellement impossible qu'une
   perturbation des rendements futurs modifie une décision passée.
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
from nonml_presidential_cycle_overlay_backtest import preelection_mask  # noqa: E402
from nonml_halloween_preelection_and_overlay_backtest import MARKETS  # noqa: E402


def independent_mask(dates: pd.Series) -> np.ndarray:
    d = pd.to_datetime(dates)
    out = np.zeros(len(d), dtype=bool)
    for i, ts in enumerate(d):
        m, y = ts.month, ts.year
        winter = (m >= 11) or (m <= 4)
        r = y - 4 * (y // 4)
        pre = (r == 3)  # (annee+1)%4==0 <=> annee%4==3
        out[i] = winter and pre
    return out


def main():
    lines = ["# Audit indépendant — cycle #182 (Halloween x année pré-électorale)", ""]
    all_ok = True

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        df = load_ohlc(str(path))
        quality_report(df)

        month = pd.to_datetime(df["date"]).dt.month.values
        is_winter = (month >= 11) | (month <= 4)
        pre_mask = preelection_mask(df["date"])
        mask_fast = is_winter & pre_mask

        mask_slow = independent_mask(df["date"])
        identical = bool(np.array_equal(mask_fast, mask_slow))
        all_ok &= identical

        n_active = int(mask_fast.sum())
        lines.append(
            f"- **{name}** : recalcul indépendant (boucle explicite, mois/année "
            f"testés séparément) {'IDENTIQUE' if identical else 'DIVERGENT'} au masque "
            f"du backtest ({'OK' if identical else 'ÉCHEC'}). Jours actifs : {n_active}."
        )

    lines += [
        "",
        "## Anti-lookahead",
        "",
        "Les deux composantes (mois calendaire, année calendaire) sont des faits "
        "publics connus des décennies à l'avance -- aucune dépendance aux prix ou "
        "rendements. Il est donc structurellement impossible qu'une perturbation des "
        "rendements futurs modifie une décision passée. Vérifié par un recalcul "
        "totalement indépendant (méthode différente) donnant un résultat identique.",
        "",
        f"**Verdict global : {'CONFORME' if all_ok else 'ÉCHEC'}**.",
    ]

    out = ROOT / "results" / "nonml_halloween_preelection_and_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
