# Résultat — Double porte AND breadth SMA200 + breadth de momentum (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Breadth SMA200(t) ≥50% ET Breadth momentum(t) ≥50% SIMULTANÉMENT, sinon 1.0x. 1133 séances testables.

%j porte combinée (AND) active : 66.1% (vs SMA200 seule 74.2%, momentum seule 78.4%)
%j porte combinée avec position résultante >1x : 52.5%
Position moyenne : 1.17x

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.55 | +57.8% | -34.4% |
| **Overlay vol-targeting gaté AND SMA200∩momentum** | **+0.61** | **+74.6%** | -34.4% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS — critère renforcé atteint.**
