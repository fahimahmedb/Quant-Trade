# Batterie de validation renforcée — amihud_illiquidity_tilt (adaptée au format portefeuille)

Coût pré-enregistré : 5.0 bps. 1270 séances. Candidat = tilt Amihud illiquidité (#261). Référence = Buy&Hold équipondéré (univers).

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.84 | +0.59 | +142.8% | +70.0% | OUI |
| 15.0 | +0.84 | +0.59 | +142.1% | +69.9% | OUI |
| 25.0 | +0.84 | +0.59 | +141.4% | +69.8% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD candidat vs référence sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 0 | -- | -- | hors couverture (<20 séances) |
| Resserrement 2022 | 251 | -33.5% | -33.9% | OUI |

**OK — MDD jamais pire que la référence sur les fenêtres couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe candidat | Sharpe référence | Bat référence |
|---|---|---|---|---|
| 1 | 317 | -0.50 | -0.69 | OUI |
| 2 | 312 | +1.37 | +1.66 | non |
| 3 | 312 | +0.61 | +0.27 | OUI |
| 4 | 314 | +2.83 | +1.98 | OUI |

**OK — bat la référence sur 3/4 folds (majorité atteinte).**

## d. SPA à 1 candidat contre la référence

p-value SPA : 0.0034
**OK — significatif à 5% : oui.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 268 (taille du backlog après le #261), Var(Sharpe essais) estimée sur 103 Sharpe extraits du backlog = 0.000601 (échelle journalière).
DSR = 0.2731
**ÉCHEC — DSR ≥ 0.95 : NON.**

## Verdict global : 4/5

**PAS de PASS RENFORCÉ (4/5).**
