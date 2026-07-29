# Résultat — Overlay vol-targeting gaté par le régime de corrélation moyenne NDX-100 (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Corrélation moyenne(t) ≤ sa médiane glissante 252j, sinon 1.0x. 1385 séances testables (échantillon restreint à la période où la corrélation est disponible).

%j porte corrélation active : 37.5%
Position moyenne : 1.12x
Corrélation moyenne observée (toute la période) : 0.278

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.68 | +101.6% | -35.6% |
| **Overlay vol-targeting gaté corrélation** | **+0.67** | **+108.8%** | -35.6% |

1. Sharpe overlay > BH : non
2. Rendement overlay > BH : OUI

**FAIL — critère renforcé NON atteint.**
