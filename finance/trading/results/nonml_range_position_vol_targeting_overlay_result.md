# Résultat — Overlay vol-targeting gaté par la position moyenne dans le range annuel NDX-100 (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Position moyenne dans le range(t) ≥ sa médiane glissante 252j, sinon 1.0x. 1385 séances testables (échantillon restreint à la période où le signal est disponible).

%j porte position range active : 25.8%
Position exposition moyenne : 1.09x
Position moyenne dans le range observée : 0.572

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.68 | +132.4% | -35.6% |
| **Overlay vol-targeting gaté position range** | **+0.70** | **+151.0%** | -35.6% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS — critère renforcé atteint.**
