# ML-2 — Features exogènes taux / cross-marché sur LogitL2 (nasdaq_composite_daily)

PREREG : `PREREG_ml_exogenous_features_rates_crossmarket.md` (committé avant calcul). Script : `scripts/ml_exogenous_features_rates_crossmarket_backtest.py`.

## 1. Mécanisme (figé au PREREG, n_trials local = 1)

- **Modèle inchangé** : LogitL2 de l'Étape B (`LogisticRegression(C=0.5, max_iter=1000)`), standardisation calée sur la fenêtre d'entraînement, labels triple barrier H=5 / ±1,5σ.
- **Features** : les 20 colonnes endogènes de `build_features` + **5 colonnes exogènes** — `exog_dgs10_level`, `exog_slope_10y_3mo` (DGS10−DGS3MO), `exog_dgs10_chg`, `exog_dgs3mo_chg`, `exog_dax_ret_lag1`.
- **Alignement causal** : chaque feature exogène au jour `t` vaut la (les) dernière(s) observation(s) **strictement antérieure(s)** à `t` de sa série (`obs_date < t`), calendrier propre à chaque série, aucun `ffill` d'observation future. Motif documenté aux cycles non-ML #110/#140 : le DAX clôture ~17:30 CET, soit **pendant** la séance NDX du même jour — utiliser sa clôture du jour `t` serait une fuite.
- **Position** : `signe(p_up − 0,5)` ∈ {−1, +1}, 0 tant qu'aucun modèle n'est entraîné. **Aucun sizing probabiliste** (enseignement ML-1, déclaré au PREREG §3 avant tout calcul) : aucune calibration n'est donc en jeu.
- Walk-forward T0=750, refit 21 j, purge/embargo 5 j, coûts 5 bps aller-retour sur |Δposition| — **protocole de l'Étape B officielle, non modifié**.
- Fraction hors-marché rémunérée à **0 % (cash nu)** — hypothèse déclarée au PREREG §7 (Règle 10), conservatrice pour l'hypothèse testée.
- OOS = 500 séances (10/07/2024 → 09/07/2026), fenêtre strictement identique à l'Étape B officielle et à ML-1.

## 2. Avec / sans features exogènes (net de coûts, fenêtre OOS complète)

| Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | Turnover moy./j | Exposition moy. |
|---|---|---|---|---|---|---|---|---|
| BuyHold | +0.78 | +1.03 | +0.62 | +18.9 % | -24.3 % | 1.15 | 0.000 | 1.00 |
| Momentum | -0.33 | -0.43 | -0.19 | -7.1 % | -32.8 % | 0.94 | 0.304 | 1.00 |
| LogitL2 | -0.68 | -0.99 | -0.26 | -14.0 % | -43.8 % | 0.88 | 0.276 | 1.00 |
| HistGB | +0.03 | +0.05 | +0.02 | +0.7 % | -28.6 % | 1.01 | 0.528 | 1.00 |
| LogitL2Exog | -1.24 | -1.76 | -0.39 | -24.0 % | -50.9 % | 0.80 | 0.436 | 1.00 |

*`LogitL2Exog` = le candidat (endogène + exogène). `LogitL2` = le même modèle avec les seules features endogènes, recalculé dans CE run (même code, mêmes labels) : c'est la comparaison interne qui isole l'effet des features exogènes.*

## 3. Accuracy directionnelle et coût de rupture

| Signal | Accuracy (jours où la stratégie parie) | Break-even (bps/trade) |
|---|---|---|
| Momentum | 53.80 % | -4.66 |
| LogitL2 | 52.00 % | -16.57 |
| HistGB | 49.80 % | +5.56 |
| LogitL2Exog | 48.00 % | -19.97 |

## 4. Deflated Sharpe Ratio

σ²(SR quotidiens des 5 signaux) = 2.2980e-03. Deux lectures :

| Signal | Sharpe quot. | DSR (n_trials=406, campagne ML entière) | DSR (n_trials=4, échelle Étape B) |
|---|---|---|---|
| BuyHold | +0.0493 | **0.017** | 0.490 |
| Momentum | -0.0210 | **0.000** | 0.054 |
| LogitL2 | -0.0427 | **0.000** | 0.021 |
| HistGB | +0.0021 | **0.001** | 0.140 |
| LogitL2Exog | -0.0783 | **0.000** | 0.003 |

*La colonne de gauche est celle qui compte : n_trials=406 = 400 (brute-force ML 1-10, closes) + 4 (univers figé Étape B) + 1 (ML-1) + 1 (ce cycle). Jamais réduit à 1 (Règle 2). La colonne de droite ne sert qu'à comparer aux chiffres publiés de `etape_B_ndx100.md`.*

## 5. Disponibilité des données exogènes — contrôle anti-artefact (PREREG §5)

- Le DAX ne commence qu'au 01/11/1999 : le candidat est **à plat (position 0) sur 0.0 % des séances OOS**, dont toute la période antérieure à sa première estimation.
- Fenêtre dot-com non couverte par cet échantillon.
- Cette pénalité (rendement annualisé mécaniquement réduit par les séances à plat) est **assumée et pré-enregistrée** : la fenêtre de verdict reste celle de l'Étape B, sans raccourci, comme au cycle ML-1.

Sur cet échantillon, les séries exogènes couvrent **toute** la fenêtre OOS : la « fenêtre restreinte » du PREREG §5 coïncide avec la fenêtre de verdict, il n'y a donc aucune lecture secondaire distincte à rapporter.

## 6. Verdict (critère chiffré du PREREG §6)

- **(A)** Sharpe LogitL2Exog (-1.24) > Sharpe BuyHold (+0.78) **ET** rendement LogitL2Exog (-24.0 %) > rendement BuyHold (+18.9 %) → **NON satisfait**.
- **(B)** Calmar LogitL2Exog (-0.39) > Calmar BuyHold (+0.62) → **NON satisfait**.

### FAIL

Effet des features exogènes sur le modèle : Sharpe -0.68 → -1.24 (-0.57), accuracy 52.00 % → 48.00 % (-4.00 pt), rendement annualisé -14.0 % → -24.0 %, MDD -43.8 % → -50.9 %, exposition moyenne 1.00 → 1.00.

Le critère pré-enregistré n'est pas atteint : l'ajout de features exogènes taux/cross-marché **ne suffit pas** à faire passer LogitL2 au-dessus de Buy & Hold. La batterie de validation renforcée n'est pas déclenchée (elle ne s'applique qu'à un PASS niveau 1). Résultat rapporté tel quel, sans ajustement des features, du sizing ni du critère a posteriori (Règle 1).

## 7. Notes de traçabilité (Règle 6)

- **Baseline recalculée, pas recopiée.** Le `LogitL2` mesuré ici (-0.68 de Sharpe) diffère du chiffre publié dans `results/etape_B_ndx100.md` (+0,30) : `triple_barrier_labels` a été modifié depuis (σ locale = écart-type glissant strict sur [t−20, t)). Les 5 lignes du §2 proviennent **du même run, du même code et des mêmes labels** — la comparaison avec/sans exogènes est donc interne et cohérente, et c'est d'elle que dépend le verdict.
- **Non-régression vérifiée par assertion dans le script** : `build_features(df, exog=...)` reproduit à l'identique les colonnes endogènes de `build_features(df)` (assert en tête de script) — aucun script existant (Étapes B/C/D, ML-1) n'est affecté par l'extension.
- **Causalité vérifiée par construction** : `_asof_prev` (`finance/src/prediction.py`) utilise `np.searchsorted(..., side="left") − 1`, soit strictement `obs_date < t`. Une observation du jour `t` ne peut pas entrer dans une feature du jour `t`.
- **σ²(SR essais)** des deux colonnes DSR du §4 est calculée sur les 5 signaux de ce run ; la colonne « échelle Étape B » sert d'ordre de grandeur, pas de verdict.
- Fichier de positions sauvegardé pour audit : `results/ml_exogenous_features_rates_crossmarket_composite_pnl.npz` (positions OOS, rendements, dates, coût, σ², n_trials).
