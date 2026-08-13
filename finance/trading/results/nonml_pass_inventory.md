# Inventaire des verdicts après la campagne de correction (#382)

**Recomptage mécanique, non pré-enregistré** : on lit les fichiers de résultat
présents dans `results/` et on compte. Aucun paramètre, aucun seuil.

## Pourquoi ce recomptage

Le chiffre **« 101 PASS niveau 1 sur 372 hypothèses »** circulait de synthèse en
synthèse. Il datait d'**avant** la campagne #375-#381, qui a fait tomber 20 PASS.
Il n'est plus utilisable et ne doit plus être cité.

## Décompte

| | |
|---|---|
| fichiers `*_result.md` présents | **269** |
| verdict **PASS** | **92** |
| verdict **FAIL** | **173** |
| verdict **indéterminé** (non analysable) | **4** |

Le dénominateur est le nombre de fichiers de résultat réellement présents, pas
un compteur historique reporté. Il ne coïncide pas avec le « 372 hypothèses »
du backlog : certains cycles étaient des synthèses ou des batteries sans
fichier de résultat propre, d'autres produisent plusieurs fichiers.

### Les 4 verdicts indéterminés

Comptés explicitement plutôt qu'écartés en silence — leur format de rapport
ne porte pas de verdict en gras analysable :

- `nonml_cash_rate_correction_44_crossmarket`
- `nonml_cash_rate_correction_44_weekly_rebalance`
- `nonml_diversification_bond_overlay_crossmarket`
- `nonml_ewma_defensive_overlay_and_triple_engine`

## Contrôle de cohérence

Le décompte pris **après** la correction de composition mais **avant** celle
d'agrégation (cycle #377) donnait **101 PASS sur 265 verdicts lisibles**. On en
compte ici **92 sur 265**.

Écart : **9**. La correction d'agrégation a fait tomber 8 PASS
(`momentum_52w_high` au #378, plus 7 au #379). Les deux chiffres se
réconcilient exactement — le décompte n'est pas un comptage indépendant qui
« retomberait » par chance, mais la conséquence arithmétique des
reclassifications documentées.

Les 12 reclassifications dues au bug de composition, elles, étaient déjà
intégrées dans le 101 : elles sont antérieures à cette mesure.

## Batteries Règle 9 : lesquelles sont caduques

Une batterie de validation renforcée qui valide une stratégie **désormais
FAIL** ne valide plus rien : elle porte sur un résultat qui n'existe plus.

| | |
|---|---|
| batteries présentes | **83** |
| **caduques** (stratégie désormais FAIL) | **13** |
| encore adossées à un PASS | 62 |
| sans résultat associé analysable | 8 |

### Batteries caduques

- `nonml_bitcoin_momentum_overlay`
- `nonml_bond_market_volatility_overlay`
- `nonml_cash_rate_correction_defensive_vol_targeting_44`
- `nonml_credit_card_delinquency_overlay`
- `nonml_cross_market_correlation_ndx_dax_overlay`
- `nonml_delinquency_nfci_baa10y_graduated_overlay`
- `nonml_delinquency_nfci_baa10y_majority_overlay`
- `nonml_dollar_neutral_composite_vol_targeted`
- `nonml_ewma_vol_targeting_overlay`
- `nonml_financial_conditions_overlay`
- `nonml_gjr_vol_managed_weekly_rebalance`
- `nonml_momentum_consistency_pit_universe`
- `nonml_volatility_managed_portfolio_gjr`

**Ces batteries ne sont pas supprimées** — l'historique est conservé — mais
elles ne doivent plus être invoquées comme validation.

## Portée

Ce décompte porte sur les fichiers de résultat **tels qu'ils existent après
correction**. Il ne rejuge aucune stratégie et n'en revalide aucune : il
constate. Un PASS recensé ici reste un PASS **de niveau 1** — le critère
renforcé Sharpe+rendement — et non un verdict final au sens de la Règle 9.
