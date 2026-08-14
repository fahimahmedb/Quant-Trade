# Extension du critère d'inactivité aux schémas panier (pré-enregistré)

Requalification **documentaire** : aucun verdict recalculé. La règle du #417 est
transposée sans assouplissement — identité du P&L entre la jambe candidate et sa
**propre** jambe de référence, hors première séance.

## Couverture

- fichiers `nonml_*_pnl.npz` : **208**
- schéma **panier**, traités par ce cycle : **21**
- schéma **deux jambes**, exclus explicitement : **13**
- schéma indiciel, déjà traités au #417 : **172**
- autres / inexploitables : **2**

Exclus (schéma « deux jambes », référence non stockée dans le fichier) :

- `cash_rate_correction_44_crossmarket_russell2000`
- `cash_rate_correction_44_crossmarket_sp500`
- `cash_rate_correction_44_weekly_rebalance_ndx`
- `cash_rate_correction_44_weekly_rebalance_russell2000`
- `cash_rate_correction_44_weekly_rebalance_sp500`
- `cash_rate_correction_defensive_vol_targeting_44`
- `defensive_diversification_bond_overlay`
- `diversification_bond_overlay_composite`
- `diversification_bond_overlay_crossmarket_russell2000`
- `diversification_bond_overlay_crossmarket_sp500`
- `diversification_bond_overlay_dax`
- `diversification_bond_triple_engine_stack`
- `diversification_bond_weekly_rebalance_stack`

Définir ce que « ne rien faire » signifie pour ces candidats demanderait une
convention inventée pour l'occasion. Ils sont comptés et listés, pas dissous.

## Résultat

- candidats panier **requalifiés** : **0**
- déjà étiquetés : **0**
- PASS panier dont la jambe candidate **agit** : **13**

**Aucun candidat requalifié.**

### PASS panier dont la jambe candidate agit

| Candidat | Séances de P&L différent | Rendement candidat | Rendement référence |
|---|---|---|---|
| `amihud_illiquidity_tilt` | 1269 / 1270 | +334.1 % | +171.6 % |
| `january_effect_lowprice_overlay` | 106 / 1375 | +470.2 % | +373.6 % |
| `january_effect_lowprice_overlay_pit_universe` | 247 / 2900 | +660.3 % | +482.3 % |
| `leaders_index52w_high_overlay` | 679 / 1144 | +220.9 % | +108.0 % |
| `leaders_trend_union_overlay` | 841 / 1144 | +270.7 % | +108.0 % |
| `leaders_vol_targeting_20_overlay` | 1123 / 1124 | +155.4 % | +127.6 % |
| `lowvol_sma200_overlay` | 1033 / 1336 | +122.4 % | +60.8 % |
| `momentum_12_1` | 1143 / 1144 | +227.4 % | +142.4 % |
| `momentum_12_1_pit_universe` | 2906 / 2907 | +511.1 % | +352.1 % |
| `momentum_turnover_doublesort` | 1143 / 1144 | +328.8 % | +222.6 % |
| `short_term_momentum` | 1390 / 1391 | +259.4 % | +209.4 % |
| `sma200_leaders_overlay` | 841 / 1144 | +270.7 % | +108.0 % |
| `winners_trend_vol_targeting_overlay` | 531 / 1376 | +318.5 % | +250.7 % |

## Lecture

Le pré-enregistrement annonçait **0 requalification**, en s'appuyant sur les
rendements déjà publiés : deux jambes affichant des rendements différents ne
peuvent pas avoir des P&L identiques.

**Attente confirmée.** La dernière dette actionnable du protocole est fermée
sans avoir rien trouvé — ce qui était l'issue annoncée, et reste un résultat :
le PASS obtenu par inactivité demeure un cas isolé, désormais vérifié sur
**tous** les schémas où la question est décidable.


> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).