# Résultat — Overlay vol-targeting gaté par la confirmation multi-marché NDX+Russell2000 (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) quand NDX ET Russell 2000 sont SIMULTANÉMENT ≥95% de leur plus haut 252j, sinon 1.0x. 10020 séances testables.

%j porte breadth active : 38.5%
Position moyenne : 1.16x

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.52 | +5429.9% | -82.9% |
| **Overlay vol-targeting gaté breadth** | **+0.54** | **+8353.6%** | -82.9% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS — critère renforcé atteint.**
