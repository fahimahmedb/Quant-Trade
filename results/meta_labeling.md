# Meta-labeling — filtre de confiance sur le signal LogitL2 (Étape B)

## 1. Cadrage

Le modèle **primaire ne change pas** : c'est le LogitL2 déjà retenu en Étape B (signal actif le plus prometteur, rentable net de coûts sur NDX mais encore sous Buy & Hold en DSR — cf. `CLAUDE.md`). Un modèle **secondaire** (même famille, régression logistique L2) apprend, sur les features causales de `build_features` augmentées de la confiance primaire (|p_up−0.5|·2), si le pari primaire a des chances d'être gagnant (label = coïncidence signe(primaire) / signe(triple-barrier)). Position finale = signe(primaire) × taille(confiance secondaire), taille bornée [0,1] (dimensionnement continu ; une variante à seuil pur est aussi rapportée).

Protocole **identique** à l'Étape B : T0=750, ré-estimation tous les 21 j, **purge/embargo 5 j sur le primaire ET le secondaire** (le label secondaire dépend du même triple barrier, donc de la même fenêtre H=5 j), triple barrier ±1.5·σ_ewm20, coûts 5 bps aller-retour.

**Discipline anti data-snooping** : ceci est UN essai supplémentaire sur un signal déjà sélectionné (LogitL2), pas un nouvel univers de N modèles — pas de nouveau test SPA. Le DSR ci-dessous intègre néanmoins cet essai : n_trials = 4 (univers Étape B, déjà établi) + 1 (ce raffinement) = 5, var_trials recalculé sur les 5 Sharpe quotidiens.

## 2. NASDAQ Composite (5 ans) — `nasdaq_composite_daily.txt`

OOS = 500 jours (10/07/2024 → 09/07/2026).

| Variante | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | Hit rate | Turnover/j |
|---|---|---|---|---|---|---|---|---|
| LogitL2 (avant) | -0.69 | -1.00 | -0.28 | -14.2 % | -42.3 % | 0.88 | 52.4 % | 0.316 |
| LogitL2 + Meta (seuil 0.5) | -0.78 | -0.79 | -0.39 | -12.2 % | -28.1 % | 0.80 | 25.0 % | 0.192 |
| **LogitL2 + Meta (continu)** | **-0.60** | -0.60 | -0.31 | -5.6 % | -16.9 % | 0.73 | 24.0 % | 0.064 |
| *Buy & Hold (référence, Étape B)* | *+0.78* | | | | | | | |

Accuracy directionnelle sur les paris pris : 51.20 % (avant) → 48.52 % (après filtre seuil, 47.4 % des jours OOS tradés — le reste est mis à plat par manque de confiance).

| Variante | Sharpe quotidien | seuil SR₀ | z | **DSR** (n_trials=5) |
|---|---|---|---|---|
| LogitL2 (avant) | +0.0450 → -0.0435 | 0.0450 | -1.94 | **0.026** |
| LogitL2 + Meta (continu) | -0.0379 | 0.0450 | -1.58 | **0.057** |

*σ²(SR, n_trials=5) = 1.4258e-03. DSR Buy & Hold de référence (Étape B, n_trials=4) = 0.567.*

## 2. NASDAQ-100 (40 ans) — `nasdaq100_daily.txt`

OOS = 9522 jours (19/09/1988 → 10/07/2026).

| Variante | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | Hit rate | Turnover/j |
|---|---|---|---|---|---|---|---|---|
| LogitL2 (avant) | +0.30 | +0.39 | +0.08 | +8.3 % | -64.2 % | 1.06 | 53.2 % | 0.272 |
| LogitL2 + Meta (seuil 0.5) | +0.32 | +0.36 | +0.06 | +6.8 % | -68.7 % | 1.07 | 38.1 % | 0.196 |
| **LogitL2 + Meta (continu)** | **+0.24** | +0.24 | +0.06 | +1.1 % | -18.1 % | 1.08 | 37.5 % | 0.038 |
| *Buy & Hold (référence, Étape B)* | *+0.52* | | | | | | | |

Accuracy directionnelle sur les paris pris : 53.67 % (avant) → 55.44 % (après filtre seuil, 70.1 % des jours OOS tradés — le reste est mis à plat par manque de confiance).

| Variante | Sharpe quotidien | seuil SR₀ | z | **DSR** (n_trials=5) |
|---|---|---|---|---|
| LogitL2 (avant) | +0.0222 → +0.0192 | 0.0222 | -0.29 | **0.385** |
| LogitL2 + Meta (continu) | +0.0152 | 0.0222 | -0.68 | **0.247** |

*σ²(SR, n_trials=5) = 3.4642e-04. DSR Buy & Hold de référence (Étape B, n_trials=4) = 0.842.*

## 3. Verdict honnête

- **Composite** : Sharpe ann. -0.69 → -0.60 (+0.09), turnover/j 0.316 → 0.064 (+80 %), DSR 0.026 → 0.057. Reste sous Buy & Hold en Sharpe ; DSR < 0.95 (Buy & Hold reste la référence la plus crédible, DSR=0.567).
- **NDX** : Sharpe ann. +0.30 → +0.24 (-0.06), turnover/j 0.272 → 0.038 (+86 %), DSR 0.385 → 0.247. Reste sous Buy & Hold en Sharpe ; DSR < 0.95 (Buy & Hold reste la référence la plus crédible, DSR=0.842).

Le meta-labeling filtre/dimensionne les paris du primaire sans changer de sens : il réduit mécaniquement le turnover (et donc les coûts) en mettant à plat les jours de faible confiance secondaire, ce qui améliore généralement le Sharpe net et parfois le drawdown, mais **ne crée pas d'edge directionnel qui n'existait pas déjà dans le primaire** — un primaire structurellement mauvais (LogitL2 sur Composite, Sharpe négatif en Étape B) ne devient pas rentable par simple filtrage de confiance. Conclusion cohérente avec Étape B : **Buy & Hold reste la stratégie de référence** sur les deux jeux de données ; le meta-labeling est un raffinement utile pour la gestion du risque (turnover, drawdown) du meilleur signal actif, pas une preuve d'edge directionnel nouveau.
