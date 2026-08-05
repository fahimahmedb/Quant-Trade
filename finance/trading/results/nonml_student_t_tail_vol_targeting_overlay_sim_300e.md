# Simulation — 300 EUR, overlay vol-targeting gaté par le ν glissant (MLE Student-t) (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). Fenêtre ν/médiane 252j/252j (ré-estimation tous les 21j), vol cible 20%, fenêtre vol 20j, CAP=2.0x.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **Overlay vol-targeting ν gaté** | **353.65 EUR** | **+17.9%** | -9.0% | +2.63 |

**Lecture honnête** : sur cette fenêtre de 63 séances, la porte est active 45.2% du temps (position moyenne 1.11x) — illustration seulement, le verdict statistique reste celui du backtest complet (PASS 4/5 marchés, seul DAX échoue) et de la robustesse (plateau correct mais pas parfait : grille CAP 3-4/5, grille fenêtre de vol 2-4/5). L'audit dédié documente par ailleurs une fragilité numérique réelle de l'estimateur ν (non-identifiabilité du MLE sur fenêtres proches de la gaussienne, cf. `..._audit.md`), sans lien avec cette fenêtre récente spécifique.
