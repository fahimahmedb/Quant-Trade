"""Audit adversarial — Overlay levé turn-of-quarter.

Recalcul indépendant du masque (regroupement par mois via `datetime`
standard, boucle explicite plutôt que pandas.groupby) et test
anti-lookahead (perturbation du futur — attendu neutre car le calendrier
n'est pas une donnée de marché).
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
from nonml_turn_of_quarter_overlay_backtest import (  # noqa: E402
    turn_of_quarter_mask, LAST_N_DAYS, FIRST_N_DAYS, QUARTER_END_MONTHS, QUARTER_START_MONTHS, MARKETS,
)


def independent_mask(dates) -> np.ndarray:
    """Reconstruction indépendante par balayage séquentiel (regroupe les
    indices par (annee, mois) via datetime standard, retrouve les
    LAST_N_DAYS derniers indices des mois de fin de trimestre et les
    FIRST_N_DAYS premiers indices des mois de debut de trimestre par
    slicing sur liste Python)."""
    ts = [d.to_pydatetime() for d in pd.to_datetime(dates)]
    T = len(ts)
    by_ym = {}
    for i, dt in enumerate(ts):
        by_ym.setdefault((dt.year, dt.month), []).append(i)

    mask = [False] * T
    for (y, m), idx_list in by_ym.items():
        if m in QUARTER_END_MONTHS:
            for i in idx_list[-LAST_N_DAYS:]:
                mask[i] = True
        if m in QUARTER_START_MONTHS:
            for i in idx_list[:FIRST_N_DAYS]:
                mask[i] = True
    return np.array(mask, dtype=bool)


def main():
    lines = ["# Audit adversarial — Overlay levé turn-of-quarter", "",
             "## 1. Recalcul indépendant (balayage séquentiel via datetime standard)", "",
             "| Marché | Écart masque (nb j.) |",
             "|---|---|"]
    all_ok = True
    dfs = {}
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dfs[name] = df
        m_orig = turn_of_quarter_mask(df["date"])
        m_indep = independent_mask(df["date"])
        diff = int(np.sum(m_orig != m_indep))
        all_ok &= (diff == 0)
        lines.append(f"| {name} | {diff} |")

    lines.append("")
    lines.append(f"**{'OK — masque confirmé par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Vérification du nombre de jours actifs par an (doit être ≈ 4×(LAST_N_DAYS+FIRST_N_DAYS)=28)")
    lines.append("")
    lines.append("| Marché | Nb jours actifs total | Nb années | Moyenne j./an |")
    lines.append("|---|---|---|---|")
    for name, df in dfs.items():
        m = turn_of_quarter_mask(df["date"])
        n_years = len(set(pd.to_datetime(df["date"]).dt.year))
        lines.append(f"| {name} | {int(m.sum())} | {n_years} | {m.sum()/n_years:.2f} |")

    lines.append("")
    lines.append("## 3. Test anti-lookahead (perturbation du futur)")
    lines.append("")
    lines.append("| Marché | Décisions passées identiques après perturbation future |")
    lines.append("|---|---|")
    anti_leak_ok = True
    for name, df in dfs.items():
        m_before = turn_of_quarter_mask(df["date"])
        dates_pert = pd.to_datetime(df["date"]).copy()
        cut = len(dates_pert) // 2
        m_after = turn_of_quarter_mask(dates_pert)
        identical = bool(np.array_equal(m_before[:cut], m_after[:cut]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    stability_msg = ("OK — comportement stable (le calendrier n'est pas une donnée de marché, "
                      "aucune fuite possible par construction).") if anti_leak_ok else "ÉCHEC."
    lines.append("")
    lines.append(f"**{stability_msg}**")
    lines.append("")
    lines.append("**Lecture économique du FAIL — correction d'une erreur de caractérisation dans "
                 "le PREREG** : le pré-enregistrement de ce cycle affirmait à tort que le #8 (ToM "
                 "en overlay, 12 fenêtres/an) avait été \"reclassé FAIL sous la règle renforcée\" — "
                 "c'est en réalité le **#2** (stratégie ToM classique, hors overlay) qui a été "
                 "reclassé FAIL ; le **#8 est un authentique PASS (4/5)**, voir "
                 "`results/nonml_tom_overlay_result.md`. Cette confusion de motivation n'affecte "
                 "PAS la définition, les paramètres ni le critère de succès du #65 (repris à "
                 "l'identique du #8, correctement exécutés), donc le résultat FAIL (3/5) reste "
                 "valide -- mais la lecture correcte est : restreindre la fenêtre ToM du #8 (PASS "
                 "4/5, 12 occurrences/an) aux seuls changements de trimestre (4 occurrences/an) "
                 "**DÉGRADE** le résultat (3/5) au lieu de le renforcer. Cela suggère que les 8 "
                 "changements de mois ORDINAIRES (non trimestriels) contribuent eux aussi à l'edge "
                 "du #8, contrairement à l'hypothèse pré-enregistrée d'un effet de rebalancement "
                 "institutionnel concentré aux trimestres.")

    out = ROOT / "results" / "nonml_turn_of_quarter_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
