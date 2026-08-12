# Batterie de validation renforcée — dollar_neutral_composite_vol_targeted (adaptée au format portefeuille)

Coût pré-enregistré : 5.0 bps. 2887 séances. Candidat = sleeve dollar-neutre composite redimensionné par sa vol (#350). Référence = Buy&Hold équipondéré (univers PIT, #349).

**Vérification de régression (doit reproduire le #350 déjà committé)** : Sharpe ann. reconstruit = +0.28 (#350 committé : +0.61), t-stat reconstruit = +1.22 (#350 committé : +2.08).

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.36 | +0.74 | +69.6% | +362.1% | non |
| 15.0 | +0.28 | +0.74 | +45.3% | +361.5% | non |
| 25.0 | +0.20 | +0.74 | +24.4% | +360.9% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD candidat vs référence sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 62 | -5.1% | -29.7% | OUI |
| Resserrement 2022 | 251 | -9.8% | -28.0% | OUI |

**OK — MDD jamais pire que la référence sur les fenêtres couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe candidat | Sharpe référence | Bat référence |
|---|---|---|---|---|
| 1 | 721 | +0.66 | +0.97 | non |
| 2 | 716 | +0.18 | +0.76 | non |
| 3 | 716 | -0.25 | +0.57 | non |
| 4 | 719 | +0.79 | +0.92 | non |

**ÉCHEC — bat la référence sur 0/4 folds (majorité NON atteinte).**

## d. SPA à 1 candidat contre la référence

p-value SPA : 1.0000
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 372 (taille du backlog), Var(Sharpe essais) estimée sur 112 Sharpe extraits du backlog = 0.000585 (échelle journalière).
DSR = 0.0044
**ÉCHEC — DSR ≥ 0.95 : NON.**

## Verdict global : 1/5

**PAS de PASS RENFORCÉ (1/5).**
