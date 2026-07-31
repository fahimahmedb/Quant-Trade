# ML-3 — Architecture unique bien régularisée : gradient boosting à early stopping purgé (nasdaq_composite_daily)

PREREG : `PREREG_ml_regularized_architecture.md` (committé avant calcul, commit `5fa9761`). Script : `scripts/ml_regularized_architecture_backtest.py`.

## 1. Architecture (figée au PREREG, n_trials local = 1)

- **Un seul modèle non linéaire**, choisi et justifié au PREREG §2 **avant tout calcul** : gradient boosting (`HistGradientBoostingClassifier`) avec early stopping sur folds purgés. La variante MLP du backlog a été écartée explicitement (pas de `torch` dans l'environnement, pas de dropout dans `sklearn`, et un MLP changerait simultanément trop de choses par rapport à la baseline) ; elle n'est **pas** repoussée à un sous-cycle de repli.
- **Hyperparamètres identiques à ceux du `HistGB` de l'Étape B** (`max_depth=3`, `learning_rate=0,05`, `l2_regularization=1,0`, `min_samples_leaf=40`, `random_state=42`) — repris tels quels, donc aucun essai caché. **Seul `max_iter` change de statut** : plafond 400 au lieu d'une valeur fixe de 150.
- **Early stopping purgé** : à chaque ré-estimation, la fenêtre d'entraînement (déjà purgée de l'embargo walk-forward) est coupée chronologiquement — validation = les **20 % les plus récents**, purge interne de **5 lignes** (= H) juste avant, apprentissage = le reste. `k*` = itération minimisant la log-loss de validation (`staged_predict_proba`), contrainte à [10, 400]. Le modèle déployé est ré-ajusté sur la fenêtre d'entraînement **complète** à `max_iter=k*`. La découpe aléatoire par défaut de scikit-learn (`early_stopping=True`) est **refusée** : elle mélangerait des labels triple-barrière chevauchants entre apprentissage et validation.
- **Aucun grid-search** : ni `GridSearchCV` ni `RandomizedSearchCV`, aucun hyperparamètre choisi sur une métrique de trading. La seule quantité sélectionnée (`k*`) l'est sur une log-loss **interne à la fenêtre d'entraînement**, jamais sur l'OOS.
- **Features** : les 20 colonnes endogènes de `build_features(df)`, `exog=None` — **aucune feature exogène** (enseignement ML-2 : une feature à historique court met le modèle à plat et ampute son rendement ; ce cycle porte sur l'architecture seule).
- **Position** : `signe(p_up − 0,5)` ∈ {−1, +1}, 0 tant qu'aucun modèle n'est entraîné. **Aucun sizing probabiliste** (enseignement ML-1, déclaré au PREREG §5) : aucune calibration n'est en jeu, l'effet mesuré est celui de l'architecture seule.
- Walk-forward T0=750, refit 21 j, purge/embargo 5 j, coûts 5 bps aller-retour sur |Δposition| — **protocole de l'Étape B officielle, non modifié**.
- Fraction hors-marché rémunérée à **0 % (cash nu)** — hypothèse déclarée au PREREG §8 (Règle 10). Le candidat est ±1 hors warmup.
- OOS = 500 séances (10/07/2024 → 09/07/2026), fenêtre strictement identique à l'Étape B officielle, à ML-1 et à ML-2.

## 2. Performance out-of-sample (nette de coûts, fenêtre OOS complète)

| Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | Turnover moy./j | Exposition moy. |
|---|---|---|---|---|---|---|---|---|
| BuyHold | +0.78 | +1.03 | +0.62 | +18.9 % | -24.3 % | 1.15 | 0.000 | 1.00 |
| Momentum | -0.33 | -0.43 | -0.19 | -7.1 % | -32.8 % | 0.94 | 0.304 | 1.00 |
| LogitL2 | -0.68 | -0.99 | -0.26 | -14.0 % | -43.8 % | 0.88 | 0.276 | 1.00 |
| HistGB | +0.03 | +0.05 | +0.02 | +0.7 % | -28.6 % | 1.01 | 0.528 | 1.00 |
| HistGB-ES | +0.39 | +0.52 | +0.38 | +9.0 % | -20.4 % | 1.07 | 0.116 | 1.00 |

*`HistGB-ES` = le candidat (capacité choisie par early stopping purgé). `HistGB` = la MÊME architecture à capacité fixe 150, recalculée dans CE run (même code, mêmes labels, même graine) : c'est la comparaison interne qui isole l'effet de la régularisation de capacité, et rien d'autre.*

## 3. Accuracy directionnelle et coût de rupture

| Signal | Accuracy (jours où la stratégie parie) | Break-even (bps/trade) |
|---|---|---|
| Momentum | 53.80 % | -4.66 |
| LogitL2 | 52.00 % | -16.57 |
| HistGB | 49.80 % | +5.56 |
| HistGB-ES | 53.60 % | +34.61 |

## 4. Capacité sélectionnée par l'early stopping (diagnostic, PREREG §5)

- Ré-estimations du candidat : **24** (dont 0 en mode de repli `max_iter=150`).
- `k*` retenu : min **10**, médiane **11**, moyenne **23**, max **146**.
- Blocs atteignant le plafond 400 : **0** (0.0 %) — le plafond n'est donc pas la contrainte active dans la grande majorité des cas.
- Part des blocs où `k*` < 150 (capacité **inférieure** à celle de l'Étape B) : **100.0 %**.

## 5. Deflated Sharpe Ratio

σ²(SR quotidiens des 5 signaux) = 1.3194e-03. Deux lectures :

| Signal | Sharpe quot. | DSR (n_trials=407, campagne ML entière) | DSR (n_trials=4, échelle Étape B) |
|---|---|---|---|
| BuyHold | +0.0493 | **0.091** | 0.598 |
| Momentum | -0.0210 | **0.002** | 0.091 |
| LogitL2 | -0.0427 | **0.000** | 0.038 |
| HistGB | +0.0021 | **0.009** | 0.209 |
| HistGB-ES | +0.0246 | **0.030** | 0.380 |

*La colonne de gauche est celle qui compte : n_trials=407 = 400 (brute-force ML 1-10, closes) + 4 (univers figé Étape B) + 1 (ML-1) + 1 (ML-2) + 1 (ce cycle). Jamais réduit à 1 (Règle 2). La colonne de droite ne sert qu'à comparer aux chiffres publiés de `etape_B_ndx100.md`.*

## 6. Contrôle « à plat » exigé au PREREG §4

- Part des séances OOS où le candidat est à plat (position 0) : **0.00 %**.
- Ces séances sont-elles exclusivement le warmup initial du walk-forward (bloc contigu en tête d'OOS, aucune interruption ensuite) : **oui**.
- Attendu : le candidat n'utilise que des features endogènes disponibles sur toute la période ; toute autre valeur signalerait un bug (le contrôle est pré-enregistré précisément pour ne pas reproduire l'artefact de ML-2).

## 7. Verdict (critère chiffré du PREREG §7)

- **(A)** Sharpe HistGB-ES (+0.39) > Sharpe BuyHold (+0.78) **ET** rendement HistGB-ES (+9.0 %) > rendement BuyHold (+18.9 %) → **NON satisfait**.
- **(B)** Calmar HistGB-ES (+0.38) > Calmar BuyHold (+0.62) → **NON satisfait**.

### FAIL

Effet de la régularisation de capacité (early stopping purgé) sur la MÊME architecture : Sharpe +0.03 → +0.39 (+0.36), accuracy 49.80 % → 53.60 % (+3.80 pt), rendement annualisé +0.7 % → +9.0 %, MDD -28.6 % → -20.4 %, turnover 0.528 → 0.116/j, break-even +5.56 → +34.61 bps/trade.

Le critère pré-enregistré n'est pas atteint : régulariser la capacité d'une architecture non linéaire par early stopping purgé **ne suffit pas** à la faire passer au-dessus de Buy & Hold. La batterie de validation renforcée n'est pas déclenchée (elle ne s'applique qu'à un PASS niveau 1). Résultat rapporté tel quel, sans changement d'architecture, d'hyperparamètres, de sizing ni de critère a posteriori (Règle 1) — en particulier **aucun basculement vers la variante MLP**, explicitement interdit par le PREREG §11.

## 8. Notes de traçabilité (Règle 6)

- **Baseline recalculée, pas recopiée.** Le `HistGB` mesuré ici (+0.03 de Sharpe) peut différer du chiffre publié dans `results/etape_B_ndx100.md` (+0,23) : `triple_barrier_labels` a été modifié depuis (σ locale = écart-type glissant strict sur [t−20, t)). Les 5 lignes du §2 proviennent **du même run, du même code et des mêmes labels** — la comparaison avec/sans early stopping est donc interne et cohérente, et c'est d'elle que dépend le verdict.
- **Absence de fuite par la validation** : la découpe est positionnelle sur des lignes déjà rangées chronologiquement, la validation est le bloc le plus RÉCENT, et un purge de 5 lignes (= H) sépare apprentissage et validation, ce qui retire les événements dont la triple barrière chevauche le bloc de validation. Aucune ligne postérieure à `tr − embargo` n'entre dans un `fit` (garanti par `walk_forward_proba`, `finance/src/prediction.py`).
- **`k*` est sélectionné sur une log-loss, jamais sur une métrique de trading** : aucun retour d'information de l'OOS vers la capacité du modèle.
- **Erratum de rédaction (sans effet sur le calcul)** : le PREREG §4 écrit « les 21 colonnes endogènes » ; `build_features(df)` en produit en réalité **20**. Le chiffre 21 était repris tel quel du PREREG ML-2, qui contenait déjà cette coquille. Aucune conséquence : le script consomme `build_features(df)` **en bloc**, sans sélection ni comptage de colonnes — l'univers de features est donc bien celui de l'Étape B officielle, inchangé. Signalé ici plutôt que corrigé dans le PREREG, qui ne doit pas être modifié après calcul (Règle 1).
- **σ²(SR essais)** des deux colonnes DSR du §5 est calculée sur les 5 signaux de ce run ; la colonne « échelle Étape B » sert d'ordre de grandeur, pas de verdict.
- Fichier de positions sauvegardé pour audit : `results/ml_regularized_architecture_composite_pnl.npz` (positions OOS, positions de la baseline HistGB, rendements, dates, coût, σ², n_trials, série des `k*`).
