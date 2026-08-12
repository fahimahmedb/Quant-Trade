# Résultat — Overlay vol-targeting gaté par la breadth de rebond rapide post-creux (pré-enregistré, règle renforcée niveau 1)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Breadth_Rebound(t) (fraction des titres NDX-100 ≥10% au-dessus de leur plus bas glissant 20j) ≥ sa médiane glissante 252j, sinon 1.0x. 1385 séances testables (échantillon restreint à la période où la breadth titre-par-titre est disponible).

%j porte rebond rapide active : 23.9%
Position moyenne : 1.07x
Breadth rebond rapide moyenne (toute la période) : 26.6%

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.68 | +132.4% | -35.6% |
| **Overlay vol-targeting gaté rebond rapide** | **+0.61** | **+121.7%** | -35.6% |

1. Sharpe overlay > BH : non
2. Rendement overlay > BH : non

**FAIL — critère renforcé NON atteint.**
