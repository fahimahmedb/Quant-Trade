# Résultat — Momentum 52-semaines (pré-enregistré, exécuté une fois, règle renforcée)

Univers : 99 tickers NDX-100, 1144 séances testables (2022-01-03 → 2026-07-27), rebalancement tous les 21j, tercile supérieur (33 titres) par ratio prix/plus-haut-52sem.

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold équipondéré (univers) | +0.55 | +56.0% | -33.8% |
| **Leaders 52w-high (tercile sup.)** | **+0.78** | **+81.6%** | -25.7% |

1. Sharpe leaders > Buy&Hold : OUI
2. Rendement total leaders > Buy&Hold : OUI

**PASS — critère renforcé (Sharpe ET rendement) atteint.**

*(Résultat d'origine ci-dessus, conservé en traçabilité — invalidé par la correction ci-dessous.)*

## Correction 01/08/2026 — exécution causale

Voir `results/nonml_same_bar_execution_audit.md` pour la méthodologie complète (mesure d'origine sur les cycles #38/#14). Le signal `close(t)/max252(t)` inclut le rendement du jour `t` lui-même, et les poids qui en découlaient étaient appliqués au rendement `R[t]` déjà réalisé — fuite d'exécution « même barre ». Correctif mécanique appliqué : `weights_leaders` et `weights_bh` sont désormais décalés d'un jour (`causal=True`, décider à la clôture de t-1, détenir pendant t) avant le calcul du PnL. Aucun seuil, aucune fenêtre, aucun paramètre n'a été modifié — seule la convention d'exécution change.

Même univers, mêmes paramètres (LOOKBACK=252, REBAL_EVERY=21, tercile 1/3, coûts 5 bps) :

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold équipondéré (univers) | +0.55 | +56.0% | -33.9% |
| **Leaders 52w-high (tercile sup., causal)** | **+0.59** | **+53.5%** | -27.6% |

1. Sharpe leaders > Buy&Hold : OUI
2. Rendement total leaders > Buy&Hold : **non**

**FAIL — critère renforcé (Sharpe ET rendement) NON atteint.** Le Sharpe reste marginalement supérieur (+0.59 vs +0.55) mais le rendement total causal (+53.5%) est désormais inférieur à la référence Buy&Hold (+56.0%) : le critère renforcé exige les deux. Le verdict PASS d'origine reposait sur une exécution qui encaissait par avance une partie du rendement ayant servi à sélectionner le tercile supérieur.
