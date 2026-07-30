# Batterie de validation renforcée — yield_curve_slope_sp500_vol_targeting_overlay

Coût pré-enregistré : 5.0 bps. 12631 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.50 | +0.49 | +5451.9% | +3370.4% | OUI |
| 15.0 | +0.46 | +0.49 | +3566.3% | +3367.0% | non |
| 25.0 | +0.42 | +0.49 | +2320.6% | +3363.5% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -58.5% | -49.1% | non |
| Crise financière 2008 | 378 | -59.8% | -56.8% | non |
| Krach COVID | 62 | -33.9% | -33.9% | OUI |
| Resserrement 2022 | 251 | -25.4% | -25.4% | OUI |

**ÉCHEC — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : NON.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 3157 | +0.55 | +0.48 | OUI |
| 2 | 3152 | +0.68 | +0.81 | non |
| 3 | 3152 | +0.11 | +0.13 | non |
| 4 | 3155 | +0.72 | +0.65 | OUI |

**ÉCHEC — bat le benchmark sur 2/4 folds (majorité NON atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.0212
**OK — significatif à 5% : oui.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 125 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000989 (estimée sur 51 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0820 (journalier), DSR = 0.0000
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : ÉCHEC
b. Stress crise : ÉCHEC
c. Stabilité temporelle : ÉCHEC
d. SPA 1-candidat : OK
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
