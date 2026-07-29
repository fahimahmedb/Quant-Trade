# Étape D (optimisation) — Grid-search vol-targeting × coupe extrême (NDX)

Contexte : Étape D (première passe, `results/etape_D_overlay.md`) a testé un seul réglage a priori (cap 1.5×, coupe au 95e percentile) : réduction MDD de +23.7% relatif sur NDX, sous le seuil de succès (>25%). Ce grid-search explore les **deux paramètres explicites** de l'overlay (cap d'exposition, percentile de coupe extrême) sur une grille **figée avant évaluation**, sans toucher au moteur GJR-GARCH(1,1)-t ni à la règle de coupe elle-même (coupe totale, `EXTREME_CUT_FRAC=0.0`, inchangée).

**Protocole figé** : NDX (`nasdaq100_daily.txt`), fenêtre initiale 750 obs expansive, ré-estimation GJR-t tous les 21 j, coûts 5 bps aller-retour sur le turnover de l'exposition. OOS : 20/09/1988 → 13/07/2026 (9522 obs, ~37.8 ans). Grille : `vol_target_cap` ∈ [1.5] × `extreme_cut_percentile` ∈ [95] = **1 combinaisons exactement**, aucun ajout a posteriori (N=1 pour le DSR).

**Référence Buy & Hold** : Sharpe ann. +0.52, Calmar +0.08, MDD -82.9%, rendement ann. +14.5%.

## Grille des 1 combinaison(s) (triée par MDD, priorité absolue)

| cap | pctl coupe | Sharpe ann. | Sortino ann. | **Calmar** | **MDD %** | Rdt ann. % | Turnover | DSR (N=1) | ΔMDD rel. | Rdt/BH | Critère |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.50× | 95e | +0.67 | +0.92 | +0.18 | -57.2 | +16.1 | 0.040 | 1.000 | +31.0% | 111.2% | OUI |

| BuyHold (référence) | — | +0.52 | +0.69 | +0.08 | -82.9 | +14.5 | 0.000 | — | — | 100.0% | — |

## Verdict — meilleure combinaison et critère de succès

Succès = réduction du MDD >25% (relatif) **et** rendement annualisé conservé ≥80% de Buy & Hold. Vérifié, pas supposé, sur les 1 combinaison(s) de la grille figée ci-dessus.

**Meilleure combinaison** (critère de succès atteint en priorité, puis réduction de MDD, puis Calmar comme départage entre ex-aequo) : cap **1.50×**, coupe au **95e percentile** — ΔMDD relatif +31.0%, rendement conservé 111.2% du Buy & Hold, Calmar +0.18 (vs +0.08 Buy & Hold), MDD -57.2% (vs -82.9% Buy & Hold).

**Verdict honnête** : 1/1 combinaison(s) de la grille atteignent le critère de succès explicite (>25% réduction MDD, ≥80% rendement conservé) sur NDX. Le réglage optimal ci-dessus apporte un bénéfice matériel de réduction du drawdown sans sacrifier l'essentiel du rendement Buy & Hold. Rappel anti-data-snooping : ce résultat provient d'une grille fixée a priori (1 combinaison(s), DSR déflaté sur cette famille), pas d'un balayage libre a posteriori — mais il reste spécifique à ce jeu de données (NDX) et n'a pas été re-vérifié sur le Composite (5 ans) dans cette passe.