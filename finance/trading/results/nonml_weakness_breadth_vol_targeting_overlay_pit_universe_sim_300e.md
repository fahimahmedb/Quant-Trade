# Simulation 300 EUR — breadth de faiblesse, univers POINT-IN-TIME

Période : 2026-04-13 → 2026-07-13 (63 séances, dont **0** avec porte active). Coûts 5 bps. Aucun paramètre retouché après lecture des résultats précédents.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| Buy&Hold (NDX) | 352.39 EUR | +17.5% | -7.0% | +2.74 |
| **Overlay gaté breadth de faiblesse (PIT)** | **352.57 EUR** | **+17.5%** | -7.0% | +2.75 |

**La porte n'est jamais active sur cette fenêtre.** La stratégie est donc par construction identique à Buy & Hold ici — ce n'est ni une performance ni une contre-performance, c'est l'absence de signal.

**Lecture honnête** : 63 séances n'ont **aucune valeur statistique**. Le verdict du cycle reste celui du backtest complet (2896 séances, 2015-2026, PASS) et de la grille de robustesse (4/4 sur CAP, 4/4 sur la fenêtre — toutes cellules identiques à Buy & Hold).

**Rappel décisif** : le verdict de ce candidat est étiqueté **NON INFORMATIF** par le critère fixé avant calcul (porte brute active 0,45 % du temps), et l'audit a établi que l'exposition ne dépasse **jamais** 1,0×. Les deux lignes ci-dessus sont donc identiques par construction, et non parce que la stratégie aurait égalé Buy & Hold sur cette fenêtre.
