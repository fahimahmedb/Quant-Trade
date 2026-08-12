# Batterie de validation renforcée — momentum_12_1_pit_universe

Coût pré-enregistré : 5.0 bps. 2907 séances. Schéma `.npz` : **portefeuille**.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.64 | +0.62 | +511.1% | +352.1% | OUI |
| 15.0 | +0.63 | +0.62 | +493.5% | +351.3% | OUI |
| 25.0 | +0.62 | +0.62 | +476.3% | +350.5% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 62 | -34.1% | -31.9% | non |
| Resserrement 2022 | 251 | -32.2% | -30.9% | non |

**ÉCHEC — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : NON.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 726 | +1.03 | +0.80 | OUI |
| 2 | 721 | +0.68 | +0.63 | OUI |
| 3 | 721 | +0.08 | +0.31 | non |
| 4 | 724 | +0.82 | +0.82 | OUI |

**OK — bat le benchmark sur 3/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.1408
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 372 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000585 (estimée sur 112 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0717 (journalier), DSR = 0.0461
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : ÉCHEC
b. Stress crise : ÉCHEC
c. Stabilité temporelle : OK
d. SPA 1-candidat : ÉCHEC
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
