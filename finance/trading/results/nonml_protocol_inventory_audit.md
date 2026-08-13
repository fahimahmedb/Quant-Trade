# Audit — inventaire vérifié de la dette de protocole (pré-enregistré)

Inspection **individuelle** des écarts comptés mécaniquement, et consignation des
deux abstentions annoncées avant toute mesure.

## Contrôle E — les 19 écarts, inspectés un par un

Le compte brut était **19**. Le pré-enregistrement annonçait qu'il ne se conclurait
pas mécaniquement. Lecture faite, ils se répartissent en **six** catégories, et
**aucune n'est un cycle abandonné** :

| Catégorie | Nombre |
|---|---|
| cycle ML — hors univers non-ML, rapport nommé `ml_*` | **4** |
| lockbox OOS — pré-enregistrement scellé, résultat publié sous un autre nom | **4** |
| correction « same-bar » — rapport groupé sous un nom d'ensemble | **4** |
| document de protocole ou de synthèse, sans backtest attendu | **3** |
| extension d'Étape D — résultat sous `etape_D_*` | **3** |
| ce cycle même — artefact créé après le passage du contrôle | **1** |
| **total** | **19** |

**cycle ML — hors univers non-ML, rapport nommé `ml_*`** :

- `ml_crossmarket_pooling`
- `ml_exogenous_features_rates_crossmarket`
- `ml_meta_labeling_logitl2_ndx`
- `ml_regularized_architecture`

**lockbox OOS — pré-enregistrement scellé, résultat publié sous un autre nom** :

- `cash_rate_correction_44_crossmarket_oos_lockbox`
- `cash_rate_correction_44_oos_lockbox`
- `diversification_bond_overlay_oos_lockbox`
- `ndx_defensive_oos_lockbox`

**correction « same-bar » — rapport groupé sous un nom d'ensemble** :

- `leaders_calendar_overlays_same_bar_correction`
- `leaders_overlays_same_bar_correction`
- `lowvol_trend_vol_targeting_same_bar_correction`
- `sma200_overlays_same_bar_correction`

**document de protocole ou de synthèse, sans backtest attendu** :

- `dispersion_battery_caduc_et_guide_v3`
- `meilleurs_candidats_guide_deploiement_v2`
- `protocole_regle_10_taux_realiste_cash`

**extension d'Étape D — résultat sous `etape_D_*`** :

- `etape_d_v3_add_149`
- `etape_d_v3_add_crossmarket`
- `etape_d_v3_bond_diversification`

**ce cycle même — artefact créé après le passage du contrôle** :

- `protocol_inventory`

Le contrôle E cherchait des `PREREG` **abandonnés** — déclarés puis jamais
exécutés. Il n'en trouve **aucun**. Les 19 sont des cycles menés à terme dont le
rapport porte un nom différent du pré-enregistrement, ce que le contrôle ne
pouvait pas savoir seul. **Faux positifs : 19/19.**

## Les deux abstentions annoncées — et tenues

### 1. Aucun pré-enregistrement rétroactif

Le contrôle B ne laisse **aucun** résultat sans pré-enregistrement une fois les
variantes résolues. Il n'y avait donc rien à antidater — mais l'engagement tenait
indépendamment du résultat, et il aurait tenu si le compte avait été non nul.

### 2. Aucun assouplissement du vérificateur anti-cheat

Le contrôle A confirme le seul cas connu : `log_return_compounding_audit` porte
**ÉCHEC — protocole violé**, faute de pré-enregistrement. Son script déclare dans
sa docstring être un audit de code, « aucun degré de liberté de calibrage, aucun
critère de succès à optimiser ».

Les deux lectures possibles, et pourquoi je n'ai tranché ni l'une ni l'autre :

- **Faux positif** — un audit de code n'a pas de paramètre à choisir après coup,
  donc le pré-enregistrement n'y protège de rien. Plausible, et c'est ce que le
  script affirme de lui-même.
- **Violation réelle** — la règle ne prévoit pas d'exception, et la première
  exception est celle qui ouvre la porte aux suivantes.

**Rendre le vérificateur tolérant créerait exactement la faille qu'il existe pour
fermer** : tout cycle futur pourrait se déclarer exempt dans sa propre docstring,
c'est-à-dire s'auto-délivrer sa dispense. Je ne modifie donc pas le vérificateur,
et je n'écris pas non plus le pré-enregistrement manquant.

> **Porté à l'arbitrage de l'utilisateur**, au même titre que `n_trials` (#421).
> Si une exception doit exister, elle devrait être **énumérée dans un fichier
> versionné** — ajouter une entrée devient alors un acte visible et relisible,
> pas une dispense que le script s'accorde à lui-même.

## Conclusion — ce que l'inventaire a réellement trouvé

| Contrôle | Compte brut | Après inspection |
|---|---|---|
| A — anti-cheat non CONFORME | 1 | **1, porté à l'arbitrage** |
| B — résultat sans PREREG | 5 | **0** (variantes résolues) |
| C — PASS sans batterie | 33 | **6** strictement postérieurs à la Règle 9 |
| D — source `data/` absente | 0 | **0** |
| E — PREREG sans artefact | 19 | **0** (19/19 faux positifs) |

**Une dette réelle a été trouvée** : les **6** PASS publiés strictement après
l'introduction de la Règle 9 sans avoir été soumis à la batterie de validation.
C'est une dette de **protocole**, pas de calcul : leur verdict de niveau 1 est
acquis, mais le second filtre que le backlog s'impose ne leur a pas été appliqué.

Deux nuances, dites plutôt que tues :

1. **17 candidats supplémentaires** datent du **jour même** où la Règle 9 est
   apparue. Rien ne permet de dire s'ils l'ont précédée de quelques heures. Ils
   sont comptés à part, ni blanchis ni chargés.
2. L'un des 6, `capitulation_gate_floor_sweep`, est un **diagnostic et non une
   stratégie** — son PASS est un faux positif de détection, établi au #427. La
   dette réelle porte donc sur **5** candidats, à confirmer par lecture avant
   toute exécution de batterie.

Le cycle n'avait rien fabriqué d'avance : il pouvait légitimement conclure « rien
d'actionnable ». Il conclut l'inverse, et c'est le contrôle C — le seul dont je
n'avais fait aucune prédiction — qui l'a fourni.
