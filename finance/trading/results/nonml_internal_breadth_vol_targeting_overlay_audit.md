# Audit adversarial — Overlay vol-targeting gaté par breadth interne NDX-100

## 1. Recalcul indépendant de la breadth (boucle explicite par titre)

Écart maximum absolu (hors NaN) : 0.00e+00
**OK — breadth confirmée par recalcul indépendant.**

## 2. Recalcul indépendant de la position (boucle explicite jour par jour, ddof=1)

Écart maximum absolu sur l'échantillon testable : 6.35e-14
**OK — position confirmée par recalcul indépendant.**

## 3. Test anti-lookahead (perturbation du futur sur l'indice)

**OK — aucune fuite (perturbation des prix indice futurs sans effet passé).**
