# Simulation — 300 EUR, overlay cycle électoral américain (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). CAP=2.0x pendant l'année pré-électorale, 1.0x sinon.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 352.39 EUR | +17.5% | -7.0% | +2.74 |
| **Overlay cycle électoral** | **352.57 EUR** | **+17.5%** | -7.0% | +2.75 |

**Lecture honnête** : 2026 est une année POST-électorale (2024 était l'année d'élection), donc la fenêtre de test récente (~3 derniers mois, 0.0% de jours levés) ne couvre PAS l'année pré-électorale (2027) -- l'overlay est identique à Buy&Hold sur cette période précise par construction, ce n'est pas un signe d'échec. Le verdict statistique reste celui du backtest complet (PASS 5/5, ~10 cycles complets sur NDX 40 ans) et de la robustesse (plateau parfait 5/5 sur CAP 1.5x-3.0x).
