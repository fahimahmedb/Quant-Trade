# Résultat — Overlay vol-targeting gaté par la dispersion des betas individuels NDX-100 (pré-enregistré, règle renforcée, cycle #109)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Dispersion des betas(t) ≥ sa médiane glissante 252j, sinon 1.0x. 1385 séances testables (échantillon restreint à la période où le signal est disponible).

%j porte dispersion betas active : 34.4%
Position moyenne : 1.11x
Dispersion des betas moyenne observée : 0.624

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.68 | +132.4% | -35.6% |
| **Overlay vol-targeting gaté dispersion betas** | **+0.64** | **+135.1%** | -35.6% |

1. Sharpe overlay > BH : non
2. Rendement overlay > BH : OUI

**FAIL — critère renforcé NON atteint.**
