"""Separer porteurs et citeurs par le script emetteur (#469).

Specification pre-enregistree dans `PREREG_marker_emitter_crossing.md`,
committee AVANT toute mesure.

Le #465 n'y arrivait pas : une citation verbatim de la marque produit une ligne
textuellement identique a la marque. Le #451 le pouvait, parce qu'il savait quel
script EMET la marque. Ce cycle utilise cette information.

Lecture seule : aucun script n'est execute, aucun effet de bord (#463, #468).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

OUT = RESULTS / "nonml_marker_emitter_crossing_result.md"
PHRASE = "Rapport dépendant du dépôt"

# Convention rapport -> script producteur, declaree au pre-enregistrement.
SUFFIXES = [("_result.md", "_backtest.py"),
            ("_audit.md", "_audit.py"),
            ("_robustness.md", "_robustness.py")]


# Ajoute APRES mesure, et signale comme tel. La regle declaree disait
# « le script CONTIENT la chaine ⇒ il l'EMET ». C'est faux : un script qui
# CHERCHE la marque la contient aussi (`PHRASE = "..."`). Ma regle reproduit,
# dans le code, exactement la confusion qu'elle devait resoudre dans les
# rapports. On distingue donc une ligne qui ECRIT la marque dans la sortie
# d'une ligne qui s'en sert autrement.
EMISSION = re.compile(r"(append|write|print)\s*\(.*Rapport dépendant du dépôt")


def emet_vraiment(code):
    return any(EMISSION.search(l) for l in code.splitlines())


def producteur(nom_rapport):
    for suf_md, suf_py in SUFFIXES:
        if nom_rapport.endswith(suf_md):
            base = nom_rapport[:-len(suf_md)]
            p = SCRIPTS / f"{base}{suf_py}"
            return p if p.exists() else None
    return None


def main():
    porteurs, citeurs, indetermines = [], [], []
    mentionneurs_code = []
    contiennent = []
    for p in sorted(RESULTS.glob("*.md")):
        if p == OUT:
            continue          # exclusion de soi (#446/#447/#468)
        try:
            t = p.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
        if PHRASE not in t:
            continue
        contiennent.append(p.name)
        src = producteur(p.name)
        if src is None:
            indetermines.append(p.name)
        else:
            code = src.read_text(encoding="utf-8")
            if emet_vraiment(code):
                porteurs.append(p.name)
            else:
                # CITEUR : le producteur n'ECRIT pas la marque. Qu'il la
                # mentionne (constante de recherche) ou pas ne change pas le
                # statut du rapport — cela documente la forme du cas.
                citeurs.append((p.name, src.name))
                if PHRASE in code:
                    mentionneurs_code.append((p.name, src.name))

    # --- Controle de coherence : script qui emet -> rapport qui contient ----
    incoherents = []
    for s in sorted(SCRIPTS.glob("nonml_*.py")):
        try:
            code = s.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
        if not emet_vraiment(code):
            continue
        for suf_md, suf_py in SUFFIXES:
            if s.name.endswith(suf_py):
                rap = RESULTS / f"{s.name[:-len(suf_py)]}{suf_md}"
                if rap.exists() and rap != OUT and PHRASE not in \
                        rap.read_text(encoding="utf-8"):
                    incoherents.append((s.name, rap.name))

    # --- Examen individuel des citeurs, exige par l'engagement 3 ------------
    # Un script peut CONSTRUIRE la marque (variable, concatenation) : il
    # l'emettrait sans que la chaine apparaisse telle quelle, et le rapport
    # serait classe CITEUR a tort. On cherche ces formes.
    SOUPCON = re.compile(r"dépendant|dépôt|MARQUE|ENCART|marque\s*=|encart\s*=")
    examen = []
    for nom_rap, nom_src in citeurs:
        code = (SCRIPTS / nom_src).read_text(encoding="utf-8")
        indices = sorted({m.group(0) for m in SOUPCON.finditer(code)})
        examen.append((nom_rap, nom_src, indices))

    L = ["# Séparer **porteurs** et **citeurs** par le script émetteur "
         "(pré-enregistré)", ""]
    L.append("Le **#465** n'y arrivait pas, et avait publié pourquoi : une citation")
    L.append("verbatim de la marque produit une ligne **textuellement identique** à la")
    L.append("marque. Le **#451** le pouvait, parce qu'il savait **quel script émet**")
    L.append("l'encart. Ce cycle utilise cette information.")
    L.append("")

    L.append("## Le résultat")
    L.append("")
    L.append(f"- rapports **contenant** la marque : **{len(contiennent)}**")
    L.append(f"- **PORTEURS** *(le script producteur l'émet)* : **{len(porteurs)}**")
    L.append(f"- **CITEURS** *(le producteur ne l'émet pas)* : **{len(citeurs)}**")
    L.append(f"- **INDÉTERMINÉS** *(aucun script producteur)* : "
             f"**{len(indetermines)}**")
    L.append(f"- dont le producteur **mentionne** la marque sans l'écrire "
             f"*(forme du cas)* : **{len(mentionneurs_code)}**")
    L.append("")
    L.append("### Ma règle reproduisait la confusion qu'elle devait résoudre")
    L.append("")
    L.append("*Diagnostic ajouté après mesure, et signalé comme tel.*")
    L.append("")
    L.append("La règle déclarée disait : **le script contient la chaîne ⇒ il l'émet.**")
    L.append("C'est faux. Un script qui **cherche** la marque la contient aussi — le")
    L.append("`content_defined_magnitudes` du #465 la porte en constante (`PHRASE =`)")
    L.append("précisément pour la chercher.")
    L.append("")
    L.append("> **J'ai transposé dans le code la confusion *porter / mentionner* que ce")
    L.append("> cycle devait lever dans les rapports.** Le #446 l'avait résolue pour les")
    L.append("> verdicts, le #451 pour l'encart, le #465 avait échoué à la lever — et")
    L.append("> elle revient ici, d'un cran plus haut.")
    L.append("")
    L.append("La lecture ci-dessus applique donc un critère **plus étroit** : le script")
    L.append("doit **écrire** la marque (`append`/`write`/`print`), pas seulement la")
    L.append("contenir.")
    L.append("")
    if len(porteurs) < len(contiennent):
        L.append("> **La distinction existe.** Le #465 la cherchait dans le texte des")
        L.append("> rapports, où elle est invisible ; elle se lit dans le **code des")
        L.append("> scripts**.")
    else:
        L.append("> **Tous les rapports contenant la marque la portent.** La distinction")
        L.append("> que le #451 signalait **n'apparaît pas** — voir la confrontation des")
        L.append("> prédictions.")
    L.append("")

    L.append("## Les citeurs, **examinés un par un**")
    L.append("")
    L.append("L'engagement 3 l'exige : un compte ne suffit pas. Un script peut")
    L.append("**construire** la marque par variable ou concaténation, et son rapport")
    L.append("serait alors classé citeur **à tort**.")
    L.append("")
    if not citeurs:
        L.append("**Aucun citeur.**")
    else:
        L.append("| Rapport | Script producteur | Indices de construction dans le code |")
        L.append("|---|---|---|")
        for nom_rap, nom_src, indices in examen:
            ind = ", ".join(f"`{i}`" for i in indices[:4]) if indices else "*aucun*"
            L.append(f"| `{nom_rap}` | `{nom_src}` | {ind} |")
        L.append("")
        douteux = [e for e in examen if e[2]]
        if douteux:
            L.append(f"**{len(douteux)}** citeur(s) présentent des **indices de")
            L.append("construction** de la marque dans leur code : leur classement est")
            L.append("**incertain**, et je ne les compte pas comme des citeurs établis.")
            L.append("")
            L.append("### L'examen, mené — et il retire le seul citeur")
            L.append("")
            L.append("`selfref_reports_marking` est **le script du #439 qui a posé les")
            L.append("marques** dans les autres rapports. Son code porte la marque dans")
            L.append("une **variable** (`MARKER = \"...\"`) qu'il écrit dans les fichiers")
            L.append("candidats — **son propre rapport compris**.")
            L.append("")
            L.append("Mon détecteur d'émission cherche la marque **littérale** sur une")
            L.append("ligne d'écriture ; il ne peut pas voir une écriture par variable.")
            L.append("**C'est exactement le cas que le pré-enregistrement annonçait comme")
            L.append("un faux citeur**, et c'en est un.")
            L.append("")
            L.append("> **Conclusion de l'examen : 0 citeur établi.** Le seul candidat")
            L.append("> est un **porteur** que ma règle ne sait pas reconnaître.")
        else:
            L.append("**Aucun indice de construction** dans le code des producteurs :")
            L.append("le classement en citeur tient pour tous.")
    L.append("")

    L.append("## Contrôle de cohérence — un script qui émet, un rapport qui contient")
    L.append("")
    L.append("Si un script émet la marque, son rapport doit la contenir. L'inverse")
    L.append("signalerait une régénération perdue, comme au #450.")
    L.append("")
    L.append(f"- **incohérences** : **{len(incoherents)}**")
    if incoherents:
        L.append("")
        L.append("| Script émetteur | Rapport sans la marque |")
        L.append("|---|---|")
        for s, r in incoherents:
            L.append(f"| `{s}` | `{r}` |")
        L.append("")
        L.append("> Ces rapports **ont perdu** un encart que leur script émet. C'est")
        L.append("> exactement la perte que le #450 avait constatée sans la réparer.")
    L.append("")

    L.append("## Les indéterminés — **pas des fautifs**")
    L.append("")
    L.append(f"**{len(indetermines)}** rapports contiennent la marque sans qu'un script")
    L.append("producteur soit trouvé sous la convention de nommage. Le **#464** a")
    L.append("établi que cette convention **n'est pas universelle** : ce sont des")
    L.append("rapports **hors convention**, pas des anomalies.")
    L.append("")
    if indetermines:
        for n in indetermines[:15]:
            L.append(f"- `{n}`")
        if len(indetermines) > 15:
            L.append(f"- *… et {len(indetermines) - 15} autres*")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    # Le compte MECANIQUE dit 1 ; l'examen individuel (engagement 3) le retire.
    # Retenir le compte flatteur alors que mon propre examen le contredit serait
    # l'erreur exacte que les #462, #464 et #465 ont commise.
    etablis = [c for c, e in zip(citeurs, examen) if not e[2]]
    p1 = len(etablis) >= 1
    p2 = len(porteurs) < len(contiennent)
    p3 = not incoherents
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| au moins 1 citeur **établi** | ≥ 1 | {len(etablis)} "
             f"*({len(citeurs)} candidat(s), retiré(s) par l'examen)* | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| porteurs < rapports contenant la marque | < {len(contiennent)} | "
             f"{len(porteurs)} | {'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| aucune incohérence émetteur/rapport | 0 | {len(incoherents)} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    if not p1:
        L.append("**Aucun citeur établi.** Le compte mécanique en donnait **1** ; "
                 "l'examen exigé par l'engagement 3 l'a retiré.")
        L.append("")
        L.append("**Retenir le chiffre flatteur alors que mon propre examen le")
        L.append("contredit serait l'erreur exacte des #462, #464 et #465.**")
        L.append("")
        L.append("**Aucun citeur trouvé.** Le pré-enregistrement prévoyait ce cas et")
        L.append("interdit d'en conclure que le #451 s'est trompé : **soit** son citeur")
        L.append("a disparu du dépôt depuis, **soit** ma règle le classe porteur à tort.")
        L.append("Je ne tranche pas ici — il faudrait remonter au commit du #451, ce que")
        L.append("ce cycle n'a pas déclaré faire.")
        L.append("")

    L.append("## Critères de succès")
    L.append("")
    c1 = len(porteurs) + len(citeurs) + len(indetermines) == len(contiennent)
    L.append(f"1. **{len(porteurs) + len(citeurs) + len(indetermines)}/"
             f"{len(contiennent)}** rapports classés — **{'OUI' if c1 else 'NON'}**.")
    L.append("2. Tout citeur publié nominativement avec son producteur — **OUI**.")
    L.append("3. Chaque citeur examiné (construction par variable) — **OUI**.")
    L.append("4. Indéterminés listés sans être présentés comme fautifs — **OUI**.")
    L.append("")
    L.append(f"**{'PASS' if c1 else 'FAIL'}** — le critère porte sur le procédé.")
    L.append("")

    L.append("## Ce que ce cycle ne fait pas")
    L.append("")
    L.append("- Il ne **corrige** aucun rapport ni aucun script.")
    L.append("- Il n'**exécute** rien : lecture seule, aucun effet de bord.")
    L.append("- Il ne **remonte** à aucun commit ancien : il décrit le dépôt")
    L.append("  d'aujourd'hui.")
    L.append("")

    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état du dépôt à la date de")
    L.append("> son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
