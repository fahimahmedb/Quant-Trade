# Batterie de validation renforcée — bond_market_volatility_overlay

Coût pré-enregistré : 5.0 bps. 5951 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.74 | +0.65 | +1489.5% | +1542.1% | non |
| 15.0 | +0.72 | +0.65 | +1374.5% | +1540.5% | non |
| 25.0 | +0.71 | +0.64 | +1267.8% | +1538.9% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 33 | -10.3% | -12.7% | OUI |
| Crise financière 2008 | 378 | -36.5% | -53.7% | OUI |
| Krach COVID | 62 | -22.3% | -28.0% | OUI |
| Resserrement 2022 | 251 | -23.8% | -35.3% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 1487 | +0.37 | +0.19 | OUI |
| 2 | 1482 | +0.95 | +0.88 | OUI |
| 3 | 1482 | +0.94 | +0.81 | OUI |
| 4 | 1485 | +0.75 | +0.74 | OUI |

**OK — bat le benchmark sur 4/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 1.0000
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 362 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000585 (estimée sur 111 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0714 (journalier), DSR = 0.0293
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : ÉCHEC
b. Stress crise : OK
c. Stabilité temporelle : OK
d. SPA 1-candidat : ÉCHEC
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
