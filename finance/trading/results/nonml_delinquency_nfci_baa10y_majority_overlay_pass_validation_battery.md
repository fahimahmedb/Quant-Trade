# Batterie de validation renforcée — delinquency_nfci_baa10y_majority_overlay

Coût pré-enregistré : 5.0 bps. 8883 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.61 | +0.50 | +4142.3% | +3129.3% | OUI |
| 15.0 | +0.61 | +0.50 | +4095.9% | +3126.1% | OUI |
| 25.0 | +0.60 | +0.50 | +4049.9% | +3123.0% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -71.9% | -82.9% | OUI |
| Crise financière 2008 | 378 | -35.4% | -53.7% | OUI |
| Krach COVID | 62 | -20.5% | -28.0% | OUI |
| Resserrement 2022 | 251 | -35.3% | -35.3% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2220 | +1.13 | +1.20 | non |
| 2 | 2215 | -0.24 | -0.35 | OUI |
| 3 | 2215 | +0.95 | +0.96 | non |
| 4 | 2218 | +0.78 | +0.76 | OUI |

**ÉCHEC — bat le benchmark sur 2/4 folds (majorité NON atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 1.0000
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 306 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000594 (estimée sur 109 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0707 (journalier), DSR = 0.0011
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : OK
b. Stress crise : OK
c. Stabilité temporelle : ÉCHEC
d. SPA 1-candidat : ÉCHEC
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
