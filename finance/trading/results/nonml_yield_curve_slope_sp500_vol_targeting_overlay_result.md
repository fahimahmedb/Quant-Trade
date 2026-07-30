# Résultat — Pente de la courbe des taux US (T10Y2Y) appliquée au S&P 500 (pré-enregistré, règle renforcée niveau 1)

Mécanisme identique au #114 (NDX), seul le marché piloté change (S&P 500). 12631 séances testables.

%j porte pente courbe active : 38.4%
Position moyenne : 1.23x

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (S&P 500) | +0.49 | +3370.4% | -56.8% |
| **Overlay vol-targeting gaté pente courbe des taux** | **+0.50** | **+5451.9%** | -62.2% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS (niveau 1) — critère renforcé atteint.**

**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer `nonml_pass_validation_battery.py yield_curve_slope_sp500_vol_targeting_overlay` (stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**
