# Batterie de validation renforcée — gjr_vol_managed_russell2000

Coût pré-enregistré : 5.0 bps. 9031 séances. Schéma `.npz` : **exposition**.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.44 | +0.39 | +2276.6% | +2014.8% | OUI |
| 15.0 | +0.34 | +0.39 | +1130.5% | +2012.7% | non |
| 25.0 | +0.25 | +0.39 | +537.1% | +2010.6% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -46.3% | -46.0% | OUI |
| Crise financière 2008 | 378 | -41.4% | -59.4% | OUI |
| Krach COVID | 62 | -22.4% | -41.6% | OUI |
| Resserrement 2022 | 251 | -22.4% | -27.4% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2257 | +1.19 | +1.01 | OUI |
| 2 | 2252 | +0.18 | +0.26 | non |
| 3 | 2252 | +0.25 | +0.29 | non |
| 4 | 2255 | +0.20 | +0.33 | non |

**ÉCHEC — bat le benchmark sur 1/4 folds (majorité NON atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.4166
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 370 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000585 (estimée sur 112 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0716 (journalier), DSR = 0.0000
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : ÉCHEC
b. Stress crise : OK
c. Stabilité temporelle : ÉCHEC
d. SPA 1-candidat : ÉCHEC
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
