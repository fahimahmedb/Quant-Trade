# Batterie de validation renforcée — amihud_illiquidity_tilt (adaptée au format portefeuille)

Coût pré-enregistré : 5.0 bps. 1270 séances. Candidat = tilt Amihud illiquidité (#261). Référence = Buy&Hold équipondéré (univers).

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | PASS |
|---|---|---|---|---|---|
| 5.0 | +1.18 | +0.90 | +330.1% | +171.6% | OUI |
| 15.0 | +1.18 | +0.90 | +328.9% | +171.4% | OUI |
| 25.0 | +1.18 | +0.90 | +327.7% | +171.3% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD candidat vs référence sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 0 | -- | -- | hors couverture (<20 séances) |
| Resserrement 2022 | 251 | -29.1% | -30.0% | OUI |

**OK — MDD jamais pire que la référence sur les fenêtres couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe candidat | Sharpe référence | Bat référence |
|---|---|---|---|---|
| 1 | 317 | -0.23 | -0.46 | OUI |
| 2 | 312 | +1.64 | +1.89 | non |
| 3 | 312 | +0.95 | +0.60 | OUI |
| 4 | 314 | +3.39 | +2.54 | OUI |

**OK — bat la référence sur 3/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre la référence

p-value SPA : 0.0004
**OK — significatif à 5% : oui.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 372 (taille du backlog après le #261), Var(Sharpe essais) estimée sur 112 Sharpe extraits du backlog = 0.000585 (échelle journalière).
DSR = 0.5398
**ÉCHEC — DSR ≥ 0.95 : NON.**

## Verdict global : 4/5

**PAS de PASS RENFORCÉ (4/5).**
