# Batterie de validation renforcée — delinquency_nfci_baa10y_corr_majority_overlay

Coût pré-enregistré : 5.0 bps. 6651 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.38 | +0.30 | +389.5% | +225.5% | OUI |
| 15.0 | +0.37 | +0.30 | +377.0% | +225.2% | OUI |
| 25.0 | +0.37 | +0.30 | +364.8% | +224.9% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 733 | -74.2% | -82.9% | OUI |
| Crise financière 2008 | 378 | -38.1% | -53.7% | OUI |
| Krach COVID | 62 | -23.3% | -28.0% | OUI |
| Resserrement 2022 | 251 | -35.3% | -35.3% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 1662 | -0.23 | -0.32 | OUI |
| 2 | 1657 | +0.40 | +0.31 | OUI |
| 3 | 1657 | +0.99 | +0.99 | OUI |
| 4 | 1660 | +0.75 | +0.76 | non |

**OK — bat le benchmark sur 3/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.3378
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 310 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000589 (estimée sur 110 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0705 (journalier), DSR = 0.0001
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : OK
b. Stress crise : OK
c. Stabilité temporelle : OK
d. SPA 1-candidat : ÉCHEC
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
