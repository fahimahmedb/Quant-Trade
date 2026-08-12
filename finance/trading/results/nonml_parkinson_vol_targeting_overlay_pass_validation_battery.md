# Batterie de validation renforcée — parkinson_vol_targeting_overlay

Coût pré-enregistré : 5.0 bps. 10252 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.75 | +0.53 | +210744.6% | +25465.6% | OUI |
| 15.0 | +0.72 | +0.53 | +162311.8% | +25440.1% | OUI |
| 25.0 | +0.69 | +0.53 | +125004.4% | +25414.6% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -66.5% | -82.9% | OUI |
| Crise financière 2008 | 378 | -45.9% | -53.7% | OUI |
| Krach COVID | 62 | -26.7% | -28.0% | OUI |
| Resserrement 2022 | 251 | -38.1% | -35.3% | non |

**ÉCHEC — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : NON.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2563 | +0.92 | +0.75 | OUI |
| 2 | 2558 | +0.41 | +0.29 | OUI |
| 3 | 2558 | +0.59 | +0.42 | OUI |
| 4 | 2558 | +1.03 | +0.84 | OUI |

**OK — bat le benchmark sur 4/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.0020
**OK — significatif à 5% : oui.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 372 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000585 (estimée sur 112 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0717 (journalier), DSR = 0.0067
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : OK
b. Stress crise : ÉCHEC
c. Stabilité temporelle : OK
d. SPA 1-candidat : OK
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
