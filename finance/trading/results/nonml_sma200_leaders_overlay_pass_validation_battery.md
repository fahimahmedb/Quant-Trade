# Batterie de validation renforcée — sma200_leaders_overlay (adaptée au format portefeuille)

Coût pré-enregistré : 5.0 bps. 1144 séances. Candidat = Leaders 52-semaines + overlay SMA200 (#33). Référence = Leaders seul (#4), PAS Buy&Hold.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.69 | +0.59 | +116.8% | +53.5% | OUI |
| 15.0 | +0.66 | +0.57 | +108.3% | +50.8% | OUI |
| 25.0 | +0.63 | +0.55 | +100.0% | +48.3% | OUI |

**OK — tient à 5x le coût nominal : oui.**

## b. Stress de crise (MDD candidat vs référence sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 0 | -- | -- | hors couverture (<20 séances) |
| Resserrement 2022 | 251 | -37.4% | -27.6% | non |

**ÉCHEC — MDD jamais pire que la référence sur les fenêtres couvertes : NON.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe candidat | Sharpe référence | Bat référence |
|---|---|---|---|---|
| 1 | 286 | -1.61 | -1.01 | non |
| 2 | 281 | +1.51 | +1.51 | non |
| 3 | 281 | +0.75 | +0.61 | OUI |
| 4 | 281 | +1.65 | +1.74 | non |

**ÉCHEC — bat la référence sur 1/4 folds (majorité NON atteinte).**

## d. SPA à 1 candidat contre la référence

p-value SPA : 0.0538
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 320 (taille du backlog après le #33), Var(Sharpe essais) estimée sur 111 Sharpe extraits du backlog = 0.000585 (échelle journalière).
DSR = 0.1808
**ÉCHEC — DSR ≥ 0.95 : NON.**

## Verdict global : 1/5

**PAS de PASS RENFORCÉ (1/5).**
