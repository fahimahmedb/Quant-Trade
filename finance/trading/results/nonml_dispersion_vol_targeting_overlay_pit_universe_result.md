# Résultat — Porte dispersion cross-sectionnelle, univers POINT-IN-TIME réel (cycle #270)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Dispersion_PIT(t) ≥ sa médiane glissante 252j, sinon 1.0x. 2645 séances testables (2016-01-04 → 2026-07-13), dispersion calculée sur les titres réellement membres du NDX-100 chaque jour (au lieu des 99 membres 2026 fixes).

%j porte dispersion active : 28.9%
Position moyenne : 1.14x

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.79 | +542.3% | -35.6% |
| **Overlay vol-targeting gaté dispersion (PIT)** | **+0.74** | **+556.4%** | -36.7% |

1. Sharpe overlay > BH : non
2. Rendement overlay > BH : OUI

**FAIL — critère renforcé NON atteint.**
