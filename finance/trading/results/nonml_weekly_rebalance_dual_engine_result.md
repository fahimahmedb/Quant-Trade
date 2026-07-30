# Résultat — Rebalancement hebdomadaire du mécanisme #121 (pré-enregistré, deux critères)

Position(t) = échantillonnage-et-maintien de la position quotidienne du #121, rafraîchie tous les 5 séances. 9522 séances (fenêtre commune #121, 20/09/1988→13/07/2026).

Turnover cumulé quotidien (#121 original) : 232.7
Turnover cumulé hebdomadaire : 121.0 (48.0% de réduction)

| | Sharpe ann. | Rendement total net | MDD | Calmar |
|---|---|---|---|---|
| Buy&Hold (NDX) | +0.52 | +4553.2% | -82.9% | 54.926 |
| #121 original (quotidien) | +0.69 | +8357.7% | -57.2% | -- |
| **Rebalancement hebdomadaire** | **+0.72** | **+10666.3%** | -55.3% | 192.839 |

1. Sharpe hebdo > BH : OUI
2. Rendement hebdo > BH : OUI
3. Critère standard (1 ET 2) : PASS
4. Critère Calmar (hebdo > BH) : PASS

**PASS (niveau 1, au moins un critère)**

**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer `nonml_pass_validation_battery.py weekly_rebalance_dual_engine` (stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**
