# Campagne de reproductibilité v2 — critère d'auto-référence et relance (pré-enregistré)

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
aucun paramètre touché, **aucun rapport publié modifié**.

## Le critère d'auto-référence, appliqué

Fixé au pré-enregistrement, **avant tout tirage**, et portant sur le **code** :
un script est auto-référent si son source balaie l'ensemble du dépôt
(`glob` sur `nonml_*_backtest.py`, `*_pnl.npz`, `nonml_*_result.md`).

Un rapport auto-référent **dérive nécessairement** dès qu'un cycle ajoute un
fichier : sa divergence ne dit rien sur la péremption d'un résultat.

- scripts avec rapport publié : **303**
- **auto-référents, exclus** : **17**
- vivier de la campagne v2 : **286**

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
- `momentum_12_1_pit_universe`
- `momentum_consistency_trend_vol_targeting_overlay`
- `momentum_dispersion_trend_and_overlay`
- `momentum_turnover_doublesort`
- `nonfarm_payrolls_overlay`
- `oil_market_volatility_overlay`
- `postelection_year_overlay`
- `ppi_inflation_overlay`
- `range_position_vol_targeting_overlay_pit_universe`
- `sma200_breadth_vol_targeting_overlay`
- `sma200_breadth_vol_targeting_overlay_pit_universe`
- `sma200_leaders_overlay_pit_universe`
- `smallcap_proxy_outperformance_breadth_overlay_pit_universe`

## Résultat

| | Nombre |
|---|---|
| **identiques** octet à octet | **24** |
| **divergents** | **0** |
| **non concluants** | **0** |

### Identiques

| Script | Durée |
|---|---|
| `atr_vol_targeting_overlay` | 2.3 s |
| `credit_spread_overlay` | 6.9 s |
| `diversification_bond_overlay_crossmarket` | 1.8 s |
| `dry_bulk_shipping_overlay` | 3.0 s |
| `em_dm_relative_strength_overlay` | 4.9 s |
| `empty_pass_requalification` | 0.4 s |
| `garman_klass_vol_targeting_overlay` | 2.2 s |
| `goldencross_vol_targeting_overlay` | 2.3 s |
| `index_skewness_regime_overlay` | 7.9 s |
| `low_vol_tilt` | 1.6 s |
| `lowvol_regime_vol_targeting_overlay` | 2.1 s |
| `momentum_12_1_pit_universe` | 4.0 s |
| `momentum_consistency_trend_vol_targeting_overlay` | 1.8 s |
| `momentum_dispersion_trend_and_overlay` | 1.7 s |
| `momentum_turnover_doublesort` | 1.8 s |
| `nonfarm_payrolls_overlay` | 7.3 s |
| `oil_market_volatility_overlay` | 4.2 s |
| `postelection_year_overlay` | 2.1 s |
| `ppi_inflation_overlay` | 7.0 s |
| `range_position_vol_targeting_overlay_pit_universe` | 6.1 s |
| `sma200_breadth_vol_targeting_overlay` | 1.7 s |
| `sma200_breadth_vol_targeting_overlay_pit_universe` | 3.9 s |
| `sma200_leaders_overlay_pit_universe` | 4.8 s |
| `smallcap_proxy_outperformance_breadth_overlay_pit_universe` | 7.2 s |

## Borne v2 — et le recul assumé

| | Sans divergence | Borne à 95 % |
|---|---|---|
| revendiqué au #435, **caduc** depuis le #436 | 36 | 8.0 % |
| **campagne v2, ce lot** | **24** | **11.7 %** |

**La borne est moins bonne qu'avant : 11.7 % contre 8.0 %.**
Le pré-enregistrement l'annonçait chiffrée avant la mesure. C'est le coût
direct du refus de reclasser 60 tirages selon une règle écrite après eux, et
ce recul est le prix d'une borne qui, elle, veut dire quelque chose.

Sur un vivier de **286** rapports non auto-référents, il reste
de la place pour **~33** divergences substantielles.

## Portée

Ce lot couvre **24** scripts sur **286** du vivier v2,
soit **8.4 %**. Tirage aléatoire à graine
fixée d'avance, donc reproductible et non choisi.


> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).