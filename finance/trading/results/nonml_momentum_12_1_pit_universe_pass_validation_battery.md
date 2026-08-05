# Batterie de validation renforcée — momentum_12_1_pit_universe (adaptée au format portefeuille)

Coût pré-enregistré : 5.0 bps. 2907 séances. Candidat = momentum 12-1, univers point-in-time (#265). Référence = Buy&Hold équipondéré (univers PIT).

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.44 | +0.39 | +147.4% | +99.6% | OUI |
| 15.0 | +0.43 | +0.39 | +140.3% | +99.3% | OUI |
| 25.0 | +0.42 | +0.39 | +133.3% | +98.9% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD candidat vs référence sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 62 | -34.7% | -32.8% | non |
| Resserrement 2022 | 251 | -34.3% | -34.5% | OUI |

**ÉCHEC — MDD jamais pire que la référence sur les fenêtres couvertes : NON.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe candidat | Sharpe référence | Bat référence |
|---|---|---|---|---|
| 1 | 726 | +0.86 | +0.60 | OUI |
| 2 | 721 | +0.54 | +0.46 | OUI |
| 3 | 721 | -0.11 | +0.07 | non |
| 4 | 724 | +0.53 | +0.45 | OUI |

**OK — bat la référence sur 3/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre la référence

p-value SPA : 0.1274
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 274 (taille du backlog après le #267), Var(Sharpe essais) estimée sur 105 Sharpe extraits du backlog = 0.000595 (échelle journalière).
DSR = 0.0123
**ÉCHEC — DSR ≥ 0.95 : NON.**

## Verdict global : 2/5

**PAS de PASS RENFORCÉ (2/5).**
