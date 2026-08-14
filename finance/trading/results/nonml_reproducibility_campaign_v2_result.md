# Campagne de reproductibilité v2 — critère d'auto-référence et relance (pré-enregistré)

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
aucun paramètre touché, **aucun rapport publié modifié**.

## Le critère d'auto-référence, appliqué

Fixé au pré-enregistrement, **avant tout tirage**, et portant sur le **code** :
un script est auto-référent si son source balaie l'ensemble du dépôt
(`glob` sur `nonml_*_backtest.py`, `*_pnl.npz`, `nonml_*_result.md`).

Un rapport auto-référent **dérive nécessairement** dès qu'un cycle ajoute un
fichier : sa divergence ne dit rien sur la péremption d'un résultat.

- scripts avec rapport publié : **302**
- **auto-référents, exclus** : **17**
- vivier de la campagne v2 : **285**

Exclus :

- `capitulation_gate_floor_sweep`
- `net_pnl_correction`
- `pnl_duplicate_sweep`
- `protocol_inventory`
- `reproducibility_campaign_v2`
- `reproducibility_campaign_v3`
- `reproducibility_campaign_v3_lot2`
- `reproducibility_campaign_v3_lot3`
- `reproducibility_sample`
- `reproducibility_sample_lot2`
- `reproducibility_sample_lot3`
- `sameday_timestamp_resolution`
- `selfref_reports_marking`
- `third_npz_schema_handling`
- `verdict_detector_complete`
- `verdict_detector_fix`
- `verdict_rule_propagation`

Tous sont des **diagnostics**, pas des stratégies : aucun verdict PASS/FAIL n'en
dépend. Ils ne sont **pas corrigés** ici — les rendre stables modifierait des
rapports publiés et relève d'un cycle de modification déclarée.

## Tirage

- graine, fixée au pré-enregistrement : **20260816**
- taille : **24**, délai maximal **300 s**

**Les 60 tirages des #434-#436 ne sont pas réutilisés.** La campagne repart de
zéro, conformément à l'engagement du #436 de ne pas reclasser des tirages selon
une règle qui n'existait pas quand ils ont été faits.

Échantillon tiré, publié **avant** les résultats individuels :

- `atr_vol_targeting_overlay`
- `credit_spread_overlay`
- `diversification_bond_overlay_crossmarket`
- `dry_bulk_shipping_overlay`
- `em_dm_relative_strength_overlay`
- `empty_pass_requalification`
- `garman_klass_vol_targeting_overlay`
- `goldencross_vol_targeting_overlay`
- `index_skewness_regime_overlay`
- `low_vol_tilt`
- `lowvol_regime_vol_targeting_overlay`
- `momentum_52w_high`
- `momentum_decile_spread_vol_targeting_overlay`
- `momentum_dispersion_vol_targeting_overlay`
- `momentum_turnover_doublesort_pit_universe`
- `npz_report_consistency`
- `oil_price_shock_overlay`
- `ppi_inflation_overlay`
- `pre_fomc_drift_overlay`
- `rate_level_regime_overlay`
- `sma200_breadth_vol_targeting_overlay_pit_universe`
- `sma200_leaders_overlay`
- `sma200_momentum_breadth_and_overlay`
- `stlfsi_financial_stress_overlay`

## Résultat

| | Nombre |
|---|---|
| **identiques** octet à octet | **23** |
| **divergents** | **1** |
| **non concluants** | **0** |

### Divergents

| Script | Durée | Lignes différentes |
|---|---|---|
| `empty_pass_requalification` | 0.3 s | 5 |

**`empty_pass_requalification` — premières lignes divergentes :**

```
```

**Non committées** : le rapport d'origine a été restauré. Ces divergences
sont **substantielles** — le critère d'auto-référence les avait écartées du
vivier — et constituent le résultat principal du cycle.

### Identiques

| Script | Durée |
|---|---|
| `atr_vol_targeting_overlay` | 2.1 s |
| `credit_spread_overlay` | 6.8 s |
| `diversification_bond_overlay_crossmarket` | 1.7 s |
| `dry_bulk_shipping_overlay` | 2.9 s |
| `em_dm_relative_strength_overlay` | 4.8 s |
| `garman_klass_vol_targeting_overlay` | 2.0 s |
| `goldencross_vol_targeting_overlay` | 2.1 s |
| `index_skewness_regime_overlay` | 7.6 s |
| `low_vol_tilt` | 1.6 s |
| `lowvol_regime_vol_targeting_overlay` | 2.3 s |
| `momentum_52w_high` | 1.6 s |
| `momentum_decile_spread_vol_targeting_overlay` | 1.8 s |
| `momentum_dispersion_vol_targeting_overlay` | 1.7 s |
| `momentum_turnover_doublesort_pit_universe` | 6.8 s |
| `npz_report_consistency` | 1.9 s |
| `oil_price_shock_overlay` | 7.7 s |
| `ppi_inflation_overlay` | 8.3 s |
| `pre_fomc_drift_overlay` | 2.2 s |
| `rate_level_regime_overlay` | 2.6 s |
| `sma200_breadth_vol_targeting_overlay_pit_universe` | 4.3 s |
| `sma200_leaders_overlay` | 2.0 s |
| `sma200_momentum_breadth_and_overlay` | 2.2 s |
| `stlfsi_financial_stress_overlay` | 6.1 s |

## Borne v2 — et le recul assumé

**Aucune borne n'est publiée** : une divergence substantielle a été observée,
et c'est elle le résultat du cycle.

## Portée

Ce lot couvre **24** scripts sur **285** du vivier v2,
soit **8.4 %**. Tirage aléatoire à graine
fixée d'avance, donc reproductible et non choisi.


> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).