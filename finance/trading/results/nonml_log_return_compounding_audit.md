# Audit — composition de rendements log avec la formule des rendements simples

**Ceci n'est pas un backtest de stratégie et n'incrémente pas le compteur
d'hypothèses.** C'est un audit de code : aucun paramètre à calibrer, aucun
seuil de succès à choisir, donc aucun degré de liberté exploitable. Il n'a
pas fait l'objet d'un pré-enregistrement pour cette raison.

## Rectification d'une première version de cet audit

Une première version (commit `0d0edd9`) annonçait **151 fichiers exploitables,
20 basculements dont 17 dans le sens dangereux**. Ces chiffres étaient FAUX :
la reconstruction du P&L y était appliquée à des fichiers de schéma composite
qu'elle ne décrit pas — notamment la famille `diversification_bond_*`, dont le
P&L combine deux jambes d'actif (`pos_eq*r_asset + pos_bond*r_alt`) alors que la
reconstruction n'en modélisait qu'une. Quatre lignes du tableau publié en
dépendaient et étaient donc erronées.

Après exclusion de ces schémas : **129 exploitables, 16 basculements dont 13
dans le sens dangereux**. Le constat de fond (bug réel, biais directionnel
favorable aux overlays défensifs) est inchangé ; son ampleur mesurée est
revue à la baisse.

## Le bug

Les scripts construisent la série de l'actif en rendements **log** :

```python
bh_full = np.log(close[1:] / close[:-1])
```

puis composent le rendement total avec la formule des rendements **simples** :

```python
ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0
```

La composition correcte de rendements log est `np.exp(pnl.sum()) - 1.0`.

Le Sharpe et le MDD ne sont PAS touchés : `trading_metrics` traite bien sa
série comme du log (`eq = np.cumsum(strat_ret)`, MDD converti par `exp(mdd)-1`).
Seule la colonne « rendement total » — et donc la jambe « Rdt>BH » du critère
renforcé — est affectée.

## Pourquoi l'erreur n'est pas neutre

`cumprod(1+x) = exp(Σ log(1+x_i))` et `log(1+x) ≈ x - x²/2`. La formule buguée
retranche donc approximativement `Σ x_i²/2` : elle **pénalise les séries à forte
variance**. Les overlays de ce backlog étant majoritairement défensifs (ils
réduisent la variance), le bug les **avantage systématiquement** sur la jambe
rendement. La direction du biais est prévisible avant même de mesurer, et les
basculements observés ci-dessous la confirment.

## Mesure

- scripts de `finance/trading/scripts/` combinant rendements log et
  composition `cumprod(1+·)` : **318** sur 837
- idiome vérifié directement dans la source pour :
  `nonml_delinquency_nfci_baa10y_corr_move_cpi_majority_overlay` (lignes 79 / 119-120),
  `nonml_bitcoin_momentum_overlay` (94 / 115-116),
  `nonml_dispersion_vol_targeting_overlay_pit_universe` (102 / 139-140),
  `nonml_volatility_managed_portfolio_gjr` (78 / 90-91).
- échelle des séries sauvegardées vérifiée : toutes en **fraction**, aucune en
  pourcentage (le script GJR convertit bien via `r_pct / 100.0`) — le balayage
  ci-dessous n'est donc pas faussé par un mélange d'unités.
- `.npz` exploitables (schéma standard `pos`/`r_asset`/`dates`/`cost_bps`) : **129**
- **exclus** (schéma composite ou illisible) : **24**

Les fichiers exclus le sont parce que la reconstruction du P&L vérifiée dans
la source ne les décrit pas : `r_alt` signale une seconde jambe d'actif
(`pos_eq*r_asset + pos_bond*r_alt`), et `pos_primary`/`var_trials` des pipelines
ML hors périmètre. Les mesurer avec `pos*r_asset` produirait un P&L faux.

<details><summary>Liste des exclus</summary>

- `ml_crossmarket_pooling_dax` — schéma composite (market, n_trials, pos_solo, var_trials) — P&L non modélisé ici
- `ml_crossmarket_pooling_russell2000` — schéma composite (market, n_trials, pos_solo, var_trials) — P&L non modélisé ici
- `ml_crossmarket_pooling_sp500` — schéma composite (market, n_trials, pos_solo, var_trials) — P&L non modélisé ici
- `ml_exogenous_features_rates_crossmarket` — schéma composite (n_trials, pos_primary, var_trials) — P&L non modélisé ici
- `ml_exogenous_features_rates_crossmarket_composite` — schéma composite (n_trials, pos_primary, var_trials) — P&L non modélisé ici
- `ml_meta_labeling_logitl2_composite` — schéma composite (n_trials, pos_primary, var_trials) — P&L non modélisé ici
- `ml_meta_labeling_logitl2_ndx` — schéma composite (n_trials, pos_primary, var_trials) — P&L non modélisé ici
- `ml_regularized_architecture` — schéma composite (k_star, n_trials, pos_primary, var_trials) — P&L non modélisé ici
- `ml_regularized_architecture_composite` — schéma composite (k_star, n_trials, pos_primary, var_trials) — P&L non modélisé ici
- `nonml_cash_rate_correction_44_crossmarket_russell2000` — schéma composite (r_alt) — P&L non modélisé ici
- `nonml_cash_rate_correction_44_crossmarket_sp500` — schéma composite (r_alt) — P&L non modélisé ici
- `nonml_cash_rate_correction_44_weekly_rebalance_ndx` — schéma composite (r_alt) — P&L non modélisé ici
- `nonml_cash_rate_correction_44_weekly_rebalance_russell2000` — schéma composite (r_alt) — P&L non modélisé ici
- `nonml_cash_rate_correction_44_weekly_rebalance_sp500` — schéma composite (r_alt) — P&L non modélisé ici
- `nonml_cash_rate_correction_defensive_vol_targeting_44` — schéma composite (r_alt) — P&L non modélisé ici
- `nonml_defensive_diversification_bond_overlay` — schéma composite (r_alt) — P&L non modélisé ici
- `nonml_diversification_bond_overlay_composite` — schéma composite (r_alt) — P&L non modélisé ici
- `nonml_diversification_bond_overlay_crossmarket_russell2000` — schéma composite (r_alt) — P&L non modélisé ici
- `nonml_diversification_bond_overlay_crossmarket_sp500` — schéma composite (r_alt) — P&L non modélisé ici
- `nonml_diversification_bond_overlay_dax` — schéma composite (r_alt) — P&L non modélisé ici
- `nonml_diversification_bond_triple_engine_stack` — schéma composite (r_alt) — P&L non modélisé ici
- `nonml_diversification_bond_weekly_rebalance_stack` — schéma composite (r_alt) — P&L non modélisé ici
- `nonml_dollar_neutral_composite_pit` — schéma non standard
- `nonml_dollar_neutral_composite_vol_targeted` — schéma non standard

</details>

- verdicts « Rdt>BH » inchangés : **113**
- verdicts qui **basculent** : **16**
  - dont OUI → non (le bug fabriquait un verdict favorable) : **13**
  - dont non → OUI (le bug masquait un verdict favorable) : **3**

### Verdicts qui basculent

| Stratégie (marché sauvegardé dans le `.npz`) | Rdt BH (bugué) | Rdt overlay (bugué) | Rdt BH (corrigé) | Rdt overlay (corrigé) | Verdict bugué | Verdict corrigé |
|---|---|---|---|---|---|---|
| nonml_bitcoin_momentum_overlay | +424.3% | +445.3% | +596.4% | +551.0% | OUI | non |
| nonml_credit_card_delinquency_overlay | +3129.3% | +3352.9% | +11049.9% | +8710.8% | OUI | non |
| nonml_cross_market_correlation_ndx_dax_overlay | +225.5% | +279.3% | +756.1% | +604.2% | OUI | non |
| nonml_defensive_calmar_vol_targeting_overlay | +6416.7% | +9256.6% | +25465.6% | +18048.2% | OUI | non |
| nonml_delinquency_nfci_baa10y_corr_move_majority_overlay | +1542.1% | +1700.5% | +2844.6% | +2781.7% | OUI | non |
| nonml_delinquency_nfci_baa10y_graduated_overlay | +3129.3% | +3227.1% | +11049.9% | +7189.9% | OUI | non |
| nonml_delinquency_nfci_baa10y_majority_overlay | +3129.3% | +4142.3% | +11049.9% | +9319.3% | OUI | non |
| nonml_delinquency_nfci_combined_overlay | +3129.3% | +3279.3% | +11049.9% | +10521.2% | OUI | non |
| nonml_dispersion_vol_targeting_overlay_pit_universe | +391.3% | +380.5% | +542.3% | +556.4% | non | OUI |
| nonml_ewma_defensive_overlay | +4553.2% | +6221.4% | +16652.5% | +11534.3% | OUI | non |
| nonml_ewma_defensive_overlay_and_triple_engine | +4553.2% | +7718.4% | +16652.5% | +15539.7% | OUI | non |
| nonml_gjr_calm_regime_overlay_russell2000 | +609.7% | +602.2% | +1570.1% | +1722.8% | non | OUI |
| nonml_gjr_vol_forecast_momentum_overlay_russell2000 | +886.7% | +815.9% | +2239.3% | +6170.8% | non | OUI |
| nonml_midterm_election_overlay | +6599.5% | +7339.6% | +26208.9% | +22786.1% | OUI | non |
| nonml_stlfsi_financial_stress_overlay | +2118.1% | +2349.2% | +7188.6% | +4351.9% | OUI | non |
| nonml_volatility_managed_portfolio_gjr | +4553.2% | +7178.8% | +16652.5% | +15557.5% | OUI | non |

## Les simulations 300 € sont touchées aussi

Les scripts `*_sim_300e.py` utilisent le même idiome
(`CAPITAL0 * np.cumprod(1.0 + pnl)` sur des rendements log). L'ampleur y est
faible parce que la fenêtre est courte (63 séances) et que le terme d'erreur
croît avec l'horizon : sur la jambe Buy&Hold NDX, **349,93 € publié contre
352,39 € corrigé** (+2,46 €, soit +0,7 %). À comparer au même bug sur 24 ans
(+1542,9 % publié contre +2846,0 % réel). Le biais est donc négligeable à
3 mois et massif à l'échelle du backtest complet.

## Portée exacte de ce que ceci établit — et ce qu'il n'établit pas

Chaque `.npz` ne contient qu'**un seul marché** (celui que le script a choisi de
sauvegarder, en général NDX). Le critère du backlog est « ≥4/5 marchés ». Un
basculement ci-dessus établit donc que le verdict de **ce marché-là** était un
artefact de la formule ; il ne renverse pas mécaniquement le PASS global de la
stratégie. Statuer exige de ré-exécuter les scripts concernés avec la
composition corrigée, sur les 5 marchés. Cet audit ne le fait pas et ne
reclasse aucune entrée du backlog.

Ce qui est établi en revanche :

1. Le bug est **réel et confirmé dans le code source**, pas une hypothèse.
2. Il est **répandu** : l'idiome coexiste avec des rendements log dans une
   large partie des scripts du backlog.
3. Son biais est **directionnel et favorable aux overlays défensifs**, c'est-à-dire
   favorable dans le sens qui produit des PASS.
4. Sur les marchés mesurables ici, il a effectivement fabriqué des verdicts
   favorables dans **13 cas sur 16 basculements**.

Les chiffres de rendement total publiés dans tous les résultats concernés sont
par ailleurs **sous-estimés** (ex. NDX Buy&Hold : +1542,9 % publié contre
+2846,0 % réel), y compris pour Buy&Hold lui-même.

## Vérification anti-cheat : ÉCHEC ATTENDU, non corrigé

`nonml_anti_cheat_check.py log_return_compounding_audit` rend **ÉCHEC (1/2)** :

- **[FAIL]** pré-enregistrement `PREREG_log_return_compounding_audit.md` non trouvé ;
- **[OK]** aucun motif de recherche de paramètres ni de dépendance ML détecté.

Cet échec est **attendu et n'a pas été corrigé**. L'outil est conçu pour des
backtests de stratégie, où le PREREG empêche de choisir seuils et univers après
avoir vu les résultats. Un audit de code n'a ni seuil ni univers à choisir : le
verdict est une propriété du code (`cumprod(1+·)` appliqué à du log), pas un
résultat sensible à un calibrage. La seconde vérification — la seule qui porte
ici — passe.

**Aucun PREREG rétroactif n'a été écrit.** En antidater un pour faire passer le
contrôle serait précisément la fraude que ce contrôle existe pour empêcher.

## Correction des 115 simulations 300 € (#381)

Les scripts `*_sim_300e.py` portaient les deux bugs. Tri identique à celui des
backtests :

- **93 simulations à P&L log** (indice ou série chargée depuis un `.npz`) :
  `equity = CAPITAL0 * np.exp(np.cumsum(pnl))` remplace
  `CAPITAL0 * np.cumprod(1.0 + pnl)`.
- **21 simulations de panier** : `R` passe en rendements simples, `cumprod(1+pnl)`
  redevient donc correct, `trading_metrics` reçoit `np.log1p(pnl)`.
- **1 simulation cumulant les deux cas** (`amihud_illiquidity_tilt`) : `R_simple`
  dédié au P&L, `R` restant en log pour le signal d'illiquidité.
- **2 exclues et signalées** : `pead_sim_300e` lit des rendements **déjà simples**
  depuis un CSV — son `cumprod` est correct et le « corriger » l'aurait cassé ;
  `dollar_neutral_composite_vol_targeted` consomme un `.npz` amont dont la
  convention n'a pas été vérifiée.

Deux échecs d'exécution rencontrés, tous deux de causes déjà connues et sans
rapport avec la correction (argument de marché manquant, dtype `object` refusé
par `np.isnan` sous pandas ≥ 3) ; corrigés.

**Ampleur mesurée sur 164 montants publiés, dans 82 fichiers de résultat :**

| | |
|---|---|
| écart moyen | **+7,00 € (+2,03 %)** |
| écart médian | +2,73 € |
| écart maximum | +53,11 € |
| montants revus à la hausse | **164 / 164** |

**Tous les montants publiés étaient sous-estimés, sans exception** — conforme au
sens du biais établi au #375. La jambe Buy&Hold NDX passe de 349,93 € à
352,39 €, exactement la valeur annoncée lors du diagnostic initial.

L'ampleur reste modeste (2 % en moyenne) parce que la fenêtre est courte
(63 séances) : le terme d'erreur croît avec l'horizon. Ces simulations étaient
donc sous-estimées mais pas trompeuses sur l'ordre de grandeur, contrairement aux
rendements de backtest sur 24 ans (+1542,9 % publié contre +2846,0 % réel).
