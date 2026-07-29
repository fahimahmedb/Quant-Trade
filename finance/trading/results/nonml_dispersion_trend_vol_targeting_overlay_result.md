# Résultat — Overlay vol-targeting gaté par double porte dispersion ET tendance (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si tendance 52w-high (#47) ET dispersion cross-sectionnelle ≥médiane (#78) sont SIMULTANÉMENT actives, sinon 1.0x. 1385 séances testables.

%j porte tendance seule active : 61.4%
%j porte dispersion seule active : 46.6%
%j porte COMBINÉE (intersection) active : 22.4%
Position moyenne : 1.07x

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.68 | +101.6% | -35.6% |
| **Overlay vol-targeting double porte** | **+0.69** | **+111.5%** | -35.6% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS — critère renforcé atteint.**
