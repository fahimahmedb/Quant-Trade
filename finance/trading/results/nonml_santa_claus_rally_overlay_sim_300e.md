# Simulation — 300 EUR, overlay Santa Claus Rally (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). CAP=2.0x (cette fenêtre avril-juillet ne contient aucun jour de la fenêtre Santa Claus — le signal est donc constant à 1.0x sur toute la période simulée).

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **Overlay Santa Claus Rally** | **350.11 EUR** | **+16.7%** | -7.2% | +2.75 |

**Lecture honnête** : sur cette fenêtre de 63 séances (avril-juillet), le signal Santa Claus Rally n'est actif AUCUN jour (0pt d'exposition excédentaire) — illustration délibérément neutre car la fenêtre testée ne recoupe jamais la période simulée des ~3 derniers mois. Le verdict statistique reste celui du backtest complet (PASS 4/5 marchés) et de la robustesse (plateau parfait 4/5 sur la grille CAP 1.5x-3.0x).
