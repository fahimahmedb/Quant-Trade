# ML-4 — Batterie de validation renforcée — S&P 500

Candidat `LogitL2Pooled`, coût pré-enregistré 5 bps, 13501 séances OOS (18/12/1972 → 10/07/2026). Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ **sur ce marché**.

Batterie exécutée **marché par marché** : `spa_test` compare un candidat à UN SEUL benchmark partagé, aucun SPA joint multi-marchés n'est tenté (PREREG §6, limite mécanique des cycles non-ML #150/#159).

## a. Stress de coûts (×1, ×3, ×5)

| Coût (bps) | Sharpe LogitL2Pooled | Sharpe BH | Rdt ann. LogitL2Pooled | Rdt ann. BH | Calmar LogitL2Pooled | Calmar BH | Critère |
|---|---|---|---|---|---|---|---|
| 5 | +0.50 | +0.44 | +9.1 % | +8.1 % | +0.10 | +0.09 | OUI |
| 15 | +0.07 | +0.44 | +1.2 % | +8.1 % | +0.01 | +0.09 | non |
| 25 | -0.36 | +0.44 | -6.2 % | +8.1 % | -0.01 | +0.09 | non |

**ÉCHEC — le critère doit tenir jusqu'à ×5 le coût nominal.**

## b. Stress de crise (MDD LogitL2Pooled vs Buy & Hold)

| Fenêtre | Séances | MDD LogitL2Pooled | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 752 | -34.4 % | -49.1 % | OUI |
| Crise financière 2008 | 378 | -47.9 % | -56.8 % | OUI |
| Krach COVID | 62 | -31.7 % | -33.9 % | OUI |
| Resserrement 2022 | 251 | -28.5 % | -25.4 % | non |

**ÉCHEC.**

## c. Stabilité temporelle (4 folds non chevauchants + embargo 5 j)

| Fold | Séances | Période | Sharpe LogitL2Pooled | Sharpe BH | LogitL2Pooled > BH |
|---|---|---|---|---|---|
| 1 | 3375 | 12/1972→04/1986 | +0.90 | +0.36 | OUI |
| 2 | 3370 | 05/1986→09/1999 | +0.62 | +0.79 | non |
| 3 | 3370 | 09/1999→02/2013 | +0.13 | +0.04 | OUI |
| 4 | 3371 | 02/2013→07/2026 | +0.53 | +0.70 | non |

**ÉCHEC — 2/4 folds battus (majorité requise).**

## d. SPA de Hansen à 1 candidat contre Buy & Hold

t_SPA = 0.441, **p = 0.3186** (bootstrap stationnaire, H0 : Buy & Hold n'est battu par aucun candidat).

**ÉCHEC — seuil p < 0,05.**

## e. DSR avec n_trials = 408 (total cumulé campagne ML, jamais 1)

Sharpe quotidien +0.0315, σ²(SR essais) = 5.0605e-04, seuil SR₀ = 0.0673, z = -4.19, **DSR = 0.000**.

**ÉCHEC — seuil DSR > 0,95.**

## Verdict de la batterie (ce marché)

| Contrôle | Statut |
|---|---|
| a. stress de coûts ×3/×5 | ÉCHEC |
| b. stress de crise | ÉCHEC |
| c. stabilité temporelle | ÉCHEC |
| d. SPA 1 candidat | ÉCHEC |
| e. DSR (n_trials=408) | ÉCHEC |

### PASS niveau 1 SEULEMENT — batterie renforcée ÉCHOUÉE (S&P 500)

Aucune notification n'est émise pour ce marché : la règle réserve l'alerte au PASS RENFORCÉ complet (5 contrôles sur 5).
