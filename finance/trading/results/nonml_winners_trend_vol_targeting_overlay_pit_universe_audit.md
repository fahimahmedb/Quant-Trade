# Audit adversarial — Winners + overlay tendance/vol-targeting, univers point-in-time

Le backtest conclut **FAIL** ; l'audit vérifie que ce FAIL est le produit d'un
calcul correct et non d'un bug — un verdict négatif mérite le même contrôle
qu'un verdict positif, sans quoi on ne filtrerait que dans un sens.

## 1. Recalcul du P&L par simulation en nombre de parts

Chemin comptable pur : capital réparti, parts détenues, portefeuille
revalorisé aux prix. Aucune formule de rendement n'intervient — ce contrôle
ne partage aucune ligne de calcul avec le backtest. Sans coûts, sur la jambe
de référence (1,0×), pour isoler la mécanique d'agrégation.

- capital final, formule `Σ wᵢ·r_simple,ᵢ` : **3.0828**
- capital final, simulation en parts : **3.5540**
- écart relatif : **13.26 %**

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
| Winners 1.0x | +0.50 | +221.6% |
| Winners + overlay | +0.43 | +222.6% |

- Sharpe overlay > référence : **non**
- Rendement overlay > référence : **OUI**

Conclusion du diagnostic : par ce second chemin le critère renforcé serait **MANQUÉ** — il concorde donc avec le FAIL du backtest.

## 2. Recalcul indépendant de la sélection Winners

Le backtest calcule le momentum 5 jours par indexation NumPy décalée
avec masque d'existence ; l'audit le recalcule par `pandas.pct_change(5)`. Les deux
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

- dates de rebalancement vérifiées : **582**
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

## 6. Attribution — l'effondrement vient-il de l'univers ou de la période ?

**Diagnostic post-hoc, déclaré comme tel** : il n'était pas pré-enregistré, il
ne modifie aucun verdict, et il est écrit ici parce que sans lui je serais tenté
d'attribuer à l'univers un effondrement dont la période est peut-être
responsable.

La référence Winners 1,0× passe de **+0,96** (cycle d'origine) à **+0,44** de
Sharpe. Mais la fenêtre a changé en même temps que l'univers : 2886 séances
depuis 2015, contre 1376 depuis 2021. Le calcul point-in-time est donc restreint
à la fenêtre d'origine, ce qui isole l'effet d'univers.

- séances retenues (PIT, depuis 2021-02-02) : **1376**

| | Sharpe ann. | Rendement total net |
|---|---|---|
| Winners 1.0x — origine, univers biaisé, 2021-2026 | +0.96 | +250.7% |
| Winners 1.0x — PIT, **même fenêtre** 2021-2026 | +0.29 | +38.1% |
| Winners 1.0x — PIT, fenêtre complète 2015-2026 | +0.44 | +179.0% |

| | Sharpe ann. | Rendement total net |
|---|---|---|
| Overlay — origine, univers biaisé, 2021-2026 | +1.02 | +318.5% |
| Overlay — PIT, **même fenêtre** 2021-2026 | +0.24 | +35.6% |

La ligne du milieu de chaque tableau est celle qui répond à la question : à
fenêtre identique, tout écart avec la première ligne est imputable à l'univers,
et tout écart avec la troisième à la période.

## Verdict de l'audit

**RÉSERVE — seul le contrôle 1 dépasse sa tolérance de 5 %.**

Les contrôles 2 à 5 passent : sélection reproductible par un chemin de code
disjoint, aucune fuite du futur, aucune sélection hors appartenance, décalage
causal exact. La seule
réserve porte sur l'écart de niveau du contrôle 1, dont le diagnostic 1b
montre qu'il ne retourne pas le verdict.

Le verdict pré-enregistré reste **FAIL** : le protocole fige la formule
d'agrégation, et on ne rejuge pas un résultat après l'avoir lu.
