# Résultat — Overlay vol-targeting gaté par la breadth de drawdown profond, seuil absolu -20% (pré-enregistré, règle renforcée niveau 1)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Breadth_DD(t) (fraction des titres NDX-100 ≥20% sous leur plus haut glissant 252j) ≥ sa médiane glissante 252j, sinon 1.0x. 1385 séances testables (échantillon restreint à la période où la breadth titre-par-titre est disponible).

%j porte drawdown profond active : 21.5%
Position moyenne : 1.06x
Breadth drawdown profond moyenne (toute la période) : 26.7%

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.68 | +101.6% | -35.6% |
| **Overlay vol-targeting gaté drawdown profond** | **+0.69** | **+109.8%** | -35.6% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS (niveau 1) — critère renforcé atteint.**

**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer `nonml_pass_validation_battery.py deep_drawdown_breadth_vol_targeting_overlay` (stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**
