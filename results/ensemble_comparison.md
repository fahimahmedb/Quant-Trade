# Comparaison univers primaires complet — NDX (4 signaux × {solo, +overlay})

## 1. Cadrage

Objectif (cf. `CLAUDE.md`, Étape D) : valider lequel des 4 signaux primaires figés de l'Étape B (BuyHold, Momentum, LogitL2, HistGB) bénéficie le plus de l'overlay de gestion du risque (vol-targeting GJR-GARCH(1,1)-t), et si une combinaison simple des 4 signaux bat Buy & Hold.

Aucun des deux moteurs n'est réinventé : le primaire (Étape B) et l'overlay (cap 2.0×, coupe totale au 90e percentile in-sample) sont ceux **déjà retenus** dans les études précédentes du repo (`results/etape_D_overlay_optimized.md`, `finance/src/integrated_pipeline.py`), pas re-optimisés ici.

**Protocole figé** : NDX (`nasdaq100_daily.txt`), walk-forward T0=750, ré-estimation tous les 21 j (signal ET GJR-t), purge/embargo 5 j (triple barrier H=5 j, ±1.5·σ_ewm20), coûts 5 bps aller-retour. OOS = 9522 jours (19/09/1988 → 10/07/2026, ~37.8 ans).

## 2. Univers de 8 variantes (FIGÉ avant évaluation — N=8 pour le DSR)

| # | Variante | Composition |
|---|---|---|
| 1 | BuyHold | toujours long |
| 2 | BuyHold+Overlay | toujours long × exposition vol-targeting |
| 3 | Momentum | signe rendement 10j |
| 4 | Momentum+Overlay | signe rendement 10j × exposition vol-targeting |
| 5 | LogitL2 | régression logistique L2 |
| 6 | LogitL2+Overlay | régression logistique L2 × exposition vol-targeting |
| 7 | HistGB | HistGradientBoosting |
| 8 | HistGB+Overlay | HistGradientBoosting × exposition vol-targeting |

## 3. Performance out-of-sample (nette de coûts)

| Variante | Sharpe ann. | Calmar | **MDD %** | Rdt ann. % | Turnover/j | Hit rate |
|---|---|---|---|---|---|---|
| BuyHold | +0.52 | +0.08 | -82.9 | +14.5 | 0.000 | 54.8 % |
| BuyHold+Overlay | +0.66 | +0.22 | -48.4 | +15.7 | 0.060 | 48.1 % |
| Momentum | -0.28 | -0.02 | -97.6 | -7.1 | 0.275 | 50.6 % |
| Momentum+Overlay | -0.28 | -0.02 | -96.8 | -6.1 | 0.358 | 44.3 % |
| LogitL2 | +0.35 | +0.10 | -59.6 | +9.5 | 0.268 | 53.4 % |
| LogitL2+Overlay | +0.44 | +0.13 | -52.4 | +10.2 | 0.320 | 46.9 % |
| HistGB | +0.46 | +0.11 | -66.9 | +12.6 | 0.376 | 52.3 % |
| HistGB+Overlay | +0.25 | +0.05 | -63.8 | +5.7 | 0.464 | 45.6 % |

## 4. Deflated Sharpe Ratio (N=8, univers des 8 variantes)

σ²(SR essais) = 5.0504e-04.

| Variante | Sharpe quotidien | seuil SR₀ | z | **DSR** |
|---|---|---|---|---|
| BuyHold | +0.0328 | 0.0328 | +0.00 | **0.501** |
| BuyHold+Overlay | +0.0413 | 0.0328 | +0.83 | **0.796** |
| Momentum | -0.0178 | 0.0328 | -4.94 | **0.000** |
| Momentum+Overlay | -0.0177 | 0.0328 | -4.94 | **0.000** |
| LogitL2 | +0.0219 | 0.0328 | -1.05 | **0.146** |
| LogitL2+Overlay | +0.0277 | 0.0328 | -0.50 | **0.309** |
| HistGB | +0.0288 | 0.0328 | -0.39 | **0.349** |
| HistGB+Overlay | +0.0157 | 0.0328 | -1.67 | **0.048** |

## 5. Effet de l'overlay, signal par signal (critère de succès explicite)

Succès si DSR(signal+overlay) ≥ DSR(BuyHold) = **0.501** OU réduction du MDD > 30% sans perdre plus de 20% de rendement annualisé, **par rapport à la variante solo du même signal** (déclaré avant lecture du résultat).

| Signal | DSR +Overlay | DSR BuyHold | Crit. DSR | ΔMDD rel. (solo→+overlay) | Rdt conservé | Crit. MDD/Rdt | Verdict |
|---|---|---|---|---|---|---|---|
| Momentum | 0.000 | 0.501 | non | +0.8% | 86% | non | échec |
| LogitL2 | 0.309 | 0.501 | non | +12.1% | 108% | non | échec |
| HistGB | 0.048 | 0.501 | non | +4.6% | 45% | non | échec |

## 6. Bonus optionnel — portefeuilles combinés (HORS du N=8 principal)

**Avertissement anti data-snooping** : les poids Sharpe-pondérés sont calculés à partir des Sharpe solo observés eux-mêmes dans ce script (poids = Sharpe positif normalisé) — ce n'est **pas** un réglage fixé a priori, c'est un choix informé par le résultat, donc structurellement optimiste. Ces 4 variantes bonus forment une famille **séparée** (n_trials=4 pour leur propre DSR), jamais mélangée au DSR=8 de la section 4, et leur résultat doit être lu avec un degré de confiance inférieur à celui de la comparaison principale.

Poids égal-poids : BuyHold=0.25, Momentum=0.25, LogitL2=0.25, HistGB=0.25. Poids Sharpe-pondéré : BuyHold=0.39, Momentum=0.00, LogitL2=0.26, HistGB=0.34.

| Variante | Sharpe ann. | Calmar | MDD % | Rdt ann. % | Turnover/j | DSR (n=4, famille bonus) |
|---|---|---|---|---|---|---|
| Equal-Weight(4) | +0.46 | +0.11 | -48.9 | +7.5 | 0.197 | 0.991 |
| Equal-Weight(4)+Overlay | +0.42 | +0.17 | -32.6 | +6.9 | 0.242 | 0.983 |
| Sharpe-Weighted(4) | +0.57 | +0.14 | -58.5 | +12.7 | 0.185 | 0.999 |
| Sharpe-Weighted(4)+Overlay | +0.57 | +0.28 | -31.1 | +11.2 | 0.236 | 0.999 |

Pour mémoire, Buy & Hold (référence, section 3-4) : Sharpe ann. +0.52, DSR (famille N=8) 0.501.

Au moins une combinaison bonus dépasse Buy & Hold en Sharpe ann. **et** en DSR (comparaison hétérogène : DSR bonus calculé sur sa propre famille n=4, DSR BuyHold sur la famille n=8 — à lire avec prudence, cf. avertissement ci-dessus, ne pas conclure à un edge validé sans re-test sur un échantillon indépendant).

## 7. Verdict honnête

- Meilleur DSR de l'univers figé (N=8) : **BuyHold+Overlay** (0.796).
- **Critère de succès NON atteint pour aucun signal actif.** Ni le DSR de la variante +overlay ne dépasse celui de Buy & Hold, ni la réduction de MDD (>30%) avec rendement conservé (≥80%) n'est observée, pour Momentum, LogitL2 ou HistGB. Cohérent avec l'Étape B/D déjà établies : Buy & Hold (nu ou avec overlay long-only) reste la référence sur NDX.
- **Discipline anti data-snooping** : univers de 8 variantes figé avant évaluation (section 2), DSR déflaté sur cette famille exacte (n_trials=8), réglages de l'overlay (cap 2.0×, coupe 90e percentile) repris tels quels d'une étude antérieure déjà publiée dans le repo — pas de balayage de paramètres ni d'ajout de variante après lecture du résultat ci-dessus. Le bonus (section 6) est explicitement hors de ce cadre et signalé comme tel.
