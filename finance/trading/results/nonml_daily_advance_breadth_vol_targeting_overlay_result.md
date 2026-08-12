# Résultat — Overlay vol-targeting gaté par la breadth d'avance journalière NDX-100 (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Breadth d'avance moyenne 5j(t) ≥50%, sinon 1.0x. 1380 séances testables.

%j porte breadth d'avance active : 35.6%
Position moyenne : 1.14x
Breadth d'avance moyenne (toute la période) : 51.7%

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.66 | +128.7% | -35.6% |
| **Overlay vol-targeting gaté breadth d'avance** | **+0.64** | **+133.1%** | -35.6% |

1. Sharpe overlay > BH : non
2. Rendement overlay > BH : OUI

**FAIL — critère renforcé NON atteint.**
