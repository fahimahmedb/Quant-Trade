# Simulation — 300 EUR, overlay vol-targeting gaté par la breadth de faiblesse (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances, dont 0 avec porte active). CAP=2.0x, aucun paramètre retouché après les résultats précédents.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **Overlay breadth de faiblesse** | **350.11 EUR** | **+16.7%** | -7.2% | +2.75 |

**Lecture honnête** : comme attendu (voir avertissement du backtest/audit/robustesse), la porte est active 0 jour(s) sur 63 dans cette fenêtre récente — le résultat est quasi identique à Buy&Hold, confirmant que le "PASS" pré-enregistré n'est pas un edge exploitable en pratique, seulement l'absence d'activation du mécanisme.
