# Résultat — Overlay vol-targeting gaté par la breadth nette hauts-bas NDX-100 (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Breadth nette(t) > 0 (plus de titres proches de leur plus haut que de leur plus bas 252j), sinon 1.0x. 1385 séances testables.

%j porte breadth nette active : 44.4%
Position moyenne : 1.15x
Breadth nette moyenne (toute la période) : +13.6pts

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.68 | +132.4% | -35.6% |
| **Overlay vol-targeting gaté breadth nette** | **+0.71** | **+162.6%** | -35.6% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS — critère renforcé atteint.**
