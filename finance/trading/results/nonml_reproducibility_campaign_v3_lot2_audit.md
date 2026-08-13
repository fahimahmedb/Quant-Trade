# Audit — campagne v3, lot 2 : la borne tombe à 6,2 %

Recalcul **indépendant** : cet audit n'importe rien du script de mesure.

## Contrôle 1 — tirage reproductible et disjoint du lot 1

- vivier recompté : **290**
- échantillon redérivé identique au publié : **oui** ✔
- scripts communs aux deux lots : **0** ✔

La disjonction n'est pas cosmétique : sans elle, le cumul de 47 compterait deux
fois les mêmes vérifications et la borne serait **fausse dans le sens flatteur**.

## Contrôle 2 — la correction reportée du #439 a-t-elle tenu ?

Au #439, `subprocess.run(timeout=…)` ne tuait que l'enfant direct : un
petit-enfant orphelin avait **réécrit un rapport publié après sa restauration**.
Le script v3 portait encore ce défaut ; la correction a été **reportée avant le
tirage**, comme le pré-enregistrement l'annonçait.

- correction présente dans le script du lot : **oui** ✔
- rapports publiés **modifiés** en fin de cycle : **0** ✔
- sentinelles subsistantes : **0** ✔

**Rien n'a fui.** Contrairement au #439, où j'avais retrouvé
`nonml_reproducibility_sample_result.md` modifié par un orphelin, l'arbre est
propre en fin de cycle.

Je ne peux pas prouver que c'est la correction qui l'explique plutôt que la
composition du tirage — aucun candidat de ce lot n'a atteint le délai, donc le
chemin de code corrigé n'a peut-être jamais été emprunté. **La correction est
un garde-fou en place, pas une victoire mesurée**, et je le note comme tel.

## Contrôle 3 — la borne cumulée, recalculée

| | Dénominateur | Borne à 95 % | Divergents encore possibles |
|---|---|---|---|
| #438 seul | 23 | 12.2 % | ~35 |
| ce lot seul | 24 | 11.7 % | ~34 |
| **cumul** | 47 | 6.2 % | ~17 |

Structurelles ce lot : **0** (exclues du dénominateur, règle du #438).

Le pré-enregistrement annonçait **≈ 6,3 %** pour un lot à 0 substantielle et
1 structurelle. Le lot n'a produit **aucune** structurelle, d'où **6.2 %**
— légèrement meilleur, et pour une raison qui n'a rien d'un ajustement : un
tirage retenu de plus au dénominateur.

## Ce que 6,2 % dit — et ne dit pas

Sur **290** rapports, la borne laisse place à **~17**
divergences substantielles non détectées. **Aucune n'a jamais été observée** sur
l'ensemble des campagnes — mais « jamais observée » n'est pas « inexistante », et
c'est précisément ce que la borne chiffre.

| Étape | Borne | Statut |
|---|---|---|
| #434 | 22,1 % | caduque (#436) |
| #435 | 8,0 % | **caduque** (#436) |
| #437 | — | non publiée |
| #438 | 12,2 % | remplacée par le cumul |
| **#440** | **6.2 %** | **publiée** |

La borne est enfin **meilleure** que le 8,0 % caduc revendiqué au #435 — mais par
un chemin qui a coûté trois remises à zéro, et elle repose sur une règle de
classification qui n'existait pas alors.

**Rendement décroissant, pour décider d'un lot 3 :**

| Dénominateur | Borne | Divergents possibles |
|---|---|---|
| 47 | 6.2 % | ~17 |
| 71 | 4.1 % | ~11 |
| 100 | 3.0 % | ~8 |
| 150 | 2.0 % | ~5 |
| 200 | 1.5 % | ~4 |

24 tirages de plus feraient passer la borne de **6,2 %** à **~4,1 %** — de ~17 à
~11 divergences possibles. Le gain se tasse ; c'est le dernier lot dont le
bénéfice reste net.

## Conclusion

| Critère pré-enregistré | Attendu | Obtenu | |
|---|---|---|---|
| tirage reproductible et disjoint | oui | oui | ✔ |
| divergents classés par le test | tous | 0 | ✔ |
| rapports modifiés / sentinelles | 0 / 0 | 0 / 0 | ✔ |
| borne publiée si 0 substantielle | oui | **6.2 %** | ✔ |

**Les quatre contrôles passent.** La correction du #439 a été reportée *avant*
le tirage plutôt qu'après en avoir vu les effets — c'est le seul point où ce
cycle fait mieux que les trois précédents, et il ne tient qu'à avoir vérifié
un script hérité au lieu de le supposer à jour.

Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.
