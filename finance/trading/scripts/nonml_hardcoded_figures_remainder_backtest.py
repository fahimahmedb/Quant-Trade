"""Les rapports non examines du #476 (#479).

Specification pre-enregistree dans `PREREG_hardcoded_figures_remainder.md`,
committee AVANT toute mesure.

Le #476 avait trouve 35 rapports portant un chiffre litteral et n'en avait
examine que 5 -- les plus charges -- en ecrivant lui-meme que son taux ne se
generalisait pas. Ce cycle lit les restants et rend le premier compte COMPLET.

Lecture du disque : aucun script execute, aucun effet de bord.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

OUT = RESULTS / "nonml_hardcoded_figures_remainder_result.md"
MOI = "hardcoded_figures_remainder"
REF_476 = {"affectes": 35, "examines": 5, "defauts": 3}

SUFFIXES = [("_result.md", "_backtest.py"), ("_audit.md", "_audit.py"),
            ("_robustness.md", "_robustness.py")]
# Les trois regles du #476, REPRISES SANS MODIFICATION.
GRAS = re.compile(r"\*\*-?\d[\d  ]*(?:[,.]\d+)?\s*(?:%|€|bps)?\*\*")
INTERPOLE = re.compile(r"f[\"']|\.format\(|%\s*[sd]|\{[^}]*\}|\"\s*\+|\+\s*\"|str\(")
ECRIT = re.compile(r"\.append\s*\(|\.write\s*\(|write_text\s*\(|print\s*\(")

DEJA_476 = {"nonml_protocol_inventory_audit.py",
            "nonml_marker_emitted_by_scripts_backtest.py",
            "nonml_repo_magnitudes_recount_backtest.py",
            "nonml_citer_451_definition_backtest.py",
            "nonml_duplicate_sweep_coverage_audit.py"}

# --- VERDICTS DE L'EXAMEN INDIVIDUEL ------------------------------------
# ECRITS A LA MAIN apres lecture de chacune des 53 lignes. Aucune regle ne
# les produit. "defaut" = litteral presente comme resultat mesure par ce
# cycle-la (forme du #451, etablie au #473). "partiel" = le script melange
# citation et resultat propre sur les memes lignes.
V = {
 "nonml_battery_backfill_lot_audit.py": ("defaut",
  "« son overlay **0,00 %** du temps » et « reste **1** candidat hors de "
  "portée » sont **deux résultats de ce cycle-là**, écrits en dur."),
 "nonml_citer_451_resolution_backtest.py": ("legitime",
  "« le **0** du #469 » — citation d'un cycle antérieur."),
 "nonml_conditional_sections_sweep_backtest.py": ("legitime",
  "« le lecteur voit « divergents : **0** » » — un **exemple illustratif** "
  "en prose, pas une mesure."),
 "nonml_content_defined_magnitudes_audit.py": ("defaut",
  "« **2** des importateurs sont… » — compte établi par cet audit, en dur."),
 "nonml_content_defined_magnitudes_backtest.py": ("defaut",
  "« au commit du #451, **8** fichiers contiennent la phrase, et ma règle en "
  "classe **8** comme porteurs », puis « il vaut probablement **7** porteurs "
  "et **1** citeur ». **Trois mesures et une estimation**, toutes en dur — "
  "et le cycle dit pourtant « vérifié plutôt que supposé »."),
 "nonml_coverage_wording_fix_audit.py": ("defaut",
  "« examine réellement les **284** scripts […] 0 illisible » — vérification "
  "de cet audit, écrite en dur."),
 "nonml_dsr_corrected_trials_backtest.py": ("partiel",
  "« Le balayage du #445 trouvait **3** groupes » est une citation ; « ce "
  "cycle en fusionne **2** » est **son propre résultat**, en dur. Les deux "
  "dans la même phrase, sans que rien ne les distingue."),
 "nonml_hardcoded_figures_sweep_backtest.py": ("legitime",
  "Les quatre littéraux sont la citation du #473 et les **exemples** de "
  "littéraux légitimes que le cycle donne lui-même (« critère : **25 %** », "
  "« **5 bps** aller-retour »). **Ma règle compte comme littéraux les "
  "exemples de littéraux** — ironie signalée, pas défaut."),
 "nonml_idempotence_famille_capable_backtest.py": ("defaut",
  "« le taux observé était d'environ **10 %**, soit **0,3** défaut attendu » "
  "— un calcul fait de tête et publié comme tel."),
 "nonml_idempotence_lot2_backtest.py": ("partiel",
  "« **0** était réellement défectueux » cite le #467 (légitime) ; « dix "
  "scripts sur **296** non éprouvés, c'est **3,4 %** » est une statistique "
  "de ce cycle, en dur."),
 "nonml_marker_emitter_crossing_backtest.py": ("defaut",
  "« Le compte mécanique en donnait **1** » — **le #469 écrit en dur son "
  "propre compte**, celui-là même dont les #472 et #473 ont ensuite cherché "
  "l'origine dans le code."),
 "nonml_net_pnl_correction_robustness.py": ("legitime",
  "« Le seuil du balayage reste **0,9999** » — constante de protocole."),
 "nonml_orphan_npz_inspection_backtest.py": ("legitime",
  "« annoncé par le #442 […] : **20** » — citation explicite."),
 "nonml_orphans_interrupted_or_lost_backtest.py": ("partiel",
  "« Le #464 avait compté **10** […] et **24** » est une citation. Mais "
  "« Sur 33 objets examinés, **1** correspond à du travail annoncé et "
  "introuvable » est **mon propre résultat au #474, écrit en dur**. **Je "
  "commets le défaut que je mesure**, deux cycles après l'avoir nommé."),
 "nonml_pnl_duplicate_sweep_audit.py": ("defaut",
  "« Correction retenue : 1 essai surnuméraire, soit 372 → **371** » — "
  "conclusion chiffrée de cet audit, en dur."),
 "nonml_pnl_duplicate_sweep_v2_audit.py": ("legitime",
  "« Le #414 mesurait **93,3 %** […] et une corrélation de **0,8679** » — "
  "deux citations attribuées."),
 "nonml_pnl_persistence_exposed_pass_audit.py": ("defaut",
  "Un tableau entier — « candidats mesurés | 33 | **42** », « détectés non "
  "mesurés | 29 | **20** », « dont portant un PASS | 10 | **0** » — écrit à "
  "la main. **Même forme que `protocol_inventory_audit` au #476.**"),
 "nonml_pnl_persistence_lot5_audit.py": ("legitime",
  "« Écart toléré, fixé avant calcul : **0** » — seuil pré-enregistré."),
 "nonml_report_idempotence_audit.py": ("legitime",
  "Les quatre littéraux — **8** rapports, **8** écritures, **3** passages, "
  "**296** scripts — citent les grandeurs du backtest audité et son "
  "protocole, dans une section de **limites**."),
 "nonml_report_idempotence_backtest.py": ("defaut",
  "« soit **5,7 %** » — pourcentage calculé par ce cycle, publié en dur."),
 "nonml_reproducibility_campaign_v2_audit.py": ("partiel",
  "« Le rapport annonçait **173** fichiers » est une citation ; « il y en a "
  "**208** aujourd'hui » est **la mesure de cet audit**, en dur — et c'est "
  "précisément le chiffre qui fonde son verdict."),
 "nonml_reproducibility_campaign_v3_lot2_audit.py": ("defaut",
  "« 24 tirages de plus feraient passer la borne de **6,2 %** à **~4,1 %** » "
  "— une projection calculée à la main."),
 "nonml_reproducibility_sample_backtest.py": ("legitime",
  "« Les lots #416-#427 ont vérifié **44** rapports » — citation."),
 "nonml_reproducibility_sample_lot2_backtest.py": ("legitime",
  "« La borne annoncée **avant** de mesurer était de **8,0 %** » — valeur "
  "pré-enregistrée, rappelée."),
 "nonml_reproducibility_sample_lot3_audit.py": ("defaut",
  "Un tableau de résultats en dur — « scripts de backtest non-ML | **284** », "
  "« couverture non-ML | **73.2 %** ». **Détail supplémentaire** : `73.2` "
  "emploie le point décimal, contre la virgule partout ailleurs — signe que "
  "la ligne a été tapée, non produite."),
 "nonml_self_inclusion_detector_backtest.py": ("legitime",
  "« Le #463 a trouvé **2** scripts non idempotents en en rejouant **18** », "
  "« **2** fautifs, **16** sains » — citations du #463, dont le script "
  "déclare par ailleurs les listes nominatives."),
 "nonml_self_inclusion_detector_v2_audit.py": ("legitime",
  "« Il éprouve **6** scripts sur les 320 », « **3** passages » — grandeurs "
  "de protocole, dans une section de limites."),
 "nonml_self_inclusion_repair_audit.py": ("legitime",
  "« restaurer les **7** rapports » — périmètre déclaré du cycle audité."),
 "nonml_sessions_column_backfill_audit.py": ("legitime",
  "« Écart toléré […] : **0** » est un seuil ; « les **16** candidats du lot "
  "5 » est un **périmètre d'entrée**, pas un résultat."),
 "nonml_sweep_basket_schema_support_audit.py": ("legitime",
  "« Le pré-enregistrement annonçait **3** candidats panier » — citation."),
 "nonml_sweep_pass_prose_fix_backtest.py": ("legitime",
  "« > **4** PASS sont **les deux** candidats… » — à l'intérieur d'un bloc "
  "de citation."),
 "nonml_tom_decomposition_npz_robustness.py": ("legitime",
  "« Le seuil du dépôt reste **0,9999** » — constante de protocole."),
}


def producteur(nom_md):
    for a, b in SUFFIXES:
        if nom_md.endswith(a):
            return SCRIPTS / f"{nom_md[:-len(a)]}{b}"
    return None


def litteraux(src):
    return [(i, l.strip()) for i, l in enumerate(src.splitlines(), 1)
            if ECRIT.search(l) and GRAS.search(l) and not INTERPOLE.search(l)]


def main():
    vus, affectes = set(), {}
    for p in sorted(RESULTS.glob("nonml_*.md")):
        if p.name.endswith("_anti_cheat.md") or MOI in p.name:
            continue
        py = producteur(p.name)
        if not (py and py.exists()) or py.name in vus:
            continue
        vus.add(py.name)
        lits = litteraux(py.read_text(encoding="utf-8"))
        if lits:
            affectes[py.name] = lits

    restants = {k: v for k, v in affectes.items() if k not in DEJA_476}
    classe = {k: V.get(k, ("non examiné", "—")) for k in restants}
    defauts = [k for k in restants if classe[k][0] == "defaut"]
    partiels = [k for k in restants if classe[k][0] == "partiel"]
    legitimes = [k for k in restants if classe[k][0] == "legitime"]
    inconnus = [k for k in restants if classe[k][0] == "non examiné"]

    fr = lambda x: f"{x:.1f}".replace(".", ",")   # noqa: E731
    ecart = len(affectes) - REF_476["affectes"]

    L = ["# Les rapports **non examinés** du #476 (pré-enregistré)", ""]
    L.append("Le **#476** avait trouvé **35** rapports portant un chiffre littéral et")
    L.append("n'en avait examiné que **5** — les plus chargés — en écrivant lui-même")
    L.append("que son taux **ne se généralisait pas**. **Ce cycle lit les restants**,")
    L.append("et rend le premier compte **complet** de la série.")
    L.append("")

    L.append("## La population, re-dérivée")
    L.append("")
    L.append("| | #476 | Ici | Écart |")
    L.append("|---|---|---|---|")
    L.append(f"| rapports affectés | {REF_476['affectes']} | **{len(affectes)}** | "
             f"**{ecart:+d}** |")
    L.append(f"| déjà examinés au #476 | {REF_476['examines']} | "
             f"**{len(DEJA_476)}** | — |")
    L.append(f"| **restants, examinés ici** | — | **{len(restants)}** | — |")
    L.append("")
    if ecart:
        L.append("> **L'effectif a monté.** Les cycles **#477** et **#478** ont été")
        L.append("> écrits depuis, et leurs propres scripts portent des littéraux — ils")
        L.append("> entrent donc dans la population qu'ils contribuent à mesurer. **Un")
        L.append("> compte de dépôt est daté** (#436-#438), et le chiffre publié ici est")
        L.append("> celui d'aujourd'hui.")
        L.append("")
    L.append(f"Je m'exclus de ma propre population (`{MOI}`) — règle des **#447/#463**,")
    L.append("appliquée avant mesure.")
    L.append("")

    L.append("## Le verdict, un par un")
    L.append("")
    L.append("**Écrits à la main après lecture de chaque ligne.** Aucune règle ne les")
    L.append("produit : c'est exactement ce qu'une règle ne sait pas faire.")
    L.append("")
    etiq = {"defaut": "**DÉFAUT**", "partiel": "**PARTIEL**",
            "legitime": "légitime", "non examiné": "**NON EXAMINÉ**"}
    for nom in sorted(restants):
        etat, motif = classe[nom]
        L.append(f"### `{nom}` — {etiq[etat]}")
        L.append("")
        L.append("```python")
        for i, ligne in restants[nom][:4]:
            L.append(f"{i}:{ligne[:112]}")
        if len(restants[nom]) > 4:
            L.append(f"... et {len(restants[nom]) - 4} autres")
        L.append("```")
        L.append("")
        L.append(motif)
        L.append("")

    L.append("## Le compte")
    L.append("")
    L.append(f"- **DÉFAUTS pleins** : **{len(defauts)}**")
    L.append(f"- **PARTIELS** *(citation et résultat propre mêlés)* : "
             f"**{len(partiels)}**")
    L.append(f"- **légitimes** : **{len(legitimes)}**")
    if inconnus:
        L.append(f"- **non examinés** : **{len(inconnus)}** — "
                 + ", ".join(f"`{n}`" for n in inconnus))
    L.append("")
    tot_def = len(defauts) + len(partiels) + REF_476["defauts"]
    L.append("### Consolidé sur toute la population")
    L.append("")
    L.append("| Origine | Défauts (pleins + partiels) | Examinés |")
    L.append("|---|---|---|")
    L.append(f"| #476 *(les 5 plus chargés)* | {REF_476['defauts']} | "
             f"{REF_476['examines']} |")
    L.append(f"| **#479** *(le reste)* | **{len(defauts) + len(partiels)}** | "
             f"**{len(restants)}** |")
    L.append(f"| **total** | **{tot_def}** | "
             f"**{len(restants) + REF_476['examines']}** |")
    L.append("")
    L.append("> **Ce total n'est plus un taux d'échantillon : c'est un dénombrement.**")
    L.append("> Toute la population a été lue. C'est le premier chiffre de cette série")
    L.append("> qui ne demande aucune extrapolation.")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    n_def = len(defauts) + len(partiels)
    p1 = n_def >= 3
    p2 = len(legitimes) >= 20
    p3 = tot_def <= 8
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| ≥ 3 défauts parmi les restants | ≥ 3 | {n_def} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| ≥ 20 légitimes *(sur 30 annoncés, {len(restants)} réels)* | ≥ 20 | "
             f"{len(legitimes)} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| total consolidé ≤ 8 défauts | ≤ 8 | {tot_def} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    if not p3:
        L.append("**Les prédictions 2 et 3 sont réfutées, et dans le mauvais sens.**")
        L.append(f"J'annonçais au plus **8** défauts au total ; il y en a **{tot_def}**.")
        L.append("Le défaut du #451, que trois cycles avaient traité comme une")
        L.append("singularité, est en réalité **un usage répandu** dans ce dépôt.")
        L.append("")
    L.append("> **Et j'en fais partie.** `orphans_interrupted_or_lost` — **mon propre")
    L.append("> cycle #474** — écrit en dur « Sur 33 objets examinés, **1** correspond")
    L.append("> à du travail annoncé et introuvable ». **Je commets le défaut que je")
    L.append("> mesure, deux cycles après l'avoir nommé.** Aucune circonstance")
    L.append("> atténuante : le #473 l'avait déjà décrit, et je l'ai reproduit.")
    L.append("")

    L.append("## Ce que cela change à la lecture du #451")
    L.append("")
    L.append("Le #473 concluait : *« la leçon utile est sur ce que coûte un nombre")
    L.append("publié sans le code qui le produit »*. Ce cycle en donne la mesure :")
    L.append(f"**{tot_def} occurrences** sur toute la population, dont deux tableaux")
    L.append("entiers de résultats tapés à la main.")
    L.append("")
    L.append("**Le #451 n'était pas fautif — il était ordinaire.** Ce qui l'a rendu")
    L.append("coûteux n'est pas d'avoir écrit un nombre à la main, c'est que **trois")
    L.append("cycles ont ensuite cherché dans le code un calcul qui n'existait pas**.")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c2 = not inconnus
    c4 = all(restants[n] for n in defauts + partiels)
    L.append(f"1. Population re-dérivée, écart signalé (**{ecart:+d}**), les 5 du #476")
    L.append("   déclarés et exclus — **OUI**.")
    L.append(f"2. **{len(restants) - len(inconnus)}/{len(restants)}** examinés avec")
    L.append(f"   ligne verbatim et verdict — **{'OUI' if c2 else 'NON'}**.")
    L.append("3. Total consolidé publié, part du #476 distinguée — **OUI**.")
    L.append(f"4. Aucun défaut compté sans sa ligne publiée — "
             f"**{'OUI' if c4 else 'NON'}**.")
    L.append("")
    L.append(f"**{'PASS' if (c2 and c4) else 'FAIL'}** — le critère porte sur le")
    L.append("**procédé**.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : aucune position, aucun")
    L.append("paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"affectes={len(affectes)} restants={len(restants)} "
          f"defauts={len(defauts)} partiels={len(partiels)} "
          f"legitimes={len(legitimes)} inconnus={len(inconnus)} total={tot_def}")
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
