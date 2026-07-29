# Résultat — Overlay vol-targeting gaté par la dispersion du momentum NDX-100 (pré-enregistré, règle renforcée, cycle #100)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Dispersion du momentum(t) ≥ sa médiane glissante 252j, sinon 1.0x. 1385 séances testables (échantillon restreint à la période où le signal est disponible).

%j porte dispersion momentum active : 37.0%
Position moyenne : 1.12x
Dispersion du momentum moyenne observée : 0.707

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.68 | +101.6% | -35.6% |
| **Overlay vol-targeting gaté dispersion momentum** | **+0.73** | **+125.4%** | -35.6% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS — critère renforcé atteint.**
