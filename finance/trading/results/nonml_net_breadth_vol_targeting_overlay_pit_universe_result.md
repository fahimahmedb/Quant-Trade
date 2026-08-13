# Résultat — breadth nette hauts-bas, univers POINT-IN-TIME (pré-enregistré)

Réutilisation stricte (Règle 7) du cycle d'origine (#90) : **aucun paramètre modifié**, seuil de porte compris (0,0). Seul l'univers change — à chaque date, seuls les titres réellement membres du NDX-100 entrent dans les comptages.

**Le P&L n'est pas un panier** : les deux jambes sont l'indice NDX-100 lui-même. L'univers titres n'alimente que la porte.

**Particularité** : la porte a un **seuil absolu** (breadth > 0), donc elle n'est pas invariante par translation du signal — contrairement aux portes à médiane glissante des #405 et #407.

Couverture moyenne (titres cotés éligibles / membres réels) : 88.4%. 2896 séances testables (2015-01-05 → 2026-07-13).

%j porte breadth nette active : 62.9%
Position moyenne : 1.32x
Breadth nette moyenne : +22.3 pts

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.76 | +597.4% | -35.6% |
| **Overlay gaté breadth nette (PIT)** | **+0.79** | **+930.4%** | -36.9% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS — critère renforcé (Sharpe ET rendement) atteint sur univers point-in-time.**

Ce résultat ne remplace pas celui du cycle d'origine : les deux coexistent. Leur comparaison mesure l'effet du biais du survivant sur ce candidat.
