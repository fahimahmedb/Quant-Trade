# Audit indépendant — témoin de vraisemblance (#515)

Le backtest réutilise les fonctions AST des #500/#497. Cet audit
recalcule **D500 par une route regex pure** (sans AST) et **D497 par un
second parcours AST indépendant**, puis vérifie une propriété
mathématique du decoy de D501.

## D500, recalculé sans AST

Une « chaîne » ici est le contenu d'un `.append("…")` tenant sur
**une seule ligne** — route plus étroite que l'AST du backtest, qui
traverse aussi les f-strings multi-lignes et les arguments complexes.

- lignes `.append("…")` capturées : **16973**
- lift recalculé : **5,4**
- lift publié : **6,4**

> Les deux routes **ne peuvent pas coïncider exactement** — la route
> regex est volontairement plus étroite. Ce qui compte est le **sens**
> : les deux doivent rester **au-dessus** du seuil de 3, sans quoi le
> lift du backtest serait un artefact de la richesse de son extraction.
> Ici, c'est **confirmé** : la route étroite donne aussi un lift ≥ 3.

## D497-P10, recalculé par un second parcours

- scripts analysés : **1007**
- `A` (importe) : **83** ; `B` (`.main()` quelque part) : **8** ;
  `A∩B` réel (P10) : **8**
- lift recalculé : **12,1**
- lift publié : **12,1**
- accord exact : **OUI**

## L'involution du decoy — une propriété que le backtest n'énonce pas

Le pré-enregistrement affirme **une seule chose** : `decoy(v) ≠ v`, toujours,
quand `decoy(v)` est déterminé (`9-d ≠ d` pour tout chiffre). **Il
n'affirme pas** que `decoy` soit une involution — vérifier
`decoy(decoy(v)) = v` testerait une propriété que le pré-enregistrement
n'a jamais posée.

| v | decoy(v) | v ≠ decoy(v) ? |
|---|---|---|
| `127` | `872` | **≠ v** |
| `8` | `1` | **≠ v** |
| `12,5` | `87,5` | **≠ v** |
| `0` | `9` | **≠ v** |
| `94,7` | `—` | **indéterminé** |
| `3` | `6` | **≠ v** |
| `459` | `540` | **≠ v** |
| `17,0` | `82,0` | **≠ v** |
| `700` | `299` | **≠ v** |

- `decoy(v) ≠ v` vérifié sur tout l'échantillon déterminé : **OUI**

**Effet de bord noté à part, sans le confondre avec la garantie
ci-dessus** : composer `decoy` deux fois n'est **pas symétrique** —
`decoy("0") = "9"`, mais `decoy("9") = indéterminé`,
car le complément de `9` a une tête à `0`. **Ce n'est pas un bug** :
le pré-enregistrement ne promet la différence qu'une fois, pas la
réversibilité. Un audit qui l'aurait présenté comme un échec aurait
testé une règle inventée après coup, pas celle écrite d'avance.

## Partition de D501

- empruntées **39** = indéterminées **1** + évaluées **38** : **OUI**

## Le seuil est-il bien celui pré-enregistré ?

- `lift ≥ 3` présent dans le pré-enregistrement : **OUI**
- `SEUIL = 3.0` dans le backtest : **OUI**

## Ce que cet audit ne prouve pas

Il ne teste **pas** si `lift ≥ 3` est le **bon** seuil — seulement que
le calcul est reproductible par une route différente et que le seuil
appliqué est bien celui annoncé, sans dérive après coup.

## Inertie et chiffres calculés

- fichiers de l'arbre modifiés hors ce cycle : **0**
- nombres en gras : **20** ; dont **tapés en dur** : **0**

## Verdict

1. D500 recalculé sans AST reste au-dessus du seuil — **OUI**.
2. D497-P10 recalculé par un second parcours reste au-dessus du seuil — **OUI**.
3. le decoy de D501 vérifie bien decoy(v) ≠ v (la garantie du pré-enregistrement, pas une involution) — **OUI**.
4. la partition de D501 est exacte — **OUI**.
5. le seuil appliqué est bien celui pré-enregistré, arbre propre — **OUI**.

**AUDIT OK** (5/5)

Anti-lookahead **sans objet au sens temporel** : aucune série de prix.
