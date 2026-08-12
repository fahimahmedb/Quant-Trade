# Batterie de validation renforcée — sma200_leaders_overlay (adaptée au format portefeuille)

Coût pré-enregistré : 5.0 bps. 1144 séances. Candidat = Leaders 52-semaines + overlay SMA200 (#33). Référence = Leaders seul (#4), PAS Buy&Hold.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.88 | +0.84 | +270.7% | +108.0% | OUI |
| 15.0 | +0.86 | +0.82 | +256.1% | +104.5% | OUI |
| 25.0 | +0.83 | +0.80 | +242.0% | +101.0% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD candidat vs référence sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 0 | -- | -- | hors couverture (<20 séances) |
| Resserrement 2022 | 251 | -35.8% | -25.7% | non |

**ÉCHEC — MDD jamais pire que la référence sur les fenêtres couvertes : NON.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe candidat | Sharpe référence | Bat référence |
|---|---|---|---|---|
| 1 | 286 | -1.47 | -0.85 | non |
| 2 | 281 | +1.64 | +1.72 | non |
| 3 | 281 | +0.96 | +0.88 | OUI |
| 4 | 281 | +1.93 | +2.12 | non |

**ÉCHEC — bat la référence sur 1/4 folds (majorité NON atteinte).**

## d. SPA à 1 candidat contre la référence

p-value SPA : 0.0384
**OK — significatif à 5% : oui.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 372 (taille du backlog après le #33), Var(Sharpe essais) estimée sur 112 Sharpe extraits du backlog = 0.000585 (échelle journalière).
DSR = 0.2966
**ÉCHEC — DSR ≥ 0.95 : NON.**

## Verdict global : 2/5

**PAS de PASS RENFORCÉ (2/5).**
