# Batterie de validation renforcée (Règle 9) — leaders_index52w_high_overlay (cycle #38)

Candidat : Leaders + overlay 52w-high indice ×2.0. Référence : portefeuille Leaders 1.0x (cycle #4), **PAS Buy&Hold** — même convention que le PREREG original du #38. Coût pré-enregistré 5 bps. 1144 séances (2022-01-03 → 2026-07-27). Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | OK |
|---|---|---|---|---|---|
| 5 | +1.50 | +0.78 | +508.3% | +81.6% | OUI |
| 15 | +1.46 | +0.76 | +473.9% | +78.5% | OUI |
| 25 | +1.41 | +0.75 | +441.5% | +75.6% | OUI |

**OK — tient jusqu'à 5x le coût nominal : oui.**

## b. Stress de crise (MDD candidat vs référence)

| Fenêtre | Séances | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 0 | -- | -- | hors couverture (<20 séances) |
| Resserrement 2022 | 251 | -25.9% | -25.7% | OUI |

**OK — 1/4 fenêtres de crise couvertes par l'historique de prix titre-par-titre disponible (2022-2026, même limite que #111/#112/#134 : dot-com/2008/COVID hors couverture) ; jugé sur la seule fenêtre disponible (resserrement 2022), pas une confirmation à 4 fenêtres indépendantes.**

## c. Stabilité temporelle (4 folds non chevauchants + embargo 5j)

| Fold | Séances | Période | Sharpe candidat | Sharpe référence | Candidat > référence |
|---|---|---|---|---|---|
| 1 | 286 | 01/2022→02/2023 | -0.82 | -0.86 | OUI |
| 2 | 281 | 03/2023→04/2024 | +2.32 | +1.84 | OUI |
| 3 | 281 | 04/2024→06/2025 | +1.38 | +0.73 | OUI |
| 4 | 281 | 06/2025→07/2026 | +2.64 | +1.95 | OUI |

**OK — 4/4 folds battus (majorité requise).**

## d. SPA de Hansen à 1 candidat contre la référence

t_SPA = 4.515, **p = 0.0000** (bootstrap stationnaire, H0 : la référence Leaders 1.0x n'est battue par aucun candidat).

**OK — seuil p < 0,05.**

## e. DSR avec n_trials = taille du backlog AVANT ce cycle (jamais 1)

n_trials=160 (backlog avant ce cycle), var(SR essais) extraite sur 68 Sharpe du backlog = 2.0173e-01 (annualisée) → 8.0052e-04 (journalière). Sharpe quotidien +0.0944, seuil SR₀ = 0.0762, z = +0.61, **DSR = 0.730**.

**ÉCHEC — seuil DSR > 0,95.**

## Verdict de la batterie

| Contrôle | Statut |
|---|---|
| a. stress de coûts ×3/×5 | OK |
| b. stress de crise | OK |
| c. stabilité temporelle | OK |
| d. SPA 1 candidat | OK |
| e. DSR (n_trials=160) | ÉCHEC |

### PASS niveau 1 SEULEMENT — batterie renforcée ÉCHOUÉE

Aucune notification Telegram n'est émise (réservée au PASS RENFORCÉ complet).
