# Résultat — Overlay vol-targeting gaté par la prévision GJR-t walk-forward (pré-enregistré, règle renforcée, NDX uniquement)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si vol_prévue_GJR-t(t) ≤ sa médiane glissante 252j, sinon 1.0x. T0=750, REFIT_EVERY=21j (walk-forward Étape C réutilisé tel quel). 9270 séances testables.

%j porte active : 39.1%
Position moyenne : 1.20x

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.51 | +3624.8% | -82.9% |
| **Overlay vol-targeting gaté prévision GJR-t** | **+0.51** | **+4337.3%** | -82.9% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS — critère renforcé atteint (marché unique NDX).**
