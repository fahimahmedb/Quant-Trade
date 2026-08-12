# Résultat — Overlay vol-targeting gaté par vote majoritaire (≥3/5 gates déjà validées) (pré-enregistré, règle renforcée niveau 1)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si ≥3/5 des gates #78/#89/#100/#104/#112 sont actives simultanément, sinon 1.0x. 1385 séances testables (intersection des 5 fenêtres individuelles).

%j porte ensemble active : 53.8%
Position moyenne : 1.13x

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.68 | +132.4% | -35.6% |
| **Overlay vote majoritaire (≥3/5)** | **+0.73** | **+166.8%** | -35.6% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS (niveau 1) — critère renforcé atteint.**

**PASS niveau 1 seulement -- pas un verdict final (Règle 9), ET biais de sélection assumé (les 5 membres sont choisis PARCE QU'ils étaient déjà PASS niveau 1). Doit encore passer `nonml_pass_validation_battery.py ensemble_vote_vol_targeting_overlay` (n_trials=taille du backlog, pas remis à 5).**
