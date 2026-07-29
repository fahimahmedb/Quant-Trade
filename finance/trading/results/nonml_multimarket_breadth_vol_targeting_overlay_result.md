# Résultat — Overlay vol-targeting gaté par la confirmation multi-marché élargie (5 marchés, pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_NDX_20j(t-1), 1.0, 2.0x) si Breadth 5-marchés(t) ≥60% (au moins 3 des 5 marchés en tendance haussière SMA200), sinon 1.0x. 1254 séances testables.

%j porte multi-marché active : 56.5%
Position moyenne : 1.21x
Breadth multi-marché moyenne (toute la période) : 70.7%

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.60 | +74.0% | -35.6% |
| **Overlay vol-targeting gaté breadth 5-marchés** | **+0.64** | **+91.9%** | -37.1% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS — critère renforcé atteint.**
