# Résultat — Low-Vol Tilt + overlay levé proximité plus haut 52-semaines indice (pré-enregistré, combinaison #15+#37)

Référence = portefeuille Low-Vol 1.0x (cycle #15), PAS Buy&Hold. 1336 séances testables (2021-03-31 → 2026-07-27). Overlay actif 61.5% du temps (indice NDX-100 ≥ 95% de son plus haut 252j).

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Low-Vol 1.0x (référence, cycle #15) | +0.54 | +40.2% | -18.9% |
| **Low-Vol + overlay 52w-high indice x2.0** | **+0.95** | **+137.5%** | -19.9% |

1. Sharpe overlay > référence : OUI
2. Rendement overlay > référence : OUI

**PASS — critère renforcé atteint.**

*(Résultat d'origine ci-dessus, conservé en traçabilité — voir nuance dans la correction ci-dessous.)*

## Correction 01/08/2026 — exécution causale

Voir `results/nonml_same_bar_execution_audit.md`. `vol.rolling(60).std()` inclut par défaut pandas le rendement du jour t dans sa fenêtre (même famille de défaut que #38/#14, hérité de la construction low-vol du #15) : les poids qui en découlent étaient appliqués à `R[t]` déjà réalisé. Correctif mécanique : `weights_base` et `weights_lev` sont décalés d'un jour (`causal=True`, décider à la clôture de t-1, détenir pendant t) avant le calcul du PnL. Aucun seuil, aucune fenêtre, aucun paramètre modifié.

Même univers, mêmes paramètres (VOL_WINDOW=60, REBAL_EVERY=21, tercile 1/3, CAP=2.0x, seuil 95%/252j, coûts 5 bps) :

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Low-Vol 1.0x (référence, cycle #15, causal) | +0.509 | +37.1% | -19.0% |
| **Low-Vol + overlay 52w-high indice x2.0 (causal)** | **+0.513** | **+52.8%** | -21.6% |

1. Sharpe overlay > référence : OUI (+0.513 vs +0.509, écart resserré)
2. Rendement overlay > référence : OUI (+52.8% vs +37.1%)

**PASS confirmé — critère renforcé (Sharpe ET rendement) toujours atteint après correction.** L'écart se resserre nettement par rapport au chiffrage d'origine (Sharpe +0.54→+0.95 devient +0.509→+0.513 ; rendement +40.2%→+137.5% devient +37.1%→+52.8%), l'essentiel de l'edge apparent venait bien de la fuite d'exécution, mais un edge résiduel — plus modeste — survit à la correction causale sur cette référence.
