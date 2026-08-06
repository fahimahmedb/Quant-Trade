# Batterie de validation renforcée — leaders_vol_targeting_20_overlay (adaptée au format portefeuille)

Coût pré-enregistré : 5.0 bps. 1124 séances. Candidat = Leaders 52-semaines + vol-targeting continu 20% (#48). Référence = Leaders seul (#4), PAS Buy&Hold.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | PASS |
|---|---|---|---|---|---|
| 5.0 | +0.74 | +0.72 | +83.7% | +69.1% | OUI |
| 15.0 | +0.70 | +0.70 | +75.8% | +66.3% | OUI |
| 25.0 | +0.65 | +0.68 | +68.2% | +63.6% | non |

**ÉCHEC — tient à 5x le coût nominal : NON.**

## b. Stress de crise (MDD candidat vs référence sur fenêtres historiques connues)

| Fenêtre | Séances dispo | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 0 | -- | -- | hors couverture (<20 séances) |
| Resserrement 2022 | 231 | -22.9% | -22.3% | OUI |

**OK — MDD jamais pire que la référence sur les fenêtres couvertes : oui.**

## c. Stabilité temporelle (folds non chevauchants + embargo 5j)

| Fold | Séances | Sharpe candidat | Sharpe référence | Bat référence |
|---|---|---|---|---|
| 1 | 281 | -0.82 | -0.66 | non |
| 2 | 276 | +1.34 | +1.45 | non |
| 3 | 276 | +0.50 | +0.50 | OUI |
| 4 | 276 | +1.97 | +1.77 | OUI |

**ÉCHEC — bat la référence sur 2/4 folds (majorité NON atteinte).**

## d. SPA à 1 candidat contre la référence

p-value SPA : 0.1876
**ÉCHEC — significatif à 5% : NON.**

## e. DSR avec n_trials = taille totale du backlog (jamais 1)

n_trials = 321 (taille du backlog après le #48), Var(Sharpe essais) estimée sur 111 Sharpe extraits du backlog = 0.000585 (échelle journalière).
DSR = 0.2151
**ÉCHEC — DSR ≥ 0.95 : NON.**

## Verdict global : 1/5

**PAS de PASS RENFORCÉ (1/5).**
