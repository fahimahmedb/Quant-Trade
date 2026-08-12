# Batterie de validation renforcée — momentum_12_1_pit_universe (adaptée au format portefeuille)

Coût pré-enregistré : 5.0 bps. 2907 séances. Candidat = momentum 12-1, univers point-in-time (#265). Référence = Buy&Hold équipondéré (univers PIT).

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.64 | +0.62 | +511.1% | +352.1% | OUI |
| 15.0 | +0.63 | +0.62 | +493.5% | +351.3% | OUI |
| 25.0 | +0.62 | +0.62 | +476.3% | +350.5% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD candidat vs référence sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 62 | -34.1% | -31.9% | non |
| Resserrement 2022 | 251 | -32.2% | -30.9% | non |

**ÉCHEC — MDD jamais pire que la référence sur les fenêtres couvertes : NON.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe candidat | Sharpe référence | Bat référence |
|---|---|---|---|---|
| 1 | 726 | +1.03 | +0.80 | OUI |
| 2 | 721 | +0.68 | +0.63 | OUI |
| 3 | 721 | +0.08 | +0.31 | non |
| 4 | 724 | +0.82 | +0.82 | OUI |

**OK — bat la référence sur 3/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre la référence

p-value SPA : 0.1408
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 372 (taille du backlog après le #267), Var(Sharpe essais) estimée sur 112 Sharpe extraits du backlog = 0.000585 (échelle journalière).
DSR = 0.0461
**ÉCHEC — DSR ≥ 0.95 : NON.**

## Verdict global : 1/5

**PAS de PASS RENFORCÉ (1/5).**
