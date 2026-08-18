# Audit indépendant — témoin de permutation (#514)

Le backtest emploie **une** permutation : les mots-clés du voisin
suivant. **Un dérangement unique peut être chanceux.** Cet audit rejoue
le test avec **tous les décalages** possibles (`k = 1…38`) et
publie la distribution.

## La distribution des taux sous permutation

- décalages évalués : **38**
- taux **réel** (mots-clés propres) : **94,9 %**
- taux sous `k=1` — celui du #514 : **64,1 %**
- **médiane** de tous les décalages : **46,2 %**
- **minimum** : **33,3 %** · **maximum** : **66,7 %**
- rang de `k=1` dans la distribution : **37** sur **38**

## L'écart du #514 est-il typique ?

- écart publié (`k=1`) : **+30,8** points
- décalages pour lesquels l'écart atteint le seuil de **20** : **38** sur **38**

> **La conclusion du #514 ne dépend pas du décalage choisi.** La
> règle bat son témoin pour **100,0 %** des dérangements possibles :
> le résultat est **structurel**, pas un coup de chance.

**Et le #514 avait tiré le décalage le plus défavorable** : `k=1`
arrive au rang **37** sur **38**, c'est-à-dire parmi les
témoins les plus **forts**.

- écart médian sur tous les décalages : **+48,7** points
- écart publié par le #514 : **+30,8** points

> **Son chiffre est donc une borne basse, pas un chiffre flatteur.**
> Le seul décalage qu'il a testé était celui qui donnait le plus de
> crédit au témoin — et la règle le battait quand même.

## Trois propriétés que le backtest n'énonce pas

- chaque emprunt reçoit bien les mots-clés d'un **autre** (dérangement) :
  **OUI**
- le taux **réel** est indépendant du décalage : **OUI** *(il ne
  l'utilise pas)*

| Grandeur | Rapport | Audit | Accord |
|---|---|---|---|
| taux réel | **94,9 %** | **94,9 %** | **oui** |
| taux permuté (`k=1`) | **64,1 %** | **64,1 %** | **oui** |

## Ce que cet audit ne prouve pas

Il teste la **robustesse au dérangement**, pas la **validité** de la
règle. Même en battant tous ses témoins, « ≥ 2 mots-clés dans ±200
caractères » reste une **convention** pour dire « même sujet » — et le
taux de faux positifs publié par le #514 reste, lui, très élevé.

## Inertie et chiffres calculés

- fichiers de l'arbre modifiés hors ce cycle : **0**
- nombres en gras : **37** ; dont **tapés en dur** : **0**

## Verdict

1. tous les **38** décalages sont évalués et publiés — **OUI**.
2. le dérangement est vérifié (aucun emprunt ne reçoit ses propres mots-clés) — **OUI**.
3. la conclusion tient pour au moins la moitié des décalages (**100 %**) — **OUI**.
4. les deux taux publiés sont recalculés à l'identique — **OUI**.
5. aucun chiffre du rapport tapé en dur, arbre propre — **OUI**.

**AUDIT OK** (5/5)

Anti-lookahead **sans objet au sens temporel** : aucune série de prix.
