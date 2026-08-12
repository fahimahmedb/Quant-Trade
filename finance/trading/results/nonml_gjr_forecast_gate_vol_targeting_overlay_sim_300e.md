# Simulation — 300 EUR, overlay vol-targeting gaté par la prévision GJR-t (~3 derniers mois, NDX)

Période : 2026-04-13 → 2026-07-13 (63 séances). Position = clip(20% / vol_réalisée_20j, 1.0, 2.0x) si porte GJR-t active, sinon 1.0x. Coûts 5 bps.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| Buy & Hold | 352.39 EUR | +17.5% | -7.0% | +2.74 |
| **Overlay vol-targeting gaté GJR-t** | **356.40 EUR** | **+18.8%** | -8.8% | +2.62 |

Exposition moyenne sur la fenêtre : 1.10x (min 1.00x, max 1.39x).

**Lecture honnête** : fenêtre purement illustrative de 63 séances, sans valeur statistique — le verdict du cycle reste celui du backtest complet (9270 séances, PASS de niveau 1, marge très marginale). Règle 9 non exécutée à ce stade (à faire si ce cycle est repris dans la file d'attente des PASS frais).
