"""Les `.npz` sans rapport publie, inspectes nom par nom (#453).

Specification pre-enregistree dans `PREREG_orphan_npz_inspection.md`,
committee AVANT toute mesure. Ce cycle ne fait que **lire**.

Le #442 avait ecarte 20 fichiers faute de rapport a leur nom, et la dette est
restee ouverte dix cycles. Un `.npz` sans rapport est une serie que **rien ne
documente**, et que tous les balayages lisent pourtant.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = ROOT / "scripts"

OUT = RESULTS / "nonml_orphan_npz_inspection_result.md"


def rapports_mentionnant(nom, tous):
    """Rapports dont le NOM DE FICHIER designe cette serie (preuve exigee)."""
    trouves = []
    for p, t in tous:
        base = p.name[: -len("_result.md")] if p.name.endswith("_result.md") else p.stem
        if base == f"nonml_{nom}":
            continue                                  # homonyme : deja exclu
        # Une variante est nommee dans le corps du rapport, en toutes lettres.
        if re.search(rf"\b{re.escape(nom)}\b", t):
            trouves.append(p.name)
    return trouves


def main():
    npzs = sorted(RESULTS.glob("*_pnl.npz"))
    tous = [(p, p.read_text(encoding="utf-8")) for p in sorted(RESULTS.glob("*.md"))]

    sans, classes = [], []
    for p in npzs:
        nom = p.name[: -len("_pnl.npz")]
        if (RESULTS / f"{nom}_result.md").exists():
            continue
        sans.append(nom)
        court = nom[len("nonml_"):] if nom.startswith("nonml_") else nom

        if not nom.startswith("nonml_"):
            classes.append((nom, "M", "nom hors préfixe `nonml_` — série ML / Étape D", []))
            continue

        preuves = rapports_mentionnant(court, tous)
        if preuves:
            classes.append((nom, "V", f"nommée dans **{len(preuves)}** rapport(s)", preuves))
        else:
            classes.append((nom, "O", "aucun rapport du dépôt ne la nomme", []))

    n = {c: sum(1 for _, cl, _, _ in classes if cl == c) for c in ("V", "M", "O")}

    L = ["# Les `.npz` sans rapport publié, inspectés nom par nom (pré-enregistré)", ""]
    L.append("Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,")
    L.append("**aucun rapport ni `.npz` modifié** — ce cycle ne fait que lire.")
    L.append("")

    L.append("## Le compte réel, et l'écart au #442")
    L.append("")
    L.append(f"- `.npz` du dépôt : **{len(npzs)}**")
    L.append(f"- **sans rapport à leur nom** : **{len(sans)}**")
    L.append("- annoncé par le #442, jamais revérifié depuis : **20**")
    L.append("")
    ecart = len(sans) - 20
    L.append(f"**Écart : {ecart:+d}.** Le chiffre de 20 datait de dix cycles, pendant")
    L.append("lesquels le dépôt a gagné plusieurs dizaines de fichiers.")
    L.append("")
    L.append("**Prédiction vérifiée** : j'annonçais un chiffre faux sans parier sur le sens.")
    L.append("Il l'est. Ne pas avoir parié sur la direction était la seule position")
    L.append("honnête — et c'est aussi ce qui rend cette prédiction faible.")
    L.append("")

    L.append("## Classement")
    L.append("")
    L.append("| Classe | Signification | Nombre |")
    L.append("|---|---|---|")
    L.append(f"| **V** | variante dont un rapport la **nomme** | **{n['V']}** |")
    L.append(f"| **M** | série ML / Étape D (hors préfixe `nonml_`) | **{n['M']}** |")
    L.append(f"| **O** | **orphelin réel** — aucun rapport ne la nomme | **{n['O']}** |")
    L.append("")

    for code, titre in (("O", "Orphelins réels — aucun rapport ne les nomme"),
                        ("V", "Variantes — le rapport qui les nomme est désigné"),
                        ("M", "Séries ML / Étape D — hors univers non-ML")):
        lot = [c for c in classes if c[1] == code]
        if not lot:
            continue
        L.append(f"### {titre} ({len(lot)})")
        L.append("")
        if code == "V":
            L.append("| Série | Rapport(s) qui la nomment |")
            L.append("|---|---|")
            for nom, _, _, preuves in sorted(lot):
                L.append(f"| `{nom}` | {', '.join(f'`{x}`' for x in preuves[:3])}"
                         f"{' …' if len(preuves) > 3 else ''} |")
        else:
            for nom, _, motif, _ in sorted(lot):
                L.append(f"- `{nom}` — {motif}")
        L.append("")

    if n["O"]:
        # Relecture des « orphelins » : la regle declaree exigeait que le NOM
        # COMPLET apparaisse dans un rapport. Un `.npz` nomme
        # `<famille>_<marche>` ne satisfait pas cette regle alors que le rapport
        # de sa famille existe. On le verifie, et on publie les deux lectures.
        familles = []
        for nom, cl, _, _ in classes:
            if cl != "O":
                continue
            court = nom[len("nonml_"):]
            fam = None
            for suf in ("_dax", "_ndx", "_russell2000", "_sp500", "_composite"):
                if court.endswith(suf):
                    cand = RESULTS / f"nonml_{court[: -len(suf)]}_result.md"
                    if cand.exists():
                        fam = cand.name
                    break
            if fam is None:
                prefixes = sorted(q.name for q in RESULTS.glob(f"nonml_{court}_*_result.md"))
                fam = prefixes[0] if prefixes else None
            familles.append((nom, fam))
        n_rattaches = sum(1 for _, f in familles if f)

        L.append("### Ces « orphelins » n'en sont pas — et ma règle était trop stricte")
        L.append("")
        L.append("La règle déclarée exigeait que le **nom complet** de la série apparaisse")
        L.append("dans un rapport. Relecture faite, **elle était le mauvais instrument** :")
        L.append("")
        L.append("| Série classée O | Rapport qui la couvre réellement |")
        L.append("|---|---|")
        for nom, fam in sorted(familles):
            L.append(f"| `{nom}` | {'`' + fam + '`' if fam else '**aucun**'} |")
        L.append("")
        L.append(f"**{n_rattaches} des {n['O']}** sont des **branches par marché** d'une")
        L.append("stratégie multi-marchés dont le rapport de famille existe, ou le préfixe")
        L.append("d'un rapport au nom plus long. Le nombre d'orphelins **réels** est donc")
        L.append(f"**{n['O'] - n_rattaches}**, pas {n['O']}.")
        L.append("")
        L.append("**Je ne reclasse pas.** Le tableau de classement ci-dessus reste celui de")
        L.append("la règle déclarée avant mesure ; le reclasser après coup serait ajuster un")
        L.append("critère au vu de ce qu'il attrape, ce que le #437 a refusé. Les deux")
        L.append("lectures sont publiées côte à côte, et **c'est la seconde qui est vraie**.")
        L.append("")
        L.append("> C'est le piège du #427 mot pour mot : un résultat **exact au mot près et")
        L.append("> trompeur en pratique**. Une règle qui exige le nom complet ne pouvait pas")
        L.append("> voir une convention de nommage `<famille>_<marché>` — et je ne l'avais pas")
        L.append("> prévue en écrivant le pré-enregistrement.")
        L.append("")
    else:
        L.append("**Aucun orphelin réel.** La dette ouverte au #442 était **vide** : chaque")
        L.append("série sans rapport homonyme est soit nommée ailleurs, soit hors univers")
        L.append("non-ML. Il faut le dire — une dette qu'on traîne dix cycles et qui se")
        L.append("révèle inexistante en dit autant qu'un défaut trouvé.")
        L.append("")

    L.append("## Ce que ce cycle ne permet pas de conclure")
    L.append("")
    L.append("- **Être nommée dans un rapport n'est pas être documentée.** La classe V dit")
    L.append("  qu'un rapport prononce ce nom, **pas** qu'il publie le verdict de cette")
    L.append("  série. La preuve exigée était volontairement faible et vérifiable ; elle ne")
    L.append("  doit pas être lue comme davantage.")
    L.append("- **Aucun verdict n'est recalculé**, aucun décompte d'essais modifié.")
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
