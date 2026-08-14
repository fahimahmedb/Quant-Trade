"""Etendre la regle de verdict aux rapports de batterie (#460).

Specification pre-enregistree dans `PREREG_verdict_rule_battery.md`, committee
AVANT toute modification et toute mesure.

Defaut trouve au #457 **en cherchant autre chose** : la regle unifiee, taillee
sur les rapports de STRATEGIE, repond « indetermine » sur tous les rapports de
batterie, dont la forme negative commence par `**PAS de PASS RENFORCE`.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(SCRIPTS))

import nonml_verdict  # noqa: E402  (regle MODIFIEE)

OUT = RESULTS / "nonml_verdict_rule_battery_result.md"
BASE = "753e765"          # commit du PREREG, epingle (lecons #445/#451)


def ancienne_regle(t):
    """La regle telle qu'elle etait AU COMMIT DE REFERENCE, moins ma branche.

    Premiere version de ce controle : j'avais reimplemente la regle d'avant le
    #448 (litteral `PASS (niveau 1)` compare en SOUS-CHAINE, decoration non
    retiree de la meme facon). Elle attribuait a ce cycle un reclassement qui
    datait en realite du #448 — un faux positif produit par une base mal
    specifiee. On reutilise donc `_nu` du module et on ne retire QUE la branche
    ajoutee ici.
    """
    for ln in t.splitlines():
        nu = nonml_verdict._nu(ln)
        if nu.startswith("**PASS") or nu.startswith("PASS (niveau 1)"):
            return "PASS"
        if nu.startswith("**FAIL"):
            return "FAIL"
    return "indéterminé"


def ligne_decisive(t):
    for ln in t.splitlines():
        nu = nonml_verdict._nu(ln)
        if (nu.startswith("**PAS de PASS RENFORCÉ") or nu.startswith("**PASS")
                or nu.startswith("**FAIL")):
            return ln.strip()
    return "— aucune —"


def main():
    tous = sorted(RESULTS.glob("*.md"))
    change, batteries = [], []
    for p in tous:
        t = p.read_text(encoding="utf-8")
        a, b = ancienne_regle(t), nonml_verdict.verdict_of(t)
        est_batterie = p.name.endswith("_pass_validation_battery.md")
        if est_batterie:
            batteries.append((p.name, a, b))
        if a != b:
            change.append((p.name, a, b, est_batterie, ligne_decisive(t)))

    strategiques = [c for c in change if not c[3]]
    n_bat_fail = sum(1 for _, _, b in batteries if b == "FAIL")
    n_bat_pass = sum(1 for _, _, b in batteries if b == "PASS")
    n_bat_indet = sum(1 for _, _, b in batteries if b == "indéterminé")

    numstat = subprocess.run(
        ["git", "diff", BASE, "--numstat", "--",
         "finance/trading/scripts/nonml_verdict.py"],
        cwd=REPO, capture_output=True, text=True).stdout.split()
    confine = len(numstat) >= 2 and numstat[1] == "0"

    L = ["# Étendre la règle de verdict aux rapports de batterie (pré-enregistré)", ""]
    L.append("Défaut trouvé au #457 **en cherchant autre chose**. La règle unifiée, taillée")
    L.append("sur les rapports de **stratégie**, répondait « indéterminé » sur tous les")
    L.append("rapports de batterie.")
    L.append("")

    L.append("## L'effet, sur tout le dépôt")
    L.append("")
    L.append(f"- fichiers `.md` examinés : **{len(tous)}**")
    L.append(f"- **reclassés** : **{len(change)}**")
    L.append(f"- dont rapports de **batterie** : **{len(change) - len(strategiques)}**")
    L.append(f"- dont rapports **hors batterie** : **{len(strategiques)}**")
    L.append("")

    L.append("## Les rapports de batterie")
    L.append("")
    L.append(f"- total dans le dépôt : **{len(batteries)}**")
    L.append(f"- désormais **FAIL** : **{n_bat_fail}**")
    L.append(f"- désormais **PASS** : **{n_bat_pass}**")
    L.append(f"- encore « indéterminé » : **{n_bat_indet}**")
    L.append("")
    if n_bat_pass == 0:
        L.append("> **Aucun rapport de batterie ne porte un PASS RENFORCÉ.** Sur les")
        L.append(f"> **{len(batteries)}** que compte le dépôt, **pas un seul** n'a jamais")
        L.append("> franchi les cinq contrôles.")
        L.append("")
        L.append("Le #457 l'avait établi sur les 29 qu'il faisait passer ; c'est vrai sur")
        L.append("**l'ensemble du dépôt**. **Prédiction vérifiée.**")
        L.append("")

    L.append("## Critère 3 — aucun rapport de stratégie reclassé")
    L.append("")
    if not strategiques:
        L.append("**Aucun.** Le risque réel de cette modification — reclasser un rapport de")
        L.append("stratégie contenant par hasard cette formule — ne s'est pas matérialisé.")
        L.append("**Prédiction vérifiée.**")
    else:
        L.append(f"**{len(strategiques)} rapport(s) hors batterie reclassé(s)** — le cycle")
        L.append("**échoue** son critère 3. Publiés avec la ligne qui décide :")
        L.append("")
        L.append("| Rapport | Avant | Après | Ligne décisive |")
        L.append("|---|---|---|---|")
        for nom, a, b, _, ln in strategiques:
            L.append(f"| `{nom}` | {a} | **{b}** | `{ln[:70]}` |")
    L.append("")

    L.append("## Critère 1 — diff confiné")
    L.append("")
    if len(numstat) >= 2:
        L.append(f"`nonml_verdict.py` : **+{numstat[0]} / −{numstat[1]}**, une seule branche")
        L.append("insérée dans `porte_verdict`.")
    L.append("")
    L.append(f"**Confiné : {'OUI' if confine else 'NON'}.**")
    L.append("")

    L.append("## Le reproche que je m'étais adressé d'avance — maintenu")
    L.append("")
    L.append("Le pré-enregistrement disait, **avant** toute mesure :")
    L.append("")
    L.append("> *Cette branche est taillée sur une formulation connue, comme la couche")
    L.append("> « étiquette » du #448 dont la robustesse avait montré qu'elle ne servait")
    L.append("> qu'à un cas. C'est une règle ajustée à un corpus existant, pas une théorie")
    L.append("> générale de l'énoncé d'un verdict.*")
    L.append("")
    L.append("**Il reste vrai maintenant que la branche fonctionne.** L'engagement 3")
    L.append("prévoyait de ne pas l'effacer si elle marchait bien — c'est tenu.")
    L.append("")
    L.append("La seule défense honnête : elle est **déclarée**, **étroite**, **vérifiable**,")
    L.append("et l'alternative — laisser des centaines de rapports « indéterminés » — est")
    L.append("pire. Ce n'est pas une bonne règle, c'est une règle moins mauvaise que le")
    L.append("silence.")
    L.append("")

    L.append("## Ce que ce cycle ne fait pas")
    L.append("")
    L.append("- Il ne **régénère** aucun rapport : les 7 consommateurs de la règle verront")
    L.append("  l'effet à leur prochaine exécution, et **mélanger cet effet avec la dérive")
    L.append("  du dépôt** est précisément ce que les #449 et #450 ont appris à éviter.")
    L.append("- Il ne **change aucun verdict de stratégie** : reclasser un rapport de")
    L.append("  batterie, c'est **lire correctement ce qu'il dit déjà**.")
    L.append("- Il ne touche ni la batterie ni sa formulation.")
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
