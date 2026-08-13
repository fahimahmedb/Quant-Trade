# Reproductibilité des rapports publiés — lot 2 (pré-enregistré)

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
aucun paramètre touché, **aucun rapport publié modifié**.

Resserre la borne publiée au #434 — **p ≤ 22,1 %** sur 12 tirages — en
échantillonnant **24 scripts supplémentaires, disjoints des 12 déjà testés**.

## Tirage

- vivier total (backtest **et** rapport publié) : **285**
- déjà testés au #434, exclus : **12**
- vivier restant : **273**
- graine, fixée au pré-enregistrement : **20260814**
- taille : **24**, délai maximal **300 s** par script

Échantillon tiré, publié **avant** les résultats individuels :

- `bitcoin_momentum_overlay`
- `cash_rate_correction_44_crossmarket`
- `cash_rate_correction_defensive_vol_targeting_44`
- `credit_card_delinquency_overlay`
- `dispersion_vol_targeting_overlay`
- `diversification_bond_overlay_crossmarket`
- `dollar_strength_overlay`
- `election_year_overlay`
- `failed_breakout_overlay`
- `gjr_calm_regime_overlay`
- `holiday_effect`
- `january_effect_lowprice_overlay`
- `leaders_index52w_high_overlay`
- `leaders_trend_union_overlay_pit_universe`
- `momentum_breadth_vol_targeting_overlay_pit_universe`
- `momentum_consistency_sma200_overlay`
- `momentum_lowvol_doublesort`
- `monthly_opex_overlay`
- `oil_price_shock_overlay`
- `short_term_reversal`
- `vix_term_structure_overlay`
- `vol_regime_overlay`
- `weekly_rebalance_dual_engine`
- `winners_trend_vol_targeting_overlay`

## Résultat du lot 2

| | Nombre |
|---|---|
| rapports **identiques** octet à octet | **24** |
| rapports **divergents** | **0** |
| **non concluants** (délai / erreur) | **0** |

**Taux sur les 24 effectivement testés : 100.0 %.**

### Identiques

| Script | Durée |
|---|---|
| `bitcoin_momentum_overlay` | 3.5 s |
| `cash_rate_correction_44_crossmarket` | 1.9 s |
| `cash_rate_correction_defensive_vol_targeting_44` | 1.6 s |
| `credit_card_delinquency_overlay` | 6.4 s |
| `dispersion_vol_targeting_overlay` | 1.9 s |
| `diversification_bond_overlay_crossmarket` | 2.0 s |
| `dollar_strength_overlay` | 4.8 s |
| `election_year_overlay` | 2.3 s |
| `failed_breakout_overlay` | 2.3 s |
| `gjr_calm_regime_overlay` | 213.7 s |
| `holiday_effect` | 2.2 s |
| `january_effect_lowprice_overlay` | 1.7 s |
| `leaders_index52w_high_overlay` | 2.0 s |
| `leaders_trend_union_overlay_pit_universe` | 6.2 s |
| `momentum_breadth_vol_targeting_overlay_pit_universe` | 4.4 s |
| `momentum_consistency_sma200_overlay` | 1.8 s |
| `momentum_lowvol_doublesort` | 1.6 s |
| `monthly_opex_overlay` | 2.2 s |
| `oil_price_shock_overlay` | 7.8 s |
| `short_term_reversal` | 1.6 s |
| `vix_term_structure_overlay` | 4.4 s |
| `vol_regime_overlay` | 7.5 s |
| `weekly_rebalance_dual_engine` | 1.3 s |
| `winners_trend_vol_targeting_overlay` | 1.8 s |

## Borne cumulée sur les deux lots

| | Sans divergence | Borne à 95 % |
|---|---|---|
| #434 seul | 12 | 22,1 % |
| **#434 + #435** | **36** | **8.0 %** |
| version prudente (−1 connu d'avance) | 35 | 8.2 % |

La borne annoncée **avant** de mesurer était de **8,0 %** (8,2 % en version
prudente), pour 24 tirages tous identiques.

## Portée

Les deux lots couvrent **36** scripts sur **285**, soit
**12.6 %** du dépôt. Les tirages étant
aléatoires à graines fixées d'avance et **disjoints**, ils sont reproductibles et
non choisis.
