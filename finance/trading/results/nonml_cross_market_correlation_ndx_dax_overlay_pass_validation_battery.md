# Batterie de validation renforcée — cross_market_correlation_ndx_dax_overlay

Coût pré-enregistré : 5.0 bps. 6651 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.34 | +0.30 | +279.3% | +225.5% | OUI |
| 15.0 | +0.33 | +0.30 | +246.4% | +225.2% | OUI |
| 25.0 | +0.31 | +0.30 | +216.3% | +224.9% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 733 | -67.6% | -82.9% | OUI |
| Crise financière 2008 | 378 | -43.7% | -53.7% | OUI |
| Krach COVID | 62 | -18.5% | -28.0% | OUI |
| Resserrement 2022 | 251 | -32.6% | -35.3% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 1662 | -0.19 | -0.32 | OUI |
| 2 | 1657 | +0.17 | +0.31 | non |
| 3 | 1657 | +0.93 | +0.99 | non |
| 4 | 1660 | +0.75 | +0.76 | non |

**ÉCHEC — bat le benchmark sur 1/4 folds (majorité NON atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 1.0000
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 194 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000725 (estimée sur 77 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0742 (journalier), DSR = 0.0000
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : ÉCHEC
b. Stress crise : OK
c. Stabilité temporelle : ÉCHEC
d. SPA 1-candidat : ÉCHEC
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
