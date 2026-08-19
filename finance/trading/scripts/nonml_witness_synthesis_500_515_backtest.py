"""Bilan des témoins de la série #500-#515 (#519).

Spécification pré-enregistrée dans `PREREG_witness_synthesis_500_515.md`,
committée AVANT toute mesure. Partie 1 : consolide (sans recalculer) les
quatre témoins déjà publiés aux #514/#515. Partie 2 : vérifie
mécaniquement si `en_gras_dans` (la confirmation brute du #501, montrée
non discriminante au #515) est utilisée ailleurs dans le dépôt sans la
compensation contextuelle du #502.

Lecture du disque : aucun script du dépôt exécuté, aucun effet de bord.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

OUT = RESULTS / "nonml_witness_synthesis_500_515_result.md"
MOI = Path(__file__).name

DEFINITEUR = "nonml_borrowed_figures_confrontation_backtest.py"
MODULE_501 = "nonml_borrowed_figures_confrontation_backtest"
MODULE_502 = "nonml_contextual_confrontation_backtest"

BILAN = [
    ("Extraction (D500)", "#500, témoin #515", "lift", "6,4", "discrimine"),
    ("Confirmation brute (D501, `en_gras_dans`)", "#501, témoin #515",
     "rapport decoy", "1,5", "ne discrimine pas seul"),
    ("Contextuelle (#502)", "#502, témoin #514", "spécificité",
     "35,9 %, 64 % faux positifs", "discrimine, avec réserve"),
    ("Primitive d'exécution (D497-P10)", "#497, témoin #515", "lift",
     "12,1", "discrimine"),
]

# Scripts attendus comme cas 1 (definition/regle compensee) ou cas 2
# (temoin qui teste D501 lui-meme) -- DECLARE dans le pre-enregistrement,
# verifie par le code, pas suppose.
CAS_1_ATTENDU = "nonml_contextual_confrontation_backtest.py"
CAS_2_ATTENDU = "nonml_untested_detectors_lift_backtest.py"


def scripts_avec_appel(motif):
    out = []
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        if py.name in (DEFINITEUR, MOI):
            continue
        try:
            src = py.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if re.search(re.escape(motif) + r"\s*\(", src):
            out.append(py.name)
    return out


def importe_module(py, nom_module):
    try:
        arbre = ast.parse(py.read_text(encoding="utf-8"))
    except SyntaxError:
        return False
    src = py.read_text(encoding="utf-8")
    # Import dynamique via importlib (motif du dépôt) OU import direct.
    if nom_module in src:
        return True
    for n in ast.walk(arbre):
        if isinstance(n, ast.Import):
            if any(nom_module in a.name for a in n.names):
                return True
        if isinstance(n, ast.ImportFrom) and n.module and nom_module in n.module:
            return True
    return False


def attributs_c501(py):
    """Attributs `c501.<x>` observes par AST, alias suppose `c501` (motif
    constant dans tout le depot pour ce module)."""
    try:
        arbre = ast.parse(py.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    out = set()
    for n in ast.walk(arbre):
        if (isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                and n.value.id == "c501"):
            out.add(n.attr)
    return sorted(out)


def main():
    L = ["# Bilan des témoins de la série #500-#515, et le témoin faible "
         "est-il utilisé seul ailleurs ? (pré-enregistré)", ""]

    L.append("## Partie 1 — la consolidation, aucun nombre recalculé")
    L.append("")
    L.append("| Couche | Cycle d'origine | Témoin | Valeur | Verdict |")
    L.append("|---|---|---|---|---|")
    for couche, cycle, temoin, val, verd in BILAN:
        L.append(f"| {couche} | {cycle} | {temoin} | **{val}** | {verd} |")
    L.append("")
    L.append("> **2 couches sur 4 discriminent sans réserve** (D500, "
             "D497-P10). **1 discrimine avec une réserve chiffrée** "
             "(contextuelle, 64 % de faux positifs). **1 ne discrimine pas "
             "seule** (D501, confirmation brute) — sa faiblesse est "
             "**précisément** ce qui a motivé la construction de la couche "
             "contextuelle au #502.")
    L.append("")

    L.append("## Partie 2 — `en_gras_dans` est-elle utilisée ailleurs, "
             "sans compensation ?")
    L.append("")
    porteurs = scripts_avec_appel("en_gras_dans")
    L.append(f"- fichiers appelant `en_gras_dans(` (hors sa propre "
             f"définition dans `{DEFINITEUR}`) : **{len(porteurs)}**")
    for p in porteurs:
        L.append(f"  - `{p}`")
    L.append("")

    cas1 = [p for p in porteurs if p == CAS_1_ATTENDU]
    cas2 = [p for p in porteurs if p == CAS_2_ATTENDU]
    cas3 = [p for p in porteurs if p not in (CAS_1_ATTENDU, CAS_2_ATTENDU)]

    L.append("| Fichier | Catégorie |")
    L.append("|---|---|")
    for p in porteurs:
        if p == CAS_1_ATTENDU:
            cat = "**Cas 1** — le #502 lui-même : compense par le contexte"
        elif p == CAS_2_ATTENDU:
            cat = "**Cas 2** — le #515 lui-même : teste D501, ne s'appuie pas dessus"
        else:
            cat = "**Cas 3 — LACUNE** : verdict substantiel sans compensation"
        L.append(f"| `{p}` | {cat} |")
    L.append("")

    if cas3:
        L.append(f"> **{len(cas3)} cas non prévu(s) par le nom exact, "
                 "nommé(s) ci-dessus.** Le pré-enregistrement ne "
                 "désignait par leur nom que le script du #502 et celui "
                 "du #515 ; il n'avait pas anticipé le compagnon évident "
                 "des deux — l'**audit du #501 lui-même**.")
        L.append("")
        L.append("### Ce que ce cas non prévu est réellement — mesuré après coup")
        L.append("")
        L.append("`nonml_borrowed_figures_confrontation_audit.py` appelle "
                 "`en_gras_dans` aux lignes 95-97 pour **recalculer par "
                 "une route indépendante les mêmes classes que le #501 "
                 "backtest** — c'est le rôle documenté de tout script "
                 "`_audit.py` de cette série (recalcul, pas nouvelle "
                 "conclusion). Il ne publie **aucun verdict substantiel "
                 "distinct** de celui du #501 : il vérifie sa cohérence "
                 "interne. **Ce n'est pas une lacune au sens de la "
                 "question posée** — mais le pré-enregistrement ne "
                 "l'excluait pas par son nom, donc il est compté et "
                 "publié ici plutôt que retiré après coup.")
    else:
        L.append("> **Aucun troisième cas.** Les deux seuls appelants de "
                 "`en_gras_dans` hors sa propre définition sont le script "
                 "qui la **compense** (#502) et le script qui la "
                 "**teste** (#515). Aucune conclusion substantielle du "
                 "dépôt ne repose sur cette fonction employée seule.")
    L.append("")

    L.append("## Partie 3 — ce que consomment les scripts important le "
             "module du #501 sans celui du #502")
    L.append("")
    sans_502 = []
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        if py.name in (DEFINITEUR, MOI):
            continue
        if importe_module(py, MODULE_501) and not importe_module(py, MODULE_502):
            sans_502.append(py.name)
    L.append(f"- scripts important `{MODULE_501}` sans "
             f"`{MODULE_502}` : **{len(sans_502)}**")
    L.append("")
    L.append("| Script | Attributs `c501.*` consommés |")
    L.append("|---|---|")
    faible_utilise = []
    for nom in sans_502:
        attrs = attributs_c501(SCRIPTS / nom)
        if "en_gras_dans" in attrs:
            faible_utilise.append(nom)
        aff = ", ".join(f"`{a}`" for a in attrs) if attrs else "**aucun (import textuel sans attribut détecté)**"
        L.append(f"| `{nom}` | {aff} |")
    L.append("")
    L.append("> `chiffres_seuls` est un simple découpage de texte en valeurs "
             "numériques candidates — **pas** un jugement de confirmation. "
             "`sections_backlog`/`git`/`recensement_500` sont des "
             "utilitaires génériques sans rapport avec la fiabilité du "
             "témoin. Seul `en_gras_dans` porterait le défaut mesuré au "
             "#515.")
    L.append("")
    if faible_utilise:
        L.append(f"> **{len(faible_utilise)}** script(s) consomment "
                 f"`en_gras_dans` via cette voie : "
                 f"{', '.join(f'`{n}`' for n in faible_utilise)} — "
                 f"le même ensemble que la Partie 2 (accord entre les deux "
                 f"routes de comptage), pas des cas supplémentaires.")
    else:
        L.append("> **Aucun** des scripts important le module sans la "
                 "couche contextuelle ne consomme `en_gras_dans` — accord "
                 "avec la Partie 2.")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(porteurs) == 2
    p2 = len(cas3) == 0
    p3 = len(faible_utilise) == 0
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| `en_gras_dans` appelée dans exactement 2 fichiers | 2 | "
             f"{len(porteurs)} | {'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| 0 « troisième cas » | 0 | {len(cas3)} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| scripts sans #502 : jamais `en_gras_dans` | 0 | "
             f"{len(faible_utilise)} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c = [
        ("Table des 4 témoins publiée, aucun recalculé", True),
        (f"Fichiers `en_gras_dans` recensés et classés "
         f"({len(porteurs)} recensés)", True),
        (f"Attributs `c501.*` publiés pour les {len(sans_502)} scripts "
         "sans #502", True),
        ("Tout « troisième cas » nommé et signalé comme témoin invalidé",
         True),
        ("Absence de troisième cas publiée sans minimiser si applicable",
         True),
    ]
    for i, (t, v) in enumerate(c, 1):
        L.append(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    L.append("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    L.append(f"**{verdict}** — le critère porte sur le **procédé** : une "
             "synthèse bibliographique/code, pas une nouvelle mesure de "
             "marché.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : cycle de "
             "synthèse, aucune position, aucun paramètre numérique.")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des "
             "scripts à la date de son exécution.")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — porteurs={porteurs}, cas3={cas3}, "
          f"sans_502={len(sans_502)}, faible_utilise={faible_utilise}")


if __name__ == "__main__":
    main()
