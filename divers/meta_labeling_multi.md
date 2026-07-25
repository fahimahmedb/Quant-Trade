# Meta-labeling multi-variantes — 3 modèles secondaires sur LogitL2 (NDX 40 ans)

## 1. Cadrage

Le modèle **primaire ne change pas** : LogitL2 déjà retenu en Étape B (signal actif le plus prometteur sur NDX, rentable net de coûts mais encore sous Buy & Hold en DSR — cf. `CLAUDE.md`). On teste ici **3 variantes de modèle SECONDAIRE**, univers FIGÉ avant évaluation (`src/meta_labeling.py::SECONDARY_MODELS`) :

1. **LogitL2** (baseline, identique à `results/meta_labeling.md`)

2. **RandomForest** (sklearn, défauts — `n_estimators=100`, seul `random_state` fixé, aucun tuning)

3. **XGBoost** (défauts `xgboost` — `n_estimators=100`, seul `random_state` fixé, aucun tuning)


Même protocole que l'Étape B pour le primaire ET pour chacun des 3 secondaires : T0=750, ré-estimation tous les 21 j, **purge/embargo 5 j** (le label secondaire dépend du même triple barrier H=5 j que le primaire), triple barrier ±1.5·σ_ewm20, coûts 5 bps aller-retour. Position finale = signe(primaire) × taille(confiance secondaire) — dimensionnement continu (variante à seuil 0.5 également rapportée pour lecture).

**Discipline anti data-snooping** : ceci n'est pas un nouvel univers de modèles primaires — c'est UN raffinement (filtrage/dimensionnement) du signal déjà sélectionné (LogitL2), testé sous 3 formes de secondaire. Le DSR ci-dessous intègre ces 3 essais : n_trials=3, var_trials calculé sur les 3 Sharpe quotidiens obtenus (dimensionnement continu).

## 2. NASDAQ-100 (40 ans) — `nasdaq100_daily.txt`

OOS = 9522 jours (19/09/1988 → 10/07/2026).

| Variante | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | Hit rate | Turnover/j |
|---|---|---|---|---|---|---|---|---|
| LogitL2 primaire (avant, référence) | +0.30 | +0.39 | +0.08 | +8.3 % | -64.2 % | 1.06 | 53.2 % | 0.272 |
| **+ Meta LogitL2 (continu)** | **+0.24** | +0.24 | +0.06 | +1.1 % | -18.1 % | 1.08 | 37.5 % | 0.038 |
| + Meta LogitL2 (seuil 0.5) | +0.32 | +0.36 | +0.06 | +6.8 % | -68.7 % | 1.07 | 38.1 % | 0.196 |
| **+ Meta RandomForest (continu)** | **+0.23** | +0.25 | +0.05 | +1.4 % | -22.5 % | 1.08 | 28.5 % | 0.105 |
| + Meta RandomForest (seuil 0.5) | +0.16 | +0.17 | +0.03 | +3.1 % | -70.9 % | 1.04 | 29.3 % | 0.374 |
| **+ Meta XGBoost (continu)** | **+0.11** | +0.11 | +0.02 | +1.3 % | -50.7 % | 1.03 | 28.1 % | 0.252 |
| + Meta XGBoost (seuil 0.5) | +0.24 | +0.25 | +0.05 | +4.7 % | -57.4 % | 1.06 | 29.2 % | 0.412 |
| *Buy & Hold (référence, Étape B)* | *+0.52* | | | | | | | |

Accuracy directionnelle du primaire sur les paris pris (avant filtre) : 53.67 %.

| Variante | Accuracy après filtre seuil | % jours tradés |
|---|---|---|
| LogitL2 | 55.44 % | 70.1 % |
| RandomForest | 54.51 % | 54.3 % |
| XGBoost | 53.66 % | 53.8 % |


### DSR (n_trials=3, univers des 3 variantes de secondaire)

| Variante | Sharpe quotidien | seuil SR₀ | z | **DSR** |
|---|---|---|---|---|
| *LogitL2 primaire (avant, référence externe, n_trials=4 Étape B)* | *+0.0192* | | | *0.372* |
| + Meta LogitL2 (continu) | +0.0152 | 0.0039 | +1.11 | **0.866** |
| + Meta RandomForest (continu) | +0.0147 | 0.0039 | +1.06 | **0.856** |
| + Meta XGBoost (continu) | +0.0070 | 0.0039 | +0.30 | **0.619** |

*σ²(SR, n_trials=3) = 2.0959e-05. DSR Buy & Hold de référence (Étape B, n_trials=4) = 0.842.*

## 3. Verdict honnête

- **LogitL2 (meilleure variante)** : Sharpe ann. +0.30 → +0.24 (-0.06), turnover/j 0.272 → 0.038 (+86 %), DSR (n_trials=3) = 0.866. Reste sous Buy & Hold en Sharpe ; DSR < 0.95 (Buy & Hold reste la référence la plus crédible, DSR=0.842).
- **RandomForest** : Sharpe ann. +0.30 → +0.23 (-0.07), turnover/j 0.272 → 0.105 (+61 %), DSR (n_trials=3) = 0.856. Reste sous Buy & Hold en Sharpe ; DSR < 0.95 (Buy & Hold reste la référence la plus crédible, DSR=0.842).
- **XGBoost (pire variante)** : Sharpe ann. +0.30 → +0.11 (-0.19), turnover/j 0.272 → 0.252 (+7 %), DSR (n_trials=3) = 0.619. Reste sous Buy & Hold en Sharpe ; DSR < 0.95 (Buy & Hold reste la référence la plus crédible, DSR=0.842).

Les 3 variantes de secondaire filtrent/dimensionnent le même primaire sans changer de sens : leur effet principal est la réduction du turnover (donc des coûts) via la mise à plat des jours de faible confiance. **LogitL2** est la variante la plus favorable au Sharpe net ici, **XGBoost** la moins favorable (peut dégrader le Sharpe net du primaire si le secondaire, plus flexible/non-linéaire, sur-apprend le bruit du label triple-barrier sur un historique encore restreint en early walk-forward). Aucune des 3 variantes ne crée d'edge directionnel qui n'existait pas déjà dans le primaire : le meta-labeling reste un raffinement de gestion du risque (turnover, drawdown), **pas une preuve de battre Buy & Hold** — cohérent avec `results/meta_labeling.md` et la conclusion de l'Étape B. Buy & Hold demeure la stratégie de référence sur NDX.
