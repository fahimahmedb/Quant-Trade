# Audit adversarial — Overlay levé breakout Donchian 20j

## 1. Recalcul indépendant (boucle explicite vs pandas.rolling.max)

| Marché | Écart masque (nb j., hors 20 premiers) |
|---|---|
| Composite (5 ans) | 0 |
| NDX (40 ans) | 0 |
| Russell 2000 | 0 |
| S&P 500 | 0 |
| DAX | 0 |

**OK — masque confirmé par recalcul indépendant.**

## 2. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

**Lecture économique du FAIL** : l'exposition levée est proche de 18-20% du temps (contre ~55-75% pour les signaux longs #29/#37) -- un breakout à 20j est un événement fréquent et souvent bruité (le prix touche régulièrement son plus haut récent sans que cela présage d'une continuation de tendance durable), confirmant le même schéma déjà observé au #36 (MACD) : plus le signal de tendance est court/réactif, moins il fonctionne bien comme déclencheur de levier, comparé aux signaux longs (SMA200, 52w-high).
