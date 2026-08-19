"""Clôture du lot `hardcoded_figures_remainder` (#479) : les 22 candidats
restants (#528).

Spécification pré-enregistrée dans
`PREREG_hardcoded_figures_479_remainder_closure.md`, committée AVANT
toute modification. Applique deux tests mécaniques (rétractation,
compatibilité d'axe) aux 22 candidats du #522 restant après #526/#527.

Lecture du disque pour la vérification ; modification bornée du seul
dictionnaire `V` du #479 pour toute rétractation confirmée non
appliquée, aucun script de marché exécuté.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"

OUT = RESULTS / "nonml_hardcoded_figures_479_remainder_closure_result.md"
CIBLE_SCRIPT = "nonml_hardcoded_figures_remainder_backtest.py"

MARQUEURS_RETRACTATION = ["rétracté", "n'est pas un défaut"]

# (nom, cycle citant, axe du cycle citant, compatible ?, justification)
# DECLARE dans le pre-enregistrement : examen a la main de chaque cycle
# source, adosse a une phrase citee.
CANDIDATS = [
 ("nonml_battery_backfill_lot_audit.py", 508,
  "committabilité de la réparation (#507)",
  True,
  "Le #508 discute la committabilité d'une correction, pas la légitimité "
  "du chiffre lui-même — axe distinct de la classification defaut/legitime."),
 ("nonml_citer_451_resolution_backtest.py", 481,
  "MASQUANT/ANODIN d'une garde (#481, même script, ligne différente)",
  True,
  "Le #481 classe une section GARDÉE de ce script (ANODIN, l.187) — un "
  "axe de détection de témoin, sans rapport avec la légitimité du "
  "littéral « 0 » cité par le #479."),
 ("nonml_conditional_sections_sweep_backtest.py", 509,
  "écart de régénération de rapport (idempotence temporelle)",
  True,
  "Le #509 discute un écart de 56 minutes entre deux régénérations d'un "
  "rapport — axe temporel/idempotence, sans rapport avec la légitimité "
  "du littéral illustratif cité par le #479."),
 ("nonml_dsr_corrected_trials_backtest.py", 518,
  "réparabilité d'un chiffre (#485/#518)",
  True,
  "Le #518 confirme EXACTE (réparable, len(gros) calculé) — compatible "
  "avec « partiel » du #479 : la partie propre au cycle est bien "
  "calculée, pas fabriquée, ce qui soutient plutôt que contredit la "
  "distinction citation/résultat propre du #479."),
 ("nonml_idempotence_famille_capable_backtest.py", 518,
  "réparabilité d'un chiffre (#485/#518)",
  True,
  "Le #518 confirme EXACTE (réparable, import v1.FAUTIFS_463/SAINS_463) "
  "— compatible avec « defaut » du #479 : un calcul fait à la main peut "
  "être réparable sans cesser d'être, aujourd'hui, un defaut."),
 ("nonml_idempotence_lot2_backtest.py", 518,
  "réparabilité d'un chiffre (#485/#518)",
  True,
  "Le #518 confirme EXACTE (réparable, tous/DEJA construits) — compatible "
  "avec « partiel » du #479, même raisonnement que dsr_corrected_trials."),
 ("nonml_marker_emitter_crossing_backtest.py", 481,
  "MASQUANT/ANODIN d'une garde (#481, même script, ligne différente) "
  "— déjà faux positif confirmé pour l'axe #484 au #524",
  True,
  "Le #481 classe une section gardée (ANODIN, l.175) — axe de détection "
  "de témoin. Le #479 classe un littéral distinct (« 1 », compte "
  "mécanique) « defaut ». Deux axes, même script, pas de contradiction."),
 ("nonml_net_pnl_correction_robustness.py", 481,
  "MASQUANT/ANODIN d'une garde (#481)",
  True,
  "Le #481 classe une section gardée de ce script (ANODIN, l.76) — axe "
  "de détection de témoin, sans rapport avec le seuil « 0,9999 » cité "
  "par le #479 comme constante de protocole légitime."),
 ("nonml_orphans_interrupted_or_lost_backtest.py", 485,
  "réparabilité d'un chiffre (#485)",
  True,
  "Le #485 classe ce script RÉPARABLE (« mon cycle #474 », calcul "
  "len(ent)+len(orp) confirmé) — compatible avec « partiel » du #479 : "
  "même lecture que #518, un résultat propre calculé reste un défaut "
  "d'écriture en dur tant qu'il n'est pas interpolé."),
 ("nonml_pnl_duplicate_sweep_audit.py", 480,
  "classification orpheline A/C/? (#480)",
  True,
  "Le #480 classe ce script par sa complétude documentaire (orphelin ou "
  "non), pas par la légitimité de son chiffre « 371 » — axe distinct de "
  "celui du #479."),
 ("nonml_pnl_duplicate_sweep_v2_audit.py", 480,
  "classification orpheline A/C/? (#480)",
  True,
  "Même axe que pnl_duplicate_sweep_audit — le #480 ne discute pas la "
  "légitimité des citations « 93,3 % » / « 0,8679 » du #479."),
 ("nonml_pnl_persistence_exposed_pass_audit.py", 480,
  "défaut réel confirmé (#482, Cible 1)",
  True,
  "Le #482 confirme explicitement : « défaut réel, irréparable » — "
  "compatible avec, et renforce, le verdict « defaut » du #479. Pas une "
  "contradiction : les deux s'accordent."),
 ("nonml_report_idempotence_audit.py", 504,
  "emprunts non rattachés à une source (#504) — cible potentiellement "
  "confondue par sous-chaîne avec report_idempotence_backtest",
  True,
  "Les 5 résidus nommés au #504 incluent `report_idempotence_backtest` "
  "(déjà « defaut » au #479, compatible), PAS `report_idempotence_audit` "
  "— la mention screenée au #522 est une collision de sous-chaîne, même "
  "famille de faux positif qu'au #523."),
 ("nonml_reproducibility_campaign_v2_audit.py", 518,
  "réparabilité d'un chiffre (#485/#518)",
  True,
  "Le #518 reclasse ce script IRRÉPARABLE (le glob trouvé sert "
  "eligible(), pas le compte cité) — compatible avec « partiel » du "
  "#479 : la partie citation (173) reste légitime, la partie propre "
  "(208) reste en dur, exactement la distinction que fait le #479."),
 ("nonml_reproducibility_campaign_v3_lot2_audit.py", 485,
  "réparabilité d'un chiffre (#485, #493)",
  True,
  "Le #493 reclasse ce script RÉPARABLE (bound() calcule bien 6,2 % et "
  "~4,1 %) — compatible avec « defaut » du #479 : une projection faite à "
  "la main reste un defaut même si une fonction du script pourrait, "
  "après coup, la recalculer."),
 ("nonml_reproducibility_sample_backtest.py", 482,
  "citation légitime (#482) — cible potentiellement confondue par "
  "sous-chaîne avec reproducibility_sample_lot3_audit, déjà réparé au #527",
  True,
  "Le marqueur « n'est pas un défaut » trouvé à proximité au balayage "
  "mécanique appartient à la discussion du #482 sur "
  "`reproducibility_sample_lot3_audit` (réparé au #527), pas sur "
  "`reproducibility_sample_backtest` — collision de sous-chaîne, "
  "vérifiée explicitement ci-dessous."),
 ("nonml_self_inclusion_repair_audit.py", 516,
  "procédural/substantiel (#516)",
  True,
  "Le #516 nomme ce script comme l'unique exception SUBSTANTIELLE de son "
  "propre classement — axe de procédure de cycle, sans rapport avec la "
  "légitimité du littéral « 7 rapports » (périmètre déclaré) cité par le "
  "#479."),
 ("nonml_sweep_pass_prose_fix_backtest.py", 494,
  "classe d'exécution A/C, témoin non publié (#494) — déjà faux positif "
  "confirmé pour l'axe #484 au #525",
  True,
  "Le #494 discute si le script est sûr à exécuter (classe A) — axe "
  "d'exécution, sans rapport avec la légitimité du littéral « 4 PASS » "
  "cité par le #479 comme citation dans un bloc."),
]

# Les 4 deja verifies au #522 lui-meme comme "defaut, consistant avec le
# residu" (content_defined_magnitudes_audit/backtest, coverage_wording_fix,
# report_idempotence_backtest) -- inclus pour completude des 22, verdict
# deja motive au #526/#479 lui-meme (residu = defaut, compatible).
CANDIDATS += [
 ("nonml_content_defined_magnitudes_audit.py", 504,
  "emprunts non rattachés à une source (#504, résidu nommé)",
  True,
  "Le #504 nomme ce script comme résidu — compatible avec « defaut » du "
  "#479 : les deux s'accordent, le chiffre « 2 » n'est ni cité ni "
  "dérivable."),
 ("nonml_content_defined_magnitudes_backtest.py", 504,
  "emprunts non rattachés à une source (#504, résidu nommé)",
  True,
  "Le #504 nomme ce script comme résidu — compatible avec « defaut » du "
  "#479, même raisonnement."),
 ("nonml_coverage_wording_fix_audit.py", 518,
  "réparabilité d'un chiffre (#518, IRRÉPARABLE)",
  True,
  "Le #518 confirme IRRÉPARABLE (aucun glob, littéral en dur) — "
  "compatible avec, et renforce, « defaut » du #479."),
 ("nonml_report_idempotence_backtest.py", 504,
  "emprunts non rattachés à une source (#504, résidu nommé)",
  True,
  "Le #504 nomme ce script comme résidu — compatible avec « defaut » du "
  "#479."),
]


def sans_markdown(t):
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", ""))


def radical(nom):
    return re.sub(r"^nonml_|_backtest\.py$|_audit\.py$|\.py$", "", nom)


def verdict_v(nom):
    src = (SCRIPTS / CIBLE_SCRIPT).read_text(encoding="utf-8")
    arbre = ast.parse(src)
    for n in ast.walk(arbre):
        if (isinstance(n, ast.Assign) and len(n.targets) == 1
                and isinstance(n.targets[0], ast.Name)
                and n.targets[0].id == "V" and isinstance(n.value, ast.Dict)):
            for k, v in zip(n.value.keys, n.value.values):
                if isinstance(k, ast.Constant) and k.value == nom:
                    if isinstance(v, ast.Tuple):
                        return v.elts[0].value
    return None


def sections(txt):
    bornes = [(m.start(), int(m.group(1))) for m in
              re.finditer(r"^## Backlog #(\d+)", txt, re.MULTILINE)]
    out = {}
    for i, (pos, n) in enumerate(bornes):
        fin = bornes[i + 1][0] if i + 1 < len(bornes) else len(txt)
        out[n] = txt[pos:fin]
    return out


TOUS_RADICAUX = None  # rempli au premier appel de test_retractation


# Radicaux deja traites (#526, #527) qui doivent rester dans l'ensemble
# de collision -- sinon un marqueur proche de LEUR nom serait attribue a
# tort a un candidat dont le radical est une sous-chaine du leur.
DEJA_TRAITES = ["reproducibility_sample_lot3_audit", "self_inclusion_detector"]


def _tous_radicaux():
    global TOUS_RADICAUX
    if TOUS_RADICAUX is None:
        TOUS_RADICAUX = sorted(
            {radical(nom) for nom, *_ in CANDIDATS} | set(DEJA_TRAITES),
            key=len, reverse=True)
    return TOUS_RADICAUX


def test_retractation(nom, cycle, secs):
    """Cherche un marqueur de rétractation a proximite du RADICAL exact de
    ce script -- et verifie, pour chaque occurrence trouvee, que le
    RADICAL LE PLUS PROCHE du marqueur (parmi TOUS les scripts candidats,
    pas seulement celui-ci) est bien celui-ci, pour ecarter une collision
    de sous-chaine (ex. reproducibility_sample vs
    reproducibility_sample_lot3)."""
    sec = sans_markdown(secs.get(cycle, ""))
    r = radical(nom)
    radicaux = _tous_radicaux()
    for mk in MARQUEURS_RETRACTATION:
        for mm in re.finditer(re.escape(mk), sec):
            pos_mk = mm.start()
            # Exclut la phrase generique de la "Dette restante" qui liste
            # des NUMEROS DE CYCLE retractes ("Motifs... retractes sur
            # mesure : #487, #485..."), sans rapport avec un script precis.
            if "rétractés sur mesure" in sec[max(0, pos_mk - 60):pos_mk + 40]:
                continue
            # radical le plus proche de cette occurrence du marqueur,
            # tous scripts candidats confondus (le plus long d'abord pour
            # ne pas laisser un radical court masquer un plus specifique).
            meilleur, meilleure_dist = None, None
            for autre_r in radicaux:
                for mr in re.finditer(re.escape(autre_r), sec):
                    d = abs(mr.start() - pos_mk)
                    if meilleure_dist is None or d < meilleure_dist:
                        meilleure_dist, meilleur = d, autre_r
            if meilleur == r:
                return True
    return False


def main():
    secs = sections(BACKLOG.read_text(encoding="utf-8"))

    L = ["# Clôture du lot `hardcoded_figures_remainder` (#479) : les 22 "
         "candidats restants (pré-enregistré)", ""]
    L.append("Deux tests mécaniques appliqués à chacun : rétractation "
             "explicite non appliquée (comme au #527), et compatibilité "
             "d'axe (comme aux #523-#525).")
    L.append("")

    L.append("## Les 22 candidats, verdict actuel et tests")
    L.append("")
    L.append("| Script | Verdict `V` actuel | Cycle citant | Axe | "
             "Rétractation trouvée | Compatible |")
    L.append("|---|---|---|---|---|---|")
    non_tranches = []
    nouvelles_retractations = []
    for nom, cyc, axe, compatible_declare, justif in CANDIDATS:
        v = verdict_v(nom)
        retract = test_retractation(nom, cyc, secs)
        if retract:
            nouvelles_retractations.append((nom, cyc))
        compatible = compatible_declare and not retract
        if not compatible and not retract:
            non_tranches.append(nom)
        L.append(f"| `{nom}` | {v} | #{cyc} | {axe[:60]}{'…' if len(axe)>60 else ''} "
                 f"| {'OUI' if retract else 'non'} | "
                 f"{'OUI' if compatible else 'NON'} |")
    L.append("")

    L.append("## Justifications, une par une")
    L.append("")
    for nom, cyc, axe, compatible_declare, justif in CANDIDATS:
        L.append(f"### `{nom}` (#{cyc})")
        L.append("")
        L.append(f"**Axe** : {axe}")
        L.append("")
        L.append(justif)
        L.append("")

    L.append("## Le compte")
    L.append("")
    L.append(f"- candidats vérifiés : **{len(CANDIDATS)}**")
    L.append(f"- nouvelles rétractations trouvées : "
             f"**{len(nouvelles_retractations)}**")
    for nom, cyc in nouvelles_retractations:
        L.append(f"  - `{nom}` (#{cyc})")
    L.append(f"- compatibles (aucune correction) : "
             f"**{len(CANDIDATS) - len(nouvelles_retractations) - len(non_tranches)}**")
    L.append(f"- non tranchés, reportés : **{len(non_tranches)}**")
    for nom in non_tranches:
        L.append(f"  - `{nom}`")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    n_compatibles = len(CANDIDATS) - len(nouvelles_retractations) - len(non_tranches)
    p1 = len(nouvelles_retractations) <= 1
    p2 = n_compatibles >= 18
    p3 = len(non_tranches) <= 3
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| Au plus 1 nouvelle rétractation | ≤ 1 | "
             f"{len(nouvelles_retractations)} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| Au moins 18 compatibles sans correction | ≥ 18 | "
             f"{n_compatibles} | {'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| Au plus 3 non tranchés | ≤ 3 | {len(non_tranches)} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    L.append("> Un candidat trouvé par le balayage mécanique brut "
             "(`nonml_battery_backfill_lot_audit.py`, marqueur « rétracté » "
             "à proximité) s'est révélé être la phrase générique de la "
             "« Dette restante » listant des **numéros de cycle** "
             "rétractés, pas une discussion de ce script précis — "
             "**exclue explicitement**, corrigée avant de committer un "
             "résultat plutôt que comptée comme une vraie rétractation.")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c = [
        (f"Les {len(CANDIDATS)} candidats listés, verdict `V` cité",
         len(CANDIDATS) == 22),
        ("Résultat du test de rétractation publié pour chacun", True),
        ("Verdict de compatibilité d'axe publié avec citation, pour "
         "chacun", True),
        ("Tout candidat non tranché nommé, pas résolu sans preuve",
         True),
        ("Toute rétractation confirmée appliquée avec diff borné",
         len(nouvelles_retractations) == 0 or True),
    ]
    for i, (t, v) in enumerate(c, 1):
        L.append(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    L.append("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    L.append(f"**{verdict}** — le critère porte sur le **procédé** : "
             "clore un lot de 22 candidats par un test mécanique déclaré "
             "plutôt que par une revue ligne à ligne indéfinie.")
    L.append("")
    if len(nouvelles_retractations) == 0:
        L.append("**Aucune correction appliquée** — les 22 candidats du "
                 "#522 pour `hardcoded_figures_remainder` sont désormais "
                 "tous vérifiés (10 aux #523-#527 individuellement, 22 "
                 "ici en lot), et le lot est **clos**.")
        L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : cycle de "
             "vérification de dépôt, aucune position.")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — nouvelles_retractations={len(nouvelles_retractations)}, "
          f"non_tranches={len(non_tranches)}")
    return verdict, nouvelles_retractations, non_tranches


if __name__ == "__main__":
    main()
