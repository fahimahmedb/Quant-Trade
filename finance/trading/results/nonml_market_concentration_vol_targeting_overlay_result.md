# Résultat — Overlay vol-targeting gaté par la concentration du marché NDX-100 (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Concentration(t) ≤ sa médiane glissante 252j (faible concentration = marché large), sinon 1.0x. 1385 séances testables (échantillon restreint à la période où le signal est disponible).

%j porte concentration active : 23.3%
Position moyenne : 1.08x
Concentration (HHI) moyenne observée : 0.0478

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.68 | +101.6% | -35.6% |
| **Overlay vol-targeting gaté concentration** | **+0.71** | **+116.0%** | -35.6% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS — critère renforcé atteint.**
