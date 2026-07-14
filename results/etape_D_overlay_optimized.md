# Étape D (optimisation) — Grid-search vol-targeting × coupe extrême (NDX)

Contexte : Étape D (première passe, `results/etape_D_overlay.md`) a testé un seul réglage a priori (cap 1.5×, coupe au 95e percentile) : réduction MDD de +23.7% relatif sur NDX, sous le seuil de succès (>25%). Ce grid-search explore les **deux paramètres explicites** de l'overlay (cap d'exposition, percentile de coupe extrême) sur une grille **figée avant évaluation**, sans toucher au moteur GJR-GARCH(1,1)-t ni à la règle de coupe elle-même (coupe totale, `EXTREME_CUT_FRAC=0.0`, inchangée).

**Protocole figé** : NDX (`nasdaq100_daily.txt`), fenêtre initiale 750 obs expansive, ré-estimation GJR-t tous les 21 j, coûts 5 bps aller-retour sur le turnover de l'exposition. OOS : 20/09/1988 → 13/07/2026 (9522 obs, ~37.8 ans). Grille : `vol_target_cap` ∈ [1.0, 1.25, 1.5, 2.0] × `extreme_cut_percentile` ∈ [90, 95, 99] = **12 combinaisons exactement**, aucun ajout a posteriori (N=12 pour le DSR).

**Référence Buy & Hold** : Sharpe ann. +0.52, Calmar +0.08, MDD -82.9%, rendement ann. +14.5%.

## Grille des 12 combinaisons (triée par MDD, priorité absolue)

| cap | pctl coupe | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | Rdt ann. % | Turnover | DSR (N=12) | ΔMDD rel. | Rdt/BH | Critère |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.00× | 90e | +0.63 | +0.81 | +0.14 | -55.1 | +12.1 | 0.023 | 1.000 | +33.5% | 83.2% | OUI |
| 2.00× | 90e | +0.65 | +0.84 | +0.19 | -55.1 | +16.5 | 0.057 | 1.000 | +33.5% | 114.0% | OUI |
| 1.25× | 90e | +0.65 | +0.85 | +0.17 | -55.1 | +14.4 | 0.033 | 1.000 | +33.5% | 99.3% | OUI |
| 1.50× | 90e | +0.66 | +0.87 | +0.18 | -55.1 | +15.8 | 0.042 | 1.000 | +33.5% | 109.2% | OUI |
| 1.00× | 95e | +0.62 | +0.83 | +0.12 | -63.3 | +12.6 | 0.017 | 1.000 | +23.7% | 86.6% | non |
| 1.50× | 95e | +0.66 | +0.90 | +0.15 | -63.3 | +16.4 | 0.037 | 1.000 | +23.7% | 112.7% | non |
| 2.00× | 95e | +0.64 | +0.87 | +0.16 | -63.3 | +17.1 | 0.052 | 1.000 | +23.7% | 117.5% | non |
| 1.25× | 95e | +0.64 | +0.88 | +0.14 | -63.3 | +14.9 | 0.027 | 1.000 | +23.7% | 102.7% | non |
| 1.00× | 99e | +0.60 | +0.83 | +0.09 | -74.0 | +12.8 | 0.012 | 1.000 | +10.7% | 88.3% | non |
| 1.50× | 99e | +0.64 | +0.91 | +0.11 | -74.0 | +16.6 | 0.031 | 1.000 | +10.7% | 114.4% | non |
| 1.25× | 99e | +0.63 | +0.89 | +0.10 | -74.0 | +15.2 | 0.022 | 1.000 | +10.7% | 104.4% | non |
| 2.00× | 99e | +0.63 | +0.89 | +0.12 | -74.0 | +17.3 | 0.046 | 1.000 | +10.7% | 119.2% | non |

| BuyHold (référence) | — | +0.52 | +0.69 | +0.08 | -82.9 | +14.5 | 0.000 | — | — | 100.0% | — |

## Verdict — meilleure combinaison et critère de succès

Succès = réduction du MDD >25% (relatif) **et** rendement annualisé conservé ≥80% de Buy & Hold. Vérifié, pas supposé, sur les 12 combinaisons de la grille figée ci-dessus.

**Meilleure combinaison** (critère de succès atteint en priorité, puis réduction de MDD, puis Calmar comme départage entre ex-aequo) : cap **2.00×**, coupe au **90e percentile** — ΔMDD relatif +33.5%, rendement conservé 114.0% du Buy & Hold, Calmar +0.19 (vs +0.08 Buy & Hold), MDD -55.1% (vs -82.9% Buy & Hold).

**Verdict honnête** : 4/12 combinaison(s) de la grille atteignent le critère de succès explicite (>25% réduction MDD, ≥80% rendement conservé) sur NDX. Le réglage optimal ci-dessus apporte un bénéfice matériel de réduction du drawdown sans sacrifier l'essentiel du rendement Buy & Hold. Rappel anti-data-snooping : ce résultat provient d'une grille fixée a priori (12 combinaisons, DSR déflaté sur cette famille), pas d'un balayage libre a posteriori — mais il reste spécifique à ce jeu de données (NDX) et n'a pas été re-vérifié sur le Composite (5 ans) dans cette passe.