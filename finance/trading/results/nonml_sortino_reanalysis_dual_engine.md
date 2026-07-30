# Re-lecture Sortino — stabilité temporelle et stress de crise du #121

PAS un nouveau backtest -- même pnl déjà committé, même découpage Règle 9, métrique de lecture Sortino au lieu de Sharpe.

## 1. Stabilité temporelle (4 folds, embargo 5j) -- Sharpe vs Sortino

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH (Sharpe) | Sortino overlay | Sortino BH | Bat BH (Sortino) |
|---|---|---|---|---|---|---|---|
| 1 | 2380 | +0.87 | +0.97 | non | +1.26 | +1.42 | non |
| 2 | 2375 | +0.31 | +0.15 | OUI | +0.47 | +0.21 | OUI |
| 3 | 2375 | +0.64 | +0.45 | OUI | +0.88 | +0.57 | OUI |
| 4 | 2377 | +0.91 | +0.80 | OUI | +1.18 | +1.00 | OUI |

Folds favorables sous Sharpe : 3/4. Sous Sortino : 3/4.

## 2. Fenêtres de crise -- MDD (officiel) vs Sortino (complémentaire)

| Fenêtre | Séances | MDD overlay | MDD BH | Sortino overlay | Sortino BH | Sortino overlay>BH |
|---|---|---|---|---|---|---|
| Dot-com crash | 752 | -57.2% | -82.9% | -1.86 | -1.49 | non |
| Crise financière 2008 | 378 | -39.3% | -53.7% | -1.39 | -1.28 | non |
| Krach COVID | 62 | -17.1% | -28.0% | -1.30 | +0.00 | non |
| Resserrement 2022 | 251 | -30.2% | -35.3% | -2.27 | -2.01 | non |

Fenêtres de crise favorables sous Sortino : 0/4.

## Conclusion

Sous Sharpe (Règle 9c officielle) : 3/4 folds favorables. Sous Sortino (lecture complémentaire) : 3/4. Le Sortino ne change PAS qualitativement la lecture -- la stabilité temporelle reste similaire sous les deux métriques.
