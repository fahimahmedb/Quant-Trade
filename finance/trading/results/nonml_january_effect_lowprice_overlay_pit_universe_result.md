# Résultat — Effet janvier (proxy prix bas) en overlay, univers POINT-IN-TIME (pré-enregistré)

Réutilisation stricte (Règle 7) du cycle d'origine : **aucun paramètre modifié**. Seul l'univers change — appartenance NDX-100 résolue à chaque date (`tickers_as_of_date`) au lieu de la liste 2026 appliquée rétroactivement.

Univers PIT : 178 tickers disponibles, couverture moyenne (éligibles / membres réels) : 88.4%. 2900 séances testables (2015-01-13 → 2026-07-27), rebalancement tous les 21j, tercile au prix de clôture le plus faible.

Overlay janvier actif 8.1% du temps (CAP 2.0x).

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Tercile prix bas 1.0x (référence) | +0.73 | +482.3% | -32.6% |
| **Tercile prix bas + overlay janvier 2.0x** | **+0.77** | **+660.3%** | -32.8% |

1. Sharpe overlay > référence : OUI
2. Rendement overlay > référence : OUI

**PASS — critère renforcé (Sharpe ET rendement) atteint sur univers point-in-time.**

**Limite héritée, inchangée :** le prix de clôture sert de proxy de taille faute de capitalisation boursière disponible. Un prix bas n'est pas une petite capitalisation — le portage sur univers point-in-time ne corrige pas cette limite et ne prétend pas le faire.

Ce résultat ne remplace pas celui du cycle d'origine : les deux coexistent. Leur comparaison mesure l'effet du biais du survivant sur ce candidat.
