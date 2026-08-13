"""Audit de l'inventaire de protocole (#431).

Spécification pré-enregistrée dans `PREREG_protocol_inventory.md`.

Inspection **individuelle** des écarts que le contrôle E a comptés
mécaniquement, et consignation des deux abstentions annoncées d'avance.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REPO = ROOT.parent.parent
OUT = RESULTS / "nonml_protocol_inventory_audit.md"

# Les 19 du controle E, inspectes un par un (lecture du depot).
E_CATEGORIES = {
    "cycle ML — hors univers non-ML, rapport nommé `ml_*`": [
        "ml_crossmarket_pooling", "ml_exogenous_features_rates_crossmarket",
        "ml_meta_labeling_logitl2_ndx", "ml_regularized_architecture",
    ],
    "lockbox OOS — pré-enregistrement scellé, résultat publié sous un autre nom": [
        "cash_rate_correction_44_crossmarket_oos_lockbox",
        "cash_rate_correction_44_oos_lockbox",
        "diversification_bond_overlay_oos_lockbox",
        "ndx_defensive_oos_lockbox",
    ],
    "correction « same-bar » — rapport groupé sous un nom d'ensemble": [
        "leaders_calendar_overlays_same_bar_correction",
        "leaders_overlays_same_bar_correction",
        "lowvol_trend_vol_targeting_same_bar_correction",
        "sma200_overlays_same_bar_correction",
    ],
    "document de protocole ou de synthèse, sans backtest attendu": [
        "dispersion_battery_caduc_et_guide_v3",
        "meilleurs_candidats_guide_deploiement_v2",
        "protocole_regle_10_taux_realiste_cash",
    ],
    "extension d'Étape D — résultat sous `etape_D_*`": [
        "etape_d_v3_add_149", "etape_d_v3_add_crossmarket",
        "etape_d_v3_bond_diversification",
    ],
    "ce cycle même — artefact créé après le passage du contrôle": [
        "protocol_inventory",
    ],
}


def main():
    L = ["# Audit — inventaire vérifié de la dette de protocole (pré-enregistré)", ""]
    L.append("Inspection **individuelle** des écarts comptés mécaniquement, et consignation des")
    L.append("deux abstentions annoncées avant toute mesure.")
    L.append("")

    # --- Inspection du contrôle E ----------------------------------------
    L.append("## Contrôle E — les 19 écarts, inspectés un par un")
    L.append("")
    L.append("Le compte brut était **19**. Le pré-enregistrement annonçait qu'il ne se conclurait")
    L.append("pas mécaniquement. Lecture faite, ils se répartissent en **six** catégories, et")
    L.append("**aucune n'est un cycle abandonné** :")
    L.append("")
    L.append("| Catégorie | Nombre |")
    L.append("|---|---|")
    total = 0
    for cat, names in E_CATEGORIES.items():
        L.append(f"| {cat} | **{len(names)}** |")
        total += len(names)
    L.append(f"| **total** | **{total}** |")
    L.append("")
    for cat, names in E_CATEGORIES.items():
        L.append(f"**{cat}** :")
        L.append("")
        for n in names:
            L.append(f"- `{n}`")
        L.append("")
    L.append("Le contrôle E cherchait des `PREREG` **abandonnés** — déclarés puis jamais")
    L.append("exécutés. Il n'en trouve **aucun**. Les 19 sont des cycles menés à terme dont le")
    L.append("rapport porte un nom différent du pré-enregistrement, ce que le contrôle ne")
    L.append("pouvait pas savoir seul. **Faux positifs : 19/19.**")
    L.append("")

    # --- Les deux abstentions --------------------------------------------
    L.append("## Les deux abstentions annoncées — et tenues")
    L.append("")
    L.append("### 1. Aucun pré-enregistrement rétroactif")
    L.append("")
    L.append("Le contrôle B ne laisse **aucun** résultat sans pré-enregistrement une fois les")
    L.append("variantes résolues. Il n'y avait donc rien à antidater — mais l'engagement tenait")
    L.append("indépendamment du résultat, et il aurait tenu si le compte avait été non nul.")
    L.append("")
    L.append("### 2. Aucun assouplissement du vérificateur anti-cheat")
    L.append("")
    L.append("Le contrôle A confirme le seul cas connu : `log_return_compounding_audit` porte")
    L.append("**ÉCHEC — protocole violé**, faute de pré-enregistrement. Son script déclare dans")
    L.append("sa docstring être un audit de code, « aucun degré de liberté de calibrage, aucun")
    L.append("critère de succès à optimiser ».")
    L.append("")
    L.append("Les deux lectures possibles, et pourquoi je n'ai tranché ni l'une ni l'autre :")
    L.append("")
    L.append("- **Faux positif** — un audit de code n'a pas de paramètre à choisir après coup,")
    L.append("  donc le pré-enregistrement n'y protège de rien. Plausible, et c'est ce que le")
    L.append("  script affirme de lui-même.")
    L.append("- **Violation réelle** — la règle ne prévoit pas d'exception, et la première")
    L.append("  exception est celle qui ouvre la porte aux suivantes.")
    L.append("")
    L.append("**Rendre le vérificateur tolérant créerait exactement la faille qu'il existe pour")
    L.append("fermer** : tout cycle futur pourrait se déclarer exempt dans sa propre docstring,")
    L.append("c'est-à-dire s'auto-délivrer sa dispense. Je ne modifie donc pas le vérificateur,")
    L.append("et je n'écris pas non plus le pré-enregistrement manquant.")
    L.append("")
    L.append("> **Porté à l'arbitrage de l'utilisateur**, au même titre que `n_trials` (#421).")
    L.append("> Si une exception doit exister, elle devrait être **énumérée dans un fichier")
    L.append("> versionné** — ajouter une entrée devient alors un acte visible et relisible,")
    L.append("> pas une dispense que le script s'accorde à lui-même.")
    L.append("")

    # --- Conclusion -------------------------------------------------------
    L.append("## Conclusion — ce que l'inventaire a réellement trouvé")
    L.append("")
    L.append("| Contrôle | Compte brut | Après inspection |")
    L.append("|---|---|---|")
    L.append("| A — anti-cheat non CONFORME | 1 | **1, porté à l'arbitrage** |")
    L.append("| B — résultat sans PREREG | 5 | **0** (variantes résolues) |")
    L.append("| C — PASS sans batterie | 33 | **6** strictement postérieurs à la Règle 9 |")
    L.append("| D — source `data/` absente | 0 | **0** |")
    L.append("| E — PREREG sans artefact | 19 | **0** (19/19 faux positifs) |")
    L.append("")
    L.append("**Une dette réelle a été trouvée** : les **6** PASS publiés strictement après")
    L.append("l'introduction de la Règle 9 sans avoir été soumis à la batterie de validation.")
    L.append("C'est une dette de **protocole**, pas de calcul : leur verdict de niveau 1 est")
    L.append("acquis, mais le second filtre que le backlog s'impose ne leur a pas été appliqué.")
    L.append("")
    L.append("Deux nuances, dites plutôt que tues :")
    L.append("")
    L.append("1. **17 candidats supplémentaires** datent du **jour même** où la Règle 9 est")
    L.append("   apparue. Rien ne permet de dire s'ils l'ont précédée de quelques heures. Ils")
    L.append("   sont comptés à part, ni blanchis ni chargés.")
    L.append("2. L'un des 6, `capitulation_gate_floor_sweep`, est un **diagnostic et non une")
    L.append("   stratégie** — son PASS est un faux positif de détection, établi au #427. La")
    L.append("   dette réelle porte donc sur **5** candidats, à confirmer par lecture avant")
    L.append("   toute exécution de batterie.")
    L.append("")
    L.append("Le cycle n'avait rien fabriqué d'avance : il pouvait légitimement conclure « rien")
    L.append("d'actionnable ». Il conclut l'inverse, et c'est le contrôle C — le seul dont je")
    L.append("n'avais fait aucune prédiction — qui l'a fourni.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
