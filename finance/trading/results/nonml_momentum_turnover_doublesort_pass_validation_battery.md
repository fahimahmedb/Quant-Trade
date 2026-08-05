# Batterie de validation renforcée — momentum_turnover_doublesort (adaptée au format portefeuille)

Coût pré-enregistré : 5.0 bps. 1144 séances. Candidat = momentum 12-1 + double-tri turnover faible (#258). Référence = momentum 12-1 seul (#73), PAS Buy&Hold.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | PASS |
|---|---|---|---|---|---|
| 5.0 | +1.04 | +0.66 | +178.3% | +93.8% | OUI |
| 15.0 | +1.02 | +0.65 | +174.0% | +91.6% | OUI |
| 25.0 | +1.01 | +0.65 | +169.6% | +89.5% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD candidat vs référence sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 0 | -- | -- | hors couverture (<20 séances) |
| Resserrement 2022 | 251 | -25.7% | -31.8% | OUI |

**OK — MDD jamais pire que la référence sur les fenêtres couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe candidat | Sharpe référence | Bat référence |
|---|---|---|---|---|
| 1 | 286 | -0.61 | -0.85 | OUI |
| 2 | 281 | +1.92 | +1.63 | OUI |
| 3 | 281 | +1.23 | +1.00 | OUI |
| 4 | 281 | +2.22 | +1.45 | OUI |

**OK — bat la référence sur 4/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre la référence

p-value SPA : 0.1062
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 265 (taille du backlog après le #258), Var(Sharpe essais) estimée sur 101 Sharpe extraits du backlog = 0.000612 (échelle journalière).
DSR = 0.4307
**ÉCHEC — DSR ≥ 0.95 : NON.**

## Verdict global : 3/5

**PAS de PASS RENFORCÉ (3/5).**
