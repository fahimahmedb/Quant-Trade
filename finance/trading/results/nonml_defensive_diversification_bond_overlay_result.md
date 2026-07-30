# Résultat — Diversification défensive vers un proxy obligataire, #115+DGS10 (pré-enregistré, deux critères)

Fraction dé-risquée de la position #115 (jamais >1.0x) allouée à un proxy obligataire (duration modifiée, DGS10) au lieu du cash. 10252 séances (fenêtre commune #115 ∩ DGS10, 1985-10-30→2026-07-13).

Position équity moyenne (#115, inchangée) : 0.87x — position obligataire moyenne : 0.13x

| | Sharpe ann. | Rendement total net | MDD | Calmar |
|---|---|---|---|---|
| Buy&Hold (NDX 100%) | +0.53 | +6416.7% | -82.9% | 77.406 |
| **#115 + proxy obligataire (au lieu de cash)** | **+0.77** | **+14405.6%** | -50.9% | 283.098 |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI
3. Critère standard (1 ET 2) : PASS
4. Critère Calmar (overlay > BH) : PASS

**PASS (niveau 1, au moins un critère)**

**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer `nonml_pass_validation_battery.py defensive_diversification_bond_overlay` (stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**
