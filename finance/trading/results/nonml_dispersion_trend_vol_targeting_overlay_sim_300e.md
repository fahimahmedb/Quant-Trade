# Simulation — 300 EUR, overlay vol-targeting gaté par double porte dispersion+tendance (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). Vol cible 20%, fenêtre 20j, CAP=2.0x quand tendance 52w-high ET dispersion cross-sectionnelle sont simultanément actives.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **Overlay vol-targeting double porte** | **353.28 EUR** | **+17.8%** | -9.0% | +2.62 |

**Lecture honnête** : sur cette fenêtre de 63 séances, l'exposition moyenne est de 1.10x — illustration seulement, le verdict statistique reste celui du backtest complet (PASS sur NDX, MDD exactement préservé) et de la robustesse (7/8 sur les grilles CAP 1.5x-3.0x et fenêtre 15-30j, seule la fenêtre 30j échoue).
