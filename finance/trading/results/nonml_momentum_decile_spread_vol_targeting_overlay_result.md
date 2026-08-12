# Résultat — Overlay vol-targeting gaté par le spread décile de momentum (pré-enregistré, règle renforcée niveau 1)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si Spread décile momentum(t) (D10-D1, queues de distribution) ≥ sa médiane glissante 252j, sinon 1.0x. 1385 séances testables (échantillon restreint à la période où le signal titre-par-titre est disponible).

%j porte spread décile active : 38.0%
Position moyenne : 1.12x
Spread décile moyen (toute la période) : 203.9 pts de %

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.68 | +132.4% | -35.6% |
| **Overlay vol-targeting gaté spread décile** | **+0.72** | **+163.1%** | -35.6% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS (niveau 1) — critère renforcé atteint.**

**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer `nonml_pass_validation_battery.py momentum_decile_spread_vol_targeting_overlay` (stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**
