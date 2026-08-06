# Audit — Combinaison ET (3/3) breakeven inflation + demandes continues + balance commerciale

## 1. Recalcul indépendant de la logique ET (boucle explicite)

| Marché | Séances (intersection) | Désaccords logique ET |
|---|---|---|
| Composite (5 ans) | 1250 | 0 |
| NDX (40 ans) | 5917 | 0 |
| Russell 2000 | 5917 | 0 |
| S&P 500 | 5917 | 0 |
| DAX | 5973 | 0 |

**OK — logique ET confirmée par recalcul indépendant (0 désaccord).**

## 2. Vérification du point de départ (intersection des 3 zones valides, NDX)
- Début individuel #200 (T10YIE) : séance 4355
- Début individuel #322 (CCSA) : séance 0
- Début individuel #327 (BOPGSTB) : séance 1622
- Début de la combinaison (calcul officiel, `argmax` sur l'intersection) : séance 4355
- Début attendu (max des 3, le plus contraignant) : séance 4355
- **OK — le point de départ de la combinaison correspond bien au signal le plus tardivement disponible (T10YIE, 2003+), aucune fuite via un signal encore indisponible**

## 3. Anti-lookahead (NDX, troncature à 6355 séances)
- Comparaison sur les 1999 premières positions post-démarrage, pleine série vs série tronquée : identique.
- **OK — aucune fuite**

## Verdict global : **CONFORME**

Note : les 3 portes individuelles (#200/#322/#327) ont chacune déjà été auditées indépendamment dans leurs cycles respectifs (alignement causal, tercile expanding, décalage de publication), et la logique de combinaison réutilise les MÊMES gates que le #334 (déjà auditées CONFORME) — cet audit se concentre spécifiquement sur la nouvelle logique ET, seul élément distinct de ce cycle par rapport au #334.
