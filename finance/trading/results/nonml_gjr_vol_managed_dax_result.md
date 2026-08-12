# Résultat — Portefeuille volatility-managed GJR-t (Moreira & Muir 2017) -- DAX (cycle #166, généralisation du #165)

Spécification figée dans `PREREG_gjr_vol_managed_crossmarket.md` (committé avant ce script), paramètres IDENTIQUES au #165 (NDX), aucun retuning par marché. Q1 (GJR-t validé au SPA sur ce marché) vérifiée dans `results/etape_C_dax.md`.

`position(t) = clip(20% / vol_prévue_GJR-t(t), 0.0, 2.0x)` — prévision walk-forward 1 pas, fenêtre initiale 750 obs expansive, ré-estimation tous les 21 j, coûts 5 bps sur |Δposition|.

## 1. Échantillon

- Marché : **DAX** (`data/dax_daily.txt`), 6777 séances, 6776 rendements (02/11/1999 → 10/07/2026).
- Fenêtre OOS évaluée (candidat ET Buy & Hold) : **6026 séances**, 15/10/2002 → 10/07/2026.
- Nombre de ré-estimations GJR-t : 287.

## 2. Comportement de l'exposition (descriptif, hors critère)

- Vol. annualisée **prévue** sur l'OOS : min 8.2 % / médiane 16.9 % / max 100.1 %.
- Exposition moyenne : **1.18x** (médiane 1.18x, min 0.20x, max 2.00x).
- Part du temps au-dessus de 1.0x : **65.9 %** ; au plafond 2.0x : 2.9 % ; sous 0,5x : 4.9 %.
- Turnover quotidien moyen |Δposition| : 0.0503 (coût total cumulé ≈ 15.2 points de rendement log).

## 3. Résultat sur la fenêtre OOS commune (net de coûts)

| Stratégie | Sharpe ann. | Rendement total | Rendement ann. | MDD | Calmar | Sortino |
|---|---|---|---|---|---|---|
| Buy & Hold | +0.43 | +779.1% | +9.5% | -54.8% | 0.115 | +0.55 |
| **Volatility-managed GJR-t** | **+0.40** | **+559.7%** | +8.2% | -47.7% | 0.122 | +0.56 |

## 4. Verdict contre le critère de succès RENFORCÉ pré-enregistré

- Jambe Sharpe : +0.4045 vs +0.4270 → **NON**
- Jambe rendement total : +559.7% vs +779.1% → **NON**

**FAIL — les deux jambes sont NON toutes atteintes (critère renforcé du 28/07/2026 : Sharpe ET rendement > Buy & Hold).**

## 5. Rappel Règle 10 (hypothèse de rémunération déclarée au PREREG)

La fraction hors-marché `(1 - position)` est rémunérée à **0 %** et la fraction empruntée (position > 1.0x) est financée à **0 %**, identique au #165 et aux cycles comparables du backlog.
