# Audit — campagne v2 : le critère que j'avais pré-enregistré était incomplet

Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,
**aucun rapport publié modifié**.

## La divergence

Sur 24 tirages dans le vivier « nettoyé » : **23 identiques**, **1 divergent** —
`empty_pass_requalification`.

```
- - fichiers `nonml_*_pnl.npz` trouvés : **173**
+ - fichiers `nonml_*_pnl.npz` trouvés : **208**
```

Le rapport annonçait **173** fichiers `.npz` ; il y en a **208** aujourd'hui.
Les 35 de plus ont été produits par mes propres cycles #416 à #427.

## Le défaut — mon critère cherchait des littéraux, pas un concept

Le critère pré-enregistré au #437 énumérait **trois écritures exactes** :

```
glob("nonml_*_backtest.py")   glob("*_pnl.npz")   glob("nonml_*_result.md")
```

Or `empty_pass_requalification` écrit `RESULTS.glob("nonml_*_pnl.npz")`. **Le même concept, une
orthographe différente** — le préfixe `nonml_` à l'intérieur des guillemets
suffit à faire échouer la correspondance littérale.

Le critère était censé être *mécanique et complet*. Il était mécanique, et
**incomplet** : j'ai encodé trois exemples au lieu de la propriété qu'ils
illustraient — « le script balaie un répertoire que les cycles alimentent ».

| Formulation du critère | Scripts capturés |
|---|---|
| **pré-enregistré** (trois littéraux) | **8** |
| **conceptuel** (`glob` sur `results/` ou `scripts/`) | **10** |
| **manqués** par le critère pré-enregistré | **2** |

- `empty_pass_basket_extension`
- `empty_pass_requalification`

L'écart est **petit en nombre** — deux scripts — mais il suffit à faire échouer
la campagne, puisqu'un seul tirage divergent suffit à annuler la borne.

## Ce que je refuse de faire, pour la deuxième fois consécutive

Le geste tentant est évident : élargir le critère au concept, relancer, publier
une borne. **Je ne le fais pas ici.**

Le critère a été pré-enregistré **avant** ce tirage. Le corriger **après** avoir
vu quel script lui échappait — et sachant que ce script est précisément celui qui
annule la borne — serait exactement le geste que le #436 avait refusé, répété un
cycle plus tard avec une justification plus sophistiquée.

> Le critère conceptuel sera **pré-enregistré au prochain cycle**, avec sa
> formulation exacte, et la campagne repartira **encore** de zéro.

**Borne v2 : non publiée.** Comme au #436.

## Ce que ces quatre cycles ont réellement produit

Aucune borne publiable, et deux constats qui valent mieux qu'une borne :

1. **Mon outillage de diagnostic est instable par construction.** Dix scripts
   embarquent un décompte du dépôt dans leur rapport ; ils divergent à chaque
   cycle qui ajoute un fichier. J'ai écrit la plupart d'entre eux, et introduit
   au #428 le compteur qui a fait tomber le premier.
2. **Un critère « mécanique » écrit trop vite reste faux.** Énumérer trois
   littéraux n'est pas formaliser une propriété. Le pré-enregistrement protège
   de l'ajustement après coup, il ne protège pas d'une spécification bâclée.

Les rapports de **stratégie**, eux, n'ont produit **aucune divergence** :
sur les 84 tirages des #434-#437, les 4 divergences observées ou attendues sont
toutes des **diagnostics auto-référents**. C'est une indication rassurante — pas
une borne, et je ne la présente pas comme telle.

## Conclusion

| Critère pré-enregistré | Attendu | Obtenu | |
|---|---|---|---|
| critère appliqué, exclus listés | oui | 7 exclus | ✔ |
| 24 tirés et classés | 24 | 24 | ✔ |
| divergence publiée avec `diff` | si présente | **oui** | ✔ |
| rapports publiés modifiés | 0 | 0 | ✔ |
| borne v2 publiée | 11,7 % | **non publiée** | — |

Le pré-enregistrement engageait à publier la borne « même si elle est moins
flatteuse ». Elle n'est pas moins flatteuse : elle est **inexistante**, et pour
une raison qui m'incombe.

Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.
