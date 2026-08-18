# Audit indépendant — verdicts de forme ou de mesure (#506)

Le backtest classe sur les **littéraux de chaîne**. Cet audit classe sur
les **appels d'ouverture** : quels fichiers sont **réellement lus**. Un
script peut nommer un `.txt` sans l'ouvrir, ou ouvrir un chemin construit
sans littéral — c'est la faiblesse de la route du #506.

## La population, et ce que la définition figée écartait

- rapports à verdict **en gras** (population du #506) : **60**
- rapports à verdict **sans gras**, écartés par la règle figée : **286**
- **corpus entier** : **346**
- écartés annoncés par le rapport : **286**
- accord sur les écartés : **OUI**

## La conclusion tient-elle sur le corpus entier ?

Route par **appels** : un script est « de mesure » s'il **ouvre**
effectivement un `.txt`, `.npz` ou `.csv`.

| Population | Effectif | Ouvrent des données | Part **sans données** |
|---|---|---|---|
| population figée | **60** | **4** | **93,3 %** |
| corpus entier | **346** | **249** | **28,0 %** |

- écart entre les deux populations : **-65,3** points

> **La population figée n'était pas représentative** : la part de
> verdicts sans données diffère nettement sur le corpus entier. Les
> chiffres du #506 décrivent **sa** minorité, pas le dépôt.

## Les deux routes se contredisent-elles ?

- scripts « de mesure » par **littéraux** (classe **M** du #506) : **12**
- scripts « de mesure » par **appels** (ici, population figée) : **4**

> Écart de **8**. Nommer un fichier
> n'est pas l'ouvrir, et ouvrir un chemin construit ne laisse pas de
> littéral : **les deux routes ne peuvent pas coïncider**, et
> l'écart mesure exactement cette différence de nature.

## Ce que cet audit ne prouve pas

Il ne dit **pas** qu'un verdict rendu sans lire de données soit **faux**.

Et il **contredit la lecture spontanée du #506** : sur le corpus entier,
**72,0 %** des rapports à verdict
sont produits par un script qui **ouvre effectivement des données.**

> **Ce dépôt n'a donc pas cessé de mesurer des marchés.** Le travail sur
> le texte est **massif dans la période récente** — le #506 le montre sur
> ses 20 derniers — mais **minoritaire sur l'ensemble**. Une conclusion
> tirée de la seule population figée aurait inversé le fait.

## Inertie et chiffres calculés

- fichiers de l'arbre modifiés hors ce cycle : **0**
- nombres en gras : **34** ; dont **tapés en dur** : **0**

## Verdict

1. le compte des rapports écartés concorde avec le rapport — **OUI**.
2. la conclusion est retestée sur le corpus entier — **OUI**.
3. les deux routes (littéraux / appels) sont publiées côte à côte — **OUI**.
4. aucun chiffre du rapport tapé en dur, arbre propre — **OUI**.

**AUDIT OK** (4/4)

Anti-lookahead **sans objet au sens temporel** : aucune série de prix —
**ce qui est précisément le sujet de ce cycle.**
