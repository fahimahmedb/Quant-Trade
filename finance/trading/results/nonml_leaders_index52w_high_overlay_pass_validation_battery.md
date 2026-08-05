# Batterie de validation renforcée (Règle 9) — leaders_index52w_high_overlay (cycle #38)

Candidat : Leaders + overlay 52w-high indice ×2.0. Référence : portefeuille Leaders 1.0x (cycle #4), **PAS Buy&Hold** — même convention que le PREREG original du #38. Coût pré-enregistré 5 bps. 1143 séances (2022-01-04 → 2026-07-27). Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | OK |
|---|---|---|---|---|---|
| 5 | +0.65 | +0.59 | +96.1% | +53.5% | OUI |
| 15 | +0.61 | +0.57 | +85.0% | +50.9% | OUI |
| 25 | +0.56 | +0.55 | +74.5% | +48.4% | OUI |

**OK — tient jusqu'à 5x le coût nominal : oui.**

## b. Stress de crise (MDD candidat vs référence)

| Fenêtre | Séances | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 0 | -- | -- | hors couverture (<20 séances) |
| Resserrement 2022 | 250 | -30.7% | -27.6% | non |

**ÉCHEC — 1/4 fenêtres de crise couvertes par l'historique de prix titre-par-titre disponible.**

## c. Stabilité temporelle (4 folds non chevauchants + embargo 5j)

| Fold | Séances | Période | Sharpe candidat | Sharpe référence | Candidat > référence |
|---|---|---|---|---|---|
| 1 | 285 | 01/2022→02/2023 | -1.16 | -1.01 | non |
| 2 | 280 | 03/2023→04/2024 | +1.53 | +1.61 | non |
| 3 | 280 | 04/2024→06/2025 | +0.61 | +0.55 | OUI |
| 4 | 283 | 06/2025→07/2026 | +1.38 | +1.72 | non |

**ÉCHEC — 1/4 folds battus (majorité requise).**

## d. SPA de Hansen à 1 candidat contre la référence

t_SPA = 1.275, **p = 0.1008** (bootstrap stationnaire, H0 : la référence Leaders 1.0x n'est battue par aucun candidat).

**ÉCHEC — seuil p < 0,05.**

## e. DSR avec n_trials = taille du backlog AVANT ce cycle (jamais 1)

n_trials=266 (backlog avant ce cycle), var(SR essais) extraite sur 101 Sharpe du backlog = 1.5414e-01 (annualisée) → 6.1165e-04 (journalière). Sharpe quotidien +0.0410, seuil SR₀ = 0.0707, z = -0.99, **DSR = 0.160**.

**ÉCHEC — seuil DSR > 0,95.**

## Verdict de la batterie

| Contrôle | Statut |
|---|---|
| a. stress de coûts ×3/×5 | OK |
| b. stress de crise | ÉCHEC |
| c. stabilité temporelle | ÉCHEC |
| d. SPA 1 candidat | ÉCHEC |
| e. DSR (n_trials=266) | ÉCHEC |

### PASS niveau 1 SEULEMENT — batterie renforcée ÉCHOUÉE

Aucune notification Telegram n'est émise (réservée au PASS RENFORCÉ complet).
