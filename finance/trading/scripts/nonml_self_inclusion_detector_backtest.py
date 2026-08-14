"""Detecter l'auto-inclusion SANS executer (#466).

Specification pre-enregistree dans `PREREG_self_inclusion_detector.md`,
committee AVANT toute mesure.

Le #463 a trouve 2 scripts non idempotents en en rejouant 18. Le depot en
compte 318 : ce cycle lit le CODE au lieu de l'executer.

Ce script ne modifie rien et n'execute rien. Il ne repare pas non plus — la
reparation regenere des rapports, et le #450 a paye cher ce melange.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

OUT = RESULTS / "nonml_self_inclusion_detector_result.md"

# --- Verite terrain du #463, recopiee ici et epinglee ----------------------
FAUTIFS_463 = {"nonml_verdict_rule_propagation_backtest.py",
               "nonml_six_reports_regeneration_backtest.py"}
SAINS_463 = {f"nonml_{n}_backtest.py" for n in (
    "npz_report_consistency_baskets", "third_npz_schema_handling",
    "net_pnl_correction", "sweep_pass_prose_fix", "verdict_detector_fix",
    "verdict_detector_complete", "marker_emitted_by_scripts",
    "tom_decomposition_npz", "orphan_npz_inspection", "verdict_variant_decision",
    "silent_skip_decision", "dsr_corrected_trials", "battery_coverage",
    "temporal_holdout", "relative_holdout", "verdict_rule_battery")}

# --- Les regles, enoncees au pre-enregistrement ----------------------------
ECRIT = re.compile(r"\bwrite_text\s*\(")
ENUMERE = re.compile(r"RESULTS\s*\.\s*glob\s*\(|RESULTS\s*\.\s*iterdir\s*\(|"
                     r"ls-tree|ls-files|glob\.glob\s*\(")
PROTEGE_UNLINK = re.compile(r"\bunlink\s*\(")
PROTEGE_NOM = re.compile(r"!=\s*OUT\b|\bOUT\s*!=|p\s*!=\s*OUT|\bMOI\b|"
                         r"not\s+in\s+.*\bOUT\b|\.name\s*!=")


def classe(txt):
    ecrit = bool(ECRIT.search(txt))
    enumere = bool(ENUMERE.search(txt))
    if not (ecrit and enumere):
        return "hors périmètre", []
    signes = []
    if PROTEGE_UNLINK.search(txt):
        signes.append("`unlink(` sur la sortie")
    if PROTEGE_NOM.search(txt):
        signes.append("exclusion nominale")
    return ("protégé" if signes else "**signalé**"), signes


def main():
    tous = sorted(SCRIPTS.glob("nonml_*_backtest.py"))
    hors, proteges, signales = [], [], []
    for p in tous:
        try:
            t = p.read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            hors.append((p.name, f"illisible : {exc}"))
            continue
        etat, signes = classe(t)
        if etat == "hors périmètre":
            hors.append((p.name, "n'écrit pas et n'énumère pas `results/`"))
        elif etat == "protégé":
            proteges.append((p.name, signes))
        else:
            signales.append(p.name)

    sig = set(signales)
    rappel = sorted(FAUTIFS_463 & sig)
    rates = sorted(FAUTIFS_463 - sig)
    faux_pos = sorted(SAINS_463 & sig)
    connus = FAUTIFS_463 | SAINS_463
    nouveaux = sorted(sig - connus)

    L = ["# Détecter l'auto-inclusion **sans exécuter** (pré-enregistré)", ""]
    L.append("Le #463 a trouvé **2** scripts non idempotents en en rejouant **18**. Le")
    L.append(f"dépôt en compte **{len(tous)}** : les rejouer deux fois chacun est hors de")
    L.append("portée d'un cycle. Ce script **lit le code**, il n'exécute rien.")
    L.append("")

    L.append("## La calibration — avant les résultats, parce qu'elle les conditionne")
    L.append("")
    L.append("Le #463 fournit une **vérité terrain** : **2** fautifs, **16** sains.")
    L.append("")
    L.append("| | Attendu | Mesuré |")
    L.append("|---|---|---|")
    L.append(f"| **rappel** (fautifs signalés) | 2 / 2 | **{len(rappel)} / 2** |")
    L.append(f"| **faux positifs** (sains signalés) | ≤ 4 | **{len(faux_pos)} / 16** |")
    L.append("")
    if rates:
        L.append("**Cas connus MANQUÉS :**")
        L.append("")
        for n in rates:
            L.append(f"- `{n}`")
        L.append("")
        L.append("> **Le détecteur rate un défaut qu'il devait trouver. Il est")
        L.append("> inutilisable en l'état**, et tout ce qui suit doit se lire avec cette")
        L.append("> réserve — un détecteur qui manque les cas connus n'autorise aucune")
        L.append("> conclusion sur les cas inconnus.")
        L.append("")
        L.append("### Pourquoi il l'a manqué — diagnostic, sans toucher à la règle")
        L.append("")
        L.append("*Ajouté après avoir vu le résultat, et signalé comme tel.*")
        L.append("")
        L.append("`six_reports_regeneration` n'énumère **pas** `results/` par un glob :")
        L.append("il exécute d'autres scripts, puis demande à **`git status --short`**")
        L.append("ce qui a bougé. Son corpus est donc **l'état du dépôt**, pas une")
        L.append("liste de fichiers — et ma condition 2 ne prévoit que la seconde forme.")
        L.append("")
        L.append("> **L'auto-inclusion n'exige pas de parcourir un dossier.** Il suffit")
        L.append("> de demander au dépôt ce qui a changé, après avoir soi-même changé")
        L.append("> quelque chose. Ma règle, écrite en pensant aux globs, était trop")
        L.append("> étroite d'une forme entière.")
        L.append("")
        L.append("**La règle n'est pas corrigée ici** : elle a été déclarée avant mesure,")
        L.append("et l'ajuster maintenant reviendrait à la tailler sur le cas qu'elle")
        L.append("vient de rater. Une règle élargie devra être **déclarée dans un cycle")
        L.append("à part**, et **recalibrée sur la même vérité terrain**.")
        L.append("")
    elif not faux_pos:
        L.append("> **Rappel parfait et aucun faux positif — et c'est un motif de")
        L.append("> méfiance, pas de satisfaction.** Sur 18 cas, un détecteur parfait")
        L.append("> est plus souvent le signe d'une règle taillée sur les cas connus que")
        L.append("> d'une bonne heuristique. Le pré-enregistrement le disait d'avance.")
        L.append("")
    if faux_pos:
        L.append("**Faux positifs** — scripts sains pourtant signalés :")
        L.append("")
        for n in faux_pos:
            L.append(f"- `{n}`")
        L.append("")
        L.append("Ils rappellent ce que le détecteur **ne voit pas** : si le glob d'un")
        L.append("script rencontre réellement son propre fichier, et si une protection")
        L.append("écrite autrement fonctionne.")
        L.append("")
        L.append("> **Nuance que le contrôle C de l'audit impose — et elle joue en ma")
        L.append("> faveur, ce qui ne la rend pas moins due.** Ces scripts écrivent leur")
        L.append("> rapport dans le dossier qu'ils énumèrent : ils sont")
        L.append("> **structurellement exposés**. Que le #463 ne les ait pas vus dériver")
        L.append("> est une **observation**, pas une garantie — leur corpus n'a")
        L.append("> peut-être pas rencontré leur propre fichier ces jours-là.")
        L.append(">")
        L.append("> Le chiffre de faux positifs ci-dessus est donc **pessimiste**. Je le")
        L.append("> laisse tel quel : il a été défini avant mesure, et le corriger à la")
        L.append("> baisse après coup serait exactement ce que je reproche aux trois")
        L.append("> cycles précédents, à l'envers.")
        L.append("")

    L.append("## Le résultat sur tout le dépôt")
    L.append("")
    L.append(f"- scripts examinés : **{len(tous)}**")
    L.append(f"- **hors périmètre** (n'écrivent pas ou n'énumèrent pas) : **{len(hors)}**")
    L.append(f"- **protégés** : **{len(proteges)}**")
    L.append(f"- **signalés** : **{len(signales)}**")
    L.append(f"- dont **inconnus du #463** : **{len(nouveaux)}**")
    L.append("")

    L.append("## Les scripts signalés")
    L.append("")
    L.append("> **« Signalé » ne veut pas dire « défectueux ».** Seule l'exécution le")
    L.append("> prouverait, et ce cycle n'exécute rien. C'est une **liste de suspects**,")
    L.append("> à valeur de priorité pour un cycle qui, lui, les rejouerait.")
    L.append("")
    if not signales:
        L.append("**Aucun.**")
    else:
        for n in signales:
            marque = ""
            if n in FAUTIFS_463:
                marque = " — *fautif confirmé au #463*"
            elif n in SAINS_463:
                marque = " — *sain au #463, donc **faux positif***"
            L.append(f"- `{n}`{marque}")
    L.append("")

    L.append("## Les protections trouvées")
    L.append("")
    L.append(f"**{len(proteges)}** scripts portent un signe de protection. Répartition :")
    L.append("")
    par_signe = {}
    for _n, signes in proteges:
        for s in signes:
            par_signe[s] = par_signe.get(s, 0) + 1
    L.append("| Signe | Nombre |")
    L.append("|---|---|")
    for s, k in sorted(par_signe.items(), key=lambda t: -t[1]):
        L.append(f"| {s} | **{k}** |")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(rappel) == 2
    p2 = len(nouveaux) >= 5
    p3 = len(faux_pos) <= 4
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| rappel 2/2 sur les cas connus | 2 | {len(rappel)} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| ≥ 5 scripts nouveaux signalés | ≥ 5 | {len(nouveaux)} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| faux positifs ≤ 4 sur 16 | ≤ 4 | {len(faux_pos)} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")

    L.append("## Ce que ce cycle ne fait pas")
    L.append("")
    L.append("- Il ne **répare** rien. La file demandait de propager l'exclusion de soi")
    L.append("  aux deux fautifs ; **c'est reporté à un cycle déclaré**, parce que")
    L.append("  réparer **régénère leurs rapports** et que le #450 a payé cher le")
    L.append("  mélange d'une réparation et d'une mesure.")
    L.append("- Il n'**exécute** aucun script : aucun effet de bord, contrairement au")
    L.append("  #463.")
    L.append("- Il ne **prouve** aucun défaut : il **priorise** des suspects.")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c1 = len(hors) + len(proteges) + len(signales) == len(tous)
    L.append(f"1. **{len(hors) + len(proteges) + len(signales)}/{len(tous)}** scripts "
             f"classés — **{'OUI' if c1 else 'NON'}**.")
    L.append("2. Calibration publiée (rappel et faux positifs) — **OUI**.")
    L.append("3. Scripts signalés listés nominativement — **OUI**.")
    L.append("4. Aucun script modifié — **OUI** (lecture seule).")
    L.append("")
    L.append(f"**{'PASS' if c1 else 'FAIL'}** — le critère porte sur le **procédé** : un")
    L.append("détecteur qui se révèle mauvais **et le montre proprement** réussit.")
    L.append("")

    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
