# Batterie de validation renforcée — gjr_vol_managed_sp500

Coût pré-enregistré : 5.0 bps. 13501 séances. Schéma `.npz` : **exposition**.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.49 | +0.44 | +19088.3% | +6325.6% | OUI |
| 15.0 | +0.45 | +0.44 | +11684.7% | +6319.2% | OUI |
| 25.0 | +0.40 | +0.44 | +7137.7% | +6312.8% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -57.9% | -49.1% | non |
| Crise financière 2008 | 378 | -45.7% | -56.8% | OUI |
| Krach COVID | 62 | -21.5% | -33.9% | OUI |
| Resserrement 2022 | 251 | -25.4% | -25.4% | OUI |

**ÉCHEC — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : NON.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 3375 | +0.36 | +0.36 | non |
| 2 | 3370 | +0.87 | +0.79 | OUI |
| 3 | 3370 | +0.04 | +0.04 | OUI |
| 4 | 3371 | +0.70 | +0.70 | OUI |

**OK — bat le benchmark sur 3/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.0306
**OK — significatif à 5% : oui.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 370 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000585 (estimée sur 112 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0716 (journalier), DSR = 0.0000
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : ÉCHEC
b. Stress crise : ÉCHEC
c. Stabilité temporelle : OK
d. SPA 1-candidat : OK
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
