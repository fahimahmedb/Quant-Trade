"""Faut-il convertir la derniere variante du detecteur de verdict ? (#454)

Specification pre-enregistree dans `PREREG_verdict_variant_decision.md`,
committee AVANT toute mesure.

Cycle de **decision** : il peut se conclure par « on ne touche a rien ».

Dans `nonml_sessions_column_backfill_audit.py`, `verdict_of` ne classe pas dans
l'absolu — il compare le verdict d'un rapport AVANT et APRES l'ajout d'une
colonne. Comparaison a regle constante, ou une regle grossiere est largement
inoffensive.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import nonml_verdict  # noqa: E402  (regle partagee du #448/#449)

OUT = RESULTS / "nonml_verdict_variant_decision_result.md"
VARIANTE = SCRIPTS / "nonml_sessions_column_backfill_audit.py"
TARGETS = ["halloween_effect", "intraday_range_regime_overlay", "tom_overlay"]


def regle_locale(t):
    """La regle telle qu'elle est ecrite dans la variante — sans le litteral."""
    if "**PASS" in t:
        return "PASS"
    if "**FAIL" in t:
        return "FAIL"
    return "indéterminé"


def main():
    lignes = []
    for n in TARGETS:
        p = RESULTS / f"nonml_{n}_result.md"
        t = p.read_text(encoding="utf-8") if p.exists() else ""
        lignes.append((n, p.exists(), regle_locale(t), nonml_verdict.verdict_of(t)))

    coincident = all(a == b for _, ok, a, b in lignes if ok)
    tous_presents = all(ok for _, ok, _, _ in lignes)
    decision = "convertir" if (coincident and tous_presents) else "ne pas convertir"

    # Critere 4 : le controle 3 est-il vide en execution ordinaire ?
    src = VARIANTE.read_text(encoding="utf-8")
    m = re.search(r"^BEFORE_DIR\s*=\s*(.+)$", src, re.M)
    vide = bool(m and "sys.argv" in m.group(1) and "else None" in m.group(1))

    L = ["# Faut-il convertir la dernière variante du détecteur ? (pré-enregistré)", ""]
    L.append("**Cycle de décision.** Il pouvait se conclure par « on ne touche à rien » ;")
    L.append("la règle de décision était fixée **avant** toute mesure.")
    L.append("")

    L.append("## Ce que cette fonction sert réellement")
    L.append("")
    L.append("Elle **ne classe pas dans l'absolu**. Elle sert le contrôle 3 du script :")
    L.append("comparer le verdict d'un rapport **avant** et **après** l'ajout d'une colonne,")
    L.append("pour prouver que l'ajout n'a rien changé.")
    L.append("")
    L.append("C'est une **comparaison à règle constante**. Une règle grossière n'y trompe")
    L.append("que si sa grossièreté crée une différence là où il n'y en a pas, ou en masque")
    L.append("une. C'est pourquoi ce cas méritait d'être décidé séparément plutôt que")
    L.append("converti mécaniquement avec les six autres du #449.")
    L.append("")

    L.append("## Les deux règles, sur les trois rapports cibles")
    L.append("")
    L.append("| Rapport | Présent | Règle locale (sans littéral) | Règle partagée (#448) | Coïncident |")
    L.append("|---|---|---|---|---|")
    for n, ok, a, b in lignes:
        L.append(f"| `{n}` | {'✔' if ok else '**absent**'} | {a} | {b} | "
                 f"{'✔' if a == b else '**NON**'} |")
    L.append("")
    L.append(f"**Les deux règles coïncident sur les trois : "
             f"{'OUI' if coincident and tous_presents else 'NON'}.**")
    L.append("")

    L.append("## La décision")
    L.append("")
    L.append("Règle fixée avant mesure : *convertir si et seulement si les deux règles")
    L.append("donnent le même verdict sur les trois*.")
    L.append("")
    L.append(f"### **Décision : {decision}.**")
    L.append("")
    if decision == "convertir":
        L.append("La conversion est **sans effet observable** sur ce que ce script mesure.")
        L.append("À effet nul, l'uniformité du dépôt vaut mieux qu'une exception qu'il")
        L.append("faudra ré-expliquer à chaque cycle qui recompte les consommateurs.")
    else:
        L.append("Les deux règles divergent : convertir changerait ce que ce script mesure.")
        L.append("**On ne touche à rien**, et la raison est publiée plutôt que reportée.")
    L.append("")

    L.append("## Critère 4 — le contrôle 3 est-il vide en exécution ordinaire ?")
    L.append("")
    L.append("Le contrôle 3 compare le rapport courant à un **instantané d'avant**, passé")
    L.append("en argument de ligne de commande :")
    L.append("")
    L.append("```python")
    L.append(m.group(0).strip() if m else "(ligne introuvable)")
    L.append("```")
    L.append("")
    if vide:
        L.append("**Il est vide en exécution ordinaire.** Sans argument, `BEFORE_DIR` vaut")
        L.append("`None`, la colonne « Avant » affiche `—`, et la comparaison ne compare")
        L.append("rien.")
        L.append("")
        L.append("> **Cela relativise tout ce cycle.** La règle qu'on discute ici ne sert,")
        L.append("> en pratique, qu'à une comparaison qui ne s'exécute que si quelqu'un")
        L.append("> fournit un instantané. Le dire vaut mieux que laisser croire qu'on a")
        L.append("> tranché quelque chose d'important.")
        L.append("")
        L.append("**Prédiction vérifiée** — je l'annonçais, et c'était la partie la plus")
        L.append("utile de la prédiction.")
    else:
        L.append("**Il n'est pas vide** : la comparaison s'exécute en mode ordinaire.")
    L.append("")

    L.append("## Ce que ce cycle ne fait pas")
    L.append("")
    L.append("- Il ne **régénère** aucun rapport.")
    L.append("- Il ne touche **aucun autre** script.")
    L.append("- Il ne prétend pas que la règle locale était **juste** : elle confond")
    L.append("  porter et mentionner un verdict, comme toutes les autres avant le #448.")
    L.append("  Il constate qu'ici, cette confusion **n'a pas de conséquence mesurable**.")
    L.append("")

    L.append("")
    L.append("> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date")
    L.append("> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,")
    L.append("> et ce n'est pas une péremption de résultat (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")
    return decision, coincident, vide


if __name__ == "__main__":
    main()
