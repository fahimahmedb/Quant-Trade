# Audit adversarial — Leaders + overlay vol-targeting 20 %, univers point-in-time

Le backtest conclut **FAIL** ; l'audit vérifie que ce FAIL est le produit d'un
calcul correct et non d'un bug — un verdict négatif mérite le même contrôle
qu'un verdict positif, sans quoi on ne filtrerait que dans un sens.

## 1. Recalcul du P&L par simulation en nombre de parts

Chemin comptable pur : capital réparti, parts détenues, portefeuille
revalorisé aux prix. Aucune formule de rendement n'intervient — ce contrôle
ne partage aucune ligne de calcul avec le backtest. Sans coûts, sur la jambe
de référence (1,0×), pour isoler la mécanique d'agrégation.

- capital final, formule `Σ wᵢ·r_simple,ᵢ` : **4.8792**
- capital final, simulation en parts : **4.5601**
- écart relatif : **7.00 %**

**ÉCART SIGNIFICATIF** — l'écart résiduel provient de la
dérive des poids entre deux rebalancements, que la formule suppose constants.

Le seuil de 5 % vient du gabarit d'audit des cycles précédents ; il est
**conservé tel quel**, pas relâché après lecture du résultat. Il est franchi
pour la même raison qu'au #401 : 11,5 ans et un panier de momentum dispersé,
là où la formule rééquilibre implicitement tous les jours.

### 1b. L'écart de niveau peut-il retourner le verdict ?

Le contrôle 1 mesure un écart de **niveau**. Question distincte : suffit-il à
changer le **verdict** ? Le P&L de la jambe levier vaut exactement
`exposure[t−1] × P&L de la jambe base` (l'exposition est un scalaire par date),
on peut donc rejouer les deux jambes à partir des rendements du chemin en parts.

**Ce diagnostic ne modifie pas le verdict pré-enregistré**, quel qu'en soit le
résultat : le protocole fige la formule d'agrégation du backtest.

| Chemin en parts | Sharpe ann. | Rendement total net |
|---|---|---|
| Leaders 1.0x | +0.66 | +352.5% |
| Leaders + vol-targeting 20 % | +0.62 | +369.3% |

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

**Ce qui n'en est pas une, mais mérite d'être documenté** : un titre sorti de
l'indice entre deux rebalancements reste détenu jusqu'au suivant — comportement
réaliste d'un portefeuille rebalancé tous les 21 jours.

- dates échantillonnées hors rebalancement : **15**
- positions détenues sur un titre sorti de l'indice : **0**

## 5. Causalité du décalage des poids

Le poids appliqué au rendement du jour t doit avoir été décidé en t−1.

- décalage d'exactement un jour vérifié : **OUI**

**CONFORME**

## 6. Causalité de l'exposition — contrôle propre à ce candidat

L'overlay n'est pas piloté par un signal externe mais par la volatilité du
portefeuille **lui-même** : c'est là que se logerait une fuite circulaire, si
l'exposition du jour t utilisait le P&L du jour t. Test : le P&L est perturbé à
partir de l'indice 7131 ; l'exposition jusqu'à cet indice **inclus** doit rester
inchangée.

- exposition inchangée jusqu'à l'indice 7131 inclus : **OUI**
- premier indice où l'exposition diffère : **7132** (attendu : ≥ 7132)

**CONFORME — la volatilité qui dimensionne la position du jour t est entièrement connue en t−1.**

## Verdict de l'audit

**RÉSERVE — seul le contrôle 1 dépasse sa tolérance de 5 %.**

Les contrôles 2 à 6 passent : sélection reproductible par un chemin de code
disjoint, aucune fuite du futur, aucune sélection hors appartenance, décalage
causal exact, et dimensionnement de position sans fuite circulaire. La seule
réserve porte sur l'écart de niveau du contrôle 1, dont le diagnostic 1b
montre qu'il ne retourne pas le verdict.

Le verdict pré-enregistré reste **FAIL** : le protocole fige la formule
d'agrégation, et on ne rejuge pas un résultat après l'avoir lu.
