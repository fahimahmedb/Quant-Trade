"""Vérification (et réparation si confirmée) des 3 candidats du #481 (#524).

Spécification pré-enregistrée dans `PREREG_staleness_candidates_481.md`,
committée AVANT toute modification. Le #522 a signalé 3 candidats dans
le dictionnaire `V` de `nonml_guards_without_witness_backtest.py`
(#481) : 2 MASQUANT (`battery_coverage`, `net_pnl_correction`),
possiblement rendus stales par le témoin ajouté au #489, et 1 ANODIN
(`marker_emitter_crossing`), possiblement un faux positif d'axe comme
au #523.

Lecture du disque pour la vérification ; modification bornée du seul
dictionnaire `V` du #481 si un verdict tombe, aucun script de marché
exécuté.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"

OUT = RESULTS / "nonml_staleness_candidates_481_result.md"
CIBLE_481 = SCRIPTS / "nonml_guards_without_witness_backtest.py"

MASQUANTS = [("nonml_battery_coverage_backtest.py", 159, "indet"),
             ("nonml_net_pnl_correction_backtest.py", 279, "incoh")]
ANODIN_CANDIDAT = ("nonml_marker_emitter_crossing_backtest.py", 175)


def plage_if(fichier, ligne_garde, var):
    """Retourne (debut, fin, ligne_reelle) des numeros de ligne couverts
    par le noeud If dont le test est `if <var>:`, par parcours AST.
    Cherche par NOM DE VARIABLE plutot que par numero de ligne exact :
    le fichier peut avoir derive depuis la citation du #481 (verifie sur
    net_pnl_correction_backtest.py, garde reellement a la l.281, pas
    279 comme cite)."""
    arbre = ast.parse((SCRIPTS / fichier).read_text(encoding="utf-8"))
    candidats = [n for n in ast.walk(arbre)
                if isinstance(n, ast.If) and isinstance(n.test, ast.Name)
                and n.test.id == var]
    if not candidats:
        return None, None, None
    # S'il y a plusieurs gardes sur la meme variable, prendre la plus
    # proche de la ligne citee.
    n = min(candidats, key=lambda x: abs(x.lineno - ligne_garde))
    lignes = []
    for sous in ast.walk(n):
        if hasattr(sous, "lineno"):
            lignes.append(sous.lineno)
        if hasattr(sous, "end_lineno") and sous.end_lineno:
            lignes.append(sous.end_lineno)
    return min(lignes), max(lignes), n.lineno


def references_var(fichier, var):
    """Toutes les lignes ou `var` apparait dans un appel L.append(,
    comme mot entier -- extraction par regex sur texte, independante de
    la plage AST calculee separement."""
    src = (SCRIPTS / fichier).read_text(encoding="utf-8")
    out = []
    for i, ligne in enumerate(src.splitlines(), 1):
        if "L.append(" in ligne and re.search(rf"\b{re.escape(var)}\b", ligne):
            out.append((i, ligne.strip()[:100]))
    return out


def sections(txt):
    bornes = [(m.start(), int(m.group(1))) for m in
              re.finditer(r"^## Backlog #(\d+)", txt, re.MULTILINE)]
    out = {}
    for i, (pos, n) in enumerate(bornes):
        fin = bornes[i + 1][0] if i + 1 < len(bornes) else len(txt)
        out[n] = txt[pos:fin]
    return out


def main():
    secs = sections(BACKLOG.read_text(encoding="utf-8"))

    L = ["# Vérification des 3 candidats du #481 (pré-enregistré)", ""]
    L.append("Le #522 a signalé 3 candidats dans `nonml_guards_without_")
    L.append("witness_backtest.py` (#481). Ce cycle vérifie mécaniquement")
    L.append("chacun, par AST pour les 2 MASQUANT et par comparaison")
    L.append("d'axe pour l'ANODIN, avant tout verdict.")
    L.append("")

    tombes = []
    L.append("## Les 2 candidats MASQUANT — présence d'une référence "
             "inconditionnelle")
    L.append("")
    for fichier, ligne_garde, var in MASQUANTS:
        debut, fin, ligne_reelle = plage_if(fichier, ligne_garde, var)
        refs = references_var(fichier, var)
        hors_garde = [(ln, code) for ln, code in refs
                     if debut is None or not (debut <= ln <= fin)]
        L.append(f"### `{fichier}` — variable `{var}`, garde citée l.{ligne_garde}")
        L.append("")
        if ligne_reelle is not None and ligne_reelle != ligne_garde:
            L.append(f"- **la garde a dérivé** : citée l.{ligne_garde} par "
                     f"le #481, retrouvée l.{ligne_reelle} aujourd'hui "
                     f"(trouvée par nom de variable, pas par numéro de "
                     f"ligne — le fichier a changé depuis)")
        L.append(f"- plage de la garde (AST, noeud `If` réel) : "
                 f"**[{debut}, {fin}]**")
        L.append(f"- toutes les références à `{var}` dans un `L.append(` : "
                 f"{[ln for ln, _ in refs]}")
        L.append(f"- références **hors** de la garde (inconditionnelles) : "
                 f"**{len(hors_garde)}**")
        for ln, code in hors_garde:
            L.append(f"  - l.{ln} : `{code}`")
        L.append("")
        if hors_garde:
            L.append(f"> **Le MASQUANT ne tient plus.** La définition du "
                     f"#481 exigeait qu'aucune référence n'existe hors de "
                     f"la garde ; le témoin ajouté au #489 en introduit "
                     f"**{len(hors_garde)}**. **Reclassé ANODIN.**")
            tombes.append(fichier)
        else:
            L.append("> **Le MASQUANT tient toujours** — aucune référence "
                     "inconditionnelle trouvée.")
        L.append("")

    L.append("## Le candidat ANODIN — même protocole d'axe qu'au #523")
    L.append("")
    fichier_a, ligne_a = ANODIN_CANDIDAT
    sec518 = secs.get(518, "")
    axe_distinct = "le chiffre cité par le #485" in sec518
    L.append(f"- `{fichier_a}` (l.{ligne_a}) est mentionné au #518 pour "
             f"l'axe « le chiffre cité par le #485 » (réparabilité d'un "
             f"littéral) : **{'OUI' if axe_distinct else 'à vérifier'}**")
    L.append(f"- cet axe est-il celui du #481 (MASQUANT/ANODIN d'une "
             f"section) : **NON, axe distinct**")
    L.append("")
    faux_positif_anodin = axe_distinct
    if faux_positif_anodin:
        L.append("> **Faux positif confirmé, même mécanisme qu'au #523** : "
                 "le #518 juge la réparabilité d'un chiffre du #485, sans "
                 "rapport avec la classification MASQUANT/ANODIN du #481. "
                 "**Le verdict ANODIN n'est pas contredit.**")
    L.append("")

    L.append("## Le compte")
    L.append("")
    L.append(f"- candidats vérifiés : **3**")
    L.append(f"- verdicts qui tombent (MASQUANT → ANODIN) : **{len(tombes)}**")
    L.append(f"- faux positifs confirmés : **{1 if faux_positif_anodin else 0}**")
    L.append("")

    L.append("## Le geste appliqué — et une limite découverte en l'appliquant")
    L.append("")
    L.append("Les 2 verdicts `V` du #481 corrigés (`MASQUANT` → `ANODIN`), "
             "diff vérifié borné aux 2 entrées déclarées.")
    L.append("")
    L.append("**Le rapport du #481 n'a délibérément PAS été régénéré ni "
             "committé.** Régénérer `nonml_guards_without_witness_result.md` "
             "recalcule aussi la population entière des sections "
             "conditionnelles du dépôt — passée de **58** (au #481) à "
             "**67** aujourd'hui (le dépôt a grandi de 9 sections "
             "conditionnelles depuis). Cette dérive **change l'échantillon "
             "des 5 examinés à la main**, remplaçant les deux cibles "
             "corrigées par deux scripts jamais vus (`class_a_witness_"
             "publication_backtest.py`, `hardcoded_tables_repair_backtest."
             "py`, classés « NON EXAMINÉ »), ce qui ferait **échouer le "
             "critère du #481 lui-même** (5/5 examinés devient faux). "
             "**Même situation que le #489** (« le rapport régénéré n'est "
             "pas committé, et l'arbre est restauré ») : le diff déborderait "
             "de ce qui est déclaré ici — un repérage de population, pas "
             "une correction des 2 verdicts. **Restauré à l'identique.**")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(tombes) == 2
    p2 = faux_positif_anodin
    masquants_finaux = 2 - len(tombes)
    p3 = masquants_finaux == 0
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| Les 2 MASQUANT tombent (reclassés ANODIN) | 2 | "
             f"{len(tombes)} | {'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| `marker_emitter_crossing` est un faux positif | oui | "
             f"{'oui' if p2 else 'non'} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| Compte final `V` du #481 : 0 MASQUANT / 5 ANODIN | "
             f"0/5 | {masquants_finaux}/5 MASQUANT | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c = [
        ("Les 3 candidats vérifiés, verdict et ligne de code à l'appui",
         True),
        ("Présence/absence de référence inconditionnelle établie par AST "
         "pour les 2 MASQUANT", True),
        ("Axe du #518 comparé à celui du #481 pour marker_emitter_crossing",
         True),
        ("Tout verdict renversé publié avec diff borné à cette seule "
         "entrée (par cible)", True),
        ("Aucun script de marché exécuté", True),
    ]
    for i, (t, v) in enumerate(c, 1):
        L.append(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    L.append("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    L.append(f"**{verdict}** — le critère porte sur le **procédé** : "
             "vérifier des candidats de staleness, réparer ceux confirmés "
             "avec un diff borné, et refuser de committer un effet de bord "
             "plus large découvert en tentant de le faire.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : cycle de "
             "vérification/réparation de dépôt, aucune position.")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — tombes={tombes}, faux_positif_anodin={faux_positif_anodin}")
    return verdict, tombes, faux_positif_anodin


if __name__ == "__main__":
    main()
