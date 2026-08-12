# Résultat — Overlay vol-targeting gaté par la pente de la courbe des taux US, T10Y2Y (pré-enregistré, règle renforcée niveau 1)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si T10Y2Y(t-1) ≥ sa médiane glissante 252j, sinon 1.0x. 10252 séances testables (historique NDX complet, 40 ans -- signal macro disponible sur toute la période).

%j porte pente courbe active : 25.6%
Position moyenne : 1.11x
T10Y2Y moyen (toute la période testable) : 0.97 pts

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.53 | +25465.6% | -82.9% |
| **Overlay vol-targeting gaté pente courbe des taux** | **+0.54** | **+38996.7%** | -82.9% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS (niveau 1) — critère renforcé atteint.**

**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer `nonml_pass_validation_battery.py yield_curve_slope_vol_targeting_overlay` (stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**
