# Résultat — Overlay vol-targeting gaté par la breadth de momentum NDX-100 (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Breadth de momentum(t) ≥50% (fraction des titres NDX-100 avec momentum 12-1 mois positif), sinon 1.0x. 1133 séances testables.

%j porte breadth de momentum active : 53.7%
Position moyenne : 1.18x
Breadth de momentum moyenne (toute la période) : 63.4%

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.55 | +57.8% | -34.4% |
| **Overlay vol-targeting gaté breadth de momentum** | **+0.60** | **+73.6%** | -34.4% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS — critère renforcé atteint.**
