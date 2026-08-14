# Les `.npz` sans rapport publié, inspectés nom par nom (pré-enregistré)

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport ni `.npz` modifié** — ce cycle ne fait que lire.

## Le compte réel, et l'écart au #442

- `.npz` du dépôt : **219**
- **sans rapport à leur nom** : **30**
- annoncé par le #442, jamais revérifié depuis : **20**

**Écart : +10.** Le chiffre de 20 datait de dix cycles, pendant
lesquels le dépôt a gagné plusieurs dizaines de fichiers.

**Prédiction vérifiée** : j'annonçais un chiffre faux sans parier sur le sens.
Il l'est. Ne pas avoir parié sur la direction était la seule position
honnête — et c'est aussi ce qui rend cette prédiction faible.

## Classement

| Classe | Signification | Nombre |
|---|---|---|
| **V** | variante dont un rapport la **nomme** | **7** |
| **M** | série ML / Étape D (hors préfixe `nonml_`) | **10** |
| **O** | **orphelin réel** — aucun rapport ne la nomme | **13** |

### Orphelins réels — aucun rapport ne les nomme (13)

- `nonml_ewma_defensive_overlay` — aucun rapport du dépôt ne la nomme
- `nonml_gjr_calm_regime_overlay_dax` — aucun rapport du dépôt ne la nomme
- `nonml_gjr_calm_regime_overlay_ndx` — aucun rapport du dépôt ne la nomme
- `nonml_gjr_calm_regime_overlay_russell2000` — aucun rapport du dépôt ne la nomme
- `nonml_gjr_calm_regime_overlay_sp500` — aucun rapport du dépôt ne la nomme
- `nonml_gjr_trend_gated_vol_managed_dax` — aucun rapport du dépôt ne la nomme
- `nonml_gjr_trend_gated_vol_managed_ndx` — aucun rapport du dépôt ne la nomme
- `nonml_gjr_trend_gated_vol_managed_russell2000` — aucun rapport du dépôt ne la nomme
- `nonml_gjr_trend_gated_vol_managed_sp500` — aucun rapport du dépôt ne la nomme
- `nonml_gjr_vol_forecast_momentum_overlay_dax` — aucun rapport du dépôt ne la nomme
- `nonml_gjr_vol_forecast_momentum_overlay_ndx` — aucun rapport du dépôt ne la nomme
- `nonml_gjr_vol_forecast_momentum_overlay_russell2000` — aucun rapport du dépôt ne la nomme
- `nonml_gjr_vol_forecast_momentum_overlay_sp500` — aucun rapport du dépôt ne la nomme

### Variantes — le rapport qui les nomme est désigné (7)

| Série | Rapport(s) qui la nomment |
|---|---|
| `nonml_cash_rate_correction_44_crossmarket_russell2000` | `nonml_cash_rate_correction_44_crossmarket_russell2000_pass_validation_battery.md`, `nonml_empty_pass_basket_extension_result.md` |
| `nonml_cash_rate_correction_44_crossmarket_sp500` | `nonml_cash_rate_correction_44_crossmarket_sp500_pass_validation_battery.md`, `nonml_empty_pass_basket_extension_result.md` |
| `nonml_cash_rate_correction_44_weekly_rebalance_ndx` | `nonml_cash_rate_correction_44_weekly_rebalance_ndx_pass_validation_battery.md`, `nonml_empty_pass_basket_extension_result.md` |
| `nonml_cash_rate_correction_44_weekly_rebalance_russell2000` | `nonml_cash_rate_correction_44_weekly_rebalance_russell2000_pass_validation_battery.md`, `nonml_empty_pass_basket_extension_result.md` |
| `nonml_diversification_bond_overlay_crossmarket_russell2000` | `nonml_diversification_bond_overlay_crossmarket_russell2000_pass_validation_battery.md`, `nonml_empty_pass_basket_extension_result.md` |
| `nonml_diversification_bond_overlay_crossmarket_sp500` | `nonml_diversification_bond_overlay_crossmarket_sp500_pass_validation_battery.md`, `nonml_empty_pass_basket_extension_result.md` |
| `nonml_etape_d_garch_defensive_overlay` | `nonml_etape_d_garch_defensive_overlay_pass_validation_battery.md` |

### Séries ML / Étape D — hors univers non-ML (10)

- `etape_D_overlay_optimized` — nom hors préfixe `nonml_` — série ML / Étape D
- `ml_crossmarket_pooling_dax` — nom hors préfixe `nonml_` — série ML / Étape D
- `ml_crossmarket_pooling_russell2000` — nom hors préfixe `nonml_` — série ML / Étape D
- `ml_crossmarket_pooling_sp500` — nom hors préfixe `nonml_` — série ML / Étape D
- `ml_exogenous_features_rates_crossmarket` — nom hors préfixe `nonml_` — série ML / Étape D
- `ml_exogenous_features_rates_crossmarket_composite` — nom hors préfixe `nonml_` — série ML / Étape D
- `ml_meta_labeling_logitl2_composite` — nom hors préfixe `nonml_` — série ML / Étape D
- `ml_meta_labeling_logitl2_ndx` — nom hors préfixe `nonml_` — série ML / Étape D
- `ml_regularized_architecture` — nom hors préfixe `nonml_` — série ML / Étape D
- `ml_regularized_architecture_composite` — nom hors préfixe `nonml_` — série ML / Étape D

### Ces « orphelins » n'en sont pas — et ma règle était trop stricte

La règle déclarée exigeait que le **nom complet** de la série apparaisse
dans un rapport. Relecture faite, **elle était le mauvais instrument** :

| Série classée O | Rapport qui la couvre réellement |
|---|---|
| `nonml_ewma_defensive_overlay` | `nonml_ewma_defensive_overlay_and_triple_engine_result.md` |
| `nonml_gjr_calm_regime_overlay_dax` | `nonml_gjr_calm_regime_overlay_result.md` |
| `nonml_gjr_calm_regime_overlay_ndx` | `nonml_gjr_calm_regime_overlay_result.md` |
| `nonml_gjr_calm_regime_overlay_russell2000` | `nonml_gjr_calm_regime_overlay_result.md` |
| `nonml_gjr_calm_regime_overlay_sp500` | `nonml_gjr_calm_regime_overlay_result.md` |
| `nonml_gjr_trend_gated_vol_managed_dax` | `nonml_gjr_trend_gated_vol_managed_result.md` |
| `nonml_gjr_trend_gated_vol_managed_ndx` | `nonml_gjr_trend_gated_vol_managed_result.md` |
| `nonml_gjr_trend_gated_vol_managed_russell2000` | `nonml_gjr_trend_gated_vol_managed_result.md` |
| `nonml_gjr_trend_gated_vol_managed_sp500` | `nonml_gjr_trend_gated_vol_managed_result.md` |
| `nonml_gjr_vol_forecast_momentum_overlay_dax` | `nonml_gjr_vol_forecast_momentum_overlay_result.md` |
| `nonml_gjr_vol_forecast_momentum_overlay_ndx` | `nonml_gjr_vol_forecast_momentum_overlay_result.md` |
| `nonml_gjr_vol_forecast_momentum_overlay_russell2000` | `nonml_gjr_vol_forecast_momentum_overlay_result.md` |
| `nonml_gjr_vol_forecast_momentum_overlay_sp500` | `nonml_gjr_vol_forecast_momentum_overlay_result.md` |

**13 des 13** sont des **branches par marché** d'une
stratégie multi-marchés dont le rapport de famille existe, ou le préfixe
d'un rapport au nom plus long. Le nombre d'orphelins **réels** est donc
**0**, pas 13.

**Je ne reclasse pas.** Le tableau de classement ci-dessus reste celui de
la règle déclarée avant mesure ; le reclasser après coup serait ajuster un
critère au vu de ce qu'il attrape, ce que le #437 a refusé. Les deux
lectures sont publiées côte à côte, et **c'est la seconde qui est vraie**.

> C'est le piège du #427 mot pour mot : un résultat **exact au mot près et
> trompeur en pratique**. Une règle qui exige le nom complet ne pouvait pas
> voir une convention de nommage `<famille>_<marché>` — et je ne l'avais pas
> prévue en écrivant le pré-enregistrement.

## Ce que ce cycle ne permet pas de conclure

- **Être nommée dans un rapport n'est pas être documentée.** La classe V dit
  qu'un rapport prononce ce nom, **pas** qu'il publie le verdict de cette
  série. La preuve exigée était volontairement faible et vérifiable ; elle ne
  doit pas être lue comme davantage.
- **Aucun verdict n'est recalculé**, aucun décompte d'essais modifié.


> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).