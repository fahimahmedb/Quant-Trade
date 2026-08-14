# Inventaire vérifié de la dette de protocole (pré-enregistré)

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
aucun paramètre touché.

Le #430 a constaté la file d'outillage vide ; le #429 avait fixé la règle pour ce
cas — **chercher une dette réelle plutôt que d'en inventer une, et l'écrire si**
**l'on n'en trouve pas**. Cinq contrôles mécaniques, définis avant toute mesure.

## Contrôle A — rapports anti-cheat dont le verdict n'est pas CONFORME

- rapports anti-cheat examinés : **350**
- verdict **non CONFORME** : **1**

- `log_return_compounding_audit` — **[FAIL]** Pré-enregistrement finance/trading/PREREG_log_return_compounding_audit.md non trouvé dans l'historique git.

## Contrôle B — rapports de résultat sans pré-enregistrement homonyme

- rapports de résultat examinés : **305**
- sans `PREREG_<nom>.md` présent **ni dans l'historique git** : **0**

- dont **résolus** : variante d'un candidat dont le pré-enregistrement porte le
  nom du parent : **5**

Un pré-enregistrement peut porter un nom différent de son résultat : une variante
de marché (`_dax`, `_sp500`) ou d'univers (`_pit_universe`) est couverte par le
pré-enregistrement de son parent. La résolution est **automatique et listée**,
pas décidée au cas par cas.

| Variante | Couverte par |
|---|---|
| `amihud_illiquidity_tilt_pit_universe` | `PREREG_amihud_illiquidity_tilt*.md` |
| `gjr_vol_managed_dax` | `PREREG_gjr_vol_managed*.md` |
| `gjr_vol_managed_russell2000` | `PREREG_gjr_vol_managed*.md` |
| `gjr_vol_managed_sp500` | `PREREG_gjr_vol_managed*.md` |
| `momentum_turnover_doublesort_pit_universe` | `PREREG_momentum_turnover_doublesort*.md` |

## Contrôle C — rapports PASS jamais soumis à la batterie (Règle 9)

- rapports **PASS** : **103**
- sans trace de batterie (fichier dédié **ni** mention interne) : **30**

La Règle 9 est apparue avec `nonml_pass_validation_battery.py`, ajouté au dépôt
le **2026-07-29**. Un PASS publié **avant** cette date n'a jamais pu y être
soumis : c'est une **antériorité**, pas une violation. Les deux sont comptées
séparément plutôt que confondues en un chiffre alarmant.

| | Nombre |
|---|---|
| PASS **antérieurs** à la Règle 9 | **10** |
| PASS du **jour même** de son introduction (ambigu) | **17** |
| PASS **strictement postérieurs**, sans batterie | **3** |

Les **17** du jour même sont **ambigus** : rien ne dit s'ils ont été publiés
avant ou après l'ajout du script dans la même journée. Je les compte à part plutôt
que de les ranger du côté qui m'arrange.

Les **strictement postérieurs** sont la dette réelle de ce contrôle :

| Candidat | Rapport publié le |
|---|---|
| `january_effect_lowprice_overlay_pit_universe` | 2026-08-13 |
| `verdict_detector_complete` | 2026-08-13 |
| `verdict_rule_propagation` | 2026-08-14 |

## Contrôle D — scripts référençant un fichier de `data/` absent

- fichiers présents dans `data/` : **66**
- noms référencés par un script mais **absents** : **0**

## Contrôle E — pré-enregistrements sans aucun artefact produit

- pré-enregistrements examinés : **427**
- sans `_result.md`, `_audit.md`, `<nom>.md` ni `_anti_cheat.md` : **19**

Compte **brut** lui aussi : un cycle d'outillage nomme parfois son rapport
autrement que son pré-enregistrement. Liste fournie pour inspection.

- `cash_rate_correction_44_crossmarket_oos_lockbox`
- `cash_rate_correction_44_oos_lockbox`
- `dispersion_battery_caduc_et_guide_v3`
- `diversification_bond_overlay_oos_lockbox`
- `etape_d_v3_add_149`
- `etape_d_v3_add_crossmarket`
- `etape_d_v3_bond_diversification`
- `leaders_calendar_overlays_same_bar_correction`
- `leaders_overlays_same_bar_correction`
- `lowvol_trend_vol_targeting_same_bar_correction`
- `marker_emitted_by_scripts`
- `meilleurs_candidats_guide_deploiement_v2`
- `ml_crossmarket_pooling`
- `ml_exogenous_features_rates_crossmarket`
- `ml_meta_labeling_logitl2_ndx`
- `ml_regularized_architecture`
- `ndx_defensive_oos_lockbox`
- `protocole_regle_10_taux_realiste_cash`
- `sma200_overlays_same_bar_correction`

## Synthèse des cinq contrôles

| Contrôle | Compte |
|---|---|
| A — anti-cheat non CONFORME | **1** |
| B — résultat sans PREREG homonyme (brut) | **0** |
| C — PASS sans trace de batterie | **30** |
| D — source `data/` absente | **0** |
| E — PREREG sans artefact (brut) | **19** |

Les comptes B et E sont **bruts et non conclusifs** — ils appellent une
inspection, faite dans l'audit de ce cycle.


> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).