# Batterie de validation renforcée (Règle 9) — leaders_index52w_high_overlay (cycle #38) — univers point-in-time 2015-2026 (cycle #163)

Candidat : Leaders + overlay 52w-high indice ×2.0. Référence : portefeuille Leaders 1.0x (cycle #4), **PAS Buy&Hold** — même convention que le PREREG original du #38. Coût pré-enregistré 5 bps. 2906 séances (2015-01-05 → 2026-07-27). Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ.

**Univers POINT-IN-TIME (cycle #163)** — correction du défaut méthodologique qui affectait les cycles #161 ET #162. À chaque date de rebalancement, seuls les titres **réellement membres du NDX-100 ce jour-là** sont investissables (composition historique issue de `nasdaq-100-ticker-history` v2026.7.0, licence MIT, vendorée dans `data/ndx100_history/`). Les cycles précédents appliquaient rétroactivement la liste des membres **de 2026**, qui ne couvre que 42 % des vrais membres de l'indice en 2015 et 68 % en 2022 (mesuré dans `results/nonml_ndx100_universe_census.md`) — les absents étant par construction les titres sortis de l'indice depuis, donc en moyenne des sous-performants. Panneau de prix : 178 des 214 tickers ayant appartenu à l'indice entre 2015 et 2026 (36 séries de titres retirés de la cote ne sont plus exposées par la source — biais résiduel quantifié ci-dessous). **Aucun paramètre du #38 ne change** (TERCILE 1/3, LOOKBACK 252, REBAL_EVERY 21, CAP 2.0, seuil indice 95 %, coût 5 bps) ; seule la définition de l'univers investissable est corrigée, comme pré-enregistré dans `PREREG_leaders_index52w_high_overlay_pit_universe.md`.

## Biais résiduel de l'univers point-in-time (mesuré, non estimé)

À chaque date de rebalancement : nombre de membres RÉELS du NDX-100 (composition point-in-time) et nombre d'entre eux réellement investissables (prix disponibles ET 252 séances d'historique). Le complément est le biais restant — titres retirés de la cote dont la série de prix n'est plus exposée par la source, ou titres entrés à l'indice avant d'avoir un an de cotation.

| Année | Rebal. | Membres réels (moy.) | Investissables (moy.) | Couverture moy. | Couverture min. |
|---|---|---|---|---|---|
| 2015 | 12 | 106 | 73.7 | 69.5% | 67.3% |
| 2016 | 12 | 105 | 77.8 | 74.3% | 71.0% |
| 2017 | 12 | 104 | 81.8 | 78.7% | 77.9% |
| 2018 | 12 | 103 | 84.2 | 81.7% | 80.6% |
| 2019 | 12 | 103 | 88.2 | 85.6% | 85.4% |
| 2020 | 12 | 103 | 91.2 | 88.5% | 86.4% |
| 2021 | 12 | 102 | 92.8 | 90.9% | 90.2% |
| 2022 | 12 | 102 | 95.3 | 93.5% | 92.2% |
| 2023 | 12 | 101 | 96.8 | 95.8% | 95.0% |
| 2024 | 12 | 101 | 98.9 | 97.9% | 97.0% |
| 2025 | 12 | 101 | 100.4 | 99.4% | 99.0% |
| 2026 | 7 | 101 | 101.0 | 100.0% | 100.0% |

**Couverture moyenne sur toute la période : 87.6% (minimum 67.3%).** À comparer aux 42 % (2015) à 68 % (2022) de couverture des cycles #161/#162, mesurés dans `results/nonml_ndx100_universe_census.md` — le biais n'est pas totalement nul ici, mais il est réduit d'un ordre de grandeur ET, surtout, il est désormais MESURÉ.

Nature du résidu, à ne pas sous-estimer : les titres encore manquants sont exclusivement des sociétés **retirées de la cote** (faillite, rachat, passage en non coté), donc en moyenne des sous-performants — le biais résiduel reste orienté dans le même sens (à la hausse), simplement beaucoup plus petit.

## a. Stress de coûts (1x, 3x, 5x)

| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | OK |
|---|---|---|---|---|---|
| 5 | +0.47 | +0.54 | +201.3% | +169.1% | non |
| 15 | +0.43 | +0.52 | +159.5% | +156.9% | non |
| 25 | +0.39 | +0.50 | +123.6% | +145.3% | non |

**ÉCHEC — tient jusqu'à 5x le coût nominal : NON.**

## b. Stress de crise (MDD candidat vs référence)

| Fenêtre | Séances | MDD candidat | MDD référence | Pas pire que référence |
|---|---|---|---|---|
| Dot-com crash | 0 | -- | -- | hors couverture (<20 séances) |
| Crise financière 2008 | 0 | -- | -- | hors couverture (<20 séances) |
| Krach COVID | 62 | -33.7% | -29.3% | non |
| Resserrement 2022 | 251 | -30.9% | -27.5% | non |

**ÉCHEC — 2/4 fenêtres de crise couvertes par l'historique de prix titre-par-titre disponible.**

## c. Stabilité temporelle (4 folds non chevauchants + embargo 5j)

| Fold | Séances | Période | Sharpe candidat | Sharpe référence | Candidat > référence |
|---|---|---|---|---|---|
| 1 | 726 | 01/2015→11/2017 | +0.83 | +0.88 | non |
| 2 | 721 | 11/2017→10/2020 | +0.41 | +0.52 | non |
| 3 | 721 | 10/2020→08/2023 | +0.08 | +0.04 | OUI |
| 4 | 723 | 09/2023→07/2026 | +0.55 | +0.74 | non |

**ÉCHEC — 1/4 folds battus (majorité requise).**

## d. SPA de Hansen à 1 candidat contre la référence

t_SPA = 0.984, **p = 0.1540** (bootstrap stationnaire, H0 : la référence Leaders 1.0x n'est battue par aucun candidat).

**ÉCHEC — seuil p < 0,05.**

## e. DSR avec n_trials = taille du backlog AVANT ce cycle (jamais 1)

n_trials=252 (backlog avant ce cycle), var(SR essais) extraite sur 88 Sharpe du backlog = 1.6566e-01 (annualisée) → 6.5738e-04 (journalière). Sharpe quotidien +0.0299, seuil SR₀ = 0.0728, z = -2.29, **DSR = 0.011**.

**ÉCHEC — seuil DSR > 0,95.**

## Verdict de la batterie

| Contrôle | Statut |
|---|---|
| a. stress de coûts ×3/×5 | ÉCHEC |
| b. stress de crise | ÉCHEC |
| c. stabilité temporelle | ÉCHEC |
| d. SPA 1 candidat | ÉCHEC |
| e. DSR (n_trials=252) | ÉCHEC |

### PASS niveau 1 SEULEMENT — batterie renforcée ÉCHOUÉE

Aucune notification Telegram n'est émise (réservée au PASS RENFORCÉ complet).
