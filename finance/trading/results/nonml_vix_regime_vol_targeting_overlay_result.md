# Résultat — Overlay vol-targeting gaté par le régime VIX, signal externe (pré-enregistré, règle renforcée niveau 1)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si VIX(t-1) ≥ sa médiane glissante 252j, sinon 1.0x. 9197 séances testables (historique VIX 1990+, plus court que NDX complet).

%j porte régime VIX active : 16.9%
Position moyenne : 1.06x

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.51 | +12855.1% | -82.9% |
| **Overlay vol-targeting gaté régime VIX** | **+0.50** | **+14196.2%** | -82.9% |

1. Sharpe overlay > BH : non
2. Rendement overlay > BH : OUI

**FAIL — critère renforcé NON atteint.**
