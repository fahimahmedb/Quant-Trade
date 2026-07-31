# ML-4 — Batterie de validation renforcée — DAX

Candidat `LogitL2Pooled`, coût pré-enregistré 5 bps, 6026 séances OOS (14/10/2002 → 09/07/2026). Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ **sur ce marché**.

Batterie exécutée **marché par marché** : `spa_test` compare un candidat à UN SEUL benchmark partagé, aucun SPA joint multi-marchés n'est tenté (PREREG §6, limite mécanique des cycles non-ML #150/#159).

## a. Stress de coûts (×1, ×3, ×5)

| Coût (bps) | Sharpe LogitL2Pooled | Sharpe BH | Rdt ann. LogitL2Pooled | Rdt ann. BH | Calmar LogitL2Pooled | Calmar BH | Critère |
|---|---|---|---|---|---|---|---|
| 5 | +0.43 | +0.43 | +9.6 % | +9.5 % | +0.12 | +0.11 | OUI |
| 15 | +0.29 | +0.43 | +6.4 % | +9.5 % | +0.06 | +0.11 | non |
| 25 | +0.15 | +0.43 | +3.2 % | +9.5 % | +0.03 | +0.11 | non |

**ÉCHEC — le critère doit tenir jusqu'à ×5 le coût nominal.**

## b. Stress de crise (MDD LogitL2Pooled vs Buy & Hold)

| Fenêtre | Séances | MDD LogitL2Pooled | MDD BH | Pas pire que BH |
|---|---|---|---|---|
| Dot-com crash | 53 | -20.4 % | -16.0 % | non |
| Crise financière 2008 | 379 | -52.9 % | -54.6 % | OUI |
| Krach COVID | 62 | -38.8 % | -38.8 % | OUI |
| Resserrement 2022 | 257 | -33.9 % | -26.4 % | non |

**ÉCHEC.**

## c. Stabilité temporelle (4 folds non chevauchants + embargo 5 j)

| Fold | Séances | Période | Sharpe LogitL2Pooled | Sharpe BH | LogitL2Pooled > BH |
|---|---|---|---|---|---|
| 1 | 1506 | 10/2002→09/2008 | +0.19 | +0.61 | non |
| 2 | 1501 | 09/2008→08/2014 | +0.74 | +0.28 | OUI |
| 3 | 1501 | 08/2014→08/2020 | +0.27 | +0.22 | OUI |
| 4 | 1503 | 08/2020→07/2026 | +0.39 | +0.65 | non |

**ÉCHEC — 2/4 folds battus (majorité requise).**

## d. SPA de Hansen à 1 candidat contre Buy & Hold

t_SPA = 0.018, **p = 0.4892** (bootstrap stationnaire, H0 : Buy & Hold n'est battu par aucun candidat).

**ÉCHEC — seuil p < 0,05.**

## e. DSR avec n_trials = 408 (total cumulé campagne ML, jamais 1)

Sharpe quotidien +0.0271, σ²(SR essais) = 5.1621e-04, seuil SR₀ = 0.0680, z = -3.17, **DSR = 0.001**.

**ÉCHEC — seuil DSR > 0,95.**

## Verdict de la batterie (ce marché)

| Contrôle | Statut |
|---|---|
| a. stress de coûts ×3/×5 | ÉCHEC |
| b. stress de crise | ÉCHEC |
| c. stabilité temporelle | ÉCHEC |
| d. SPA 1 candidat | ÉCHEC |
| e. DSR (n_trials=408) | ÉCHEC |

### PASS niveau 1 SEULEMENT — batterie renforcée ÉCHOUÉE (DAX)

Aucune notification n'est émise pour ce marché : la règle réserve l'alerte au PASS RENFORCÉ complet (5 contrôles sur 5).
