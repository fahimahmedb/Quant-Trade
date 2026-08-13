# Résultat — breadth de faiblesse, univers POINT-IN-TIME (pré-enregistré)

Réutilisation stricte (Règle 7) du cycle d'origine (#89) : **aucun paramètre modifié**, seuil de porte compris (50 %). Seul l'univers change — à chaque date, seuls les titres réellement membres du NDX-100 entrent dans les comptages.

**Le P&L n'est pas un panier** : les deux jambes sont l'indice NDX-100 lui-même. L'univers titres n'alimente que la porte.

Couverture moyenne (titres cotés éligibles / membres réels) : 88.4%. 2896 séances testables (2015-01-05 → 2026-07-13).

## Activation de la porte — mesure décisive pour ce candidat

- porte **brute** (breadth ≥ 50 %) active : **13 séance(s) sur 2896** (0.45 %)
- porte **effective** (exposition > 1,0×, après clip du vol-targeting) active : 0.00 % des séances
- breadth de faiblesse observée : moyenne 8.0 %, maximum 64.9 %
- exposition moyenne : 1.00×

Critère d'informativité **fixé au pré-enregistrement** : porte brute active sur ≥ 2 % des séances.

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.76 | +597.4% | -35.6% |
| **Overlay gaté breadth de faiblesse (PIT)** | **+0.76** | **+597.8%** | -35.6% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS — critère renforcé (Sharpe ET rendement) atteint sur univers point-in-time.**

**⚠️ VERDICT NON INFORMATIF** — la porte brute ne s'active que sur 0.45 % des séances, sous le seuil de 2 % fixé **avant** calcul. La stratégie est donc quasi identique à Buy & Hold sur cette période, et le verdict ci-dessus mesure cette inactivité, **pas un edge**. Même conclusion qu'au cycle d'origine, dont le rapport portait déjà cet avertissement.

Ce résultat ne remplace pas celui du cycle d'origine : les deux coexistent. Leur comparaison mesure l'effet du biais du survivant sur ce candidat.
