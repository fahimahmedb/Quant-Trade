# Batterie de validation renforcée — momentum_consistency_pit_universe (adaptée au format portefeuille)

Coût pré-enregistré : 5.0 bps. 2907 séances. Candidat = momentum de constance, univers point-in-time (#266). Référence = Buy&Hold équipondéré (univers PIT).

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.61 | +0.62 | +403.8% | +350.6% | non |
| 15.0 | +0.60 | +0.62 | +390.1% | +349.8% | non |
| 25.0 | +0.59 | +0.62 | +376.7% | +349.0% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD candidat vs référence sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 62 | -34.8% | -31.9% | non |
| Resserrement 2022 | 251 | -30.1% | -30.9% | OUI |

**ÉCHEC — MDD jamais pire que la référence sur les fenêtres couvertes : NON.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe candidat | Sharpe référence | Bat référence |
|---|---|---|---|---|
| 1 | 726 | +0.89 | +0.80 | OUI |
| 2 | 721 | +0.55 | +0.62 | non |
| 3 | 721 | +0.12 | +0.31 | non |
| 4 | 724 | +0.96 | +0.82 | OUI |

**ÉCHEC — bat la référence sur 2/4 folds (majorité NON atteinte).**

## d. SPA à 1 candidat contre la référence

p-value SPA : 0.3336
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 372 (taille du backlog après le #268), Var(Sharpe essais) estimée sur 112 Sharpe extraits du backlog = 0.000585 (échelle journalière).
DSR = 0.0394
**ÉCHEC — DSR ≥ 0.95 : NON.**

## Verdict global : 0/5

**PAS de PASS RENFORCÉ (0/5).**
