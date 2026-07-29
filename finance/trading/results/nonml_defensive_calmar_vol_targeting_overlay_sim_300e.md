# Simulation — 300 EUR, vol-targeting défensif critère Calmar (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). TARGET_VOL_ANNUAL=20%, jamais de levier, aucun paramètre retouché après les résultats précédents.

| | Capital final | Rendement période | MDD | Sharpe ann. | Calmar |
|---|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 | 8.845 |
| **Overlay défensif** | **346.04 EUR** | **+15.3%** | -7.0% | +2.97 | **8.313** |

**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement, régime haussier calme (peu de coupes défensives attendues sur une fenêtre sans stress) — le verdict statistique réel reste celui du backtest complet (PASS Calmar 4/5, Sharpe ET MDD améliorés sur tous les marchés testés) et de la robustesse (plateau parfait 8/8 sur les deux grilles). Doit encore passer la batterie Règle 9 (`nonml_pass_validation_battery.py defensive_calmar_vol_targeting_overlay`), avec la nuance explicite que ses contrôles sont bâtis sur le critère Sharpe/rendement standard, pas Calmar.
