# Campagne de reproductibilité v3 — classification par test sentinelle (pré-enregistré)

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
aucun paramètre touché, **aucun rapport publié modifié**.

Les campagnes v1 et v2 ont échoué en tentant de reconnaître « le rapport
compte-t-il le dépôt ? » par des **motifs de code**. Ici la propriété est
**testée** : on ajoute au dépôt des fichiers neutres, on ré-exécute, et on
regarde si le rapport bouge. Aucune orthographe n'intervient.

## Tirage

- vivier **entier** (aucune exclusion syntaxique) : **290**
- graine, fixée au pré-enregistrement : **20260818**
- taille : **24**, délai **300 s**

**Les 84 tirages des #434-#437 ne sont pas réutilisés** — troisième remise à
zéro.

- `amihud_illiquidity_tilt_pit_universe`
- `correlation_regime_vol_targeting_overlay`
- `cot_positioning_overlay`
- `credit_spread_overlay`
- `dollar_neutral_composite_vol_targeted`
- `electoral_cycle_combined_overlay`
- `ethereum_momentum_overlay`
- `january_effect_lowprice_overlay_pit_universe`
- `job_openings_overlay`
- `kurtosis_regime_defensive_overlay`
- `leaders_halloween_overlay`
- `macd_overlay`
- `momentum_consistency`
- `momentum_consistency_trend_vol_targeting_overlay`
- `natural_gas_price_overlay`
- `overnight_gap_volatility_overlay`
- `overnight_vs_intraday`
- `parkinson_vol_targeting_overlay`
- `rogers_satchell_vol_targeting_overlay`
- `sma200_trend_overlay`
- `smallcap_proxy_outperformance_breadth_overlay`
- `treasury_bond_etf_overlay`
- `vol_targeting_20_overlay`
- `winners_trend_vol_targeting_overlay`

## Résultat

| | Nombre |
|---|---|
| **identiques** octet à octet | **24** |
| divergences **structurelles** (le rapport compte le dépôt) | **0** |
| divergences **SUBSTANTIELLES** | **0** |
| non concluants | **0** |

### Identiques

| Script | Durée |
|---|---|
| `amihud_illiquidity_tilt_pit_universe` | 10.4 s |
| `correlation_regime_vol_targeting_overlay` | 2.5 s |
| `cot_positioning_overlay` | 3.9 s |
| `credit_spread_overlay` | 6.8 s |
| `dollar_neutral_composite_vol_targeted` | 1.3 s |
| `electoral_cycle_combined_overlay` | 2.2 s |
| `ethereum_momentum_overlay` | 3.2 s |
| `january_effect_lowprice_overlay_pit_universe` | 4.5 s |
| `job_openings_overlay` | 4.9 s |
| `kurtosis_regime_defensive_overlay` | 8.1 s |
| `leaders_halloween_overlay` | 1.7 s |
| `macd_overlay` | 2.2 s |
| `momentum_consistency` | 1.6 s |
| `momentum_consistency_trend_vol_targeting_overlay` | 1.9 s |
| `natural_gas_price_overlay` | 6.4 s |
| `overnight_gap_volatility_overlay` | 7.8 s |
| `overnight_vs_intraday` | 2.1 s |
| `parkinson_vol_targeting_overlay` | 2.3 s |
| `rogers_satchell_vol_targeting_overlay` | 2.3 s |
| `sma200_trend_overlay` | 2.2 s |
| `smallcap_proxy_outperformance_breadth_overlay` | 2.2 s |
| `treasury_bond_etf_overlay` | 5.2 s |
| `vol_targeting_20_overlay` | 2.3 s |
| `winners_trend_vol_targeting_overlay` | 1.9 s |

## Borne

La borne porte sur les divergences **substantielles uniquement** : les
structurelles sont comptées, listées et **exclues du dénominateur**, règle fixée
au pré-enregistrement avant tout tirage.

- tirages retenus **ce lot** : **24** (24 identiques + 0 substantielles)
- tirages retenus **au #438** : **23**

| | Dénominateur | Borne à 95 % |
|---|---|---|
| #438 seul | 23 | 12,2 % |
| ce lot seul | 24 | 11.7 % |
| **cumul #438 + #440** | **47** | **6.2 %** |

Sur un vivier de **290**, il reste de la place pour **~17** divergences substantielles non détectées.

Le cumul est légitime : les deux lots sont **disjoints par construction** et
classés par la **même règle**, fixée au #438 avant tout tirage.

## Contrôle des sentinelles

- fichiers sentinelles subsistant : **0** ✔

## Portée

Ce lot couvre **24** scripts sur **290**, soit
**8.3 %**, par tirage aléatoire à graine fixée.
