# Batterie de validation renforcée — halloween_postelection_multiplicative_overlay

Coût pré-enregistré : 5.0 bps. 10272 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.52 | +0.53 | +243445.3% | +26208.9% | non |
| 15.0 | +0.51 | +0.53 | +221816.9% | +26182.6% | non |
| 25.0 | +0.50 | +0.53 | +202109.3% | +26156.3% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -90.8% | -82.9% | non |
| Crise financière 2008 | 378 | -69.3% | -53.7% | non |
| Krach COVID | 62 | -48.2% | -28.0% | non |
| Resserrement 2022 | 251 | -52.8% | -35.3% | non |

**ÉCHEC — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : NON.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2568 | +0.87 | +0.79 | OUI |
| 2 | 2563 | +0.38 | +0.28 | OUI |
| 3 | 2563 | +0.31 | +0.43 | non |
| 4 | 2563 | +0.65 | +0.83 | non |

**ÉCHEC — bat le benchmark sur 2/4 folds (majorité NON atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.0142
**OK — significatif à 5% : oui.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 372 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000585 (estimée sur 112 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0717 (journalier), DSR = 0.0000
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : ÉCHEC
b. Stress crise : ÉCHEC
c. Stabilité temporelle : ÉCHEC
d. SPA 1-candidat : OK
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
