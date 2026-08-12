# Batterie de validation renforcée — leaders_vol_targeting_20_overlay

Coût pré-enregistré : 5.0 bps. 1124 séances. Schéma `.npz` : **portefeuille**.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.98 | +0.97 | +155.4% | +127.6% | OUI |
| 15.0 | +0.93 | +0.95 | +144.3% | +123.8% | non |
| 25.0 | +0.89 | +0.93 | +133.8% | +120.1% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD overlay vs Buy&Hold sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD overlay | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 0 | -- | -- | hors couverture (<20 séances) |
| Resserrement 2022 | 231 | -21.9% | -21.1% | OUI |

**OK — MDD jamais pire que Buy&Hold sur les fenêtres de crise couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH |
|---|---|---|---|---|
| 1 | 281 | -0.69 | -0.51 | non |
| 2 | 276 | +1.54 | +1.67 | non |
| 3 | 276 | +0.74 | +0.76 | non |
| 4 | 276 | +2.34 | +2.15 | OUI |

**ÉCHEC — bat le benchmark sur 1/4 folds (majorité NON atteinte).**

## d. SPA à 1 candidat contre Buy&Hold

p-value SPA : 0.1788
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 372 (taille totale du backlog), var_trials (échelle journalière, convertie depuis les Sharpe annualisés extraits) ≈ 0.000585 (estimée sur 112 Sharpe extractibles de l'historique du backlog -- univers hétérogène, approximation prudente).
SR0 (seuil de sélection) = 0.0717 (journalier), DSR = 0.3687
**ÉCHEC — DSR>0,95 : NON.**

## Verdict de la batterie renforcée

a. Stress coûts : ÉCHEC
b. Stress crise : OK
c. Stabilité temporelle : ÉCHEC
d. SPA 1-candidat : ÉCHEC
e. DSR (n_trials=backlog) : ÉCHEC

**PAS de PASS RENFORCÉ — au moins un contrôle échoue, verdict initial insuffisant pour validation finale.**
