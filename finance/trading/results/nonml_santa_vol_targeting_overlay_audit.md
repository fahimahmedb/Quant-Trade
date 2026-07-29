# Audit adversarial — Overlay vol-targeting gaté par Santa Claus Rally

## 1. Recalcul totalement indépendant (porte + vol-targeting, boucle explicite)

| Marché | Écart position max (hors marge de fenêtre) |
|---|---|
| Composite (5 ans) | 6.22e-15 |
| NDX (40 ans) | 4.26e-14 |
| Russell 2000 | 1.73e-14 |
| S&P 500 | 1.03e-13 |
| DAX | 2.26e-14 |

**OK — position confirmée par recalcul totalement indépendant.**

## 2. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

**Lecture économique du PASS** : la porte est active seulement 1,7-2,3% du temps (la plus étroite combinée au mécanisme hiérarchique dans ce backlog), ce qui explique un MDD quasi inchangé partout -- l'amplification concerne trop peu de séances pour affecter significativement le profil de risque, contrairement aux portes plus larges (#47, #54, #57, #68). Le résultat reproduit exactement le schéma du #64 (Composite seul en échec), confirmant que le mécanisme hiérarchique n'introduit ni bug ni dégradation même sur une fenêtre extrêmement resserrée.
