# Pré-enregistrement — faire émettre l'encart « dépendant du dépôt » par les scripts

**Écrit et committé AVANT toute modification et toute mesure.** `n_trials = 1`.

**Cycle de MODIFICATION**, septième après les #445 → #450.

## Le défaut, établi au #450

Le #439 avait ajouté un encart — *« Rapport dépendant du dépôt »* — à des
rapports publiés. Le #450 a démontré, **sur des cas réels**, que cet encart ne
survit pas : ajouté **au fichier** et non **au script qui le produit**, il est
effacé par la première régénération. Quatre l'ont été.

> Un encart qui décrit le comportement d'un script doit être **émis par ce
> script**.

## Le périmètre est lui aussi suspect

Le backlog annonce « **6 autres** condamnés à l'être ». Ce chiffre vient du #439,
et il n'a pas été revérifié depuis. **Il est présumé faux**, pour la raison
devenue habituelle : un rapport qui **cite** l'encart — comme celui du #450, qui
le reproduit pour l'expliquer — est compté par une recherche de texte comme s'il
le **portait**.

Le périmètre sera donc **rétabli par lecture** : un rapport porte l'encart si son
script ne l'émet pas et que le fichier le contient hors citation. L'écart avec le
chiffre du backlog sera publié.

## La modification — régime annoncé

Pour **chaque script retenu**, une **seule** insertion : le bloc de l'encart
ajouté à la liste qui compose le rapport, **immédiatement avant l'écriture du
fichier**. Aucune autre ligne touchée.

Le texte de l'encart est **repris mot pour mot** de celui du #439, sans
reformulation : le réécrire ferait de ce cycle une réécriture déguisée.

## Critère de succès — chiffré, et il peut échouer

1. **Diff confiné** : une insertion par script, rien d'autre.
2. **Survie à la régénération** — le cœur du cycle. Chaque script visé est
   exécuté **deux fois**, et l'encart doit être présent **après les deux**.
   C'est exactement ce que le marquage du #439 ne passait pas.
3. **Aucun doublon** : aucun rapport ne doit finir avec l'encart deux fois.
4. **Le périmètre réel est publié**, avec l'écart au chiffre de 6 annoncé par le
   backlog.
5. **Aucun verdict, aucun compte modifié** par l'ajout : l'encart est du texte
   ajouté en fin de rapport, il ne doit rien déplacer d'autre. Vérifié par diff.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédiction — falsifiable

- **Le chiffre de 6 est faux**, et le vrai périmètre est **plus petit** — j'ai
  déjà constaté, en établissant le périmètre, que la recherche de texte compte
  des citations. Je ne sais pas combien il en reste exactement.
- J'attends que l'ajout soit **sans effet** sur le reste des rapports : les
  lignes qui précèdent ne doivent pas bouger. Si elles bougent, ce sera de la
  dérive du dépôt, à attribuer comme au #450.

## Ce que ce cycle ne fait pas

- Il ne **réécrit pas** le texte de l'encart.
- Il ne l'ajoute **pas** aux rapports dont le script l'émet déjà.
- Il ne traite **pas** les rapports produits par des scripts absents ou
  inexécutables : ce cas serait publié, pas contourné.

## Engagements

1. Résultat rapporté tel quel, y compris un **FAIL**.
2. Aucune ligne hors de la région annoncée.
3. Le périmètre réel publié, même s'il contredit le backlog — surtout s'il le
   contredit.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
