# Résultat — Winners momentum court terme + overlay levé proximité plus haut 52-semaines indice (pré-enregistré, combinaison #14+#37)

Référence = portefeuille Winners 1.0x (cycle #14), PAS Buy&Hold. 1391 séances testables (2021-01-11 → 2026-07-27). Overlay actif 61.5% du temps (indice NDX-100 ≥ 95% de son plus haut 252j).

**Prudence forte héritée du #14** : le portefeuille Winners affiche un edge extrême potentiellement propre au bull market IA/semiconducteurs 2021-2026, généralisabilité non garantie.

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Winners 1.0x (référence, cycle #14) | +2.35 | +1813.4% | -22.4% |
| **Winners + overlay 52w-high indice x2.0** | **+3.00** | **+29636.2%** | -26.9% |

1. Sharpe overlay > référence : OUI
2. Rendement overlay > référence : OUI

**PASS — critère renforcé atteint.**

*(Résultat d'origine ci-dessus, conservé en traçabilité — invalidé par la correction ci-dessous, cf. le #14 lui-même déjà reclassé FAIL.)*

## Correction 01/08/2026 — exécution causale

Voir `results/nonml_same_bar_execution_audit.md`. Le signal `close(i)/close(i-SIGNAL_WINDOW)-1` inclut le rendement du jour i lui-même (même défaut confirmé sur le #14 dont ce script hérite la construction) : les poids qui en découlaient étaient appliqués à `R[i]` déjà réalisé. Correctif mécanique : `weights_base` et `weights_lev` sont décalés d'un jour (`causal=True`, décider à la clôture de t-1, détenir pendant t) avant le calcul du PnL. Aucun seuil, aucune fenêtre, aucun paramètre modifié.

Même univers, mêmes paramètres (SIGNAL_WINDOW=5, REBAL_EVERY=5, tercile 1/3, CAP=2.0x, seuil 95%/252j, coûts 5 bps) :

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Winners 1.0x (référence, cycle #14, causal) | +0.67 | +107.2% | -40.6% |
| **Winners + overlay 52w-high indice x2.0 (causal)** | **+0.71** | **+186.1%** | -46.2% |

1. Sharpe overlay > référence : OUI
2. Rendement overlay > référence : OUI

**PASS confirmé — critère renforcé (Sharpe ET rendement) toujours atteint après correction.** La référence causale (+0.67, +107.2%) reproduit exactement le chiffrage indépendant du #14 sur l'univers d'origine 2021-2026 (`results/nonml_same_bar_execution_audit.md` §B.2), ce qui valide la cohérence du correctif. Comme pour le #14 lui-même, ce PASS marginal repose sur l'univers d'origine (2021-2026) et non sur l'univers point-in-time 2015-2026 retenu comme référence d'évaluation depuis #163/#164 — le #14 est FAIL sur ce dernier, et ce dérivé en hériterait vraisemblablement (non ré-exécuté sur l'univers PIT ici, hors périmètre de cette correction mécanique). L'ampleur de l'edge chute radicalement par rapport au chiffrage d'origine (Sharpe +2,35→+3,00 devenu +0,67→+0,71 ; rendement +1813%→+29636% devenu +107%→+186%) : l'essentiel de la performance spectaculaire d'origine était la fuite d'exécution.
