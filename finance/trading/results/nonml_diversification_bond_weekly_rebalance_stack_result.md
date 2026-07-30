# Résultat — Empilement diversification obligataire (#134) + rebalancement hebdomadaire (#131) (pré-enregistré, deux critères)

Position équity #131 (hebdomadaire, peut dépasser 1,0x) ; fraction (1-pos_eq) allouée au proxy obligataire DGS10 du #134 (négative = financement du levier au taux obligataire quand pos_eq>1). 9522 séances (fenêtre commune #131 ∩ DGS10).

Fraction du temps avec levier (pos_eq>1,0x, donc allocation obligataire négative) : 62.8%

| | Sharpe ann. | Rendement total net | MDD | Calmar |
|---|---|---|---|---|
| Buy&Hold (NDX 100%) | +0.52 | +4553.2% | -82.9% | 54.926 |
| #131 seul (déjà committé) | -- | -- | -57,2%→-55,3% (cf. résultat #131) | -- |
| **#131 + diversification obligataire (#134)** | **+0.74** | **+12228.3%** | -46.5% | 262.830 |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI
3. Critère standard (1 ET 2) : PASS
4. Critère Calmar (overlay > BH) : PASS

**PASS (niveau 1, au moins un critère)**

**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer `nonml_pass_validation_battery.py diversification_bond_weekly_rebalance_stack` (stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**
