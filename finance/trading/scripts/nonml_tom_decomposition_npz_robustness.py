"""Robustesse (7a) — la conclusion du #452 tient-elle hors d'un seul chiffre ?

Ce n'est **PAS un retuning** : ni la strategie ni le seuil du balayage ne
changent. Le #452 conclut que la variante A et le #8 ne sont pas
interchangeables (correlation +0,963 < 0,9999). Deux perturbations declarees
AVANT execution :

1. le **seuil** de quasi-doublon, desserre par ordres de grandeur ;
2. la **periode** — la correlation tient-elle par sous-echantillon, ou n'est-elle
   elevee que grace a un regime particulier ?
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import nonml_pnl_duplicate_sweep_backtest as sw  # noqa: E402

OUT = RESULTS / "nonml_tom_decomposition_npz_robustness.md"

SEUILS = [0.9999, 0.999, 0.99, 0.98, 0.95]     # declares avant execution
N_TRANCHES = 4                                  # declare avant execution


def main():
    a, _ = sw.net_pnl(np.load(RESULTS / "nonml_tom_decomposition_overlay_pnl.npz",
                              allow_pickle=True))
    h, _ = sw.net_pnl(np.load(RESULTS / "nonml_tom_overlay_pnl.npz", allow_pickle=True))
    a, h = np.asarray(a, float), np.asarray(h, float)
    corr = float(np.corrcoef(a, h)[0, 1])

    L = ["# Robustesse — la conclusion du #452 hors d'un seul chiffre", ""]
    L.append("**Étape 7a. Ce n'est pas un retuning** : ni la stratégie ni le seuil du")
    L.append("balayage ne changent. Les deux grilles étaient fixées avant exécution.")
    L.append("")
    L.append(f"Corrélation mesurée au #452 entre la variante A et le #8 : **{corr:+.6f}**.")
    L.append("")

    L.append("## Perturbation 1 — le seuil de quasi-doublon")
    L.append("")
    L.append("Une perturbation de ±20 % n'a pas de sens sur une corrélation (0,9999 × 1,2 >")
    L.append("1). La perturbation pertinente est de **desserrer** le seuil : cela rend la")
    L.append("conclusion « les deux ne sont pas interchangeables » **plus difficile** à tenir.")
    L.append("")
    L.append("| Seuil | Les deux séries seraient-elles appariées ? |")
    L.append("|---|---|")
    for s in SEUILS:
        L.append(f"| **{s}** | {'**OUI — appariées**' if corr >= s else 'non'} |")
    L.append("")
    bascule = next((s for s in SEUILS if corr >= s), None)
    if bascule is None:
        L.append("La conclusion tient sur **toute** la grille : même à un seuil aussi lâche")
        L.append(f"que **{SEUILS[-1]}**, les deux séries ne sont pas appariées.")
    else:
        L.append(f"**La conclusion bascule à {bascule}.** À ce seuil, le balayage les")
        L.append("apparierait. Le seuil du dépôt reste **0,9999** et n'est pas touché : ce")
        L.append("tableau dit seulement à quelle distance du verdict on se trouve.")
    L.append("")

    L.append("## Perturbation 2 — la période")
    L.append("")
    L.append(f"La corrélation d'ensemble pourrait masquer un régime. Découpage en")
    L.append(f"**{N_TRANCHES} tranches** de longueur égale, déclaré avant exécution :")
    L.append("")
    L.append("| Tranche | Séances | Corrélation |")
    L.append("|---|---|---|")
    bornes = np.linspace(0, len(a), N_TRANCHES + 1).astype(int)
    cs = []
    for i in range(N_TRANCHES):
        s, e = bornes[i], bornes[i + 1]
        sub_a, sub_h = a[s:e], h[s:e]
        c = (float(np.corrcoef(sub_a, sub_h)[0, 1])
             if len(sub_a) > 2 and sub_a.std() > 0 and sub_h.std() > 0 else float("nan"))
        cs.append(c)
        L.append(f"| {i + 1} | {e - s} | {c:+.6f} |")
    L.append("")
    fini = [c for c in cs if np.isfinite(c)]
    if fini:
        L.append(f"- minimum : **{min(fini):+.6f}** — maximum : **{max(fini):+.6f}**")
        L.append("")
        if max(fini) < sw.CORR_THRESHOLD:
            L.append("**Aucune tranche n'atteint le seuil.** La conclusion du #452 ne repose")
            L.append("pas sur un régime particulier : sur chaque quart de l'échantillon, les")
            L.append("deux séries restent distinctes.")
        else:
            L.append("**Au moins une tranche atteint le seuil** : sur cette période, les deux")
            L.append("séries seraient appariées. Rapporté tel quel — la conclusion d'ensemble")
            L.append("tient, mais elle n'est pas uniforme dans le temps.")
    L.append("")

    L.append("## Ce que cette robustesse ne montre pas")
    L.append("")
    L.append("Elle porte sur la **comparaison de deux séries**, pas sur la valeur de la")
    L.append("stratégie. Que la variante A soit distincte du #8 ne dit **rien** de sa")
    L.append("rentabilité : son PASS reste celui de son propre rapport, avec ses propres")
    L.append("réserves. Ce cycle n'a jamais prétendu la valider.")
    L.append("")

    L.append("")
    L.append("> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date")
    L.append("> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,")
    L.append("> et ce n'est pas une péremption de résultat (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
