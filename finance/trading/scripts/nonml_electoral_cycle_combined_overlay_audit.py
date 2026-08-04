"""Audit indépendant — cycle #179 (cycle électoral combiné).

Les masques individuels (`preelection_mask` du #30, `midterm_mask` du
#176) ont déjà chacun leur audit dédié. Ce qui est NOUVEAU ici et doit
être vérifié : la COMBINAISON des deux masques ne se chevauche jamais
(aucune année ne peut être à la fois pré-électorale ET mid-term) et la
position résultante est exactement celle attendue par construction.

1. Preuve arithmétique : `preelection_mask` marque `(année+1)%4==0`
   c'est-à-dire `année%4==3` ; `midterm_mask` marque `année%4==2`. Ces
   deux conditions sont mutuellement exclusives par construction (un
   reste modulo 4 ne peut valoir 3 et 2 simultanément) — vérifié ici par
   énumération exhaustive des 4 restes possibles, pas seulement par
   l'assertion runtime du backtest.
2. Recalcul indépendant de la position combinée (boucle explicite
   année par année) et comparaison à la construction vectorisée du
   backtest.
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
from nonml_midterm_election_overlay_backtest import CUT, midterm_mask  # noqa: E402
from nonml_electoral_cycle_combined_overlay_backtest import CAP, MARKETS  # noqa: E402


def independent_position(dates: pd.Series) -> np.ndarray:
    years = pd.to_datetime(dates).dt.year.values
    pos = np.empty(len(years))
    for i, y in enumerate(years):
        r = y - 4 * (y // 4)
        if r == 3:      # (annee+1)%4==0 <=> annee%4==3
            pos[i] = CAP
        elif r == 2:
            pos[i] = CUT
        else:
            pos[i] = 1.0
    return pos


def main():
    lines = [
        "# Audit indépendant — cycle #179 (cycle électoral combiné)",
        "",
        "## 1. Preuve d'exclusivité mutuelle (énumération exhaustive)",
        "",
        "| année % 4 | pré-électorale ((année+1)%4==0) | mid-term (année%4==2) |",
        "|---|---|---|",
    ]
    all_ok = True
    for r in range(4):
        pre = ((r + 1) % 4) == 0
        mid = (r == 2)
        overlap = pre and mid
        all_ok &= not overlap
        lines.append(f"| {r} | {'OUI' if pre else 'non'} | {'OUI' if mid else 'non'} |")
    lines += [
        "",
        f"**Aucun chevauchement possible pour aucun des 4 restes : "
        f"{'CONFIRMÉ' if all_ok else 'ÉCHEC'}.**",
        "",
        "## 2. Recalcul indépendant de la position combinée",
        "",
    ]

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        df = load_ohlc(str(path))
        quality_report(df)

        pre_mask = preelection_mask(df["date"])
        mid_mask = midterm_mask(df["date"])
        pos_fast = np.ones(len(df))
        pos_fast[pre_mask] = CAP
        pos_fast[mid_mask] = CUT

        pos_slow = independent_position(df["date"])
        identical = bool(np.array_equal(pos_fast, pos_slow))
        all_ok &= identical

        lines.append(
            f"- **{name}** : recalcul indépendant (boucle explicite, division/modulo "
            f"manuels) {'IDENTIQUE' if identical else 'DIVERGENT'} à la position du "
            f"backtest ({'OK' if identical else 'ÉCHEC'})."
        )

    lines += [
        "",
        f"**Verdict global : {'CONFORME' if all_ok else 'ÉCHEC'}**.",
    ]

    out = ROOT / "results" / "nonml_electoral_cycle_combined_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
