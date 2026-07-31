# ML-2 — Features exogènes taux / cross-marché sur LogitL2 (nasdaq100_daily)

PREREG : `PREREG_ml_exogenous_features_rates_crossmarket.md` (committé avant calcul). Script : `scripts/ml_exogenous_features_rates_crossmarket_backtest.py`.

## 1. Mécanisme (figé au PREREG, n_trials local = 1)

- **Modèle inchangé** : LogitL2 de l'Étape B (`LogisticRegression(C=0.5, max_iter=1000)`), standardisation calée sur la fenêtre d'entraînement, labels triple barrier H=5 / ±1,5σ.
- **Features** : les 20 colonnes endogènes de `build_features` + **5 colonnes exogènes** — `exog_dgs10_level`, `exog_slope_10y_3mo` (DGS10−DGS3MO), `exog_dgs10_chg`, `exog_dgs3mo_chg`, `exog_dax_ret_lag1`.
- **Alignement causal** : chaque feature exogène au jour `t` vaut la (les) dernière(s) observation(s) **strictement antérieure(s)** à `t` de sa série (`obs_date < t`), calendrier propre à chaque série, aucun `ffill` d'observation future. Motif documenté aux cycles non-ML #110/#140 : le DAX clôture ~17:30 CET, soit **pendant** la séance NDX du même jour — utiliser sa clôture du jour `t` serait une fuite.
- **Position** : `signe(p_up − 0,5)` ∈ {−1, +1}, 0 tant qu'aucun modèle n'est entraîné. **Aucun sizing probabiliste** (enseignement ML-1, déclaré au PREREG §3 avant tout calcul) : aucune calibration n'est donc en jeu.
- Walk-forward T0=750, refit 21 j, purge/embargo 5 j, coûts 5 bps aller-retour sur |Δposition| — **protocole de l'Étape B officielle, non modifié**.
- Fraction hors-marché rémunérée à **0 % (cash nu)** — hypothèse déclarée au PREREG §7 (Règle 10), conservatrice pour l'hypothèse testée.
- OOS = 9522 séances (19/09/1988 → 10/07/2026), fenêtre strictement identique à l'Étape B officielle et à ML-1.

## 2. Avec / sans features exogènes (net de coûts, fenêtre OOS complète)

| Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | Turnover moy./j | Exposition moy. |
|---|---|---|---|---|---|---|---|---|
| BuyHold | +0.52 | +0.69 | +0.08 | +14.5 % | -82.9 % | 1.10 | 0.000 | 1.00 |
| Momentum | -0.28 | -0.38 | -0.02 | -7.1 % | -97.6 % | 0.95 | 0.275 | 1.00 |
| LogitL2 | +0.35 | +0.45 | +0.10 | +9.5 % | -59.6 % | 1.07 | 0.268 | 1.00 |
| HistGB | +0.46 | +0.63 | +0.11 | +12.6 % | -66.9 % | 1.09 | 0.376 | 1.00 |
| LogitL2Exog | +0.32 | +0.35 | +0.07 | +7.4 % | -63.2 % | 1.07 | 0.157 | 0.69 |

*`LogitL2Exog` = le candidat (endogène + exogène). `LogitL2` = le même modèle avec les seules features endogènes, recalculé dans CE run (même code, mêmes labels) : c'est la comparaison interne qui isole l'effet des features exogènes.*

## 3. Accuracy directionnelle et coût de rupture

| Signal | Accuracy (jours où la stratégie parie) | Break-even (bps/trade) |
|---|---|---|
| Momentum | 51.21 % | -5.60 |
| LogitL2 | 54.20 % | +18.42 |
| HistGB | 53.44 % | +17.56 |
| LogitL2Exog | 55.08 % | +22.99 |

## 4. Deflated Sharpe Ratio

σ²(SR quotidiens des 5 signaux) = 4.0811e-04. Deux lectures :

| Signal | Sharpe quot. | DSR (n_trials=406, campagne ML entière) | DSR (n_trials=4, échelle Étape B) |
|---|---|---|---|
| BuyHold | +0.0328 | **0.004** | 0.870 |
| Momentum | -0.0178 | **0.000** | 0.000 |
| LogitL2 | +0.0219 | **0.000** | 0.527 |
| HistGB | +0.0288 | **0.001** | 0.770 |
| LogitL2Exog | +0.0200 | **0.000** | 0.450 |

*La colonne de gauche est celle qui compte : n_trials=406 = 400 (brute-force ML 1-10, closes) + 4 (univers figé Étape B) + 1 (ML-1) + 1 (ce cycle). Jamais réduit à 1 (Règle 2). La colonne de droite ne sert qu'à comparer aux chiffres publiés de `etape_B_ndx100.md`.*

## 5. Disponibilité des données exogènes — contrôle anti-artefact (PREREG §5)

- Le DAX ne commence qu'au 01/11/1999 : le candidat est **à plat (position 0) sur 30.7 % des séances OOS**, dont toute la période antérieure à sa première estimation.
- Fenêtre dot-com (01/2000 → 12/2002, 752 séances) : MDD candidat -63.2 % vs Buy & Hold -82.9 % ; le candidat y est à plat sur 8.8 % des séances.
- Cette pénalité (rendement annualisé mécaniquement réduit par les séances à plat) est **assumée et pré-enregistrée** : la fenêtre de verdict reste celle de l'Étape B, sans raccourci, comme au cycle ML-1.

### 5.1 Lecture secondaire — fenêtre restreinte (aucun effet sur le verdict)

Fenêtre où le candidat est réellement opérationnel : 06/04/2000 → 10/07/2026 (6603 séances), **Buy & Hold recalculé sur exactement la même fenêtre**.

| Signal | Sharpe ann. | Calmar | Rdt ann. | MDD |
|---|---|---|---|---|
| BuyHold | +0.28 | +0.05 | +7.8 % | -81.3 % |
| LogitL2 | +0.32 | +0.10 | +8.9 % | -55.7 % |
| LogitL2Exog | +0.38 | +0.10 | +10.8 % | -63.2 % |

Sur cette fenêtre : critère (A) satisfait, critère (B) satisfait. **Lecture informative uniquement** — le verdict du §6 reste celui de la fenêtre OOS complète (PREREG §5).

**Avertissement de lecture (obligatoire, quel que soit le sens du résultat)** : cette fenêtre écarte les 2919 premières séances OOS (19/09/1988 → 05/04/2000) — elle s'ouvre à quelques mois du sommet de marché de 2000, donc juste avant le krach dot-com. Elle ne change pas seulement le candidat : elle affaiblit aussi le benchmark — Sharpe Buy & Hold +0.52 (fenêtre complète) → +0.28 (fenêtre restreinte, -0.24). Un raccourcissement de fenêtre qui déplace ainsi le benchmark favorise mécaniquement le candidat, indépendamment de sa qualité prédictive. La fenêtre est **imposée par la disponibilité du DAX (01/11/1999), pas choisie** — mais c'est exactement pour ce type de biais que le PREREG §5 lui refuse tout effet sur le verdict. Un candidat qui ne franchit le seuil que sur cette fenêtre n'est PAS un PASS et ne déclenche NI la batterie renforcée NI de notification.

## 6. Verdict (critère chiffré du PREREG §6)

- **(A)** Sharpe LogitL2Exog (+0.32) > Sharpe BuyHold (+0.52) **ET** rendement LogitL2Exog (+7.4 %) > rendement BuyHold (+14.5 %) → **NON satisfait**.
- **(B)** Calmar LogitL2Exog (+0.07) > Calmar BuyHold (+0.08) → **NON satisfait**.

### FAIL

Effet des features exogènes sur le modèle : Sharpe +0.35 → +0.32 (-0.03), accuracy 54.20 % → 55.08 % (+0.88 pt), rendement annualisé +9.5 % → +7.4 %, MDD -59.6 % → -63.2 %, exposition moyenne 1.00 → 0.69.

Le critère pré-enregistré n'est pas atteint : l'ajout de features exogènes taux/cross-marché **ne suffit pas** à faire passer LogitL2 au-dessus de Buy & Hold. La batterie de validation renforcée n'est pas déclenchée (elle ne s'applique qu'à un PASS niveau 1). Résultat rapporté tel quel, sans ajustement des features, du sizing ni du critère a posteriori (Règle 1).

## 7. Notes de traçabilité (Règle 6)

- **Baseline recalculée, pas recopiée.** Le `LogitL2` mesuré ici (+0.35 de Sharpe) diffère du chiffre publié dans `results/etape_B_ndx100.md` (+0,30) : `triple_barrier_labels` a été modifié depuis (σ locale = écart-type glissant strict sur [t−20, t)). Les 5 lignes du §2 proviennent **du même run, du même code et des mêmes labels** — la comparaison avec/sans exogènes est donc interne et cohérente, et c'est d'elle que dépend le verdict.
- **Non-régression vérifiée par assertion dans le script** : `build_features(df, exog=...)` reproduit à l'identique les colonnes endogènes de `build_features(df)` (assert en tête de script) — aucun script existant (Étapes B/C/D, ML-1) n'est affecté par l'extension.
- **Causalité vérifiée par construction** : `_asof_prev` (`finance/src/prediction.py`) utilise `np.searchsorted(..., side="left") − 1`, soit strictement `obs_date < t`. Une observation du jour `t` ne peut pas entrer dans une feature du jour `t`.
- **σ²(SR essais)** des deux colonnes DSR du §4 est calculée sur les 5 signaux de ce run ; la colonne « échelle Étape B » sert d'ordre de grandeur, pas de verdict.
- Fichier de positions sauvegardé pour audit : `results/ml_exogenous_features_rates_crossmarket_pnl.npz` (positions OOS, rendements, dates, coût, σ², n_trials).
