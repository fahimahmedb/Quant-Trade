# Résultat — Tilt Amihud illiquidité (pré-enregistré, exécuté une fois, règle renforcée)

Univers : 99 tickers NDX-100 avec prix ET volume disponibles (0 exclus faute de volume : aucun), 1270 séances testables (2021-07-06 → 2026-07-27), rebalancement tous les 21j, tercile LE PLUS ILLIQUIDE (ILLIQ = |rendement|/volume-dollars, moyenne glissante 126j). Construction causale dès le départ (`lag_one_day` appliqué à la construction).

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold équipondéré (univers) | +0.90 | +171.6% | -31.0% |
| **Tilt illiquidité (tercile le plus illiquide)** | **+1.19** | **+334.1%** | -31.2% |

1. Sharpe > Buy&Hold : OUI
2. Rendement total > Buy&Hold : OUI

**PASS — critère renforcé (Sharpe ET rendement) atteint.**
