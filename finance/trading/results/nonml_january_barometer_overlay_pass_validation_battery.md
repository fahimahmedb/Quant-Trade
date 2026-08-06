# Batterie de validation renforcée — january_barometer_overlay

Coût pré-enregistré : 5.0 bps. 10272 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.59 | +0.53 | +63752.5% | +6599.5% | OUI |
| 15.0 | +0.59 | +0.53 | +60243.7% | +6592.7% | OUI |
| 25.0 | +0.58 | +0.53 | +56924.6% | +6585.9% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -89.6% | -82.9% | non |
| Crise financière 2008 | 378 | -56.9% | -53.7% | non |
| Krach COVID | 62 | -48.2% | -28.0% | non |
| Resserrement 2022 | 251 | -35.3% | -35.3% | OUI |

**ÉCHEC — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : NON.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2568 | +0.72 | +0.79 | non |
| 2 | 2563 | +0.36 | +0.28 | OUI |
| 3 | 2563 | +0.49 | +0.43 | OUI |
| 4 | 2563 | +0.90 | +0.83 | OUI |

**OK — bat le benchmark sur 3/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.0000
**OK — significatif à 5% : oui.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 318 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000585 (estimée sur 111 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0705 (journalier), DSR = 0.0004
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : OK
b. Stress crise : ÉCHEC
c. Stabilité temporelle : OK
d. SPA 1-candidat : OK
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
