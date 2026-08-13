# Simulation 300 EUR — effet janvier (proxy prix bas), univers POINT-IN-TIME

Période : 2026-04-27 → 2026-07-27 (63 séances). Coûts 5 bps.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| Tercile prix bas 1.0x (référence) | 320.61 EUR | +6.9% | -3.7% | +2.07 |
| **Tercile prix bas + overlay janvier** | **320.61 EUR** | **+6.9%** | -3.7% | +2.07 |

Séances de janvier dans la fenêtre : **0**.

**La fenêtre ne contient AUCUN mois de janvier.** L'overlay n'est donc jamais actif et la stratégie est, par construction, **strictement identique à sa référence** sur cette période. Les deux lignes ci-dessus sont égales pour cette raison mécanique — ce n'est ni une performance ni une contre-performance, c'est l'absence de signal.

**Lecture honnête** : 63 séances n'ont **aucune valeur statistique**. Le verdict du cycle reste celui du backtest complet (2900 séances, 2015-2026, PASS) et de la grille de robustesse (4/4).
