# Résultat — Double porte AND dispersion momentum + tendance 52w-high (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si proximité 52w-high(t) ET dispersion momentum(t) ≥ médiane 252j SIMULTANÉMENT, sinon 1.0x. 1385 séances testables.

%j porte combinée (AND) active : 37.7% (vs tendance seule 61.4%, dispersion seule 50.6%)
%j porte combinée avec position résultante >1x : 32.1%
Position moyenne : 1.11x

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.68 | +132.4% | -35.6% |
| **Overlay vol-targeting gaté AND dispersion∩tendance** | **+0.72** | **+161.8%** | -35.6% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS — critère renforcé atteint.**
