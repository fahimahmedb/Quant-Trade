# Batterie de validation renforcée — defensive_calmar_vol_targeting_overlay

Coût pré-enregistré : 5.0 bps. 10252 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.71 | +0.53 | +9256.6% | +6416.7% | OUI |
| 15.0 | +0.70 | +0.53 | +8306.0% | +6410.2% | OUI |
| 25.0 | +0.68 | +0.53 | +7451.9% | +6403.7% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -58.5% | -82.9% | OUI |
| Crise financière 2008 | 378 | -39.1% | -53.7% | OUI |
| Krach COVID | 62 | -17.4% | -28.0% | OUI |
| Resserrement 2022 | 251 | -27.6% | -35.3% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2563 | +0.88 | +0.75 | OUI |
| 2 | 2558 | +0.45 | +0.29 | OUI |
| 3 | 2558 | +0.56 | +0.42 | OUI |
| 4 | 2558 | +0.97 | +0.84 | OUI |

**OK — bat le benchmark sur 4/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 1.0000
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 110 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.001068 (estimée sur 47 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0838 (journalier), DSR = 0.0000
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : OK
b. Stress crise : OK
c. Stabilité temporelle : OK
d. SPA 1-candidat : ÉCHEC
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
