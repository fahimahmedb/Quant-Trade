# Résultat — Momentum de constance (pré-enregistré, exécuté une fois, règle renforcée)

Univers : 99 tickers NDX-100, 1144 séances testables (2022-01-03 → 2026-07-27), rebalancement tous les 21j, tercile supérieur par fraction de 12 blocs de 21j positifs.

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold équipondéré (univers) | +0.55 | +56.0% | -33.8% |
| **Momentum de constance (tercile sup.)** | **+0.67** | **+81.7%** | -28.2% |

1. Sharpe > Buy&Hold : OUI
2. Rendement total > Buy&Hold : OUI

**PASS — critère renforcé (Sharpe ET rendement) atteint.**

*(Résultat d'origine ci-dessus, conservé en traçabilité — voir nuance dans la correction ci-dessous.)*

## Correction 01/08/2026 — exécution causale

Voir `results/nonml_same_bar_execution_audit.md`. `consistency_at` calcule la fraction de blocs positifs sur les BLOCK_LEN séances précédant ET INCLUANT le jour t (`end_idx = t`) : le premier bloc contient le rendement du jour t lui-même, dont les poids issus de ce signal étaient appliqués à `R[t]` déjà réalisé. Correctif mécanique : `weights_consistency` et `weights_bh` sont décalés d'un jour (`causal=True`, décider à la clôture de t-1, détenir pendant t) avant le calcul du PnL. Aucun seuil, aucune fenêtre, aucun paramètre modifié.

Même univers, mêmes paramètres (BLOCK_LEN=21, N_BLOCKS=12, REBAL_EVERY=21, tercile 1/3, coûts 5 bps) :

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold équipondéré (univers, causal) | +0.55 | +56.0% | -33.9% |
| **Momentum de constance (tercile sup., causal)** | **+0.64** | **+74.8%** | -28.8% |

1. Sharpe > Buy&Hold : OUI
2. Rendement total > Buy&Hold : OUI

**PASS confirmé — critère renforcé (Sharpe ET rendement) toujours atteint après correction.** L'edge se réduit modérément (Sharpe +0.67→+0.64, rendement +81.7%→+74.8%, MDD +28.2%→+28.8%) mais reste net des deux côtés du critère renforcé. Contrairement au #38/#14/#4, ce signal (fraction de blocs positifs sur 12 mois) est beaucoup moins sensible au rendement d'un seul jour parmi les 252 utilisés — la contamination « même barre » ne représente qu'1/21 d'un seul bloc parmi 12, ce qui explique pourquoi le PASS résiste ici alors qu'il s'effondrait pour des signaux plus concentrés sur le très court terme.
