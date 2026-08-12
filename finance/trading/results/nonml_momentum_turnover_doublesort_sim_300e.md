# Simulation — 300 EUR, momentum 12-1 + double-tri turnover (NDX-100, ~3 derniers mois)

Période : 2026-04-27 → 2026-07-27 (63 séances). Référence = momentum 12-1 seul (cycle #73), PAS Buy&Hold — cohérent avec le critère renforcé du backtest. Spécification pré-enregistrée (TURNOVER_WINDOW=126j), aucun paramètre retouché après les résultats précédents.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| Momentum 12-1 seul (référence) | 327.06 EUR | +9.0% | -16.9% | +0.77 |
| **Momentum 12-1 + double-tri turnover faible** | **305.42 EUR** | **+1.8%** | -7.7% | +0.25 |

**Lecture honnête** : fenêtre de 3 mois illustrative uniquement (~3 rebalancements mensuels observés) — le verdict statistique réel reste celui du backtest complet (2022-2026, PASS Sharpe+rendement) et de la robustesse (5/5 variantes voisines de TURNOVER_WINDOW restent OUI/OUI, plateau parfait).
