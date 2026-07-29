# Audit adversarial — Effet week-end conditionnel lundi|vendredi

## 1. Recalcul indépendant du masque (approche pandas différente)

| Marché | Écart (nb jours différents) |
|---|---|
| Composite (5 ans) | 0 |
| NDX (40 ans) | 0 |
| Russell 2000 | 0 |
| S&P 500 | 0 |
| DAX | 0 |

**OK — masque confirmé par recalcul indépendant sur les 5 marchés.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes, NDX)

Écart de masque sur les séances antérieures à la mutation : 0
**OK — aucune fuite, le passé est bien inchangé.**

## 3. Plausibilité de la fréquence d'activation

Fraction de séances NDX avec porte active : 10.0% (attendu approximativement 1/5 des lundis avec vendredi précédent positif, soit ~10% si environ 50% des vendredis sont positifs — cohérent).
