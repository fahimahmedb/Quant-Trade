# Résultat — Overlay défensif combiné (moyenne #115 + GJR-GARCH corrigé du #118) (pré-enregistré)

Position(t) = (Position_#115(t) + Position_GARCH(t)) / 2, fenêtre commune 9522 séances (1988-09-20 → 2026-07-13). Écart max résiduel entre les deux séries de rendement NDX sous-jacentes (vérif. cohérence, arrondis des deux pipelines) : 1.76e-15.

| | Sharpe ann. | Rendement total net | MDD | Calmar |
|---|---|---|---|---|
| Buy&Hold (NDX) | +0.52 | +4553.2% | -82.9% | 0.077 |
| **Overlay combiné (#115+GARCH)/2** | **+0.69** | **+8357.7%** | -57.2% | **0.162** |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI
3. Calmar overlay > BH : OUI

**Critère standard (Sharpe ET rendement) : PASS.**
**Critère Calmar : PASS.**

**PASS niveau 1 sur au moins un critère seulement -- pas un verdict final (Règle 9). Doit encore passer `nonml_pass_validation_battery.py dual_engine_defensive_overlay` (stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**
