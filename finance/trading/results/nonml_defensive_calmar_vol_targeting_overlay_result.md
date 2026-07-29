# Résultat — Vol-targeting défensif, critère Calmar (pré-enregistré, critère DÉLIBÉRÉMENT différent de la règle renforcée standard)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 0.0, 1.0x) — jamais de levier. Critère : Calmar overlay > Calmar BH sur ≥4/5 marchés (PAS Sharpe+rendement).

| Marché | BH Calmar | BH Sharpe | BH Rdt total | BH MDD | Overlay Calmar | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Calmar>BH |
|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 0.260 | +0.52 | +56.5% | -36.4% | **0.324** | +0.62 | +61.0% | -29.8% | OUI |
| NDX (40 ans) | 0.077 | +0.53 | +6416.7% | -82.9% | **0.145** | +0.71 | +9256.6% | -58.5% | OUI |
| Russell 2000 | 0.081 | +0.34 | +610.3% | -59.9% | **0.105** | +0.39 | +634.1% | -46.3% | OUI |
| S&P 500 | 0.095 | +0.46 | +3696.8% | -56.8% | **0.103** | +0.51 | +3585.6% | -51.4% | OUI |
| DAX | 0.042 | +0.24 | +116.5% | -72.7% | **0.041** | +0.25 | +108.5% | -64.3% | non |

**4/5 marchés avec Calmar overlay > Calmar BH.**

**PASS (critère Calmar ≥4/5) — atteint.**

**PASS niveau 1 (critère Calmar) seulement -- pas un verdict final. La batterie Règle 9 (`nonml_pass_validation_battery.py defensive_calmar_vol_targeting_overlay`) sera exécutée à titre informatif, mais ses contrôles (a) coûts et (c) stabilité sont bâtis sur le critère Sharpe/rendement standard, PAS Calmar -- un échec de ces contrôles précis ne contredit pas nécessairement ce succès Calmar (voir PREREG).**
