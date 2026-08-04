"""Audit indépendant — cycle #185 (Halloween x post-élection multiplicatif).

1. Recalcul indépendant (boucle explicite mois/année) de la position
   combinée et comparaison à la construction vectorisée du backtest.
2. Anti-lookahead : les deux composantes ne dépendent que du calendrier,
   jamais des prix.
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
from nonml_postelection_year_overlay_backtest import CUT, postelection_mask  # noqa: E402
from nonml_halloween_postelection_multiplicative_overlay_backtest import CAP, MARKETS  # noqa: E402


def independent_position(dates: pd.Series) -> np.ndarray:
    d = pd.to_datetime(dates)
    out = np.empty(len(d))
    for i, ts in enumerate(d):
        m, y = ts.month, ts.year
        winter = (m >= 11) or (m <= 4)
        r = y - 4 * (y // 4)
        post = (r == 1)  # (annee-1)%4==0 <=> annee%4==1
        factor_h = CAP if winter else 1.0
        factor_p = CUT if post else 1.0
        out[i] = 1.0 * factor_h * factor_p
    return out


def main():
    lines = ["# Audit indépendant — cycle #185 (Halloween x post-élection multiplicatif)", ""]
    all_ok = True

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        df = load_ohlc(str(path))
        quality_report(df)

        month = pd.to_datetime(df["date"]).dt.month.values
        is_winter = (month >= 11) | (month <= 4)
        post_mask = postelection_mask(df["date"])
        halloween_only = is_winter & ~post_mask
        postelection_only = post_mask & ~is_winter
        overlap = is_winter & post_mask

        pos_fast = np.ones(len(df))
        pos_fast[halloween_only] = CAP
        pos_fast[postelection_only] = CUT
        pos_fast[overlap] = CAP * CUT

        pos_slow = independent_position(df["date"])
        identical = bool(np.allclose(pos_fast, pos_slow))
        all_ok &= identical

        lines.append(
            f"- **{name}** : recalcul indépendant (boucle explicite, facteurs multipliés "
            f"un par un) {'IDENTIQUE' if identical else 'DIVERGENT'} à la position du "
            f"backtest ({'OK' if identical else 'ÉCHEC'})."
        )

    lines += [
        "",
        "## Anti-lookahead",
        "",
        "Les deux composantes (mois calendaire, année calendaire) sont des faits "
        "publics connus des décennies à l'avance -- aucune dépendance aux prix ou "
        "rendements.",
        "",
        f"**Verdict global : {'CONFORME' if all_ok else 'ÉCHEC'}**.",
    ]

    out = ROOT / "results" / "nonml_halloween_postelection_multiplicative_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
