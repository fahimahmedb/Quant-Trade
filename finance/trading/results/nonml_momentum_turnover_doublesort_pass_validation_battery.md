# Batterie de validation renforcée — momentum_turnover_doublesort (adaptée au format portefeuille)

Coût pré-enregistré : 5.0 bps. 1144 séances. Candidat = momentum 12-1 + double-tri turnover faible (#258). Référence = momentum 12-1 seul (#73), PAS Buy&Hold.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | PASS |
|---|---|---|---|---|---|
| 5.0 | +1.30 | +0.93 | +328.8% | +222.6% | OUI |
| 15.0 | +1.28 | +0.92 | +322.1% | +219.1% | OUI |
| 25.0 | +1.27 | +0.91 | +315.5% | +215.5% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD candidat vs référence sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 0 | -- | -- | hors couverture (<20 séances) |
| Resserrement 2022 | 251 | -23.2% | -29.9% | OUI |

**OK — MDD jamais pire que la référence sur les fenêtres couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe candidat | Sharpe référence | Bat référence |
|---|---|---|---|---|
| 1 | 286 | -0.46 | -0.70 | OUI |
| 2 | 281 | +2.16 | +1.88 | OUI |
| 3 | 281 | +1.51 | +1.29 | OUI |
| 4 | 281 | +2.59 | +1.81 | OUI |

**OK — bat la référence sur 4/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre la référence

p-value SPA : 0.1368
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 372 (taille du backlog après le #258), Var(Sharpe essais) estimée sur 112 Sharpe extraits du backlog = 0.000585 (échelle journalière).
DSR = 0.6323
**ÉCHEC — DSR ≥ 0.95 : NON.**

## Verdict global : 3/5

**PAS de PASS RENFORCÉ (3/5).**
