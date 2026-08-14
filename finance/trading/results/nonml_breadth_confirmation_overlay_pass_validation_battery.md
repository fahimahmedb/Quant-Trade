# Batterie de validation renforcée — breadth_confirmation_overlay

Coût pré-enregistré : 5.0 bps. 10020 séances. Schéma `.npz` : **exposition**.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.53 | +0.52 | +76614.6% | +21358.1% | OUI |
| 15.0 | +0.49 | +0.52 | +47990.9% | +21336.7% | non |
| 25.0 | +0.45 | +0.52 | +30047.2% | +21315.2% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -83.8% | -82.9% | OUI |
| Crise financière 2008 | 378 | -54.6% | -53.7% | OUI |
| Krach COVID | 62 | -32.8% | -28.0% | non |
| Resserrement 2022 | 251 | -35.3% | -35.3% | OUI |

**ÉCHEC — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : NON.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2505 | +0.63 | +0.76 | non |
| 2 | 2500 | +0.26 | +0.23 | OUI |
| 3 | 2500 | +0.51 | +0.49 | OUI |
| 4 | 2500 | +0.85 | +0.81 | OUI |

**OK — bat le benchmark sur 3/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.0204
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
