# Batterie de validation renforcée — dollar_neutral_composite_vol_targeted (adaptée au format portefeuille)

Coût pré-enregistré : 5.0 bps. 2887 séances. Candidat = sleeve dollar-neutre composite redimensionné par sa vol (#350). Référence = Buy&Hold équipondéré (univers PIT, #349).

**Vérification de régression (doit reproduire le #350 déjà committé)** : Sharpe ann. reconstruit = +0.61 (#350 committé : +0.61), t-stat reconstruit = +2.08 (#350 committé : +2.08).

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.61 | +0.40 | +175.3% | +104.8% | OUI |
| 15.0 | +0.53 | +0.40 | +135.8% | +104.5% | OUI |
| 25.0 | +0.45 | +0.40 | +102.0% | +104.3% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD candidat vs référence sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 62 | -4.5% | -32.8% | OUI |
| Resserrement 2022 | 251 | -8.4% | -34.5% | OUI |

**OK — MDD jamais pire que la référence sur les fenêtres couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe candidat | Sharpe référence | Bat référence |
|---|---|---|---|---|
| 1 | 721 | +0.88 | +0.68 | OUI |
| 2 | 716 | +0.39 | +0.46 | non |
| 3 | 716 | +0.10 | +0.21 | non |
| 4 | 719 | +1.02 | +0.47 | OUI |

**ÉCHEC — bat la référence sur 2/4 folds (majorité NON atteinte).**

## d. SPA à 1 candidat contre la référence

p-value SPA : 0.4136
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 356 (taille du backlog), Var(Sharpe essais) estimée sur 111 Sharpe extraits du backlog = 0.000585 (échelle journalière).
DSR = 0.0406
**ÉCHEC — DSR ≥ 0.95 : NON.**

## Verdict global : 1/5

**PAS de PASS RENFORCÉ (1/5).**
