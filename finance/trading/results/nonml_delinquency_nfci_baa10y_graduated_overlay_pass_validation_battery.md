# Batterie de validation renforcée — delinquency_nfci_baa10y_graduated_overlay

Coût pré-enregistré : 5.0 bps. 8883 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.58 | +0.50 | +3227.1% | +3129.3% | OUI |
| 15.0 | +0.57 | +0.50 | +3160.1% | +3126.1% | OUI |
| 25.0 | +0.57 | +0.50 | +3094.6% | +3123.0% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -72.9% | -82.9% | OUI |
| Crise financière 2008 | 378 | -35.2% | -53.7% | OUI |
| Krach COVID | 62 | -23.1% | -28.0% | OUI |
| Resserrement 2022 | 251 | -32.8% | -35.3% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2220 | +1.15 | +1.20 | non |
| 2 | 2215 | -0.26 | -0.35 | OUI |
| 3 | 2215 | +0.99 | +0.96 | OUI |
| 4 | 2218 | +0.78 | +0.76 | OUI |

**OK — bat le benchmark sur 3/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 1.0000
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 308 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000589 (estimée sur 110 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0705 (journalier), DSR = 0.0007
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : ÉCHEC
b. Stress crise : OK
c. Stabilité temporelle : OK
d. SPA 1-candidat : ÉCHEC
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
