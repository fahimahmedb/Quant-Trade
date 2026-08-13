# Audit adversarial — breadth de drawdown profond, univers point-in-time

## 1. Recalcul indépendant de la breadth

Le backtest calcule le plus haut glissant par une boucle sur fenêtres ;
l'audit le recalcule avec `pandas.rolling(252, min_periods=252).max()`,
puis restreint aux membres point-in-time par une autre voie (sélection de
colonnes plutôt que masque booléen).

- dates comparées : **2907**
- écart absolu maximum : **0.00e+00**
- dates s'écartant de plus de 1e-12 : **0**

**CONFORME** — les deux chemins de calcul coïncident à la précision flottante.

## 2. Anti-lookahead — perturbation du futur

Les rendements après l'indice 5136 sont multipliés par -3. La position
AVANT cette date doit être **strictement** inchangée.

- positions identiques avant la coupure : **OUI**

**CONFORME — aucune fuite du futur détectée.**

## 3. Cohérence de l'appartenance point-in-time

- dates échantillonnées : **8**
- dates sans aucun membre résolu : **0**
- couverture moyenne rapportée par le backtest : **88.4%**
- tickers PIT exploitables : **174**

**CONFORME** — l'appartenance est résolue à chaque date testée.

## Verdict de l'audit

**CONFORME — les trois contrôles passent.**
