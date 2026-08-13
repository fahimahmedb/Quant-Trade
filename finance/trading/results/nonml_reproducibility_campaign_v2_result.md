# Campagne de reproductibilité v2 — critère d'auto-référence et relance (pré-enregistré)

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
aucun paramètre touché, **aucun rapport publié modifié**.

## Le critère d'auto-référence, appliqué

Fixé au pré-enregistrement, **avant tout tirage**, et portant sur le **code** :
un script est auto-référent si son source balaie l'ensemble du dépôt
(`glob` sur `nonml_*_backtest.py`, `*_pnl.npz`, `nonml_*_result.md`).

Un rapport auto-référent **dérive nécessairement** dès qu'un cycle ajoute un
fichier : sa divergence ne dit rien sur la péremption d'un résultat.

- scripts avec rapport publié : **288**
- **auto-référents, exclus** : **7**
- vivier de la campagne v2 : **281**

Exclus :

- `capitulation_gate_floor_sweep`
- `pnl_duplicate_sweep`
- `protocol_inventory`
- `reproducibility_sample`
- `reproducibility_sample_lot2`
- `reproducibility_sample_lot3`
- `sameday_timestamp_resolution`

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
- `oil_market_volatility_overlay`
- `overnight_intraday`
- `presidential_cycle_overlay`
- `quarter_end_window_dressing`
- `rate_volatility_regime_overlay`
- `sma200_momentum_breadth_and_overlay`
- `sma200_slope_overlay`
- `sma200_trend_overlay`
- `tom_decomposition_overlay`

## Résultat

| | Nombre |
|---|---|
| **identiques** octet à octet | **23** |
| **divergents** | **1** |
| **non concluants** | **0** |

### Divergents

| Script | Durée | Lignes différentes |
|---|---|---|
| `empty_pass_requalification` | 0.4 s | 5 |

**`empty_pass_requalification` — premières lignes divergentes :**

```
- - fichiers `nonml_*_pnl.npz` trouvés : **173**
+ - fichiers `nonml_*_pnl.npz` trouvés : **208**
- - exploitables (schéma `pos` / `r_asset`) : **158**
+ - exploitables (schéma `pos` / `r_asset`) : **185**
- - inexploitables (autre schéma) : **15**
+ - inexploitables (autre schéma) : **23**
```

**Non committées** : le rapport d'origine a été restauré. Ces divergences
sont **substantielles** — le critère d'auto-référence les avait écartées du
vivier — et constituent le résultat principal du cycle.

### Identiques

| Script | Durée |
|---|---|
| `atr_vol_targeting_overlay` | 2.3 s |
| `credit_spread_overlay` | 6.9 s |
| `diversification_bond_overlay_crossmarket` | 1.8 s |
| `dry_bulk_shipping_overlay` | 3.1 s |
| `em_dm_relative_strength_overlay` | 5.0 s |
| `garman_klass_vol_targeting_overlay` | 2.3 s |
| `goldencross_vol_targeting_overlay` | 2.3 s |
| `index_skewness_regime_overlay` | 7.9 s |
| `low_vol_tilt` | 1.6 s |
| `lowvol_regime_vol_targeting_overlay` | 2.1 s |
| `momentum_52w_high` | 1.6 s |
| `momentum_decile_spread_vol_targeting_overlay` | 1.8 s |
| `momentum_dispersion_vol_targeting_overlay` | 1.9 s |
| `momentum_turnover_doublesort_pit_universe` | 7.1 s |
| `oil_market_volatility_overlay` | 4.3 s |
| `overnight_intraday` | 2.2 s |
| `presidential_cycle_overlay` | 2.3 s |
| `quarter_end_window_dressing` | 2.3 s |
| `rate_volatility_regime_overlay` | 11.1 s |
| `sma200_momentum_breadth_and_overlay` | 2.1 s |
| `sma200_slope_overlay` | 2.2 s |
| `sma200_trend_overlay` | 2.1 s |
| `tom_decomposition_overlay` | 3.5 s |

## Borne v2 — et le recul assumé

**Aucune borne n'est publiée** : une divergence substantielle a été observée,
et c'est elle le résultat du cycle.

## Portée

Ce lot couvre **24** scripts sur **281** du vivier v2,
soit **8.5 %**. Tirage aléatoire à graine
fixée d'avance, donc reproductible et non choisi.
