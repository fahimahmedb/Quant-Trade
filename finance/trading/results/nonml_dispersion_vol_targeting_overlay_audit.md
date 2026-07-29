# Audit adversarial — Overlay vol-targeting gaté par dispersion cross-sectionnelle NDX-100

## 1. Recalcul indépendant de la dispersion (boucle explicite jour par jour)

Écart maximum absolu (jours où les deux calculs sont définis) : 2.08e-17
**OK — dispersion confirmée par recalcul indépendant.**

## 2. Recalcul indépendant de la position (boucle explicite, ddof=1)

Écart maximum absolu sur l'échantillon testable : 6.35e-14
**OK — position confirmée par recalcul indépendant.**

## 3. Test anti-lookahead (perturbation du futur sur l'indice)

**OK — aucune fuite (perturbation des prix indice futurs sans effet passé).**
