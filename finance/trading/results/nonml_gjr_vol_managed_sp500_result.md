# Résultat — Portefeuille volatility-managed GJR-t (Moreira & Muir 2017) -- S&P 500 (cycle #166, généralisation du #165)

Spécification figée dans `PREREG_gjr_vol_managed_crossmarket.md` (committé avant ce script), paramètres IDENTIQUES au #165 (NDX), aucun retuning par marché. Q1 (GJR-t validé au SPA sur ce marché) vérifiée dans `results/etape_C_sp500.md`.

`position(t) = clip(20% / vol_prévue_GJR-t(t), 0.0, 2.0x)` — prévision walk-forward 1 pas, fenêtre initiale 750 obs expansive, ré-estimation tous les 21 j, coûts 5 bps sur |Δposition|.

## 1. Échantillon

- Marché : **S&P 500** (`data/sp500_daily.txt`), 14252 séances, 14251 rendements (05/01/1970 → 13/07/2026).
- Fenêtre OOS évaluée (candidat ET Buy & Hold) : **13501 séances**, 19/12/1972 → 13/07/2026.
- Nombre de ré-estimations GJR-t : 643.

## 2. Comportement de l'exposition (descriptif, hors critère)

- Vol. annualisée **prévue** sur l'OOS : min 6.7 % / médiane 13.2 % / max 105.7 %.
- Exposition moyenne : **1.47x** (médiane 1.52x, min 0.19x, max 2.00x).
- Part du temps au-dessus de 1.0x : **83.9 %** ; au plafond 2.0x : 16.0 % ; sous 0,5x : 1.7 %.
- Turnover quotidien moyen |Δposition| : 0.0361 (coût total cumulé ≈ 24.4 points de rendement log).

## 3. Résultat sur la fenêtre OOS commune (net de coûts)

| Stratégie | Sharpe ann. | Rendement total | Rendement ann. | MDD | Calmar | Sortino |
|---|---|---|---|---|---|---|
| Buy & Hold | +0.44 | +6325.6% | +8.1% | -56.8% | 0.093 | +0.56 |
| **Volatility-managed GJR-t** | **+0.49** | **+19088.3%** | +10.3% | -60.0% | 0.107 | +0.69 |

## 4. Verdict contre le critère de succès RENFORCÉ pré-enregistré

- Jambe Sharpe : +0.4917 vs +0.4446 → **OUI**
- Jambe rendement total : +19088.3% vs +6325.6% → **OUI**

**PASS — les deux jambes sont atteintes (critère renforcé du 28/07/2026 : Sharpe ET rendement > Buy & Hold).**

## 5. Rappel Règle 10 (hypothèse de rémunération déclarée au PREREG)

La fraction hors-marché `(1 - position)` est rémunérée à **0 %** et la fraction empruntée (position > 1.0x) est financée à **0 %**, identique au #165 et aux cycles comparables du backlog.
