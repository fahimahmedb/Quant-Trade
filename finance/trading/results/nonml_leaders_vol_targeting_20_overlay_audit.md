# Audit adversarial — Leaders 52-semaines + overlay de vol-targeting continu, cible 20%

Recalcul indépendant de l'exposition (boucle explicite, ddof=1) : écart max = 1.24e-14
**OK.**

Exposition totale appliquée (jours avec position) : écart max = 4.44e-16
**OK — exposition exactement conforme.**

Test anti-lookahead (perturbation du futur) : OK — aucune fuite.

**Lecture** : confirme l'hypothèse -- en relevant la cible de vol à 20% (au lieu de 15% au #45), l'exposition moyenne passe de 0,91x à 1,21x, ce qui referme l'écart de rendement (+98,7%→+116,4%) tout en gardant un Sharpe quasi stable. Le MDD se dégrade légèrement (-21,3%→-22,9%), cohérent avec une exposition moyenne désormais >1.0x.
