# Détecteur d'auto-inclusion — **deuxième essai** (pré-enregistré)

**`n_trials = 2`.** Le #466 a tenté la même hypothèse et échoué
(rappel 1/2). Le protocole impose de **compter cet essai**, pas de
repartir à 1.

## La calibration est **contaminée** — dit avant, répété ici

La règle est élargie à l'énumération par `git status` **en connaissant la
cause de l'échec du #466**. La recalibrer sur les **mêmes 18 cas**, c'est
ajuster une règle sur les données qui servent à la juger.

| | Mesuré |
|---|---|
| rappel sur les fautifs connus | **2 / 2** |
| faux positifs sur les sains connus | **10 / 16** |

> **Le rappel est parfait, et il ne prouve rien.** Je l'ai obtenu en
> regardant la réponse. C'est écrit dans le pré-enregistrement pour
> que je ne puisse pas m'en prévaloir maintenant.

## Le résultat sur tout le dépôt

- scripts examinés : **320**
- **signalés** : **21** *(contre 20 au #466)*
- dont **inconnus** de toute vérité terrain : **9**

## Le vrai test — validation **hors échantillon**

Les **6 premiers** nouveaux signalés, par ordre
alphabétique — règle fixée **avant** d'avoir vu la liste. Chacun exécuté
**deux fois**, empreintes comparées.

| Script | État | Passage 1 | Passage 2 |
|---|---|---|---|
| `nonml_content_defined_magnitudes_backtest.py` | idempotent | `5bcf982a3681` | `5bcf982a3681` |
| `nonml_empty_pass_basket_extension_backtest.py` | idempotent | `b12a26f13d99` | `b12a26f13d99` |
| `nonml_empty_pass_requalification_backtest.py` | idempotent | `40b40b67ffa5` | `40b40b67ffa5` |
| `nonml_npz_report_consistency_backtest.py` | idempotent | `da7286665cf8` | `da7286665cf8` |
| `nonml_pnl_duplicate_sweep_backtest.py` | idempotent | `52c5793c6130` | `52c5793c6130` |
| `nonml_prereg_convention_coverage_backtest.py` | idempotent | `aae5a76c41c8` | `aae5a76c41c8` |

- éprouvés : **6** / 6
- **réellement non idempotents** : **0**

> **Le détecteur sur-signale.** Sur les
> **6** scripts éprouvés hors échantillon, seuls
> **0** sont réellement défectueux. **Sa liste de
> suspects n'a pas de valeur de priorité**, et le
> pré-enregistrement en tire la conséquence qu'il avait fixée :
> **la piste « détection statique » est déclarée CLOSE**, pas
> retentée une troisième fois.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| rappel 2/2 *(sans valeur, dit d'avance)* | 2 | 2 | **vérifiée** |
| **≥ 2 des 6 hors échantillon défectueux** | ≥ 2 | 0 | **réfutée** |
| faux positifs ≥ 8 sur 16 | ≥ 8 | 10 | **vérifiée** |

## L'effet de bord

La validation **exécute** des scripts, donc réécrit des rapports. Arbre
restauré (leçon du #450).

- résidus sous `results/` après restauration : **0**

**Aucun rapport régénéré n'est committé.**

## Critères de succès

1. **320/320** scripts classés — **OUI**.
2. Calibration publiée **avec sa contamination** — **OUI**.
3. Les 6 hors échantillon traités — **OUI**.
4. Arbre propre après restauration — **OUI**.

**PASS** — le critère porte sur le
**procédé**. Un détecteur condamné par sa propre validation, publié
proprement, **réussit ce cycle**.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).