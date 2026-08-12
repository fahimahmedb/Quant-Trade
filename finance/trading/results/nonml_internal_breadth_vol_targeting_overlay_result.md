# Résultat — Overlay vol-targeting gaté par la breadth interne NDX-100 (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Breadth(t) ≥50% (fraction des titres NDX-100 proches à ≥95% de leur plus haut 252j), sinon 1.0x. 1385 séances testables.

%j porte breadth interne active : 5.1%
Position moyenne : 1.02x
Breadth moyenne (toute la période) : 20.5%

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.68 | +132.4% | -35.6% |
| **Overlay vol-targeting gaté breadth interne** | **+0.67** | **+132.7%** | -35.6% |

1. Sharpe overlay > BH : non
2. Rendement overlay > BH : OUI

**FAIL — critère renforcé NON atteint.**
