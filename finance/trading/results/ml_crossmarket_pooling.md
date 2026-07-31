# ML-4 — Cross-market pooling : entraînement conjoint Russell 2000 / S&P 500 / DAX

PREREG : `PREREG_ml_crossmarket_pooling.md` (committé avant tout calcul, commit `064ae48`). Script : `scripts/ml_crossmarket_pooling_backtest.py`.

**Dernier axe fixé a priori de la section 3 du backlog ML.**

## 1. Définition du candidat (figée au PREREG, n_trials local = 1)

- **`LogitL2Pooled`** = `LogisticRegression(C=0.5, max_iter=1000)` — **exactement** les hyperparamètres du `LogitL2` de l'Étape B officielle (`scripts/run_etape_b.py` ligne 68), repris tels quels. Aucun hyperparamètre réglé, aucun grid-search, aucune variante. **La seule chose qui change par rapport à la baseline est la composition de l'échantillon d'entraînement.**
- **Pooling (PREREG §3.4)** : à chaque ré-estimation du marché évalué *m* d'indice `tr`, la ligne `i` du marché `k` (quel qu'il soit) entre dans l'entraînement **si et seulement si** sa date de fin de label `L_k[i] = date_k[min(i+H, n_k−1)]` est **strictement antérieure** à `D_test = date_m[tr]`. Purge exprimée en **dates calendaires**, jamais en indices — les calendriers de bourse US et allemand diffèrent, un embargo en indices laisserait fuir des labels étrangers dans la fenêtre de test.
- **Standardisation (PREREG §3.5)** : par marché, sur les lignes d'entraînement de CE marché ; les lignes de test du marché *m* sont standardisées par `(µ_m, σ_m)`, statistiques d'entraînement de leur propre marché. Aucune statistique n'est calculée sur des données de test.
- **Aucune pondération** : concaténation simple, pas de `class_weight`, pas de rééquilibrage par marché, pas de pondération par récence (PREREG §3.4-5).
- **Features** : les 20 colonnes endogènes de `build_features(df)`, `exog=None`, calculées indépendamment sur chaque marché. Aucune feature exogène ni cross-marché (enseignement ML-2 : ce cycle teste le pooling d'**échantillons**, pas l'injection d'information contemporaine d'un marché dans un autre — déjà testée et échouée en ML-2).
- **Labels** : `triple_barrier_labels(H=5, vol_span=20, mult=1,5)` calculés indépendamment par marché (barrières ∝ volatilité locale, donc automatiquement homogénéisées entre marchés de volatilités différentes).
- **Position** : `signe(p_up − 0,5)` ∈ {−1, +1}, 0 pendant le warmup. **Aucun sizing probabiliste** (enseignement ML-1 : un sizing par probabilité non calibrée détruit l'exposition).
- Walk-forward T0=750, refit 21 j, purge/embargo 5 j (forme calendaire ci-dessus), coûts 5 bps aller-retour sur |Δposition| — **protocole de l'Étape B officielle / ML-1 / ML-2 / ML-3, non modifié**.
- Fraction hors-marché rémunérée à **0 % (cash nu)** — le candidat est ±1 hors warmup, hypothèse sans effet matériel (Règle 10, PREREG §4).

## 2. Données et contrôle qualité (Règle 7)

| Marché | Fichier | Période | Séances | Dates dupliquées | OHLC incohérents | |Rdt| max | Fenêtre OOS (évaluation séparée) |
|---|---|---|---|---|---|---|---|
| Russell 2000 | `data/russell2000_daily.txt` | 10/09/1987 → 13/07/2026 | 9782 | 0 | 0 | 15.4 % | 28/08/1990 → 10/07/2026 (9031) |
| S&P 500 | `data/sp500_daily.txt` | 02/01/1970 → 13/07/2026 | 14252 | 0 | 0 | 22.9 % | 18/12/1972 → 10/07/2026 (13501) |
| DAX | `data/dax_daily.txt` | 01/11/1999 → 10/07/2026 | 6777 | 0 | 0 | 13.1 % | 14/10/2002 → 09/07/2026 (6026) |

*`quality_report()` lève une exception sur toute date dupliquée ou toute barre OHLC incohérente : les trois fichiers l'ont passée, sinon ce rapport n'existerait pas.*

## 3. Test de non-régression du pooling (exigé au PREREG §3.4-3)

Le pooling restreint au **seul marché évalué** doit redonner **exactement** la baseline `walk_forward_proba` (équivalence des masques prouvée analytiquement au PREREG : `date_m[i+5] < date_m[tr] ⟺ i ≤ tr−6 ⟺` masque `indice < tr − EMBARGO`). Vérification numérique :

| Marché | Support des prédictions identique | max &#124;Δp_up&#124; | Points comparés |
|---|---|---|---|
| Russell 2000 | oui | 0.00e+00 | 9032 |
| S&P 500 | oui | 0.00e+00 | 13502 |
| DAX | oui | 0.00e+00 | 6027 |

*Le pooling est donc une **extension stricte** de la baseline : tout écart observé plus bas est imputable au seul ajout des marchés étrangers dans l'échantillon d'entraînement, à aucune autre différence de code. Le script s'arrête (`SystemExit`) si ce test échoue.*

## 4. Taille effective de l'échantillon d'entraînement (l'effet visé)

| Marché évalué | Lignes d'entraînement (solo) — médiane | Lignes (poolé) — médiane | Facteur | Marchés contributeurs (médiane) |
|---|---|---|---|---|
| Russell 2000 | 4,979 | 16,364 | **×3.29** | 3 |
| S&P 500 | 7,205 | 9,940 | **×1.38** | 2 |
| DAX | 3,467 | 20,929 | **×6.04** | 3 |

*C'est le mécanisme même du cycle : le pooling multiplie bien la taille de l'échantillon d'apprentissage. La question du §7 est de savoir si cela se traduit en performance.*

## 5. Performance out-of-sample par marché (nette de coûts, fenêtre propre à chaque marché)

### Russell 2000 — OOS 28/08/1990 → 10/07/2026 (9031 séances)

| Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | Turnover moy./j | Exposition moy. | DSR (n_trials=408) |
|---|---|---|---|---|---|---|---|---|---|
| BuyHold | +0.39 | +0.50 | +0.09 | +8.9 % | -59.9 % | 1.07 | 0.000 | 1.00 | 0.126 |
| Momentum | -0.03 | -0.04 | -0.00 | -0.7 % | -87.5 % | 0.99 | 0.270 | 1.00 | 0.000 |
| LogitL2Solo | +0.17 | +0.22 | +0.02 | +3.7 % | -83.5 % | 1.03 | 0.465 | 1.00 | 0.007 |
| LogitL2Pooled | -0.01 | -0.01 | -0.00 | -0.2 % | -85.1 % | 1.00 | 0.383 | 1.00 | 0.000 |

### S&P 500 — OOS 18/12/1972 → 10/07/2026 (13501 séances)

| Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | Turnover moy./j | Exposition moy. | DSR (n_trials=408) |
|---|---|---|---|---|---|---|---|---|---|
| BuyHold | +0.44 | +0.56 | +0.09 | +8.1 % | -56.8 % | 1.09 | 0.000 | 1.00 | 0.000 |
| Momentum | -0.25 | -0.35 | -0.01 | -4.3 % | -97.1 % | 0.95 | 0.270 | 1.00 | 0.000 |
| LogitL2Solo | +0.44 | +0.58 | +0.07 | +8.0 % | -68.2 % | 1.09 | 0.283 | 1.00 | 0.000 |
| LogitL2Pooled | +0.50 | +0.67 | +0.10 | +9.1 % | -57.6 % | 1.10 | 0.300 | 1.00 | 0.000 |

### DAX — OOS 14/10/2002 → 09/07/2026 (6026 séances)

| Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | Turnover moy./j | Exposition moy. | DSR (n_trials=408) |
|---|---|---|---|---|---|---|---|---|---|
| BuyHold | +0.43 | +0.55 | +0.11 | +9.5 % | -54.8 % | 1.08 | 0.000 | 1.00 | 0.001 |
| Momentum | -0.32 | -0.44 | -0.04 | -6.6 % | -85.2 % | 0.94 | 0.276 | 1.00 | 0.000 |
| LogitL2Solo | +0.03 | +0.04 | +0.01 | +0.7 % | -63.7 % | 1.01 | 0.262 | 1.00 | 0.000 |
| LogitL2Pooled | +0.43 | +0.56 | +0.12 | +9.6 % | -54.7 % | 1.08 | 0.118 | 1.00 | 0.001 |

*`LogitL2Solo` = le MÊME modèle entraîné sur le seul marché évalué, recalculé dans CE run (même code, mêmes labels, même graine) : c'est le contraste interne qui isole l'effet du pooling et rien d'autre.*

## 6. Diagnostics — accuracy, break-even, turnover (JAMAIS un critère)

Enseignement ML-3, rappelé au PREREG §2 : trois cycles consécutifs ont amélioré la *qualité* des paris sans jamais franchir Buy & Hold. Ces chiffres sont donc rapportés **à titre purement descriptif** et n'entrent dans **aucune** branche du critère du §7.

| Marché | Signal | Accuracy (jours où la stratégie parie) | Break-even (bps/trade) |
|---|---|---|---|
| Russell 2000 | Momentum | 51.33 % | +4.00 |
| Russell 2000 | LogitL2Solo | 52.83 % | +8.11 |
| Russell 2000 | LogitL2Pooled | 53.07 % | +4.82 |
| S&P 500 | Momentum | 50.74 % | -1.44 |
| S&P 500 | LogitL2Solo | 54.83 % | +15.77 |
| S&P 500 | LogitL2Pooled | 54.77 % | +16.55 |
| DAX | Momentum | 50.93 % | -4.82 |
| DAX | LogitL2Solo | 52.36 % | +6.04 |
| DAX | LogitL2Pooled | 55.84 % | +35.64 |

## 7. Contrôle de couverture « à plat » (PREREG §2, enseignement ML-2)

Chaque marché est évalué sur SA PROPRE fenêtre de test, définie par SON PROPRE historique : la couverture est de 100 % par construction. Contrôle opérationnel exigé d'avance : **0,00 % de séances à plat hors warmup**.

| Marché | Part OOS à plat (position 0) | Part à plat APRÈS le 1er pari | Exclusivement le warmup |
|---|---|---|---|
| Russell 2000 | 0.00 % | 0.00 % | oui |
| S&P 500 | 0.00 % | 0.00 % | oui |
| DAX | 0.00 % | 0.00 % | oui |

*L'artefact de ML-2 (candidat à plat sur 30,7 % de l'OOS faute d'historique exogène) n'est pas reproduit : l'historique DAX borné au 01/11/1999 n'affecte que la **composition du pool d'entraînement** des autres marchés aux dates anciennes (§4), jamais une fenêtre de test.*

## 8. Verdict par marché (critère chiffré du PREREG §5)

| Marché | (A) Sharpe ET rendement > BuyHold | (B) Calmar > BuyHold | Verdict marché |
|---|---|---|---|
| Russell 2000 | -0.01 vs +0.39 et -0.2 % vs +8.9 % → **NON** | -0.00 vs +0.09 → **NON** | **FAIL** |
| S&P 500 | +0.50 vs +0.44 et +9.1 % vs +8.1 % → **satisfait** | +0.10 vs +0.09 → **satisfait** | **PASS niveau 1** |
| DAX | +0.43 vs +0.43 et +9.6 % vs +9.5 % → **satisfait** | +0.12 vs +0.11 → **satisfait** | **PASS niveau 1** |

## 9. Verdict global (règle d'agrégation FIXÉE AU PREREG §6, avant tout calcul)

Règle pré-enregistrée : **PASS niveau 1 global si et seulement si au moins 2 marchés sur 3 passent**. Justification écrite d'avance : évaluer 3 marchés c'est se donner 3 chances (une règle « 1 sur 3 suffit » contredirait la Règle 2), tandis qu'exiger 3/3 serait excessivement sévère vu l'historique plus court du DAX ; l'hypothèse testée est que le pooling **généralise**, et la majorité stricte en est la traduction fidèle.

**Marchés passant le critère : 2 / 3.**

### PASS niveau 1 (global)

- **Russell 2000** — effet du pooling sur le MÊME modèle : Sharpe +0.17 → -0.01 (-0.17), rendement annualisé +3.7 % → -0.2 %, MDD -83.5 % → -85.1 %, accuracy 52.83 % → 53.07 %, turnover 0.465 → 0.383/j. Benchmark BuyHold du même marché : +0.39 / +8.9 % / Calmar +0.09.
- **S&P 500** — effet du pooling sur le MÊME modèle : Sharpe +0.44 → +0.50 (+0.06), rendement annualisé +8.0 % → +9.1 %, MDD -68.2 % → -57.6 %, accuracy 54.83 % → 54.77 %, turnover 0.283 → 0.300/j. Benchmark BuyHold du même marché : +0.44 / +8.1 % / Calmar +0.09.
- **DAX** — effet du pooling sur le MÊME modèle : Sharpe +0.03 → +0.43 (+0.40), rendement annualisé +0.7 % → +9.6 %, MDD -63.7 % → -54.7 %, accuracy 52.36 % → 55.84 %, turnover 0.262 → 0.118/j. Benchmark BuyHold du même marché : +0.43 / +9.5 % / Calmar +0.11.

Ce PASS est un **niveau 1 uniquement**. Il n'a de valeur qu'après la batterie de validation renforcée (§2.4 du backlog ML, 5 contrôles a-e), exécutée **séparément par marché** — `spa_test` compare un candidat à UN SEUL benchmark partagé, aucun SPA joint multi-marchés n'est tenté (limite mécanique déjà rencontrée aux cycles non-ML #150/#159). Voir `ml_crossmarket_pooling_battery.md`. Aucune notification n'est émise sur un PASS niveau 1 seul.

## 10. Deflated Sharpe Ratio

`n_trials = 408` = 400 (brute-force ML 1-10, closes) + 4 (univers figé Étape B) + 1 (ML-1) + 1 (ML-2) + 1 (ML-3) + 1 (ce cycle ML-4). **Jamais réduit à 1** (Règle 2). DSR calculé **séparément par marché** (jamais sur une série poolée) ; `var_trials` = variance des Sharpe quotidiens des 4 signaux du marché concerné.

| Marché | σ²(SR quot.) | DSR BuyHold | DSR LogitL2Solo | DSR LogitL2Pooled |
|---|---|---|---|---|
| Russell 2000 | 1.499e-04 | 0.126 | 0.007 | **0.000** |
| S&P 500 | 5.060e-04 | 0.000 | 0.000 | **0.000** |
| DAX | 5.162e-04 | 0.001 | 0.000 | **0.001** |

## 11. Traçabilité (Règle 6)

- Script : `finance/trading/scripts/ml_crossmarket_pooling_backtest.py` — toute statistique de ce rapport en sort directement.
- Positions OOS sauvegardées pour audit : `results/ml_crossmarket_pooling_russell2000_pnl.npz`, `results/ml_crossmarket_pooling_sp500_pnl.npz`, `results/ml_crossmarket_pooling_dax_pnl.npz`.
- PREREG : `PREREG_ml_crossmarket_pooling.md`, commit `064ae48`, antérieur à toute exécution de ce script.
- Commande : `python3 finance/trading/scripts/ml_crossmarket_pooling_backtest.py`.
