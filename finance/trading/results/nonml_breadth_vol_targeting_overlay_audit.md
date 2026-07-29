# Audit adversarial — Overlay vol-targeting gaté par breadth NDX+Russell2000

## 1. Recalcul totalement indépendant (porte + vol-targeting, boucle explicite)

Écart position max (hors 252 premiers jours) : 6.35e-14

**OK — position confirmée par recalcul totalement indépendant.**

## 2. Test anti-lookahead (perturbation du futur, séparément sur chaque marché)

| Marché perturbé | Décisions passées identiques après perturbation future |
|---|---|
| NDX (primaire) | OUI |
| Russell 2000 (confirmation) | OUI |

**OK — aucune fuite de données futures (ni du marché primaire ni du marché de confirmation).**

**Lecture économique du PASS** : la porte breadth est active 38,5% du temps (contre ~55-75% pour les signaux de tendance simples #29/#37 utilisés seuls), un filtre plus sélectif qui, combiné au vol-targeting, préserve exactement le MDD de Buy&Hold (-82,9%→-82,9%) tout en améliorant Sharpe et rendement -- confirme la généralisation du mécanisme hiérarchique (#47 tendance, #54 calendrier, maintenant #57 breadth) à un troisième type de signal de porte, y compris un signal par ailleurs jugé marginal en overlay binaire (#52).
