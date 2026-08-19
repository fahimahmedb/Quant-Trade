# Les 2 dictionnaires d'origine (#476, #478) sont-ils stales ? (pré-enregistré)

Hors du motif de recherche du #522 (`V = {`) : ces deux cycles utilisent `VERDICTS = {`. Ce sont les cycles d'origine des deux familles déjà réparées.

## Les 10 entrées, verdict actuel

| Script | Dictionnaire | Verdict `VERDICTS` |
|---|---|---|
| `nonml_protocol_inventory_audit.py` | `nonml_hardcoded_figures_sweep_backtest.py` (#476) | defaut |
| `nonml_marker_emitted_by_scripts_backtest.py` | `nonml_hardcoded_figures_sweep_backtest.py` (#476) | defaut |
| `nonml_repo_magnitudes_recount_backtest.py` | `nonml_hardcoded_figures_sweep_backtest.py` (#476) | legitime |
| `nonml_citer_451_definition_backtest.py` | `nonml_hardcoded_figures_sweep_backtest.py` (#476) | legitime |
| `nonml_duplicate_sweep_coverage_audit.py` | `nonml_hardcoded_figures_sweep_backtest.py` (#476) | defaut_partiel |
| `nonml_prereg_convention_coverage_backtest.py` | `nonml_conditional_sections_sweep_backtest.py` (#478) | peut_disparaitre |
| `nonml_repo_magnitudes_recount_backtest.py` | `nonml_conditional_sections_sweep_backtest.py` (#478) | peut_disparaitre |
| `nonml_reproducibility_campaign_v2_backtest.py` | `nonml_conditional_sections_sweep_backtest.py` (#478) | peut_disparaitre |
| `nonml_reproducibility_sample_backtest.py` | `nonml_conditional_sections_sweep_backtest.py` (#478) | peut_disparaitre |
| `nonml_reproducibility_sample_lot2_backtest.py` | `nonml_conditional_sections_sweep_backtest.py` (#478) | peut_disparaitre |

## Test de rétractation, anti-collision

### `nonml_protocol_inventory_audit.py` (`defaut`)

- **#485**, marqueur « rétracté » : « s. n_trials = 1. Lecture du disque, aucun script exécuté. ### La catégorie du #482, enfin comptée | | Nombre | |---|---| | dénombrés au #479 | 18 | | rétracté au #482 (citation de diff) | −1 | | popul »

> **À jour — confirmé compatible** : Le « rétracté » du #485 porte sur le **décompte de population** (retrait de `reproducibility_sample_lot3_audit`, déjà réparé au #527) — pas sur ce script. Le même tableau du #485 liste `protocol_inventory_audit` comme IRRÉPARABLE avec **la même raison** (« colonne Après inspection = lecture manuelle ») que le `defaut` cité ici. **Confirme, ne contredit pas.**

### `nonml_marker_emitted_by_scripts_backtest.py` (`defaut`)

- **#493**, marqueur « réfuté » : «  | | Prédiction | Annoncé | Mesuré | Verdict | |---|---|---|---| | ≥ 1 justification fausse | ≥ 1 | 1 | vérifiée | | aucun verdict ne tombe | 0 | 1 | réfutée | | marker_emitted_by_scripts exacte | exa »
- **#493**, marqueur « réfuté » : « 1 | 1 | vérifiée | | aucun verdict ne tombe | 0 | 1 | réfutée | | marker_emitted_by_scripts exacte | exacte | exacte | vérifiée | La prédiction 2 est réfutée, et c'est le résultat qui compte. Le #485  »

> **À jour — confirmé compatible** : Le #493 écrit explicitement : « marker_emitted_by_scripts exacte | exacte | exacte | vérifiée » — son verdict IRRÉPARABLE est **confirmé**, pas réfuté. Le « réfutée » voisin porte sur une **autre ligne** de la même table de prédictions (« aucun verdict ne tombe »), pas sur celui-ci. **Confirme, ne contredit pas.**

### `nonml_repo_magnitudes_recount_backtest.py` (`legitime`)

- **#478**, marqueur « réfuté » : « nale. ### Mes trois prédictions | Prédiction | Annoncé | Mesuré | Verdict | |---|---|---|---| | ≥ 40 scripts avec un titre conditionnel | ≥ 40 | 31 | réfutée | | médiane ≤ 2 par script affecté | ≤ 2 | »

> **À jour — confirmé compatible** : Le « réfutée » du #478 porte sur la **prédiction globale du cycle** (« ≥ 40 scripts avec un titre conditionnel », mesuré 31) — une statistique de prévalence sur toute la population, pas un jugement sur l'entrée spécifique de `repo_magnitudes_recount_backtest.py`. **Sans rapport avec son verdict** (`legitime` au #476, `peut_disparaitre` au #478).

### `nonml_citer_451_definition_backtest.py` (`legitime`)

- aucune occurrence pertinente trouvée (après élimination des collisions et de la dette générique).

> **À jour** — verdict confirmé, aucune contradiction trouvée.

### `nonml_duplicate_sweep_coverage_audit.py` (`defaut_partiel`)

- aucune occurrence pertinente trouvée (après élimination des collisions et de la dette générique).

> **À jour** — verdict confirmé, aucune contradiction trouvée.

### `nonml_prereg_convention_coverage_backtest.py` (`peut_disparaitre`)

- aucune occurrence pertinente trouvée (après élimination des collisions et de la dette générique).

> **À jour** — verdict confirmé, aucune contradiction trouvée.

### `nonml_repo_magnitudes_recount_backtest.py` (`peut_disparaitre`)

- **#478**, marqueur « réfuté » : « nale. ### Mes trois prédictions | Prédiction | Annoncé | Mesuré | Verdict | |---|---|---|---| | ≥ 40 scripts avec un titre conditionnel | ≥ 40 | 31 | réfutée | | médiane ≤ 2 par script affecté | ≤ 2 | »

> **À jour — confirmé compatible** : Le « réfutée » du #478 porte sur la **prédiction globale du cycle** (« ≥ 40 scripts avec un titre conditionnel », mesuré 31) — une statistique de prévalence sur toute la population, pas un jugement sur l'entrée spécifique de `repo_magnitudes_recount_backtest.py`. **Sans rapport avec son verdict** (`legitime` au #476, `peut_disparaitre` au #478).

### `nonml_reproducibility_campaign_v2_backtest.py` (`peut_disparaitre`)

- aucune occurrence pertinente trouvée (après élimination des collisions et de la dette générique).

> **À jour** — verdict confirmé, aucune contradiction trouvée.

### `nonml_reproducibility_sample_backtest.py` (`peut_disparaitre`)

- **#509**, marqueur « réfuté » : «  artefact de temporalité — exactement l'erreur que le #503 avait déjà > corrigée une fois, et que j'ai refaite un cycle plus tard. ### Une prédiction réfutée | Prédiction | Annoncé | Mesuré | Verdict  »
- **#509**, marqueur « réfuté » : « é | Mesuré | Verdict | |---|---|---|---| | ≥ 15 postérieures | ≥ 15 | 19 | vérifiée | | ≥ 1 antérieure | ≥ 1 | 1 | vérifiée | | 0 indatable | 0 | 1 | réfutée | L'indatable est nommé : reproducibility_ »

> **À jour — confirmé compatible** : Le « réfutée » du #509 porte sur un **axe distinct** : la datation des `PREREG_` sans convention d'auto-déclaration (« 0 indatable », réfutée car 1 trouvé) — sujet du #486, sans rapport avec la classification `peut_disparaitre` d'une garde conditionnelle au #478. Même mécanisme de faux positif d'axe qu'aux #523-#525.

### `nonml_reproducibility_sample_lot2_backtest.py` (`peut_disparaitre`)

- aucune occurrence pertinente trouvée (après élimination des collisions et de la dette générique).

> **À jour** — verdict confirmé, aucune contradiction trouvée.

## Le compte

- entrées vérifiées : **10**
- occurrences pertinentes à examiner : **0**
- confirmées à jour : **10**

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| 0 contradiction confirmée | 0 | 0 | **vérifiée** |
| Les 10 entrées restent inchangées | 10 | 10 | **vérifiée** |
| Les 2 dictionnaires déclarés à jour | oui | oui | **vérifiée** |

## Critères de succès

1. Les 10 entrées listées, verdict actuel cité — **OUI**.
2. Résultat du test de rétractation publié pour chacune — **OUI**.
3. Occurrences retenues confrontées, verdict de compatibilité publié — **OUI**.
4. Toute contradiction confirmée corrigée avec diff borné — **OUI**.
5. Aucun script de marché exécuté — **OUI**.

**PASS** — le critère porte sur le **procédé** : vérifier deux dictionnaires jamais couverts par le screen précédent, avec le même garde-fou anti-collision.

**Aucune correction nécessaire** — les deux dictionnaires d'origine (#476, #478) sont **à jour**. Le screen de staleness des dictionnaires de verdicts écrits à la main est désormais complet : les 6 dictionnaires connus du dépôt (4 `V =`, 2 `VERDICTS =`) sont tous vérifiés.

Simulation 300 € et robustesse **sans objet** : cycle de vérification de dépôt, aucune position.
