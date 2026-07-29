# Résultat — Overlay vol-targeting gaté par la breadth SMA200 NDX-100 (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Breadth SMA200(t) ≥50% (fraction des titres NDX-100 au-dessus de leur propre SMA200), sinon 1.0x. 1186 séances testables.

%j porte breadth SMA200 active : 55.0%
Position moyenne : 1.18x
Breadth SMA200 moyenne (toute la période) : 60.1%

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.60 | +69.6% | -35.6% |
| **Overlay vol-targeting gaté breadth SMA200** | **+0.66** | **+89.6%** | -36.9% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS — critère renforcé atteint.**
