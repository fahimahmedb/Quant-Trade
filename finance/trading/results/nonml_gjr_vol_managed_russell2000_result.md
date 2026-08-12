# Résultat — Portefeuille volatility-managed GJR-t (Moreira & Muir 2017) -- Russell 2000 (cycle #166, généralisation du #165)

Spécification figée dans `PREREG_gjr_vol_managed_crossmarket.md` (committé avant ce script), paramètres IDENTIQUES au #165 (NDX), aucun retuning par marché. Q1 (GJR-t validé au SPA sur ce marché) vérifiée dans `results/etape_C_russell2000.md`.

`position(t) = clip(20% / vol_prévue_GJR-t(t), 0.0, 2.0x)` — prévision walk-forward 1 pas, fenêtre initiale 750 obs expansive, ré-estimation tous les 21 j, coûts 5 bps sur |Δposition|.

## 1. Échantillon

- Marché : **Russell 2000** (`data/russell2000_daily.txt`), 9782 séances, 9781 rendements (11/09/1987 → 13/07/2026).
- Fenêtre OOS évaluée (candidat ET Buy & Hold) : **9031 séances**, 29/08/1990 → 13/07/2026.
- Nombre de ré-estimations GJR-t : 431.

## 2. Comportement de l'exposition (descriptif, hors critère)

- Vol. annualisée **prévue** sur l'OOS : min 6.5 % / médiane 16.7 % / max 141.4 %.
- Exposition moyenne : **1.25x** (médiane 1.19x, min 0.14x, max 2.00x).
- Part du temps au-dessus de 1.0x : **65.8 %** ; au plafond 2.0x : 13.8 % ; sous 0,5x : 4.4 %.
- Turnover quotidien moyen |Δposition| : 0.0729 (coût total cumulé ≈ 32.9 points de rendement log).

## 3. Résultat sur la fenêtre OOS commune (net de coûts)

| Stratégie | Sharpe ann. | Rendement total | Rendement ann. | MDD | Calmar | Sortino |
|---|---|---|---|---|---|---|
| Buy & Hold | +0.39 | +2014.8% | +8.9% | -59.9% | 0.093 | +0.50 |
| **Volatility-managed GJR-t** | **+0.44** | **+2276.6%** | +9.2% | -48.9% | 0.132 | +0.62 |

## 4. Verdict contre le critère de succès RENFORCÉ pré-enregistré

- Jambe Sharpe : +0.4353 vs +0.3888 → **OUI**
- Jambe rendement total : +2276.6% vs +2014.8% → **OUI**

**PASS — les deux jambes sont atteintes (critère renforcé du 28/07/2026 : Sharpe ET rendement > Buy & Hold).**

## 5. Rappel Règle 10 (hypothèse de rémunération déclarée au PREREG)

La fraction hors-marché `(1 - position)` est rémunérée à **0 %** et la fraction empruntée (position > 1.0x) est financée à **0 %**, identique au #165 et aux cycles comparables du backlog.
