# Batterie de validation renforcée — yang_zhang_vol_targeting_overlay

Coût pré-enregistré : 5.0 bps. 10252 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.74 | +0.53 | +35833.7% | +6416.7% | OUI |
| 15.0 | +0.71 | +0.53 | +27167.6% | +6410.2% | OUI |
| 25.0 | +0.68 | +0.53 | +20591.0% | +6403.7% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -61.1% | -82.9% | OUI |
| Crise financière 2008 | 378 | -40.3% | -53.7% | OUI |
| Krach COVID | 62 | -18.4% | -28.0% | OUI |
| Resserrement 2022 | 251 | -33.5% | -35.3% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2563 | +0.89 | +0.75 | OUI |
| 2 | 2558 | +0.49 | +0.29 | OUI |
| 3 | 2558 | +0.54 | +0.42 | OUI |
| 4 | 2558 | +1.02 | +0.84 | OUI |

**OK — bat le benchmark sur 4/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.0202
**OK — significatif à 5% : oui.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 229 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000688 (estimée sur 83 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0737 (journalier), DSR = 0.0037
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : OK
b. Stress crise : OK
c. Stabilité temporelle : OK
d. SPA 1-candidat : OK
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
