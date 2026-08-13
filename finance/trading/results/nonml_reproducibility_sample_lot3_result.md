# Reproductibilité des rapports publiés — lot 3 (pré-enregistré)

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
aucun paramètre touché, **aucun rapport publié modifié**.

## Volet A — tirage

- vivier total : **285**
- déjà testés aux #434 / #435, exclus : **36**
- vivier restant : **249**
- graine, fixée au pré-enregistrement : **20260815**
- taille : **24**, délai maximal **300 s**

Échantillon tiré, publié **avant** les résultats individuels :

- `beta_dispersion_vol_targeting_overlay`
- `breadth_vol_targeting_overlay`
- `cash_rate_correction_44_weekly_rebalance_sp500`
- `conditional_weekend_overlay`
- `continuing_claims_overlay`
- `ethereum_momentum_overlay`
- `financial_conditions_overlay`
- `kurtosis_regime_defensive_overlay`
- `long_horizon_index_reversal_overlay`
- `lunar_phase_overlay`
- `market_concentration_vol_targeting_overlay`
- `market_concentration_vol_targeting_overlay_pit_universe`
- `midmonth_payday_effect`
- `net_breadth_vol_targeting_overlay`
- `parkinson_c2c_ratio_vol_targeting_overlay`
- `pnl_duplicate_sweep`
- `post_holiday_overlay`
- `range_position_vol_targeting_overlay_pit_universe`
- `real_gdp_overlay`
- `rebound_speed_breadth_vol_targeting_overlay`
- `rogers_satchell_vol_targeting_overlay`
- `skewness_vol_targeting_overlay`
- `stlfsi_financial_stress_overlay`
- `trend_vol_targeting_overlay`

## Volet A — résultat

| | Nombre |
|---|---|
| **identiques** octet à octet | **23** |
| **divergents** | **1** |
| **non concluants** | **0** |

### Divergents

| Script | Durée | Lignes différentes |
|---|---|---|
| `pnl_duplicate_sweep` | 5.9 s | 8 |

**`pnl_duplicate_sweep` — premières lignes divergentes :**

```
- | scripts de backtest non-ML du dépôt | **284** |
+ | scripts de backtest non-ML du dépôt | **289** |
- | **couverture non-ML** | **73.2 %** |
+ | **couverture non-ML** | **72.0 %** |
- **La soustraction 284 − 208 ne compte rien de réel** : les deux
+ **La soustraction 289 − 208 ne compte rien de réel** : les deux
```

**Non committées** : le rapport d'origine a été restauré.

### Identiques

| Script | Durée |
|---|---|
| `beta_dispersion_vol_targeting_overlay` | 2.1 s |
| `breadth_vol_targeting_overlay` | 1.7 s |
| `cash_rate_correction_44_weekly_rebalance_sp500` | 1.4 s |
| `conditional_weekend_overlay` | 2.2 s |
| `continuing_claims_overlay` | 7.2 s |
| `ethereum_momentum_overlay` | 3.2 s |
| `financial_conditions_overlay` | 7.3 s |
| `kurtosis_regime_defensive_overlay` | 7.8 s |
| `long_horizon_index_reversal_overlay` | 2.6 s |
| `lunar_phase_overlay` | 2.3 s |
| `market_concentration_vol_targeting_overlay` | 1.9 s |
| `market_concentration_vol_targeting_overlay_pit_universe` | 4.8 s |
| `midmonth_payday_effect` | 2.2 s |
| `net_breadth_vol_targeting_overlay` | 2.1 s |
| `parkinson_c2c_ratio_vol_targeting_overlay` | 2.2 s |
| `post_holiday_overlay` | 2.2 s |
| `range_position_vol_targeting_overlay_pit_universe` | 5.8 s |
| `real_gdp_overlay` | 7.2 s |
| `rebound_speed_breadth_vol_targeting_overlay` | 1.8 s |
| `rogers_satchell_vol_targeting_overlay` | 2.3 s |
| `skewness_vol_targeting_overlay` | 27.3 s |
| `stlfsi_financial_stress_overlay` | 6.0 s |
| `trend_vol_targeting_overlay` | 2.1 s |

## Volet A — borne cumulée sur les trois lots

**La borne ne s'applique plus** — une divergence a été observée. Le résultat
principal du cycle est la divergence elle-même.

## Volet B — représentativité en âge du cumul

La borne suppose que les scripts testés sont **représentatifs** du dépôt. Si les
tirages se concentraient sur les rapports **récents**, elle serait rassurante à
tort : le code partagé a évolué et les corrections #375-#404 ont touché des
fonctions communes **après** la publication de beaucoup de rapports.

| | Vivier | Testés |
|---|---|---|
| effectif | 285 | 60 |
| date de publication médiane | 2026-08-04 | 2026-08-01 |

- part des testés dans le vivier entier : **21.1 %**
- part des testés dans le **tiers le plus ancien** (95 rapports) : **17.9 %**
- écart : **-3.2 points** — tolérance fixée avant mesure : **±10 points**

**Tirage représentatif en âge.** Les rapports anciens sont couverts à la même
fréquence que les récents : la borne du volet A s'applique au dépôt entier,
pas seulement à sa partie récente.

## Portée

Les trois lots couvrent **60** scripts sur **285**, soit
**21.1 %** du dépôt, par tirages aléatoires
**disjoints** à graines fixées d'avance.
