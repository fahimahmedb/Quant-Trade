# Batterie de validation renforcée — diversification_bond_overlay_crossmarket_sp500

Coût pré-enregistré : 5.0 bps. 14231 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.55 | +0.46 | +4982.2% | +3696.8% | OUI |
| 15.0 | +0.55 | +0.46 | +4674.2% | +3693.0% | OUI |
| 25.0 | +0.54 | +0.46 | +4384.8% | +3689.3% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -48.5% | -49.1% | OUI |
| Crise financière 2008 | 378 | -38.5% | -56.8% | OUI |
| Krach COVID | 62 | -19.9% | -33.9% | OUI |
| Resserrement 2022 | 251 | -23.9% | -25.4% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 3557 | +0.32 | +0.31 | OUI |
| 2 | 3552 | +1.04 | +0.90 | OUI |
| 3 | 3552 | +0.11 | +0.07 | OUI |
| 4 | 3555 | +0.84 | +0.74 | OUI |

**OK — bat le benchmark sur 4/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.4280
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 125 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000929 (estimée sur 56 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0795 (journalier), DSR = 0.0000
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : OK
b. Stress crise : OK
c. Stabilité temporelle : OK
d. SPA 1-candidat : ÉCHEC
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
