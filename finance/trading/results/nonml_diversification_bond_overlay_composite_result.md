# Résultat — Diversification obligataire sur le Composite (échantillon de référence, pré-enregistré, deux critères)

**Limite reconnue à l'avance** : échantillon court (1230 séances, 5 ans) vs 9522-14231 pour NDX/S&P500/Russell2000 -- puissance statistique bien moindre, une seule fenêtre de crise couverte (2022).

| | Sharpe ann. | Rendement total net | MDD | Calmar |
|---|---|---|---|---|
| Buy&Hold (Composite 100%) | +0.52 | +77.6% | -36.4% | 2.133 |
| **Diversification obligataire** | **+0.59** | **+69.9%** | -32.5% | 2.147 |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : non
3. Critère standard (1 ET 2) : FAIL
4. Critère Calmar (overlay > BH) : PASS

**PASS (niveau 1, au moins un critère)**

**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer `nonml_pass_validation_battery.py diversification_bond_overlay_composite`.**
