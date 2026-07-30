# Batterie de validation renforcée — diversification_bond_overlay_crossmarket_russell2000

Coût pré-enregistré : 5.0 bps. 9761 séances.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.44 | +0.34 | +896.4% | +610.3% | OUI |
| 15.0 | +0.43 | +0.34 | +819.8% | +609.6% | OUI |
| 25.0 | +0.42 | +0.34 | +749.1% | +608.9% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -42.1% | -46.0% | OUI |
| Crise financière 2008 | 378 | -33.0% | -59.4% | OUI |
| Krach COVID | 62 | -27.3% | -41.6% | OUI |
| Resserrement 2022 | 251 | -25.9% | -27.4% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 2440 | +0.89 | +0.66 | OUI |
| 2 | 2435 | +0.39 | +0.38 | OUI |
| 3 | 2435 | +0.30 | +0.15 | OUI |
| 4 | 2436 | +0.38 | +0.40 | non |

**OK — bat le benchmark sur 3/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 1.0000
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
