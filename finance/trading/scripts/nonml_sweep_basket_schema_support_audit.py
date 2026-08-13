"""Audit de l'extension du volet B au schéma panier (#425).

Spécification pré-enregistrée dans `PREREG_sweep_basket_schema_support.md`,
committée avant toute modification du balayage.

Trois contrôles, tous fixés avant calcul :

1. **Non-régression** — les 55 activations déjà mesurées au schéma indiciel
   doivent rester identiques au bit près.
2. **Validation** — l'activation récupérée par division doit retrouver le
   chiffre déjà publié par le candidat, à **1 point de pourcentage** près.
   Seuls les rapports publiant une grandeur *comparable* entrent dans ce
   contrôle ; voir plus bas, c'est le point délicat du cycle.
3. **Couverture** — publiée avant et après.
"""
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = RESULTS / "nonml_sweep_basket_schema_support_audit.md"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonml_capitulation_gate_floor_sweep_backtest as sweep  # noqa: E402

TOLERANCE_POINTS = 1.0  # FIXÉE AVANT CALCUL, pré-enregistrement #425

# Activations mesurées avant l'extension, relevées sur le balayage inchangé.
BEFORE_JSON = Path(__file__).resolve().parents[0] / "_sweep_activation_before.json"

# Chiffre publié COMPARABLE à « exposition > 1,0× », relevé par lecture des
# rapports. `frac_at_floor` est le complément direct de la grandeur mesurée ;
# « Overlay actif X % » ne l'est PAS (voir la section « ce que le
# pré-enregistrement avait mal spécifié »).
PUBLISHED_COMPARABLE = {
    # candidat : (grandeur publiée en %, nature, activation attendue en %)
    "momentum_consistency_trend_vol_targeting_15_overlay": (79.0, "plancher 1,0× 79,0 % du temps", 21.0),
}

# Chiffre publié NON comparable : mesure l'ouverture de la porte, pas
# l'exposition. Listé pour que l'absence de contrôle soit visible, pas dissoute.
PUBLISHED_NOT_COMPARABLE = {
    "lowvol_trend_vol_targeting_overlay": "Overlay actif 61,5 % (tendance haussière)",
    "momentum_consistency_trend_vol_targeting_overlay": "Overlay actif 72,8 % (tendance haussière)",
    "winners_trend_vol_targeting_overlay": "Overlay actif 61,1 % (tendance haussière)",
    "winners_trend_vol_targeting_overlay_pit_universe": "Overlay actif 67,0 %",
}


def main():
    buf = io.StringIO()
    with redirect_stdout(buf):
        structured, measured, unmeasured, inactive, empty_pass = sweep.main()

    by_name = {m[0]: m for m in measured}
    n_basket = sum(1 for m in measured if m[3] == "panier")
    n_index = len(measured) - n_basket

    before = json.loads(BEFORE_JSON.read_text(encoding="utf-8"))

    # --- Contrôle 1 : non-régression -------------------------------------
    regressions, disparus = [], []
    for name, act_before in before.items():
        if name not in by_name:
            disparus.append(name)
            continue
        act_after = by_name[name][1]
        if act_after != act_before:
            regressions.append((name, act_before, act_after))

    # --- Contrôle 2 : validation contre chiffre publié -------------------
    validations = []
    for name, (published, nature, expected) in PUBLISHED_COMPARABLE.items():
        if name not in by_name:
            validations.append((name, expected, None, None, "non mesuré"))
            continue
        got = 100.0 * by_name[name][1]
        gap = abs(got - expected)
        validations.append((name, expected, got, gap, "OK" if gap <= TOLERANCE_POINTS else "ÉCHEC"))

    gaps = [v[3] for v in validations if v[3] is not None]
    max_gap = max(gaps) if gaps else None
    validation_ok = bool(gaps) and max_gap <= TOLERANCE_POINTS

    L = ["# Audit — lecture du schéma panier par le volet B du balayage #415 (pré-enregistré)", ""]
    L.append("Cycle d'**outillage**. Aucune stratégie évaluée, aucun verdict recalculé,")
    L.append("aucun paramètre de stratégie touché.")
    L.append("")

    # --- Ce que le pré-enregistrement avait mal spécifié ------------------
    L.append("## Deux écarts au pré-enregistrement, signalés avant les résultats")
    L.append("")
    L.append("### 1. Le nombre de candidats panier était faux")
    L.append("")
    L.append("Le pré-enregistrement annonçait **3** candidats panier parmi les 7 non mesurés,")
    L.append(f"chiffre repris du #424 sans re-vérification. Le décompte direct en donne **{n_basket}**.")
    L.append("La prédiction chiffrée « couverture 55 → 58 » était donc construite sur un")
    L.append("décompte inexact ; je le publie plutôt que d'ajuster la prédiction après coup.")
    L.append("")
    L.append("### 2. Le contrôle de validation visait la mauvaise grandeur")
    L.append("")
    L.append("Le pré-enregistrement voulait comparer l'activation récupérée au chiffre publié")
    L.append("« Overlay actif X % du temps ». **Ces deux grandeurs ne mesurent pas la même chose.**")
    L.append("Lecture des scripts : « Overlay actif » vaut `trend_aligned.mean()`, la fraction de")
    L.append("séances où la **porte** est ouverte ; l'activation du balayage est la fraction de")
    L.append("séances où l'**exposition dépasse 1,0×**. Une porte ouverte laisse passer une")
    L.append("exposition qui reste au plancher quand la volatilité est déjà à la cible.")
    L.append("")
    L.append("La tolérance de **1 point n'est pas modifiée**. Le contrôle est appliqué là où la")
    L.append("comparaison est définie — les rapports publiant `plancher 1,0× X % du temps`, dont")
    L.append("le complément est exactement la grandeur mesurée. Les autres sont listés comme")
    L.append("**non contrôlables** plutôt que comparés à une grandeur qui ne leur correspond pas.")
    L.append("")
    L.append(f"- candidats panier avec chiffre publié **comparable** : **{len(PUBLISHED_COMPARABLE)}**")
    L.append(f"- candidats panier dont le chiffre publié est **non comparable** : "
             f"**{len(PUBLISHED_NOT_COMPARABLE)}**")
    L.append("")
    for n, why in sorted(PUBLISHED_NOT_COMPARABLE.items()):
        L.append(f"- `{n}` — {why} : mesure la porte, pas l'exposition.")
    L.append("")

    # --- Contrôle 2 ------------------------------------------------------
    L.append("## Contrôle 2 — validation contre un chiffre déjà publié")
    L.append("")
    L.append(f"> Tolérance fixée avant calcul : **{TOLERANCE_POINTS:.0f} point de pourcentage**.")
    L.append("")
    L.append("| Candidat | Attendu (rapport) | Récupéré (division) | Écart | Verdict |")
    L.append("|---|---|---|---|---|")
    for name, expected, got, gap, status in validations:
        g = f"{got:.2f} %" if got is not None else "—"
        e = f"{gap:.2f} pt" if gap is not None else "—"
        L.append(f"| `{name}` | {expected:.1f} % | {g} | {e} | {status} |")
    L.append("")
    if validation_ok:
        L.append(f"**Contrôle passé** — écart maximal **{max_gap:.2f} point**, sous la tolérance.")
        L.append("La récupération de l'exposition par division retrouve un chiffre produit")
        L.append("indépendamment par le script du candidat, à partir de la variable `exposure`")
        L.append("elle-même. L'identité `ov = exposition × bh` tient sur données réelles.")
    elif gaps:
        L.append(f"**Contrôle ÉCHOUÉ** — écart maximal **{max_gap:.2f} point**, au-dessus de la")
        L.append("tolérance. L'identité `ov = exposition × bh` ne tient pas comme supposé : les")
        L.append("activations panier ci-dessous ne sont pas fiables et le pré-enregistrement")
        L.append("prévoyait que ce soit le résultat principal du cycle.")
    else:
        L.append("**Contrôle non exécutable** — aucun candidat panier ne publie de grandeur")
        L.append("comparable.")
    L.append("")
    L.append("Un seul candidat porte ce contrôle. C'est peu, et je ne le présente pas comme")
    L.append("davantage : il valide la **méthode** de récupération, pas chacun des résultats.")
    L.append("")

    # --- Contrôle 1 ------------------------------------------------------
    L.append("## Contrôle 1 — non-régression sur les activations déjà mesurées")
    L.append("")
    L.append(f"- activations relevées avant l'extension : **{len(before)}**")
    L.append(f"- candidats disparus du balayage : **{len(disparus)}**")
    L.append(f"- activations **modifiées** : **{len(regressions)}**")
    L.append("")
    if regressions:
        L.append("| Candidat | Avant | Après |")
        L.append("|---|---|---|")
        for n, a, b in regressions:
            L.append(f"| `{n}` | {100*a:.4f} % | {100*b:.4f} % |")
        L.append("")
        L.append("**Régression détectée** — l'extension a touché la branche indicielle. Bloquant.")
    else:
        L.append("**0 régression.** L'extension n'a touché que la branche panier.")
    L.append("")

    # --- Contrôle 3 ------------------------------------------------------
    L.append("## Contrôle 3 — couverture du volet B")
    L.append("")
    L.append("| | Avant | Après |")
    L.append("|---|---|---|")
    L.append(f"| candidats structurés (volet A) | {len(structured)} | {len(structured)} |")
    L.append(f"| **mesurés** (volet B) | {len(before)} | **{len(measured)}** |")
    L.append(f"| dont schéma indiciel | {len(before)} | {n_index} |")
    L.append(f"| dont schéma panier | 0 | **{n_basket}** |")
    L.append(f"| non mesurés | {len(structured) - len(before)} | **{len(unmeasured)}** |")
    L.append("")
    if unmeasured:
        L.append("Restent non mesurés, faute de `.npz` — pas d'une limite d'outil :")
        L.append("")
        for n in unmeasured:
            L.append(f"- `{n}`")
        L.append("")

    # --- Effet sur le diagnostic -----------------------------------------
    L.append("## Effet sur le diagnostic du balayage")
    L.append("")
    basket_rows = sorted([m for m in measured if m[3] == "panier"], key=lambda t: t[1])
    L.append("| Candidat panier | Exposition > 1,0× | Inactif (< 2 %) | Verdict au rapport |")
    L.append("|---|---|---|---|")
    for n, a, v, s, e in basket_rows:
        L.append(f"| `{n}` | {100*a:.2f} % | {'**OUI**' if a < sweep.INACTIVE_MAX else 'non'} | {v} |")
    L.append("")
    new_inactive = [m for m in inactive if m[3] == "panier"]
    new_empty = [m for m in empty_pass if m[3] == "panier"]
    L.append(f"- nouveaux candidats **structurellement inactifs** : **{len(new_inactive)}**")
    L.append(f"- nouveaux **PASS vides** : **{len(new_empty)}**")
    L.append("")
    if new_empty:
        for n, a, v, s, e in new_empty:
            L.append(f"- `{n}` — activation {100*a:.2f} %, rapport : {v}. À confirmer par lecture.")
        L.append("")
    else:
        L.append("Aucun PASS vide révélé par l'extension : ces candidats prennent des positions")
        L.append("effectivement distinctes de leur référence. Le cas isolé du #410 le reste.")
        L.append("")

    # --- Observation a posteriori ----------------------------------------
    L.append("### Observation faite après calcul — la distinction porte/exposition était réelle")
    L.append("")
    L.append("Signalée comme **post-hoc**, elle n'est pas un contrôle réussi : la classification")
    L.append("« comparable / non comparable » a été fixée avant de lancer le calcul.")
    L.append("")
    L.append("| Candidat | « Overlay actif » publié (porte) | Exposition > 1,0× mesurée | Écart |")
    L.append("|---|---|---|---|")
    for name, why in sorted(PUBLISHED_NOT_COMPARABLE.items()):
        if name not in by_name:
            continue
        pub = float(why.split("actif ")[1].split(" %")[0].replace(",", "."))
        got = 100.0 * by_name[name][1]
        L.append(f"| `{name}` | {pub:.1f} % | {got:.2f} % | {abs(got - pub):.2f} pt |")
    L.append("")
    L.append("Trois des quatre écarts dépassent largement le point de pourcentage. Avoir comparé")
    L.append("l'activation à ces chiffres, comme le pré-enregistrement le prévoyait, aurait")
    L.append("produit un **échec de validation qui n'aurait rien dit de la méthode** — seulement")
    L.append("que deux grandeurs différentes diffèrent. Le quatrième coïncide au centième près :")
    L.append("sur ce candidat, la porte ouverte implique une exposition au-dessus du plancher.")
    L.append("C'est une propriété de ce candidat, pas une validation de plus.")
    L.append("")

    # --- Conclusion ------------------------------------------------------
    ok = (not regressions) and validation_ok and n_basket > 0
    L.append("## Conclusion")
    L.append("")
    L.append("| Critère pré-enregistré | Attendu | Obtenu | |")
    L.append("|---|---|---|---|")
    L.append(f"| candidats panier mesurés | 3 (décompte faux) | {n_basket} | "
             f"{'✔' if n_basket else '✘'} |")
    L.append(f"| écart maximal à un chiffre publié | ≤ 1 pt | "
             f"{f'{max_gap:.2f} pt' if max_gap is not None else '—'} | "
             f"{'✔' if validation_ok else '✘'} |")
    L.append(f"| régressions | 0 | {len(regressions)} | {'✔' if not regressions else '✘'} |")
    L.append(f"| couverture publiée | oui | {len(measured)}/{len(structured)} | ✔ |")
    L.append("")
    if ok:
        L.append(f"**Extension validée.** Le volet B couvre désormais **{len(measured)}/{len(structured)}**")
        L.append(f"candidats au lieu de {len(before)}. La prédiction déductive « écart ≤ 1 point,")
        L.append("0 régression » est **vérifiée** ; sa partie chiffrée « couverture 55 → 58 »")
        L.append(f"est **fausse dans son chiffre** — la couverture atteint {len(measured)}, parce que le")
        L.append("décompte de départ était erroné, non parce que la méthode a mieux marché.")
    else:
        L.append("**Extension NON validée** — voir les contrôles en échec ci-dessus.")
    L.append("")
    L.append("Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
