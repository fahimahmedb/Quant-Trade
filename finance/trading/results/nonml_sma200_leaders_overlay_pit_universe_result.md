# Résultat — Leaders + overlay SMA200, univers POINT-IN-TIME (pré-enregistré)

Réutilisation stricte (Règle 7) du cycle d'origine (#33) : **aucun paramètre modifié**. Seul l'univers de sélection des Leaders change. Exécution causale (#253). Le signal SMA200 porte sur l'indice et est inchangé.

Référence = portefeuille Leaders 1,0× (convention du #4), **pas** Buy&Hold.

Univers PIT : 174 tickers, couverture moyenne 87.7%. 2900 séances testables (2015-01-13 → 2026-07-27). Overlay actif 81.7% du temps (indice au-dessus de sa SMA200).

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Leaders 1.0x (référence) | +0.70 | +393.0% | -32.5% |
| **Leaders + overlay SMA200 2.0x** | **+0.66** | **+1109.9%** | -48.3% |

1. Sharpe overlay > référence : non
2. Rendement overlay > référence : OUI

**FAIL — critère renforcé (Sharpe ET rendement) NON atteint sur univers point-in-time.**

## Coïncidence avec le #401 — mesure pré-enregistrée

Le PREREG annonçait, **avant tout calcul**, que ce cycle pouvait n'être qu'une identité arithmétique du #401 : l'audit du #41 avait établi que sur 2022-2026 le signal 52w-high était un sous-ensemble strict du signal SMA200, rendant leur union identique à SMA200 seul.

Séances où le signal SMA200 diffère de l'union SMA200 ∪ 52w-high, sur la fenêtre testée (2900 séances) : **0**.

**L'inclusion tient encore sur 2015-2026.** Ce cycle reproduit donc exactement le #401 : ce n'est **pas une observation nouvelle** mais la même stratégie sous un autre nom. Conformément à la règle de comptage fixée d'avance, il n'est **pas** ajouté au décompte des candidats testés de l'axe.

Ce résultat ne remplace pas celui du cycle d'origine : les deux coexistent.
