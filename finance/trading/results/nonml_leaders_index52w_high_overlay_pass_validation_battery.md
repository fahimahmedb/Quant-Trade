# Batterie de validation renforcée — leaders_index52w_high_overlay

Coût pré-enregistré : 5.0 bps. 1144 séances. Schéma `.npz` : **portefeuille**.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.87 | +0.84 | +220.9% | +108.0% | OUI |
| 15.0 | +0.82 | +0.82 | +202.5% | +104.5% | non |
| 25.0 | +0.78 | +0.80 | +185.1% | +101.0% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 0 | -- | -- | hors couverture (<20 séances) |
| Resserrement 2022 | 251 | -28.8% | -25.7% | non |

**ÉCHEC — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : NON.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 286 | -1.01 | -0.85 | non |
| 2 | 281 | +1.58 | +1.72 | non |
| 3 | 281 | +0.89 | +0.88 | OUI |
| 4 | 281 | +1.69 | +2.12 | non |

**ÉCHEC — bat le benchmark sur 1/4 folds (majorité NON atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.0672
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 372 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000585 (estimée sur 112 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0717 (journalier), DSR = 0.2851
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : ÉCHEC
b. Stress crise : ÉCHEC
c. Stabilité temporelle : ÉCHEC
d. SPA 1-candidat : ÉCHEC
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
