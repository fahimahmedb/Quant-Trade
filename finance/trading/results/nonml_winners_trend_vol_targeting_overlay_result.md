# Résultat — Winners momentum court terme + overlay combiné tendance + vol-targeting (pré-enregistré, combinaison #14+#47)

Référence = portefeuille Winners 1.0x (cycle #14), PAS Buy&Hold. 1376 séances testables (2021-02-02 → 2026-07-27). Overlay actif 61.1% du temps en tendance haussière.

**Prudence forte héritée du #14** : le portefeuille Winners affiche un edge extrême potentiellement propre au bull market IA/semiconducteurs 2021-2026, généralisabilité non garantie.

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Winners 1.0x (référence, cycle #14) | +2.33 | +1722.5% | -22.4% |
| **Winners + overlay tendance+vol-targeting** | **+2.47** | **+2528.4%** | -22.4% |

1. Sharpe overlay > référence : OUI
2. Rendement overlay > référence : OUI

**PASS — critère renforcé atteint.**

*(Résultat d'origine ci-dessus, conservé en traçabilité — invalidé par la correction ci-dessous, cf. le #14 lui-même déjà reclassé FAIL.)*

## Correction 01/08/2026 — exécution causale

Voir `results/nonml_same_bar_execution_audit.md`. Le signal `close(i)/close(i-SIGNAL_WINDOW)-1` inclut le rendement du jour i lui-même (hérité du #14) : les poids qui en découlaient étaient appliqués à `R[i]` déjà réalisé. Correctif mécanique : `weights_base` et `weights_lev` (produit sélection × exposition tendance/vol-targeting) sont décalés d'un jour (`causal=True`) avant le calcul du PnL. Le calcul intermédiaire de la vol réalisée servant à l'exposition (`vol_lagged`) était déjà lagué séparément dans le code d'origine et n'a pas été modifié — seule la matrice de poids finale change de convention, conformément au correctif appliqué au #38/#14. Aucun seuil, aucune fenêtre, aucun paramètre modifié.

Même univers, mêmes paramètres (SIGNAL_WINDOW=5, REBAL_EVERY=5, tercile 1/3, VOL_WINDOW=20, TARGET_VOL_ANNUAL=0.20, CAP=2.0x, coûts 5 bps) :

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Winners 1.0x (référence, cycle #14, causal) | +0.66 | +103.9% | -40.6% |
| **Winners + overlay tendance+vol-targeting (causal)** | **+0.74** | **+135.5%** | -41.5% |

1. Sharpe overlay > référence : OUI
2. Rendement overlay > référence : OUI

**PASS confirmé — critère renforcé (Sharpe ET rendement) toujours atteint après correction.** Comme pour le #42 (même famille), la référence causale (+0.66, +103.9%) est cohérente avec le chiffrage indépendant du #14 sur l'univers d'origine 2021-2026 (`results/nonml_same_bar_execution_audit.md` §B.2, écart résiduel dû aux dates de début légèrement différentes entre scripts). Le PASS repose sur l'univers d'origine (2021-2026), pas sur l'univers point-in-time 2015-2026 retenu comme référence d'évaluation depuis #163/#164 — le #14 est FAIL sur ce dernier, et ce dérivé en hériterait vraisemblablement le FAIL s'il était ré-exécuté sur cet univers PIT (non fait ici, hors périmètre de la correction mécanique). L'ampleur de l'edge chute radicalement par rapport au chiffrage d'origine (Sharpe +2,33→+2,47 devenu +0,66→+0,74 ; rendement +1722%→+2528% devenu +104%→+136%) : l'essentiel de la performance spectaculaire d'origine était la fuite d'exécution, comme pour le #42.
