"""Propagation de la regle du #448 aux autres consommateurs (#449).

Specification pre-enregistree dans `PREREG_verdict_rule_propagation.md`,
committee AVANT toute modification et toute mesure.

Le compte de « 8 scripts a corriger » venait d'un grep — donc d'une recherche
en sous-chaine, l'instrument meme dont les #446-#448 ont montre qu'il confond
le code et le discours sur le code. Il est ici **recompte par lecture**.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(SCRIPTS))

import nonml_verdict  # noqa: E402
import nonml_pnl_duplicate_sweep_backtest as sw  # noqa: E402

OUT = RESULTS / "nonml_verdict_rule_propagation_result.md"

# Classement PAR LECTURE de chaque occurrence (cf. rapport).
CONVERTIS = [
    "nonml_capitulation_gate_floor_sweep_backtest.py",
    "nonml_empty_pass_basket_extension_backtest.py",
    "nonml_empty_pass_requalification_backtest.py",
    "nonml_pnl_persistence_lot4_audit.py",
    "nonml_protocol_inventory_backtest.py",
    "nonml_sameday_timestamp_resolution_backtest.py",
]
VARIANTE = [("nonml_sessions_column_backfill_audit.py",
             '`"**PASS" in text` **seul**, sans le littéral `"PASS (niveau 1)"`',
             "Le convertir **ajouterait** le littéral : ce serait redéfinir sa "
             "sémantique, pas corriger un défaut. Laissé tel quel, comme le "
             "pré-enregistrement l'annonçait.")]
HISTORIQUES = [
    ("nonml_verdict_detector_fix_backtest.py", "`verdict_avant()` — reproduit "
     "l'ancienne règle pour la **mesurer** (#447)"),
    ("nonml_verdict_detector_fix_audit.py", "`ancienne()` — même rôle, dans "
     "l'audit du #447"),
    ("nonml_pnl_duplicate_sweep_backtest.py", "un **commentaire** qui cite "
     "l'ancienne règle ; le code, lui, est converti depuis le #448"),
    ("nonml_sweep_pass_prose_fix_audit.py", "audit **figé sur l'état du #446** :"
     " il vérifie des noms publiés sous la règle de l'époque"),
]


def ancienne(t):
    if "**PASS" in t or "PASS (niveau 1)" in t:
        return "PASS"
    if "**FAIL" in t:
        return "FAIL"
    return "indéterminé"


def main():
    rapports = sorted(RESULTS.glob("nonml_*_result.md"))

    # --- Equivalence module <-> balayage, sur tout le depot ----------------
    div = [p.name for p in rapports
           if any(nonml_verdict.porte_verdict(p.read_text(encoding="utf-8"), m)
                  != sw.porte_verdict(p.read_text(encoding="utf-8"), m)
                  for m in ("PASS", "FAIL"))]

    # --- Effet du changement sur le corpus commun --------------------------
    change = []
    for p in rapports:
        t = p.read_text(encoding="utf-8")
        a, b = ancienne(t), nonml_verdict.verdict_of(t)
        if a != b:
            change.append((p.name[len("nonml_"):-len("_result.md")], a, b))

    numstat = subprocess.run(
        ["git", "diff", "HEAD", "--numstat", "--", "finance/trading/scripts/"],
        cwd=REPO, capture_output=True, text=True).stdout.strip().splitlines()
    stats = {ln.split("\t")[2].split("/")[-1]: (ln.split("\t")[0], ln.split("\t")[1])
             for ln in numstat if "\t" in ln}
    confine = all(stats.get(f, ("0", "0")) == ("3", "1") for f in CONVERTIS)

    L = ["# Propagation de la règle du #448 aux autres consommateurs (pré-enregistré)", ""]
    L.append("**Cycle de MODIFICATION**, cinquième après les #445 → #448.")
    L.append("")

    L.append("## Critère 1 — le compte de « 8 scripts » était-il juste ?")
    L.append("")
    L.append("Il venait d'un `grep`, donc d'une **recherche en sous-chaîne** — l'instrument")
    L.append("même dont ces cycles ont montré qu'il confond le code et le discours sur le")
    L.append("code. Recompté **par lecture** :")
    L.append("")
    L.append("| Catégorie | Nombre |")
    L.append("|---|---|")
    L.append(f"| **usages** convertis | **{len(CONVERTIS)}** |")
    L.append(f"| **variante** non convertible | **{len(VARIANTE)}** |")
    L.append(f"| **réimplémentations / citations** laissées intactes | **{len(HISTORIQUES)}** |")
    L.append("")
    L.append(f"**Le compte de 8 était faux.** Il y a **{len(CONVERTIS)} usages** réels ; le")
    L.append("reste n'avait pas à être touché. **Prédiction vérifiée** : j'attendais moins")
    L.append("de 8, sans savoir combien.")
    L.append("")

    L.append("### Les usages convertis")
    L.append("")
    L.append("Tous sont une fonction `verdict_of` qui **décide** d'un classement :")
    L.append("")
    for f in CONVERTIS:
        i, d = stats.get(f, ("—", "—"))
        L.append(f"- `{f}` — diff **+{i} / −{d}**")
    L.append("")

    L.append("### La variante, laissée telle quelle")
    L.append("")
    for f, quoi, pourquoi in VARIANTE:
        L.append(f"- `{f}` : {quoi}.")
        L.append(f"  {pourquoi}")
    L.append("")
    L.append("Le pré-enregistrement avait annoncé ce cas de figure **avant** de le")
    L.append("rencontrer, et prescrit de ne pas y toucher. C'est appliqué.")
    L.append("")

    L.append("### Les réimplémentations et citations, laissées intactes")
    L.append("")
    for f, quoi in HISTORIQUES:
        L.append(f"- `{f}` — {quoi}")
    L.append("")
    L.append("> **Une entorse, signalée.** Le pré-enregistrement ne déclarait que deux")
    L.append("> catégories : *usage* et *réimplémentation historique*.")
    L.append("> `nonml_sweep_pass_prose_fix_audit.py` n'est ni l'un ni l'autre au sens")
    L.append("> strict — il n'reproduit pas l'ancienne règle pour la comparer, il **audite")
    L.append("> un cycle passé avec la règle de son époque**. Le convertir ferait re-vérifier")
    L.append("> le #446 sous une règle qui n'existait pas alors, et son audit deviendrait")
    L.append("> faussement NON CONFORME. Je le classe **historique** parce que l'effet est le")
    L.append("> même — y toucher détruit la mesure qu'il porte — et je signale l'écart plutôt")
    L.append("> que d'ajouter une troisième catégorie après coup.")
    L.append("")

    L.append("## Critère 2 — équivalence du module et du balayage")
    L.append("")
    L.append(f"- rapports comparés : **{len(rapports)}**")
    L.append(f"- verdicts divergents entre `nonml_verdict` et le balayage : **{len(div)}**")
    L.append("")
    if div:
        for n in div[:10]:
            L.append(f"- divergent : `{n}`")
        L.append("")
    else:
        L.append("**Aucune divergence** : le module est bien la règle du #448, pas une")
        L.append("variante qui lui ressemble.")
        L.append("")

    L.append("## Critère 3 — diff confiné aux régions déclarées")
    L.append("")
    L.append(f"Chaque script converti : **+3 / −1** — la zone d'imports (déclarée d'avance")
    L.append("cette fois) et la ligne de l'occurrence.")
    L.append("")
    L.append(f"**Confiné : {'OUI' if confine else 'NON'}.**")
    L.append("")
    L.append("Aux #447 et #448, la zone d'imports **n'était pas** déclarée, ce qui m'avait")
    L.append("obligé à écrire la règle en clair puis en opérations de chaînes pour rester")
    L.append("dans le régime. La leçon a été tirée **avant** d'écrire, pas après avoir buté")
    L.append("dessus — et le code s'en trouve plus simple, pas plus contorsionné.")
    L.append("")

    L.append("## Critère 5 — l'effet du changement, mesuré")
    L.append("")
    L.append(f"Sur les **{len(rapports)}** rapports du dépôt, **{len(change)}** changent de")
    L.append("classe entre l'ancienne règle et celle du module :")
    L.append("")
    if change:
        L.append("| Rapport | Ancienne règle | Règle #448 |")
        L.append("|---|---|---|")
        for n, a, b in change:
            L.append(f"| `{n}` | {a} | **{b}** |")
        L.append("")
    L.append("Chacun de ces rapports était **mal classé** par les six consommateurs")
    L.append("convertis. C'est la mesure de ce que la propagation corrige.")
    L.append("")

    L.append("## Ce que ce cycle ne fait pas — dit d'avance, et tenu")
    L.append("")
    L.append("**Aucun rapport publié n'est régénéré.** Les régénérer mélangerait l'effet de")
    L.append("la règle et la dérive du dépôt — le #445 a montré que **9 lignes sur 10**")
    L.append("d'un rapport régénéré ne venaient pas de la modification — et six fois plutôt")
    L.append("qu'une.")
    L.append("")
    L.append("Ce cycle crée donc **sciemment** un écart entre le code corrigé et les")
    L.append("rapports publiés par ces six scripts. **Cet écart est le prix d'une mesure")
    L.append("lisible**, il est inscrit à la dette, et le régénérer proprement est un cycle")
    L.append("à lui seul.")
    L.append("")

    ok = confine and not div
    L.append("## Verdict")
    L.append("")
    L.append("| | Critère | État |")
    L.append("|---|---|---|")
    L.append("| 1 | chaque occurrence classée par lecture | ✔ |")
    L.append(f"| 2 | équivalence module / balayage | {'✔' if not div else '**NON**'} |")
    L.append(f"| 3 | diff confiné aux régions déclarées | {'✔' if confine else '**NON**'} |")
    L.append("| 4 | aucune réimplémentation historique modifiée | voir audit |")
    L.append("| 5 | effet publié par script | ✔ |")
    L.append("")
    L.append(f"### **{'PASS' if ok else 'FAIL'}** *(sous réserve du critère 4, vérifié par l'audit)*")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
