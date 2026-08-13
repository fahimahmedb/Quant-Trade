# Résultat — breadth de surperformance « petites caps » proxy, univers POINT-IN-TIME (pré-enregistré)

Réutilisation stricte (Règle 7) du cycle d'origine (#123) : **aucun paramètre modifié**. Seul l'univers servant à calculer la breadth change — à chaque date, seuls les titres réellement membres du NDX-100 entrent dans le calcul.

**Limite de données assumée, identique à l'origine** : aucune capitalisation boursière disponible ; « petite capitalisation » est un PROXY (moitié supérieure par volatilité idiosyncratique glissante 60 j).

**Le P&L n'est pas un panier** : les deux jambes sont l'indice NDX-100 lui-même. L'univers titres n'alimente que le signal — c'est le seul canal par lequel le biais du survivant peut agir ici.

Couverture moyenne (titres éligibles / membres réels) : 88.2%. 2645 séances testables (2016-01-04 → 2026-07-13).

%j porte surperformance petites caps active : 36.1%
Position moyenne : 1.18x
Breadth surperformance moyenne : 48.6%

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.79 | +542.3% | -35.6% |
| **Overlay gaté breadth petites caps (PIT)** | **+0.82** | **+715.5%** | -35.6% |

1. Sharpe overlay > BH : OUI
2. Rendement overlay > BH : OUI

**PASS (niveau 1) — critère renforcé atteint sur univers point-in-time.**

**PASS niveau 1 seulement — pas un verdict final (Règle 9).** Pour mémoire, la batterie renforcée du candidat d'origine donne **1/5**.

Ce résultat ne remplace pas celui du cycle d'origine : les deux coexistent. Leur comparaison mesure l'effet du biais du survivant sur ce candidat.
