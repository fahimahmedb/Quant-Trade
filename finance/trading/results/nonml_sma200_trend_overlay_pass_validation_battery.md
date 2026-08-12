# Batterie de validation renforcée — sma200_trend_overlay

Coût pré-enregistré : 5.0 bps. 10072 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.59 | +0.51 | +1411093.8% | +19772.5% | OUI |
| 15.0 | +0.57 | +0.51 | +1071803.5% | +19752.7% | OUI |
| 25.0 | +0.55 | +0.51 | +814088.0% | +19732.8% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -91.7% | -82.9% | non |
| Crise financière 2008 | 378 | -64.8% | -53.7% | non |
| Krach COVID | 62 | -43.8% | -28.0% | non |
| Resserrement 2022 | 251 | -47.6% | -35.3% | non |

**ÉCHEC — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : NON.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2518 | +0.75 | +0.73 | OUI |
| 2 | 2513 | +0.35 | +0.25 | OUI |
| 3 | 2513 | +0.49 | +0.47 | OUI |
| 4 | 2513 | +0.95 | +0.82 | OUI |

**OK — bat le benchmark sur 4/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.0000
**OK — significatif à 5% : oui.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 372 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000585 (estimée sur 112 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0717 (journalier), DSR = 0.0003
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : OK
b. Stress crise : ÉCHEC
c. Stabilité temporelle : OK
d. SPA 1-candidat : OK
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
