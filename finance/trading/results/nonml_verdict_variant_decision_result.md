# Faut-il convertir la dernière variante du détecteur ? (pré-enregistré)

**Cycle de décision.** Il pouvait se conclure par « on ne touche à rien » ;
la règle de décision était fixée **avant** toute mesure.

## Ce que cette fonction sert réellement

Elle **ne classe pas dans l'absolu**. Elle sert le contrôle 3 du script :
comparer le verdict d'un rapport **avant** et **après** l'ajout d'une colonne,
pour prouver que l'ajout n'a rien changé.

C'est une **comparaison à règle constante**. Une règle grossière n'y trompe
que si sa grossièreté crée une différence là où il n'y en a pas, ou en masque
une. C'est pourquoi ce cas méritait d'être décidé séparément plutôt que
converti mécaniquement avec les six autres du #449.

## Les deux règles, sur les trois rapports cibles

| Rapport | Présent | Règle locale (sans littéral) | Règle partagée (#448) | Coïncident |
|---|---|---|---|---|
| `halloween_effect` | ✔ | PASS | PASS | ✔ |
| `intraday_range_regime_overlay` | ✔ | PASS | PASS | ✔ |
| `tom_overlay` | ✔ | PASS | PASS | ✔ |

**Les deux règles coïncident sur les trois : OUI.**

## La décision

Règle fixée avant mesure : *convertir si et seulement si les deux règles
donnent le même verdict sur les trois*.

### **Décision : convertir.**

La conversion est **sans effet observable** sur ce que ce script mesure.
À effet nul, l'uniformité du dépôt vaut mieux qu'une exception qu'il
faudra ré-expliquer à chaque cycle qui recompte les consommateurs.

## Critère 4 — le contrôle 3 est-il vide en exécution ordinaire ?

Le contrôle 3 compare le rapport courant à un **instantané d'avant**, passé
en argument de ligne de commande :

```python
BEFORE_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else None
```

**Il est vide en exécution ordinaire.** Sans argument, `BEFORE_DIR` vaut
`None`, la colonne « Avant » affiche `—`, et la comparaison ne compare
rien.

> **Cela relativise tout ce cycle.** La règle qu'on discute ici ne sert,
> en pratique, qu'à une comparaison qui ne s'exécute que si quelqu'un
> fournit un instantané. Le dire vaut mieux que laisser croire qu'on a
> tranché quelque chose d'important.

**Prédiction vérifiée** — je l'annonçais, et c'était la partie la plus
utile de la prédiction.

## Ce que ce cycle ne fait pas

- Il ne **régénère** aucun rapport.
- Il ne touche **aucun autre** script.
- Il ne prétend pas que la règle locale était **juste** : elle confond
  porter et mentionner un verdict, comme toutes les autres avant le #448.
  Il constate qu'ici, cette confusion **n'a pas de conséquence mesurable**.


> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).