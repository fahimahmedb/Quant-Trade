"""Les 11 justifications RÉPARABLE du #485 jamais relues (#518).

Spécification pré-enregistrée dans `PREREG_reparable_justifications_485.md`,
committée AVANT toute mesure -- examen à la main DÉCLARÉ compris.

Le #517 a établi que le tableau des 5 justifications IRRÉPARABLE du #485
est entièrement couvert depuis le #493. Mais le #485 classait aussi 12
figures RÉPARABLE, chacune avec sa propre justification écrite à la main.
Une seule (`battery_backfill_lot_audit`) a été relue depuis (#511, tombée).
Les 11 autres n'avaient jamais été relues. Ce cycle les relit, même forme
que le #493.

Lecture du disque : aucun script du dépôt exécuté, aucun effet de bord.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

OUT = RESULTS / "nonml_reparable_justifications_485_result.md"
DEJA_511 = "nonml_battery_backfill_lot_audit.py"

ONZE = [
    ("nonml_duplicate_sweep_coverage_audit.py",
     "`n_missing` interpolé, la ventilation porte sur l'ensemble déjà "
     "construit"),
    ("nonml_content_defined_magnitudes_audit.py",
     "l'audit énumère les importateurs pour les examiner"),
    ("nonml_content_defined_magnitudes_backtest.py",
     "mesure sur objets git que le script lit déjà (+ 1 ligne signalée "
     "par le #485 lui-même comme une estimation en prose, non réparable)"),
    ("nonml_coverage_wording_fix_audit.py",
     "un `glob` — le cas le plus trivialement réparable"),
    ("nonml_dsr_corrected_trials_backtest.py",
     "le résultat de la fusion que le script opère"),
    ("nonml_idempotence_famille_capable_backtest.py",
     "se dérive de `v1.FAUTIFS_463`/`v1.SAINS_463`, importés"),
    ("nonml_idempotence_lot2_backtest.py",
     "le script construit `tous` et `DEJA`"),
    ("nonml_marker_emitter_crossing_backtest.py",
     "le compte que ce script calcule (`douteux`)"),
    ("nonml_orphans_interrupted_or_lost_backtest.py",
     "le script calcule `len(ent) + len(orp)`"),
    ("nonml_report_idempotence_backtest.py",
     "rapport de l'univers figé #443-#460 au total, lu par `glob`"),
    ("nonml_reproducibility_campaign_v2_audit.py",
     "un `glob` sur `results/*.npz`"),
]

# --- VERDICTS DE L'EXAMEN A LA MAIN -------------------------------------
# DECLARE dans le pre-enregistrement. Chacun adosse a une ligne de code.
V = {
 "nonml_duplicate_sweep_coverage_audit.py": ("EXACTE",
  "`n_missing = len(names_scripts - names_npz)` (l.164) est une différence "
  "ensembliste calculée dans le script, puis interpolée trois fois "
  "(`f\"...est **{n_missing}**\"`, l.168 et l.176). **La justification "
  "tient à la lettre.**"),
 "nonml_content_defined_magnitudes_audit.py": ("EXACTE",
  "`f449 = grep_l(...)`, `len(f449)`, `len(instrument)`, `len(autres)` "
  "sont tous calculés par `grep_l()` (grep sur objets git) puis interpolés "
  "dans le rapport (l.90-101). **Le script énumère bien les importateurs.**"),
 "nonml_content_defined_magnitudes_backtest.py": ("EXACTE",
  "Le module définit `git()` (l.33-34) et lit les objets via `ls-tree`/"
  "`show` (l.39, 60, 67) ; `po`/`me` (porteurs/mentionneurs) en sont "
  "dérivés et interpolés à la ligne 135 (`**{v451}**`). **La mesure sur "
  "objets git existe bel et bien.** Réserve : le « 8 » de la ligne 154-155 "
  "est écrit en dur plutôt que réinterpolé depuis `po` — la même valeur "
  "apparaît donc à la fois interpolée (l.135) et littérale (l.154-155), "
  "défaut mineur de la même famille que le #499, mais qui ne change pas "
  "la dérivabilité : la ligne 154-155 duplique une valeur que le script "
  "calcule ailleurs, il ne l'invente pas. La ligne « 7 porteurs et 1 "
  "citeur » (l.165) reste, comme le #485 l'avait lui-même annoncé, une "
  "**estimation en prose non réparable — non rejugée ici**."),
 "nonml_coverage_wording_fix_audit.py": ("FAUSSE_VERDICT_TOMBE",
  "**Aucun appel `.glob(` nulle part dans le fichier.** Le script ne lit "
  "que `nonml_pnl_duplicate_sweep_result.md` (l.46) ; « 284 » (l.133) est "
  "un littéral brut dans une chaîne simple (pas de `f\"...\"`), absent "
  "aussi du fichier qu'il lit. **La justification du #485 — « un glob, le "
  "cas le plus trivialement réparable » — est fausse : ce script précis "
  "ne calcule ce chiffre par aucune voie.**"),
 "nonml_dsr_corrected_trials_backtest.py": ("EXACTE",
  "`groupes = groupes_exacts(series)` (l.81), `gros = [g for g in groupes "
  "if len(g) > 1]` (l.128), et `L.append(f\"**{len(gros)}** groupes de "
  "doublons exacts fusionnés\")` (l.129). **« fusionne 2 » est le résultat "
  "de `len(gros)`, calculé, pas tapé.**"),
 "nonml_idempotence_famille_capable_backtest.py": ("EXACTE",
  "`import nonml_self_inclusion_detector_backtest as v1` (l.23) et "
  "`DEJA = v1.FAUTIFS_463 | v1.SAINS_463 | ...` (l.48). **Correspond "
  "littéralement à la justification.**"),
 "nonml_idempotence_lot2_backtest.py": ("EXACTE",
  "`tous = sorted(p.name for p in SCRIPTS.glob(\"nonml_*_backtest.py\"))` "
  "(l.72) et `DEJA = DEJA_463 | DEJA_467` (l.36). **Les deux variables "
  "citées existent et sont construites comme décrit.**"),
 "nonml_marker_emitter_crossing_backtest.py": ("EXACTE",
  "`douteux = [e for e in examen if e[2]]` (l.169), suivi de "
  "`len(douteux)` interpolé (l.171). **Le compte cité est bien calculé "
  "par le script.**"),
 "nonml_orphans_interrupted_or_lost_backtest.py": ("EXACTE",
  "`ent = examiner(aucun_fichier)` (l.160), `orp = examiner(orphelins)` "
  "(l.161), `total = len(ent) + len(orp)` (l.433). **La somme citée par "
  "la justification est exactement celle du code.**"),
 "nonml_report_idempotence_backtest.py": ("FAUSSE_VERDICT_TOMBE",
  "**Aucun appel `.glob(` nulle part dans le fichier.** « Le dépôt compte "
  "**314** `nonml_*_backtest.py` » (l.123) est un littéral brut à "
  "l'intérieur d'une f-string qui n'interpole que `len(NOMS)`, pas 314 ; "
  "« soit **5,7 %** » (l.124) est une chaîne simple, non calculée. "
  "**Contrairement à `idempotence_lot2_backtest.py` (même famille de "
  "constat, ci-dessus), ce script ne lit jamais le dépôt pour obtenir son "
  "dénominateur — la justification du #485 est fausse, et par le même "
  "critère que le #511 a appliqué à `battery_backfill_lot_audit`** "
  "(ouvrir une source que le script n'ouvre pas n'est pas une "
  "interpolation), **le verdict ne tient pas.**"),
 "nonml_reproducibility_campaign_v2_audit.py": ("FAUSSE_VERDICT_TOMBE",
  "Le seul `.glob(` du fichier porte sur `SCRIPTS.glob(\"nonml_*_backtest."
  "py\")` (l.28), pour une fonction `eligible()` sans rapport avec le "
  "compte cité. « 208 » (l.53 et l.56) est un littéral brut, jamais issu "
  "d'un `RESULTS.glob(\"nonml_*_pnl.npz\")` que **ce script** n'exécute "
  "nulle part — seul le rapport qu'il *audite* est censé le faire. "
  "**La justification du #485 attribuait à cet audit un calcul qu'il ne "
  "fait pas ; verdict à revoir, même critère qu'au-dessus.**"),
}


def enumere(py):
    src = py.read_text(encoding="utf-8")
    out = []
    for motif, lab in ((r"\.glob\(", "`glob`"),
                       (r"\.iterdir\(", "`iterdir`"),
                       (r"\.read_text\(", "`read_text`"),
                       (r"^import nonml_|^from nonml_", "import du dépôt"),
                       (r"subprocess\.run\(\[\"git\"", "`git` (subprocess)")):
        if re.search(motif, src, re.M):
            out.append(lab)
    cst = re.findall(r"^([A-Z_]{3,})\s*=\s*\[", src, re.M)
    return out, cst


def interpolations(py):
    return len(re.findall(r"\.append\(f[\"']", py.read_text(encoding="utf-8")))


def fonctions(py):
    try:
        arbre = ast.parse(py.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    return [n.name for n in ast.walk(arbre) if isinstance(n, ast.FunctionDef)]


def main():
    L = ["# Les 11 justifications RÉPARABLE du #485 jamais relues (pré-enregistré)", ""]
    L.append("Le **#517** a établi que le tableau des **5** justifications "
             "IRRÉPARABLE du #485 est entièrement couvert depuis le #493. Le #485 "
             "classait aussi **12** figures RÉPARABLE ; une seule "
             "(`battery_backfill_lot_audit`) a été relue depuis (#511, tombée). "
             "**Les 11 autres n'avaient jamais été relues.**")
    L.append("")
    L.append(f"> `{DEJA_511[:-3]}`, tranché au #511, est **exclu** de ce cycle : il "
             "n'est pas rejugé.")
    L.append("")

    L.append("## Ce que chacun énumère — mécanique, avant toute lecture")
    L.append("")
    L.append("| Script | Énumère | Constantes en dur | Interpolations | Fonctions |")
    L.append("|---|---|---|---|---|")
    for nom, _j in ONZE:
        py = SCRIPTS / nom
        en, cst = enumere(py)
        it, fn = interpolations(py), fonctions(py)
        L.append(f"| `{nom}` | {', '.join(en) if en else '**rien**'} | "
                 f"{', '.join('`' + c + '`' for c in cst) if cst else '—'} | "
                 f"**{it}** | {len(fn)} |")
    L.append("")

    L.append("## Les verdicts, un par un")
    L.append("")
    L.append("**Écrits à la main après lecture, chacun adossé à une ligne de code.**")
    L.append("")
    tombes, fausses = [], []
    for nom, just in ONZE:
        etat, motif = V.get(nom, ("NON EXAMINÉ", "—"))
        etiq = {"EXACTE": "**JUSTIFICATION EXACTE**",
                "FAUSSE_VERDICT_SURVIT": "**JUSTIFICATION FAUSSE, verdict survivant**",
                "FAUSSE_VERDICT_TOMBE": "**JUSTIFICATION FAUSSE, VERDICT À REVOIR**"
                }.get(etat, "**NON EXAMINÉ**")
        if etat.startswith("FAUSSE"):
            fausses.append(nom)
        if etat == "FAUSSE_VERDICT_TOMBE":
            tombes.append(nom)
        L.append(f"### `{nom}` — {etiq}")
        L.append("")
        L.append(f"Justification du #485, **verbatim** : « {just} »")
        L.append("")
        L.append(motif)
        L.append("")

    L.append("## Le compte")
    L.append("")
    L.append(f"- justifications **exactes** : **{len(ONZE) - len(fausses)} / "
             f"{len(ONZE)}**")
    L.append(f"- justifications **fausses** : **{len(fausses)}**")
    L.append(f"- **verdicts réparables qui tombent** (reclassés IRRÉPARABLE) : "
             f"**{len(tombes)}**")
    for n in tombes:
        L.append(f"  - `{n}`")
    L.append("")
    if tombes:
        L.append("### Le compte courant du #485 est corrigé une troisième fois")
        L.append("")
        L.append("| | #485 | #493 | #511 | Ici |")
        L.append("|---|---|---|---|---|")
        L.append(f"| irréparables | 5 | 4 | 5 | **{5 + len(tombes)}**|")
        L.append(f"| réparables | 12 | 13 | 12 | **{12 - len(tombes)}** |")
        L.append("")
        L.append("> **Ma prédiction 2 annonçait qu'au plus 2 tomberaient. Elle est "
                 f"réfutée : {len(tombes)} tombent.** Les trois partagent le même "
                 "défaut — un chiffre publié en prose, sans aucun `.glob(` ni lecture "
                 "de dépôt dans le fichier qui le publie — exactement le critère que "
                 "le **#511** avait déjà appliqué à `battery_backfill_lot_audit`, "
                 "appliqué ici de façon identique, pas assoupli ni durci après avoir "
                 "vu le résultat.")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(fausses) >= 1
    p2 = len(tombes) <= 2
    p3 = V.get("nonml_coverage_wording_fix_audit.py", ("",))[0] == "EXACTE"
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| ≥ 1 justification fausse | ≥ 1 | {len(fausses)} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| au plus 2 verdicts tombent | ≤ 2 | {len(tombes)} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| `coverage_wording_fix_audit` exacte | exacte | "
             f"{'exacte' if p3 else 'FAUSSE'} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    if not p3:
        L.append("**La prédiction 3 est la plus instructive : réfutée.** Le #485 "
                 "désignait ce cas comme *« le plus trivialement réparable de la "
                 "liste »*, précisément parce qu'il semblait le plus évident à l'œil. "
                 "**C'est celui-là qui ne contient aucun calcul du tout** — le "
                 "chiffre le plus \"évidemment un glob\" est un pur littéral.")
        L.append("")
    if not p2:
        L.append("**La prédiction 2 est réfutée** — 3 tombent, pas au plus 2. Publié "
                 "tel quel, sans ajuster le seuil après mesure.")
        L.append("")

    L.append("## Critères de succès")
    L.append("")
    c3 = all(V.get(n, ("NON EXAMINÉ",))[0] != "NON EXAMINÉ" for n, _j in ONZE)
    L.append(f"1. Les **{len(ONZE)}** nommés, justification citée verbatim — **OUI**.")
    L.append(f"2. **{len(ONZE)}/{len(ONZE)}** examinés, chacun adossé à une ligne "
             f"de code — **{'OUI' if c3 else 'NON'}**.")
    L.append(f"3. Tout verdict renversé publié, compte du #485 corrigé — "
             + ("**OUI**" if tombes else "**sans objet**") + ".")
    L.append("4. `content_defined_magnitudes_backtest.py` traité en deux parties, "
             "sans rejuger la partie déjà tranchée — **OUI**.")
    L.append(f"5. `{DEJA_511[:-3]}` exclu explicitement — **OUI**.")
    L.append("")
    verdict = "PASS" if c3 else "FAIL"
    L.append(f"**{verdict}** — le critère porte sur le **procédé** : un cycle qui "
             "relit ses propres verdicts et publie les chutes, y compris quand elles "
             "sont plus nombreuses qu'annoncé.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : aucune position, aucun "
             "paramètre de stratégie. **Aucun script du dépôt n'a été exécuté.**")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la "
             "date de son exécution.")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"{verdict} — exactes={len(ONZE)-len(fausses)} fausses={len(fausses)} "
          f"tombes={len(tombes)} -> reparables 12 -> {12-len(tombes)}")
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
