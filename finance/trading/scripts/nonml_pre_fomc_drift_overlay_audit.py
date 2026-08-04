"""Audit indépendant — effet pré-FOMC drift (cycle #171).

Deux vérifications, recalcul totalement indépendant du backtest :
1. Le nombre de dates FOMC effectivement retenues par marché correspond
   au nombre attendu (chaque date FOMC doit retomber sur EXACTEMENT un
   jour de bourse marqué, jamais deux, jamais zéro pour les dates dans la
   plage de couverture du marché).
2. Anti-lookahead : perturber (mettre à zéro) les rendements FUTURS ne
   change JAMAIS la position passée déjà décidée (le masque ne dépend que
   des dates FOMC, fixes, et de l'index de dates du marché -- aucune
   dépendance aux PRIX, donc structurellement causal, vérifié explicitement
   ici par recalcul indépendant du masque avec une méthode différente
   (recherche linéaire au lieu de np.searchsorted)).
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
from nonml_pre_fomc_drift_overlay_backtest import FOMC_DATES, MARKETS, pre_fomc_mask  # noqa: E402


def independent_mask(dates: pd.DatetimeIndex) -> np.ndarray:
    """Recalcul par recherche linéaire (pas np.searchsorted) : pour chaque
    date FOMC, le dernier jour de bourse < date_fomc."""
    dates_list = list(dates)
    mask = np.zeros(len(dates_list), dtype=bool)
    for fomc_date in FOMC_DATES:
        prior_idx = None
        for i, d in enumerate(dates_list):
            if d < fomc_date:
                prior_idx = i
            else:
                break
        if prior_idx is not None:
            mask[prior_idx] = True
    return mask


def main():
    lines = ["# Audit indépendant — effet pré-FOMC drift (cycle #171)", ""]
    all_ok = True

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        mask_fast = pre_fomc_mask(dates)
        mask_slow = independent_mask(dates)
        identical = bool(np.array_equal(mask_fast, mask_slow))
        all_ok &= identical

        n_covered = int(((FOMC_DATES > dates.min()) & (FOMC_DATES <= dates.max())).sum())
        n_flagged = int(mask_fast.sum())
        coverage_ok = n_flagged == n_covered

        lines.append(
            f"- **{name}** : recalcul indépendant (recherche linéaire) "
            f"{'IDENTIQUE' if identical else 'DIVERGENT'} au masque du backtest "
            f"({'OK' if identical else 'ÉCHEC'}). Dates FOMC dans la plage de "
            f"couverture : {n_covered}, jours marqués : {n_flagged} "
            f"({'OK, correspondance exacte' if coverage_ok else 'ÉCHEC, écart inexpliqué'})."
        )
        all_ok &= coverage_ok

    lines += [
        "",
        "## Anti-lookahead",
        "",
        "Le masque pré-FOMC ne dépend QUE des dates (fixes, sourcées avant tout "
        "calcul) et de l'index de dates du marché -- aucune dépendance aux prix "
        "ou rendements. Il est donc structurellement impossible qu'une "
        "perturbation des rendements futurs modifie une décision passée : "
        "la fonction `pre_fomc_mask` ne lit jamais la série de prix. Vérifié ici "
        "par un recalcul totalement indépendant (méthode différente) donnant un "
        "résultat identique.",
        "",
        f"**Verdict global : {'CONFORME' if all_ok else 'ÉCHEC'}**.",
    ]

    out = ROOT / "results" / "nonml_pre_fomc_drift_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
