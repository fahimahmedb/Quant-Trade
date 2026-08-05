# Résultat — Momentum court terme, 1 semaine, winners (pré-enregistré, règle renforcée)

Univers : 178 tickers NDX-100, 2907 séances testables (2015-01-02 → 2026-07-27), signal = rendement 5j, rebalancement hebdomadaire, tercile SUPÉRIEUR (34 titres).

**Univers POINT-IN-TIME (cycle #164)** — à chaque rebalancement, seuls les titres réellement membres du NDX-100 ce jour-là sont éligibles, **et la référence équipondérée est construite sur ce même univers réel**. Corrige le biais du survivant qui affectait le #14 d'origine (liste des membres de 2026 appliquée rétroactivement, couverture 68 % en 2022 / 42 % en 2015 — cf. `results/nonml_ndx100_universe_census.md`). Aucun paramètre du #14 ne change (SIGNAL_WINDOW=5, REBAL_EVERY=5, TERCILE=1/3, coût 5 bps). Pré-enregistré dans `PREREG_short_term_momentum_pit_universe.md`.

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold équipondéré (univers) | +0.37 | +91.0% | -36.2% |
| **Winners (tercile sup., momentum)** | **-0.01** | **-25.3%** | -44.6% |

1. Sharpe winners > Buy&Hold : non
2. Rendement total winners > Buy&Hold : non

**FAIL — critère renforcé (Sharpe ET rendement) NON atteint.**

**Comparaison directe avec le cycle #5** (même signal, même univers, tercile opposé) : à mettre en regard de `results/nonml_short_term_reversal_result.md` (losers : Sharpe -1.02, rendement -83.6%).

## Biais résiduel de l'univers point-in-time (mesuré, non estimé)

| Année | Rebal. | Membres réels (moy.) | Investissables (moy.) | Couverture moy. |
|---|---|---|---|---|
| 2015 | 51 | 106 | 75.3 | 71.0% |
| 2016 | 50 | 105 | 79.4 | 75.8% |
| 2017 | 50 | 104 | 82.6 | 79.4% |
| 2018 | 51 | 103 | 85.6 | 83.1% |
| 2019 | 50 | 103 | 89.9 | 87.3% |
| 2020 | 51 | 103 | 91.7 | 89.1% |
| 2021 | 50 | 102 | 92.8 | 91.0% |
| 2022 | 50 | 102 | 96.3 | 94.6% |
| 2023 | 50 | 101 | 97.5 | 96.5% |
| 2024 | 51 | 101 | 99.2 | 98.3% |
| 2025 | 50 | 101 | 100.5 | 99.4% |
| 2026 | 28 | 101 | 101.0 | 100.0% |

**Couverture moyenne : 88.3% (minimum 68.6%)**, contre 42-68 % pour la liste de 2026 appliquée rétroactivement (cf. `results/nonml_ndx100_universe_census.md`). Le résidu correspond aux sociétés retirées de la cote dont la série de prix n'est plus exposée par la source — biais restant orienté à la hausse, mais réduit d'un ordre de grandeur et mesuré.

