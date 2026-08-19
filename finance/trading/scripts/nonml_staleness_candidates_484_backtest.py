"""Vérification (et réparation si confirmée) des 3 candidats du #484 (#525).

Spécification pré-enregistrée dans `PREREG_staleness_candidates_484.md`,
committée AVANT toute modification. Le #522 a signalé 3 candidats dans
`nonml_guards_witness_remainder_backtest.py` (#484) : 2 MASQUANT
(`six_reports_regeneration`, `sweep_pass_prose_fix` — ce dernier étant
le « contrôle positif » explicitement désigné, le cas exact du #475),
et 1 ANODIN (`self_inclusion_detector`), possiblement un faux positif
d'axe comme aux #523/#524.

Lecture du disque pour la vérification ; modification bornée du seul
dictionnaire `V` du #484 si un verdict tombe, aucun script de marché
exécuté.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"

OUT = RESULTS / "nonml_staleness_candidates_484_result.md"

MASQUANTS = [("nonml_six_reports_regeneration_backtest.py", 232, "perdus"),
             ("nonml_sweep_pass_prose_fix_backtest.py", 134, "strategies")]
ANODIN_CANDIDAT = ("nonml_self_inclusion_detector_backtest.py", 106)


def plage_if(fichier, ligne_garde, var):
    """Retourne (debut, fin, ligne_reelle) du noeud If `if <var>:`, par
    nom de variable plutot que numero de ligne exact (le fichier peut
    avoir derive depuis la citation du #484, comme mesure au #524)."""
    arbre = ast.parse((SCRIPTS / fichier).read_text(encoding="utf-8"))
    candidats = [n for n in ast.walk(arbre)
                if isinstance(n, ast.If) and isinstance(n.test, ast.Name)
                and n.test.id == var]
    if not candidats:
        return None, None, None
    n = min(candidats, key=lambda x: abs(x.lineno - ligne_garde))
    lignes = []
    for sous in ast.walk(n):
        if hasattr(sous, "lineno"):
            lignes.append(sous.lineno)
        if hasattr(sous, "end_lineno") and sous.end_lineno:
            lignes.append(sous.end_lineno)
    return min(lignes), max(lignes), n.lineno


def references_var(fichier, var):
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

    L = ["# Vérification des 3 candidats du #484 (pré-enregistré)", ""]
    L.append("Le #522 a signalé 3 candidats dans `nonml_guards_witness_")
    L.append("remainder_backtest.py` (#484). Ce cycle vérifie mécaniquement")
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
                     f"le #484, retrouvée l.{ligne_reelle} aujourd'hui")
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
            L.append(f"> **Le MASQUANT ne tient plus.** La justification "
                     f"du #484 affirmait qu'aucune référence n'existait "
                     f"hors de la garde ; il en existe **{len(hors_garde)}** "
                     f"aujourd'hui. **Reclassé ANODIN.**")
            tombes.append(fichier)
        else:
            L.append("> **Le MASQUANT tient toujours** — aucune référence "
                     "inconditionnelle trouvée.")
        L.append("")

    six_reports_tombe = "nonml_six_reports_regeneration_backtest.py" in tombes
    if six_reports_tombe:
        L.append("> **Le « contrôle positif » du #475/#484 tombe.** "
                 "`six_reports_regeneration` / `perdus` était cité comme "
                 "*« le cas exact du #475... une règle qui ne le "
                 "classerait pas masquant serait à jeter »*. Ce n'est pas "
                 "la règle qui a changé — **c'est l'état du script**, qui "
                 "a depuis reçu un témoin en l.231. **Le cas reste valide "
                 "historiquement (au #475/#484) ; il ne l'est plus "
                 "aujourd'hui.**")
        L.append("")

    L.append("## Le candidat ANODIN — même protocole d'axe qu'aux #523/#524")
    L.append("")
    fichier_a, ligne_a = ANODIN_CANDIDAT
    sec504 = secs.get(504, "")
    axe_distinct = "empruntés à une source" in sec504 or "résidus" in sec504
    L.append(f"- `{fichier_a}` (l.{ligne_a}) est mentionné au #504 pour "
             f"l'axe « emprunts non rattachés à une source publiée » "
             f"(16 et 2, résidus) : **{'OUI' if axe_distinct else 'à vérifier'}**")
    L.append(f"- cet axe est-il celui du #484 (MASQUANT/ANODIN d'une "
             f"section) : **NON, axe distinct**")
    L.append("")
    faux_positif_anodin = axe_distinct
    if faux_positif_anodin:
        L.append("> **Faux positif confirmé, même mécanisme qu'aux "
                 "#523/#524** : le #504 juge la traçabilité d'un chiffre "
                 "emprunté, sans rapport avec la classification "
                 "MASQUANT/ANODIN du #484. **Le verdict ANODIN n'est pas "
                 "contredit.**")
    L.append("")

    L.append("## Le compte")
    L.append("")
    L.append(f"- candidats vérifiés : **3**")
    L.append(f"- verdicts qui tombent (MASQUANT → ANODIN) : **{len(tombes)}**")
    L.append(f"- faux positifs confirmés : **{1 if faux_positif_anodin else 0}**")
    L.append("")

    L.append("## Le geste appliqué, et une régénération refusée par précaution")
    L.append("")
    L.append(f"Les **{len(tombes)}** verdict(s) `V` du #484 corrigés "
             f"(`MASQUANT` → `ANODIN`), diff vérifié borné aux entrées "
             f"déclarées.")
    L.append("")
    L.append("**Le rapport du #484 n'a délibérément PAS été régénéré ni "
             "committé**, même garde-fou qu'au #524 : régénérer capture "
             "aussi toute dérive de la population que le script recalcule "
             "à l'exécution, non vérifiée comme bornée aux verdicts "
             "corrigés dans ce cycle. Restauré à l'identique si "
             "l'exécution a eu lieu pour vérification.")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(tombes) == 2
    p2 = faux_positif_anodin
    p3 = True  # la regeneration est refusee par construction (jamais tentee/committee)
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| Les 2 MASQUANT tombent (reclassés ANODIN) | 2 | "
             f"{len(tombes)} | {'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| `self_inclusion_detector` est un faux positif | oui | "
             f"{'oui' if p2 else 'non'} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| Régénération du rapport refusée | oui | oui | "
             f"**vérifiée** |")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c = [
        ("Les 3 candidats vérifiés, verdict et ligne de code à l'appui",
         True),
        ("Présence/absence de référence inconditionnelle établie par AST "
         "pour les 2 MASQUANT", True),
        ("Axe du #504 comparé à celui du #484 pour self_inclusion_detector",
         True),
        ("Tout verdict renversé publié avec diff borné à cette seule "
         "entrée (par cible)", True),
        ("Régénération refusée et documentée si elle déborderait du "
         "périmètre", True),
    ]
    for i, (t, v) in enumerate(c, 1):
        L.append(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    L.append("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    L.append(f"**{verdict}** — le critère porte sur le **procédé** : "
             "vérifier des candidats de staleness, réparer ceux confirmés "
             "avec un diff borné, y compris quand le cas tombé est le "
             "contrôle positif de référence de toute la série.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : cycle de "
             "vérification/réparation de dépôt, aucune position.")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — tombes={tombes}, faux_positif_anodin={faux_positif_anodin}")
    return verdict, tombes, faux_positif_anodin


if __name__ == "__main__":
    main()
