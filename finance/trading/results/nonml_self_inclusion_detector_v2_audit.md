# Audit adversarial — détecteur d'auto-inclusion v2 (#467)

Le backtest conclut à **fermer la piste**. Un abandon mérite le même
examen qu'une découverte : **s'il est prématuré, on jette un outil qui
marchait.**

## A. L'échantillon est-il celui que la règle désigne ?

La règle — « 6 premiers nouveaux signalés, ordre alphabétique » — était
fixée avant de voir la liste. On la ré-applique **sans réutiliser le code**
du backtest.

- attendu par l'audit : **6** scripts
- publiés par le rapport : **6**

**CONCORDANT.**

## B. Idempotents, ou idempotents **par chance** ?

Deux passages identiques ne prouvent pas la stabilité : une dérive de
**période 2** y échapperait. Chacun est rejoué une **troisième** fois.

| Script | P1=P2 (rapport) | P3 | Verdict |
|---|---|---|---|
| `nonml_content_defined_magnitudes_backtest.py` | oui | `5bcf982a3681` | stable sur 3 |
| `nonml_empty_pass_basket_extension_backtest.py` | oui | `b12a26f13d99` | stable sur 3 |
| `nonml_empty_pass_requalification_backtest.py` | oui | `40b40b67ffa5` | stable sur 3 |
| `nonml_npz_report_consistency_backtest.py` | oui | `da7286665cf8` | stable sur 3 |
| `nonml_pnl_duplicate_sweep_backtest.py` | oui | `3a2f3fd66255` | stable sur 3 |
| `nonml_prereg_convention_coverage_backtest.py` | oui | `aae5a76c41c8` | stable sur 3 |

**CONCORDANT** — aucun des 6 ne dérive au troisième passage. Le
**0/6** du rapport tient, et l'abandon repose sur une mesure solide.

## C. L'élargissement a-t-il élargi ?

- signalés par la règle **élargie** : **21**
- signalés par la règle **étroite** du #466 : **20**

**CONCORDANT** — la règle élargie signale bien davantage.

## D. Idempotence de mon propre rapport

- avant : `9e7fb73c244e06a5`
- après : `c4498fb1148961cf`

**ÉCART.**

## Ce que cet audit ne couvre pas

- Il éprouve **6** scripts sur les 320 : la fermeture de la piste repose
  sur un échantillon étroit, et le rapport ne le cache pas.
- Il ne teste que **3** passages : une dérive de période plus longue lui
  échapperait encore.

## Verdict — **ÉCART** (3/4)

**Au moins un contrôle échoue — voir ci-dessus.**