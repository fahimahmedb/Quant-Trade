# Reproductibilité des rapports publiés — échantillon tiré au sort (pré-enregistré)

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
aucun paramètre touché, **aucun rapport publié modifié**.

Question jamais posée : un rapport publié se reproduit-il encore à partir de son
propre code ? Les lots #416-#427 ont vérifié **44** rapports, mais seulement ceux
dont le script venait d'être modifié.

## Tirage

- scripts éligibles (backtest **et** rapport publié) : **285**
- graine, fixée au pré-enregistrement : **20260813**
- taille de l'échantillon : **12**
- délai maximal par script : **300 s**

Échantillon tiré, publié **avant** les résultats individuels :

- `corporate_profits_overlay`
- `dispersion_vol_targeting_overlay_pit_universe`
- `diversification_bond_weekly_rebalance_stack`
- `dual_engine_defensive_overlay`
- `gjr_trend_gated_vol_managed`
- `halloween_effect` — *chronométré avant le pré-enregistrement*
- `leveraged_bh`
- `macro_combo_breakeven_claims_trade_overlay`
- `rolling_sharpe_regime_overlay`
- `short_volume_ratio_overlay`
- `weakness_breadth_vol_targeting_overlay`
- `winners_trend_vol_targeting_overlay_pit_universe`

**1** des 12 avaient été chronométrés avant le
pré-enregistrement pour dimensionner le délai, et s'étaient reproduits. Ils
sont restés dans le tirage — les exclure l'aurait biaisé — mais leur résultat
était **connu d'avance** et ne doit pas compter comme une vérification neuve.

## Résultat

| | Nombre |
|---|---|
| rapports **identiques** octet à octet | **12** |
| rapports **divergents** | **0** |
| **non concluants** (délai / erreur) | **0** |

**Taux de reproductibilité sur les 12 scripts effectivement testés : 100.0 %.**

### Identiques

| Script | Durée |
|---|---|
| `corporate_profits_overlay` | 5.4 s |
| `dispersion_vol_targeting_overlay_pit_universe` | 5.6 s |
| `diversification_bond_weekly_rebalance_stack` | 1.0 s |
| `dual_engine_defensive_overlay` | 1.3 s |
| `gjr_trend_gated_vol_managed` | 167.4 s |
| `halloween_effect` *(connu d'avance)* | 2.3 s |
| `leveraged_bh` | 1.6 s |
| `macro_combo_breakeven_claims_trade_overlay` | 10.0 s |
| `rolling_sharpe_regime_overlay` | 6.2 s |
| `short_volume_ratio_overlay` | 2.7 s |
| `weakness_breadth_vol_targeting_overlay` | 1.5 s |
| `winners_trend_vol_targeting_overlay_pit_universe` | 3.8 s |

## Portée — ce que 12 tirages disent, et ne disent pas

L'échantillon couvre **12** scripts sur **285** éligibles, soit
**4.2 %**. Un résultat sur 12 tirages ne prouve rien
sur les 276 autres : il indique seulement s'il existe un problème **massif** ou
**fréquent**. Une divergence rare passerait au travers.

Le tirage étant aléatoire à graine fixée, il est **reproductible et non choisi**.
