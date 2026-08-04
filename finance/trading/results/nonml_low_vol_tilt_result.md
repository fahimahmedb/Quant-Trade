# Résultat — Low-Volatility Tilt (pré-enregistré, règle renforcée)

Univers : 99 tickers NDX-100, 1336 séances testables (2021-03-31 → 2026-07-27), vol réalisée 60j, rebalancement 21j, tercile INFÉRIEUR de vol (33 titres).

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold équipondéré (univers) | +0.65 | +86.1% | -35.2% |
| **Low-Vol (tercile inf.)** | **+0.54** | **+40.2%** | -18.9% |

1. Sharpe low-vol > Buy&Hold : non
2. Rendement total low-vol > Buy&Hold : non

**FAIL — critère renforcé (Sharpe ET rendement) NON atteint.**

*(Résultat d'origine ci-dessus, reconstruit depuis la citation du backlog — voir confirmation identique ci-dessous.)*

## Correction 01/08/2026 — exécution causale

Voir `results/nonml_same_bar_execution_audit.md`. `vol.rolling(60).std()` inclut par défaut pandas le rendement du jour t dans sa fenêtre (même famille de défaut que #38/#14) : les poids qui en découlent étaient appliqués à `R[t]` déjà réalisé. Ce cycle était déjà un FAIL avant correction — pas de risque de fausse confiance — mais il est ré-exécuté ici par souci d'exhaustivité (même famille que le #39, qui hérite de cette même construction). Correctif mécanique : `weights_lowvol` et `weights_bh` sont décalés d'un jour (`causal=True`) avant le calcul du PnL. Aucun seuil, aucune fenêtre, aucun paramètre modifié.

Même univers, mêmes paramètres (VOL_WINDOW=60, REBAL_EVERY=21, tercile 1/3, coûts 5 bps) :

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold équipondéré (univers, causal) | +0.64 | +83.7% | -35.2% |
| **Low-Vol (tercile inf., causal)** | **+0.51** | **+37.1%** | -19.0% |

1. Sharpe low-vol > Buy&Hold : non
2. Rendement total low-vol > Buy&Hold : non

**FAIL confirmé — critère renforcé (Sharpe ET rendement) toujours NON atteint après correction.** Le verdict ne change pas : la correction déplace légèrement les deux jambes (Sharpe low-vol +0.54→+0.51, Buy&Hold +0.65→+0.64) sans jamais rapprocher le low-vol de sa référence. Le sens du biais de la fuite n'était de toute façon pas garanti favorable sur un FAIL (cf. note du backlog) — c'est confirmé ici : la correction ne change rien à la conclusion, seulement les décimales.
