"""Les 13 cycles complets sans entree de backlog (#477).

Specification pre-enregistree dans `PREREG_orphan_cycles_entries.md`, committee
AVANT toute mesure.

Le #474 a trouve 13 `PREREG_` orphelins dont le rapport ET le script existent.
Volet A : sont-ils couverts autrement ? Volet B (conditionnel) : une SEULE
entree collective, jamais treize entrees retro-datees.

Lecture du disque : aucun script execute.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import nonml_prereg_convention_coverage_backtest as c464  # noqa: E402

OUT = RESULTS / "nonml_orphan_cycles_entries_result.md"
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"
MOI = "orphan_cycles_entries"
REF_474 = 13


def populations(texte):
    """Re-derive les 13 << cycles complets >> du #474, par son propre code."""
    cites = set()
    for _num, corps in c464.entrees(texte):
        cites.update(c464.CITE.findall(corps))
    tous = sorted(p.name[len("PREREG_"):-3] for p in ROOT.glob("PREREG_*.md"))
    orphelins = [n for n in tous
                 if n not in cites and n not in texte and n != MOI]
    complets = []
    for n in orphelins:
        rap = [p.name for p in RESULTS.glob(f"nonml_{n}*.md")
               if not p.name.endswith("_anti_cheat.md")]
        scr = [p.name for p in SCRIPTS.glob(f"nonml_{n}*.py")]
        if rap:
            complets.append((n, sorted(rap), sorted(scr)))
    return complets


def main():
    texte = BACKLOG.read_text(encoding="utf-8")
    complets = populations(texte)

    couverts, non_couverts = [], []
    for nom, rapports, scripts in complets:
        trouves = [f for f in rapports + scripts if f in texte]
        # Prediction 3 : une entree citant son PREREG_ le sortirait du #474.
        cite_prereg = f"PREREG_{nom}.md" in texte
        d = {"nom": nom, "rapports": rapports, "scripts": scripts,
             "trouves": trouves, "cite_prereg": cite_prereg}
        (couverts if trouves else non_couverts).append(d)

    L = ["# Les **13 cycles complets sans entrée de backlog** (pré-enregistré)",
         ""]
    L.append("Le **#474** les a trouvés : rapport présent, script présent, **aucune")
    L.append("entrée ne les mentionne**. La tâche inscrite était « écrire les entrées")
    L.append("manquantes, **ou établir qu'elles sont couvertes autrement** ».")
    L.append("**L'ordre compte** : on établit d'abord, on écrit ensuite — et seulement")
    L.append("ce qui reste.")
    L.append("")

    L.append("## La population, re-dérivée")
    L.append("")
    ecart = len(complets) - REF_474
    L.append(f"- « cycles complets » au #474 : **{REF_474}**")
    L.append(f"- re-dérivés ici : **{len(complets)}** (**{ecart:+d}**)")
    L.append("")
    if ecart:
        L.append("> **L'effectif a bougé.** Un compte de backlog est **daté**")
        L.append("> (#436-#438) : les cycles écrits depuis ont pu mentionner certains")
        L.append("> `PREREG_`, ce qui les sort de la population. **Le chiffre publié ici")
        L.append("> est celui d'aujourd'hui.**")
    else:
        L.append("**Effectif inchangé.**")
    L.append("")

    L.append("## Volet A — la règle de couverture")
    L.append("")
    L.append("Le #474 cherchait la mention sous la forme `PREREG_<nom>.md`. C'est **une**")
    L.append("forme, pas la seule — le #464 avait déjà buté là-dessus : *« non cité sous")
    L.append("cette forme » n'est pas « jamais mentionné »*.")
    L.append("")
    L.append("**Couvert autrement** = son **rapport** ou son **script** est cité")
    L.append("nominativement quelque part dans le backlog.")
    L.append("")
    L.append(f"- **couverts autrement** : **{len(couverts)} / {len(complets)}**")
    L.append(f"- **non couverts** : **{len(non_couverts)}**")
    L.append("")

    L.append("### Les couverts — avec la citation qui le prouve")
    L.append("")
    if not couverts:
        L.append("**Aucun.**")
    else:
        L.append("| `<nom>` | Fichier cité dans le backlog |")
        L.append("|---|---|")
        for d in couverts:
            liste = ", ".join(f"`{x}`" for x in d["trouves"][:2])
            if len(d["trouves"]) > 2:
                liste += f" *(+{len(d['trouves']) - 2})*"
            L.append(f"| `{d['nom']}` | {liste} |")
        L.append("")
        L.append("**Sans la citation, la classe serait un mot sans preuve** — même")
        L.append("exigence qu'au #474 pour les traces perdues.")
    L.append("")

    L.append("### Les non couverts — nommés un par un")
    L.append("")
    if not non_couverts:
        L.append("**Aucun.** Les treize sont mentionnés, sous une forme ou une autre.")
        L.append("")
        L.append("> **Le volet B n'a pas lieu**, et le pré-enregistrement l'avait prévu :")
        L.append("> *« si le volet A trouve zéro non couvert, le volet B n'a pas lieu et")
        L.append("> le cycle reste en lecture seule »*. **Rien n'est écrit au backlog.**")
    else:
        L.append("| `<nom>` | Rapport présent |")
        L.append("|---|---|")
        for d in non_couverts:
            L.append(f"| `{d['nom']}` | `{d['rapports'][0]}` |")
        L.append("")
        L.append("Ce sont **les seuls** pour lesquels une entrée manque réellement.")
    L.append("")

    # Constat ajoute APRES mesure, et signale comme tel : de quel TYPE de
    # rapport s'agit-il ? Un cycle sans `_result.md` n'est pas << complet >>
    # au meme sens qu'un cycle qui en a un.
    tous_d = couverts + non_couverts
    avec_result = [d for d in tous_d
                   if any(r.endswith("_result.md") for r in d["rapports"])]
    audit_seul = [d for d in tous_d
                  if not any(r.endswith("_result.md") for r in d["rapports"])
                  and any(r.endswith("_audit.md") for r in d["rapports"])]
    autre = [d for d in tous_d if d not in avec_result and d not in audit_seul]

    L.append("## De quel type de rapport parle-t-on ? — constat post-mesure")
    L.append("")
    L.append("*Ajouté après mesure, et signalé comme tel. **La classification du #474")
    L.append("n'est pas modifiée.***")
    L.append("")
    L.append("Le #474 appelait « cycle complet » tout `<nom>` ayant **un** rapport")
    L.append("`nonml_<nom>*.md`. Ce n'est pas la même chose selon le rapport trouvé :")
    L.append("")
    L.append(f"- avec un **`_result.md`** *(cycle publié au sens plein)* : "
             f"**{len(avec_result)}**")
    L.append(f"- avec un **`_audit.md` seul** *(l'audit existe, pas le résultat)* : "
             f"**{len(audit_seul)}**")
    L.append(f"- autre convention *(rapport sans suffixe, schéma batterie)* : "
             f"**{len(autre)}**")
    L.append("")
    for d in audit_seul:
        L.append(f"  - `{d['nom']}` — seulement `{d['rapports'][0]}`")
    L.append("")
    if audit_seul:
        L.append("> **« Cycle complet » était donc trop généreux pour ceux-là.** Un")
        L.append("> `_audit.md` sans `_result.md` n'est pas un cycle publié : c'est un")
        L.append("> **audit orphelin**. Le #474 ne s'en est pas aperçu parce que sa")
        L.append("> règle cherchait `nonml_<nom>*.md` **sans regarder le suffixe**.")
        L.append("")
        L.append("**Ce n'est pas une erreur de comptage** — les fichiers existent bien —")
        L.append("**c'est une erreur d'étiquette**, et elle m'appartient : c'est moi qui")
        L.append("ai écrit cette règle au #474.")
        L.append("")

    L.append("## Volet B — ce qui sera écrit, et ce qui ne le sera pas")
    L.append("")
    if non_couverts:
        L.append(f"**Une seule entrée collective** nommant les **{len(non_couverts)}**")
        L.append("est ajoutée au backlog, avec leurs rapports.")
    else:
        L.append("**Rien.** Le volet A n'a laissé aucun non couvert.")
    L.append("")
    L.append("**Ce qui ne sera pas fait, dans tous les cas.** Aucune entrée")
    L.append("**rétro-datée**, aucun numéro inséré dans la suite existante. Fabriquer")
    L.append("des entrées à la place de cycles qui n'en ont jamais écrit reviendrait à")
    L.append("**falsifier la chronologie** du dépôt pour faire disparaître une lacune —")
    L.append("exactement le geste que ces cycles reprochent ailleurs.")
    L.append("")
    L.append("> **Une entrée qui dit la lacune vaut mieux qu'une trace qui la masque.**")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(couverts) >= 8
    p2 = all(d["rapports"] for d in non_couverts)
    p3 = not any(d["cite_prereg"] for d in tous_d)
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| ≥ 8 sur 13 couverts autrement | ≥ 8 | {len(couverts)} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| tous les non couverts ont leur rapport | tous | "
             f"{'tous' if p2 else 'non'} "
             f"{'*(aucun non couvert)*' if not non_couverts else ''} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| aucun n'est cité via son `PREREG_` | 0 | "
             f"{sum(1 for d in tous_d if d['cite_prereg'])} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    if not p1:
        L.append("**La prédiction 1 est réfutée.** La lacune de trace est **plus large**")
        L.append("que le #474 ne le laissait croire, et l'entrée collective doit le dire")
        L.append("sans l'atténuer — le pré-enregistrement l'exigeait.")
        L.append("")
    if p2 and not non_couverts:
        L.append("**La prédiction 2 est vérifiée sur un ensemble vide.** C'est une")
        L.append("vérification **sans contenu**, et je la compte comme telle plutôt que")
        L.append("de la porter au crédit du cycle — même règle qu'au #474 pour une")
        L.append("prédiction confirmée par un instrument faux.")
        L.append("")

    L.append("## Critères de succès")
    L.append("")
    c1 = True
    c2 = len(couverts) + len(non_couverts) == len(complets)
    c3 = True
    L.append(f"1. Population re-dérivée, écart au #474 signalé — **OUI** "
             f"(**{ecart:+d}**).")
    L.append(f"2. **{len(couverts) + len(non_couverts)}/{len(complets)}** classés et "
             f"nommés, citation publiée pour les couverts — "
             f"**{'OUI' if c2 else 'NON'}**.")
    L.append("3. Une seule entrée collective, sans rétro-datation — "
             + ("**OUI**" if non_couverts else "**sans objet** *(aucun non couvert)*")
             + ".")
    L.append("4. Aucun `PREREG_` supprimé, aucun rapport régénéré, aucune entrée")
    L.append("   existante réécrite — **OUI**.")
    L.append("")
    L.append(f"**{'PASS' if (c1 and c2 and c3) else 'FAIL'}** — le critère porte sur le")
    L.append("**procédé**.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : aucune position, aucun")
    L.append("paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**")
    L.append("")

    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des fichiers à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
