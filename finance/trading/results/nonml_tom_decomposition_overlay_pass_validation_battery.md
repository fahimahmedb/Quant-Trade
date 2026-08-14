# Batterie de validation renforcée — tom_decomposition_overlay

Coût pré-enregistré : 5.0 bps. 10272 séances. Schéma `.npz` : **exposition**.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.53 | +0.53 | +100638.1% | +26208.9% | OUI |
| 15.0 | +0.46 | +0.53 | +37746.0% | +26182.6% | non |
| 25.0 | +0.38 | +0.53 | +14118.2% | +26156.3% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -89.3% | -82.9% | non |
| Crise financière 2008 | 378 | -50.9% | -53.7% | OUI |
| Krach COVID | 62 | -33.0% | -28.0% | non |
| Resserrement 2022 | 251 | -39.5% | -35.3% | non |

**ÉCHEC — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : NON.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2568 | +1.02 | +0.79 | OUI |
| 2 | 2563 | +0.15 | +0.28 | non |
| 3 | 2563 | +0.46 | +0.43 | OUI |
| 4 | 2563 | +0.84 | +0.83 | OUI |

**OK — bat le benchmark sur 3/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.0206
**OK — significatif à 5% : oui.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 370 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000585 (estimée sur 112 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0716 (journalier), DSR = 0.0001
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : ÉCHEC
b. Stress crise : ÉCHEC
c. Stabilité temporelle : OK
d. SPA 1-candidat : OK
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
