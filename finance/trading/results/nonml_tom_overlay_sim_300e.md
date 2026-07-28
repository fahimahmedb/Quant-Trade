# Simulation — 300 EUR, overlay Turn-of-Month levé (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). Spécification pré-enregistrée (CAP=2.0x pendant la fenêtre ToM, 1.0x sinon), aucun paramètre retouché après les résultats précédents.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **Overlay ToM x2** | **380.07 EUR** | **+26.7%** | -7.5% | +3.33 |

**Lecture honnête** : fenêtre courte (~3 mois, 1-2 cycles ToM observés) — illustration uniquement, le verdict statistique réel reste celui du backtest complet (PASS 4/5 marchés) et de la robustesse (plateau stable 4/5 sur CAP 1.5x-3.0x). Le MDD de l'overlay levé doit être comparé à celui du Buy&Hold : le levier amplifie aussi les pertes, pas seulement les gains.
