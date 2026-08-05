# Batterie de validation renforcée — slope_vol_targeting_overlay

Coût pré-enregistré : 5.0 bps. 10052 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.54 | +0.51 | +8482.1% | +4956.4% | OUI |
| 15.0 | +0.51 | +0.51 | +6462.6% | +4951.4% | OUI |
| 25.0 | +0.49 | +0.51 | +4918.1% | +4946.3% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -82.9% | -82.9% | OUI |
| Crise financière 2008 | 378 | -53.9% | -53.7% | OUI |
| Krach COVID | 62 | -28.6% | -28.0% | OUI |
| Resserrement 2022 | 251 | -35.3% | -35.3% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2513 | +0.64 | +0.66 | non |
| 2 | 2508 | +0.22 | +0.24 | non |
| 3 | 2508 | +0.51 | +0.50 | OUI |
| 4 | 2508 | +0.91 | +0.82 | OUI |

**ÉCHEC — bat le benchmark sur 2/4 folds (majorité NON atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.0118
**OK — significatif à 5% : oui.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 212 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000698 (estimée sur 80 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0736 (journalier), DSR = 0.0000
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : ÉCHEC
b. Stress crise : OK
c. Stabilité temporelle : ÉCHEC
d. SPA 1-candidat : OK
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
