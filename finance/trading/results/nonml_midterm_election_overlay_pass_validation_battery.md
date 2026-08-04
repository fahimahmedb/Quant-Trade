# Batterie de validation renforcée — midterm_election_overlay

Coût pré-enregistré : 5.0 bps. 10272 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.57 | +0.53 | +7339.6% | +6599.5% | OUI |
| 15.0 | +0.57 | +0.53 | +7262.2% | +6592.7% | OUI |
| 25.0 | +0.57 | +0.53 | +7185.6% | +6585.9% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -76.1% | -82.9% | OUI |
| Crise financière 2008 | 378 | -53.7% | -53.7% | OUI |
| Krach COVID | 62 | -28.0% | -28.0% | OUI |
| Resserrement 2022 | 251 | -19.6% | -35.3% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2568 | +0.88 | +0.79 | OUI |
| 2 | 2563 | +0.29 | +0.28 | OUI |
| 3 | 2563 | +0.37 | +0.43 | non |
| 4 | 2563 | +1.03 | +0.83 | OUI |

**OK — bat le benchmark sur 3/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 1.0000
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 188 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000724 (estimée sur 76 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0738 (journalier), DSR = 0.0001
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : OK
b. Stress crise : OK
c. Stabilité temporelle : OK
d. SPA 1-candidat : ÉCHEC
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
