# Batterie de validation renforcée — weekly_rebalance_dual_engine

Coût pré-enregistré : 5.0 bps. 9522 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.72 | +0.52 | +10666.3% | +4553.2% | OUI |
| 15.0 | +0.70 | +0.52 | +9438.9% | +4548.6% | OUI |
| 25.0 | +0.69 | +0.52 | +8351.2% | +4544.0% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -55.3% | -82.9% | OUI |
| Crise financière 2008 | 378 | -38.5% | -53.7% | OUI |
| Krach COVID | 62 | -17.4% | -28.0% | OUI |
| Resserrement 2022 | 251 | -30.3% | -35.3% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2380 | +0.95 | +0.97 | non |
| 2 | 2375 | +0.32 | +0.15 | OUI |
| 3 | 2375 | +0.64 | +0.45 | OUI |
| 4 | 2377 | +0.92 | +0.80 | OUI |

**OK — bat le benchmark sur 3/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.3028
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 125 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000946 (estimée sur 55 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0802 (journalier), DSR = 0.0003
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : OK
b. Stress crise : OK
c. Stabilité temporelle : OK
d. SPA 1-candidat : ÉCHEC
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
