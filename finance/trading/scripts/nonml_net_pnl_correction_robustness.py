"""Robustesse de la conclusion du #445 — plateau, pas pic isole.

Etape 7a : la conclusion « la correction ne deplace aucun appariement » a ete
etablie au seuil de correlation du balayage (0,9999). Est-elle un artefact de
ce seuil ?

Ce n'est **PAS un retuning** : le seuil du balayage reste 0,9999, inchange. On
verifie seulement que la conclusion tient sur une grille de seuils voisins.
Aucun resultat n'est reconsidere en fonction de ce que la grille montre.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from nonml_net_pnl_correction_backtest import (  # noqa: E402
    collect, net_pnl_avant, pairs_and_groups)
import nonml_pnl_duplicate_sweep_backtest as sw  # noqa: E402

OUT = RESULTS / "nonml_net_pnl_correction_robustness.md"

# Grille declaree AVANT execution. 0,9999 est le seuil du balayage ; les autres
# descendent d'ordres de grandeur, la seule perturbation qui ait un sens pour
# une correlation (0,9999 x 1,2 > 1 n'existe pas).
GRILLE = [0.9999, 0.999, 0.99, 0.95, 0.90]


def groups_at(series, thr):
    """Appariements au seuil `thr`, en reutilisant la logique du balayage."""
    old = sw.CORR_THRESHOLD
    try:
        sw.CORR_THRESHOLD = thr
        return pairs_and_groups(series)
    finally:
        sw.CORR_THRESHOLD = old


def main():
    before, _ = collect(net_pnl_avant)
    after, _ = collect(sw.net_pnl)

    rows = []
    for thr in GRILLE:
        gb, eb, qb = groups_at(before, thr)
        ga, ea, qa = groups_at(after, thr)
        rows.append((thr, len(gb), len(ga), gb == ga, eb == ea, qb == qa,
                     len(qb), len(qa)))

    tous = all(r[3] and r[4] and r[5] for r in rows)

    L = ["# Robustesse — la conclusion du #445 tient-elle hors du seuil du balayage ?", ""]
    L.append("**Étape 7a. Ce n'est pas un retuning.** Le seuil du balayage reste **0,9999**,")
    L.append("inchangé par ce rapport. On vérifie seulement que la conclusion « la correction")
    L.append("ne déplace aucun appariement » n'est pas un artefact de ce seuil précis.")
    L.append("")
    L.append("La grille a été fixée **avant exécution**. Une perturbation de ±20 % n'a pas de")
    L.append("sens sur une corrélation (0,9999 × 1,2 > 1) : la perturbation pertinente est de")
    L.append("**desserrer** le seuil par ordres de grandeur, ce qui augmente le nombre")
    L.append("d'appariements et rend donc la conclusion **plus difficile** à tenir.")
    L.append("")
    L.append("| Seuil | Groupes avant | Groupes après | Groupes identiques | Paires exactes id. | Paires quasi id. | quasi (av./ap.) |")
    L.append("|---|---|---|---|---|---|---|")
    for thr, nb, na, gsame, esame, qsame, nqb, nqa in rows:
        mark = " *(seuil du balayage)*" if thr == 0.9999 else ""
        L.append(f"| **{thr}**{mark} | {nb} | {na} | {'oui' if gsame else '**NON**'} | "
                 f"{'oui' if esame else '**NON**'} | {'oui' if qsame else '**NON**'} | "
                 f"{nqb} / {nqa} |")
    L.append("")

    if tous:
        L.append("## Plateau, pas pic")
        L.append("")
        L.append("Sur **toute** la grille, la correction laisse les appariements inchangés —")
        L.append("y compris aux seuils desserrés, où le balayage apparie beaucoup plus de")
        L.append("paires et où un déplacement aurait donc été plus probable.")
        L.append("")
        L.append("La conclusion du #445 ne dépend pas du seuil : elle tient parce que la série")
        L.append("corrigée n'a **qu'une seule** série de même longueur dans tout le dépôt, avec")
        L.append("une corrélation de **+0,017** — très loin de n'importe quel seuil plausible.")
    else:
        L.append("## La conclusion ne tient pas partout")
        L.append("")
        L.append("Au moins un seuil de la grille déplace un appariement. **Rapporté tel quel** :")
        for thr, nb, na, gsame, esame, qsame, _, _ in rows:
            if not (gsame and esame and qsame):
                L.append(f"- seuil **{thr}** : groupes {nb} → {na}, "
                         f"exactes identiques : {esame}, quasi identiques : {qsame}")
        L.append("")
        L.append("Aucun ajustement n'en est tiré : le seuil du balayage reste 0,9999, et le")
        L.append("verdict du #445 reste celui qui a été pré-enregistré.")
    L.append("")

    L.append("## Ce que ce rapport ne montre pas")
    L.append("")
    L.append("Il perturbe **un** paramètre — le seuil de corrélation. La conclusion dépend")
    L.append("aussi du filtre de **longueur égale** (deux séries de tailles différentes ne")
    L.append("sont jamais comparées), qui n'est pas un seuil réglable mais une règle du")
    L.append("balayage. C'est elle, plus que le seuil, qui isole la série corrigée.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
