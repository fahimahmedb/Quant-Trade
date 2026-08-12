# Résultat — Porte breadth SMA200, univers POINT-IN-TIME réel (cycle #271)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Breadth_PIT SMA200(t) ≥50% (fraction des titres RÉELLEMENT membres au-dessus de leur propre SMA200), sinon 1.0x. 2896 séances testables (2015-01-05 → 2026-07-13).

%j porte breadth SMA200 active : 62.4%
Position moyenne : 1.32x
Breadth SMA200 PIT moyenne (toute la période post-2015) : 62.3%

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.76 | +597.4% | -35.6% |
| **Overlay vol-targeting gaté breadth SMA200 (PIT)** | **+0.78** | **+897.9%** | -36.9% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS — critère renforcé atteint.**
