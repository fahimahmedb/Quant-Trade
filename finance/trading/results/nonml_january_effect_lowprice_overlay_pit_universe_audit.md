# Audit adversarial — effet janvier (proxy prix bas), univers point-in-time

## 1. Recalcul du P&L par simulation en nombre de parts

Chemin comptable pur : capital réparti, parts détenues, portefeuille
revalorisé aux prix. Aucune formule de rendement n'intervient — ce contrôle
ne partage aucune ligne de calcul avec le backtest. Sans coûts, pour isoler
la mécanique d'agrégation.

- capital final, formule `Σ wᵢ·r_simple,ᵢ` : **5.8359**
- capital final, simulation en parts : **5.8290**
- écart relatif : **0.12 %**

**CONFORME** — l'écart résiduel provient de la
dérive des poids entre deux rebalancements, que la formule suppose constants.

## 2. Anti-lookahead — perturbation du futur

Les prix après l'indice 7131 sont multipliés par 5. Les poids AVANT cette
date doivent être **strictement** identiques.

- poids identiques avant la coupure : **OUI**

**CONFORME — aucune fuite du futur.**

## 3. Respect de l'appartenance point-in-time

**Ce qui constituerait une fuite** : sélectionner à la date de DÉCISION un
titre pas encore membre de l'indice.

- dates de rebalancement vérifiées : **139**
- sélections d'un non-membre à la décision : **0**

**CONFORME** — aucun titre n'est sélectionné avant son entrée dans l'indice.

**Ce qui n'en est pas une, mais mérite d'être documenté** : un titre qui SORT
de l'indice entre deux rebalancements reste détenu jusqu'au suivant. C'est le
comportement réaliste d'un portefeuille rebalancé tous les 21 jours, pas une
anticipation du futur.

- dates échantillonnées hors rebalancement : **15**
- positions détenues sur un titre sorti de l'indice : **9**


## 4. Causalité du décalage

Le poids appliqué au rendement du jour t doit avoir été décidé en t−1.

- décalage d'exactement un jour vérifié : **OUI**

**CONFORME**

## Verdict de l'audit

**CONFORME — les quatre contrôles passent.**
