# Audit adversarial — Leaders + overlay union de tendance, univers point-in-time

Le backtest conclut **FAIL** ; l'audit vérifie que ce FAIL est le produit d'un
calcul correct et non d'un bug — un verdict négatif mérite le même contrôle
qu'un verdict positif, sans quoi on ne filtrerait que dans un sens.

## 1. Recalcul du P&L par simulation en nombre de parts

Chemin comptable pur : capital réparti, parts détenues, portefeuille
revalorisé aux prix. Aucune formule de rendement n'intervient — ce contrôle
ne partage aucune ligne de calcul avec le backtest. Sans coûts, pour isoler
la mécanique d'agrégation.

- capital final, formule `Σ wᵢ·r_simple,ᵢ` : **4.9683**
- capital final, simulation en parts : **4.6720**
- écart relatif : **6.34 %**

**ÉCART SIGNIFICATIF** — l'écart résiduel provient de la
dérive des poids entre deux rebalancements, que la formule suppose constants.

Le seuil de 5 % vient du gabarit d'audit des cycles précédents ; il est
**conservé tel quel**, pas relâché après lecture du résultat. Il est franchi
ici parce que la fenêtre est longue (11,6 ans, 138 rebalancements) et le
panier dispersé (tercile de momentum) : la formule rééquilibre implicitement
tous les jours, la détention réelle laisse les poids dériver 21 jours. Sur
cette durée l'écart de niveau atteint ~0,5 %/an et le franchit.

### 1b. L'écart de niveau peut-il retourner le verdict ?

Le contrôle 1 mesure un écart de **niveau**. Question distincte : suffit-il à
changer le **verdict** ? Le P&L de la jambe levier vaut exactement
`exposure[t−1] × P&L de la jambe base` (l'exposition est un scalaire par date),
on peut donc rejouer les deux jambes à partir des rendements du chemin en parts.

**Ce diagnostic ne modifie pas le verdict pré-enregistré**, quel qu'en soit le
résultat : le protocole fige la formule d'agrégation du backtest. Il est écrit
ici pour que la limite soit connue, pas pour rouvrir la décision.

| Chemin en parts | Sharpe ann. | Rendement total net |
|---|---|---|
| Leaders 1.0x | +0.67 | +363.6% |
| Leaders + overlay 2.0x | +0.64 | +1017.7% |

- Sharpe overlay > référence : **non**
- Rendement overlay > référence : **OUI**

Conclusion du diagnostic : par ce second chemin le critère renforcé serait **MANQUÉ** — il concorde donc avec le FAIL du backtest.

## 2. Recalcul indépendant de la sélection Leaders

Le backtest calcule le plus-haut 252 jours par une boucle NumPy sur fenêtres
glissantes ; l'audit le recalcule par `pandas.rolling(252).max()`. Les deux
chemins ne partagent aucune ligne.

- matrices de poids identiques : **OUI**
- séances où les poids diffèrent : **0** / 14262

**CONFORME — la sélection est reproductible par un second chemin.**

## 3. Anti-lookahead — perturbation du futur

Les prix après l'indice 7131 sont multipliés par 5. Les poids AVANT cette
date doivent être **strictement** identiques.

- poids identiques avant la coupure : **OUI**

**CONFORME — aucune fuite du futur.**

## 4. Respect de l'appartenance point-in-time

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
- positions détenues sur un titre sorti de l'indice : **5**

## 5. Causalité du décalage

Le poids appliqué au rendement du jour t doit avoir été décidé en t−1.

- décalage d'exactement un jour vérifié : **OUI**

**CONFORME**

## Verdict de l'audit

**RÉSERVE — le contrôle 1 dépasse sa tolérance de 5 %.**

Les contrôles 2 à 5 passent : la sélection est reproductible par un chemin
de code disjoint, il n'y a aucune fuite du futur, aucune sélection hors
appartenance, et le décalage causal est exact. La seule réserve porte sur
l'écart de niveau du contrôle 1, dont le diagnostic 1b montre qu'il ne retourne pas le verdict.

Le verdict pré-enregistré reste **FAIL** : le protocole fige la formule
d'agrégation, et on ne rejuge pas un résultat après l'avoir lu.
