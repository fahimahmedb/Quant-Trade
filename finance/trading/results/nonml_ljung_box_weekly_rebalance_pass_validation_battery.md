# Batterie de validation renforcée — ljung_box_weekly_rebalance

Coût pré-enregistré : 5.0 bps. 9768 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.52 | +0.49 | +5670.6% | +3669.6% | OUI |
| 15.0 | +0.51 | +0.49 | +5101.6% | +3665.9% | OUI |
| 25.0 | +0.50 | +0.49 | +4588.6% | +3662.1% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -82.9% | -82.9% | OUI |
| Crise financière 2008 | 378 | -53.9% | -53.7% | OUI |
| Krach COVID | 62 | -29.1% | -28.0% | non |
| Resserrement 2022 | 251 | -35.3% | -35.3% | OUI |

**ÉCHEC — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : NON.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2442 | +0.74 | +0.75 | non |
| 2 | 2437 | +0.18 | +0.19 | non |
| 3 | 2437 | +0.43 | +0.45 | non |
| 4 | 2437 | +0.95 | +0.81 | OUI |

**ÉCHEC — bat le benchmark sur 1/4 folds (majorité NON atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.0136
**OK — significatif à 5% : oui.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 249 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000657 (estimée sur 88 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0727 (journalier), DSR = 0.0000
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : OK
b. Stress crise : ÉCHEC
c. Stabilité temporelle : ÉCHEC
d. SPA 1-candidat : OK
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
