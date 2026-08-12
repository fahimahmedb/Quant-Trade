# Simulation — 300 EUR, overlay de régime par le range intra-séance (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances, dont 13 en régime calme). Spécification pré-enregistrée (CAP=2.0x en régime calme, 1.0x sinon), aucun paramètre retouché après les résultats précédents.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 352.39 EUR | +17.5% | -7.0% | +2.74 |
| **Overlay régime range x2** | **375.63 EUR** | **+25.2%** | -7.0% | +3.26 |

**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement — le verdict statistique réel reste celui du backtest complet (PASS 5/5 marchés) et de la robustesse (plateau parfait 5/5 sur CAP 1.5x-3.0x). Le MDD de l'overlay levé doit être comparé à celui du Buy&Hold : le levier amplifie aussi les pertes, pas seulement les gains.
