# Batterie de validation renforcée — cash_rate_correction_44_weekly_rebalance_ndx

Coût pré-enregistré : 5.0 bps. 10252 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.83 | +0.53 | +11028.1% | +6416.7% | OUI |
| 15.0 | +0.82 | +0.53 | +9946.9% | +6410.2% | OUI |
| 25.0 | +0.80 | +0.53 | +8970.6% | +6403.7% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -36.3% | -82.9% | OUI |
| Crise financière 2008 | 378 | -26.2% | -53.7% | OUI |
| Krach COVID | 62 | -14.8% | -28.0% | OUI |
| Resserrement 2022 | 251 | -27.9% | -35.3% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2563 | +1.00 | +0.75 | OUI |
| 2 | 2558 | +0.65 | +0.29 | OUI |
| 3 | 2558 | +0.70 | +0.42 | OUI |
| 4 | 2558 | +0.96 | +0.84 | OUI |

**OK — bat le benchmark sur 4/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 1.0000
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 125 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000801 (estimée sur 68 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0738 (journalier), DSR = 0.0168
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : OK
b. Stress crise : OK
c. Stabilité temporelle : OK
d. SPA 1-candidat : ÉCHEC
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
