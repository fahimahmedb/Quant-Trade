# Résultat — Empilement diversification obligataire (#134) + ensemble 3 moteurs (#124) (pré-enregistré, deux critères)

Position équity #124 (moyenne réalisé+GARCH+EWMA, peut légèrement dépasser 1,0x) ; fraction (1-pos_eq) allouée au proxy obligataire DGS10 du #134. 9522 séances (fenêtre commune #124 ∩ DGS10).

Fraction du temps avec levier léger (pos_eq>1,0x) : 60.1%

| | Sharpe ann. | Rendement total net | MDD | Calmar |
|---|---|---|---|---|
| Buy&Hold (NDX 100%) | +0.52 | +16652.5% | -82.9% | 200.881 |
| **#124 + diversification obligataire (#134)** | **+0.73** | **+19201.3%** | -48.4% | 396.844 |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI
3. Critère standard (1 ET 2) : PASS
4. Critère Calmar (overlay > BH) : PASS

**PASS (niveau 1, au moins un critère)**

**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer `nonml_pass_validation_battery.py diversification_bond_triple_engine_stack` (stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**
