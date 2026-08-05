# Batterie de validation renforcée — vol_of_vol_vol_targeting_overlay

Coût pré-enregistré : 5.0 bps. 9748 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.58 | +0.54 | +11242.9% | +6044.4% | OUI |
| 15.0 | +0.57 | +0.54 | +9545.3% | +6038.3% | OUI |
| 25.0 | +0.55 | +0.54 | +8101.6% | +6032.2% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -82.9% | -82.9% | OUI |
| Crise financière 2008 | 378 | -53.8% | -53.7% | OUI |
| Krach COVID | 62 | -28.6% | -28.0% | OUI |
| Resserrement 2022 | 251 | -35.3% | -35.3% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2437 | +1.05 | +1.04 | OUI |
| 2 | 2432 | +0.17 | +0.18 | non |
| 3 | 2432 | +0.48 | +0.48 | OUI |
| 4 | 2432 | +0.99 | +0.83 | OUI |

**OK — bat le benchmark sur 3/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.0022
**OK — significatif à 5% : oui.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 227 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000688 (estimée sur 83 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0736 (journalier), DSR = 0.0001
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : OK
b. Stress crise : OK
c. Stabilité temporelle : OK
d. SPA 1-candidat : OK
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
