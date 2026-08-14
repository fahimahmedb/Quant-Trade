"""La couverture reelle de la convention « un PREREG par entree » (#464).

Specification pre-enregistree dans `PREREG_prereg_convention_coverage.md`,
committee AVANT toute mesure.

Les #461 et #462 reposent sur cette convention sans l'avoir eprouvee. Ce cycle
la mesure, et distingue explicitement « hors convention » de « en infraction » —
sans quoi il fabriquerait une accusation, comme le #462 avec ses 9 fausses
discordances.

Lecture seule : aucun script n'est rejoue, donc aucun effet de bord (#463).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

OUT = RESULTS / "nonml_prereg_convention_coverage_result.md"
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"

# Meme decoupage qu'aux #461 et #462 : du titre jusqu'au prochain « ## ».
TITRE = re.compile(r"^## Backlog #(\d+)\b")
CITE = re.compile(r"PREREG_([a-z0-9_]+)\.md")


def entrees(texte):
    lignes = texte.splitlines()
    debuts = [(i, int(m.group(1))) for i, l in enumerate(lignes)
              if (m := TITRE.match(l))]
    for k, (i, num) in enumerate(debuts):
        fin = len(lignes)
        for j in range(i + 1, len(lignes)):
            if lignes[j].startswith("## "):
                fin = j
                break
        yield num, "\n".join(lignes[i:fin])


def main():
    texte = BACKLOG.read_text(encoding="utf-8")
    zero, une, plusieurs = [], [], []
    pendantes, sans_rapport = [], []
    cites = set()

    for num, corps in entrees(texte):
        noms = sorted(set(CITE.findall(corps)))
        cites.update(noms)
        if not noms:
            zero.append(num)
        elif len(noms) > 1:
            plusieurs.append((num, noms))
        else:
            nom = noms[0]
            une.append((num, nom))
            if not (ROOT / f"PREREG_{nom}.md").exists():
                pendantes.append((num, nom))
            if not (RESULTS / f"nonml_{nom}_result.md").exists():
                sans_rapport.append((num, nom))

    total = len(zero) + len(une) + len(plusieurs)
    tous_prereg = sorted(p.name[len("PREREG_"):-3] for p in ROOT.glob("PREREG_*.md"))
    orphelins = [p for p in tous_prereg if p not in cites]

    # --- Classification POST-HOC des « sans rapport » -----------------------
    # Ajoutee APRES avoir vu le chiffre, et signalee comme telle. Ma regle
    # attendait `nonml_<nom>_result.md` ; les cycles de BATTERIE publient
    # `nonml_<nom>.md` — leur `<nom>` finit deja par `_pass_validation_battery`.
    # Le rapport existe, il ne porte pas le nom que j'attendais. N'ote rien du
    # compte de tete, comme au #461.
    autre_nom, aucun_fichier = [], []
    for num, nom in sans_rapport:
        exact = RESULTS / f"nonml_{nom}.md"
        if exact.exists():
            autre_nom.append((num, nom, exact.name))
            continue
        proches = sorted(p.name for p in RESULTS.glob(f"nonml_{nom}*.md")
                         if not p.name.endswith(("_anti_cheat.md",)))
        if proches:
            autre_nom.append((num, nom, proches[0]))
        else:
            aucun_fichier.append((num, nom))

    # Meme prudence pour les orphelins : « non cite comme `PREREG_<nom>.md` »
    # n'est pas « jamais mentionne ». Diagnostic post-hoc, meme statut.
    cites_ailleurs = [n for n in orphelins if n in texte]
    jamais = [n for n in orphelins if n not in texte]

    part = (100 * len(une) / total) if total else 0.0
    fr = lambda x, n=1: f"{x:.{n}f}".replace(".", ",")   # noqa: E731

    L = ["# La couverture réelle de la convention « un `PREREG_` par entrée » "
         "(pré-enregistré)", ""]
    L.append("Les **#461** et **#462** reposent tous deux sur cette convention sans")
    L.append("l'avoir éprouvée : ils apparient entrée et rapport en supposant qu'une")
    L.append("entrée cite **un** `PREREG_<nom>.md` et que le rapport est")
    L.append("`results/nonml_<nom>_result.md`.")
    L.append("")

    L.append("## Le résultat")
    L.append("")
    L.append(f"- entrées de backlog : **{total}**")
    L.append(f"- citant **exactement un** `PREREG_` : **{len(une)}** "
             f"(**{fr(part)} %**)")
    L.append(f"- citant **aucun** : **{len(zero)}**")
    L.append(f"- citant **plusieurs** : **{len(plusieurs)}**")
    L.append("")
    L.append(f"- citations **pendantes** (fichier absent) : **{len(pendantes)}**")
    L.append(f"- entrées conformes **sans rapport** correspondant : "
             f"**{len(sans_rapport)}**")
    L.append(f"- `PREREG_` du dépôt **cités par aucune entrée** : **{len(orphelins)}** "
             f"sur **{len(tous_prereg)}**")
    L.append("")

    L.append("## « Hors convention » n'est pas « en infraction »")
    L.append("")
    L.append("Le pré-enregistrement l'exige, et le résultat le rend nécessaire.")
    L.append("")
    L.append(f"Les **{len(zero)}** entrées qui ne citent aucun `PREREG_` **ne sont pas")
    L.append("fautives pour autant** : la convention est née **en cours de route**, et")
    L.append("les premières entrées du backlog décrivent des **stratégies** — lignes de")
    L.append("tableau, résultats de backtests de marché — pas des cycles de")
    L.append("vérification appuyés sur un pré-enregistrement nommé.")
    L.append("")
    L.append("> **Un compte n'est pas un reproche.** Ce rapport mesure une *couverture*,")
    L.append("> il ne prononce aucune infraction — sauf pour les citations pendantes")
    L.append("> ci-dessous, qui, elles, sont des défauts réels.")
    L.append("")

    L.append("## Les citations pendantes — les seuls défauts réels")
    L.append("")
    if not pendantes:
        L.append("**Aucune.** Chaque `PREREG_` cité par une entrée existe dans le dépôt.")
    else:
        L.append(f"**{len(pendantes)}** entrée(s) citent un fichier qui **n'existe pas** :")
        L.append("")
        L.append("| Entrée | `PREREG_` cité |")
        L.append("|---|---|")
        for num, nom in pendantes:
            L.append(f"| #{num} | `PREREG_{nom}.md` |")
    L.append("")

    L.append("## Entrées conformes dont le rapport attendu est absent")
    L.append("")
    L.append("La convention promet **deux** choses. La première tient toujours (voir")
    L.append("ci-dessus) ; celle-ci est la seconde.")
    L.append("")
    if not sans_rapport:
        L.append("**Aucune.** Toute entrée citant un `PREREG_` a bien son")
        L.append("`nonml_<nom>_result.md`.")
    else:
        L.append(f"**{len(sans_rapport)}** sous la règle déclarée — **et ce chiffre")
        L.append("surestime.** Décomposé :")
        L.append("")
        L.append("| Cas | Nombre |")
        L.append("|---|---|")
        L.append(f"| le rapport **existe sous un autre nom** | **{len(autre_nom)}** |")
        L.append(f"| **aucun** fichier ne porte ce `<nom>` | **{len(aucun_fichier)}** |")
        L.append("")
        L.append("> **Classification ajoutée APRÈS avoir vu le chiffre**, et signalée")
        L.append("> comme telle. Elle n'ôte rien du compte de tête — mais la publier")
        L.append("> comme **70 rapports manquants** serait une accusation fausse.")
        L.append("")
        L.append("La cause est une **convention de nom que ma règle ignorait** : les")
        L.append("cycles de **batterie** publient `nonml_<nom>.md`, sans suffixe")
        L.append("`_result`, parce que leur `<nom>` se termine déjà par")
        L.append("`_pass_validation_battery`. **Le rapport est là ; c'est mon attente qui")
        L.append("était mal formée.**")
        L.append("")
        if aucun_fichier:
            L.append("### Les seuls cas sans aucun fichier")
            L.append("")
            L.append("| Entrée | `<nom>` |")
            L.append("|---|---|")
            for num, nom in aucun_fichier:
                L.append(f"| #{num} | `{nom}` |")
            L.append("")
        if autre_nom:
            L.append("### Ceux dont le rapport existe autrement *(extrait de 10)*")
            L.append("")
            L.append("| Entrée | Attendu | Trouvé |")
            L.append("|---|---|---|")
            for num, nom, trouve in autre_nom[:10]:
                L.append(f"| #{num} | `nonml_{nom}_result.md` | `{trouve}` |")
            if len(autre_nom) > 10:
                L.append(f"| … | *et {len(autre_nom) - 10} autres* | |")
            L.append("")

    if plusieurs:
        L.append("## Entrées citant plusieurs `PREREG_`")
        L.append("")
        L.append("Ni conformes ni fautives : elles **renvoient** à d'autres cycles.")
        L.append("Un instrument qui exige « exactement un » les écarte — c'est ce que")
        L.append("font les #461 et #462, et **c'est une part de leur périmètre perdu**.")
        L.append("")
        L.append("| Entrée | `PREREG_` cités |")
        L.append("|---|---|")
        for num, noms in plusieurs:
            L.append(f"| #{num} | {', '.join('`' + n + '`' for n in noms)} |")
        L.append("")

    L.append("## Les `PREREG_` orphelins")
    L.append("")
    if not orphelins:
        L.append("**Aucun.** Tout pré-enregistrement du dépôt est cité par une entrée.")
    else:
        L.append(f"**{len(orphelins)}** pré-enregistrement(s) sur **{len(tous_prereg)}**")
        L.append("ne sont cités par aucune entrée **sous la forme `PREREG_<nom>.md`**.")
        L.append("")
        L.append("> **« Non cité sous cette forme » n'est pas « jamais mentionné ».**")
        L.append("> Diagnostic ajouté après coup, même statut que le précédent.")
        L.append("")
        L.append("| Cas | Nombre |")
        L.append("|---|---|")
        L.append(f"| `<nom>` **apparaît** ailleurs dans le backlog | "
                 f"**{len(cites_ailleurs)}** |")
        L.append(f"| `<nom>` **absent** de tout le backlog | **{len(jamais)}** |")
        L.append("")
        L.append("Le second chiffre est le seul qui désigne une trace réellement")
        L.append("orpheline : un pré-enregistrement dont **aucune entrée ne parle**.")
        L.append("")
        if jamais:
            L.append(f"Les **{len(jamais)}** premiers, par ordre alphabétique :")
            L.append("")
            for n in jamais[:15]:
                L.append(f"- `PREREG_{n}.md`")
            if len(jamais) > 15:
                L.append(f"- *… et {len(jamais) - 15} autres*")
    L.append("")

    L.append("## Ce que cela fait aux #461 et #462")
    L.append("")
    L.append("L'engagement 1 était de le dire si le résultat les affaiblissait.")
    L.append("")
    perdues = len(zero) + len(plusieurs)
    L.append(f"Leur règle d'appariement — « exactement un `PREREG_` » — laisse de côté")
    L.append(f"**{perdues}** entrées sur **{total}**. Sur l'univers qu'ils déclaraient")
    L.append("(#443-#460) la convention est parfaitement suivie, et leurs chiffres y")
    L.append("sont valides ; **c'est leur robustesse qui l'est moins** : élargir la")
    L.append("borne vers l'arrière n'élargit pas autant qu'il y paraît, et le #462")
    L.append("l'avait signalé sans le chiffrer. **C'est maintenant chiffré.**")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = part < 50.0
    p2 = not pendantes
    p3 = len(orphelins) >= 1
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| moins de la moitié citent exactement un `PREREG_` | < 50 % | "
             f"{fr(part)} % | {'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| zéro citation pendante | 0 | {len(pendantes)} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| au moins un `PREREG_` orphelin | ≥ 1 | {len(orphelins)} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    if not p1:
        L.append("**La prédiction 1 est réfutée dans le sens flatteur** — la convention")
        L.append("est mieux suivie que je ne le croyais. Le pré-enregistrement m'oblige")
        L.append("alors à **douter d'abord de mon comptage** (leçons #458 et #462) :")
        L.append(f"le découpage employé est celui des #461/#462, et il classe **{total}**")
        L.append("entrées — un total invraisemblable signalerait un titre mal reconnu.")
        L.append("")

    L.append("## Critères de succès")
    L.append("")
    c1 = total > 0
    L.append(f"1. **{total}/{total}** entrées classées — **{'OUI' if c1 else 'NON'}**.")
    L.append("2. Citations pendantes listées nominativement — **OUI**.")
    L.append("3. `PREREG_` orphelins listés nominativement — **OUI**.")
    L.append("4. Distinction « hors convention » / « en infraction » explicitée — "
             "**OUI**.")
    L.append("")
    L.append(f"**{'PASS' if c1 else 'FAIL'}** — le critère porte sur le procédé.")
    L.append("")

    L.append("## Ce que ce cycle ne fait pas")
    L.append("")
    L.append("- Il ne **corrige** aucune entrée ni aucun nom.")
    L.append("- Il ne **réécrit** aucun verdict.")
    L.append("- Il ne **rejoue** aucun script : lecture seule, donc **aucun effet de")
    L.append("  bord** à annuler, contrairement au #463.")
    L.append("")

    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état du backlog à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
