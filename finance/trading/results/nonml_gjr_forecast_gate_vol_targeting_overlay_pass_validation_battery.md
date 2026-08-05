# Batterie de validation renforcée — gjr_forecast_gate_vol_targeting_overlay

Coût pré-enregistré : 5.0 bps. 9270 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.51 | +0.51 | +4337.3% | +3624.8% | OUI |
| 15.0 | +0.48 | +0.51 | +3140.7% | +3621.0% | non |
| 25.0 | +0.45 | +0.51 | +2266.5% | +3617.3% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -82.9% | -82.9% | OUI |
| Crise financière 2008 | 378 | -54.1% | -53.7% | OUI |
| Krach COVID | 62 | -28.4% | -28.0% | OUI |
| Resserrement 2022 | 251 | -35.3% | -35.3% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2317 | +0.88 | +0.92 | non |
| 2 | 2312 | +0.03 | +0.03 | non |
| 3 | 2312 | +0.50 | +0.54 | non |
| 4 | 2314 | +0.81 | +0.78 | OUI |

**ÉCHEC — bat le benchmark sur 1/4 folds (majorité NON atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.1030
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 235 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000688 (estimée sur 83 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0739 (journalier), DSR = 0.0000
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : ÉCHEC
b. Stress crise : OK
c. Stabilité temporelle : ÉCHEC
d. SPA 1-candidat : ÉCHEC
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
