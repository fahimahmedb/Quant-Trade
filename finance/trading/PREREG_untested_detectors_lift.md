# Pré-enregistrement — un **témoin de vraisemblance** pour les trois détecteurs jamais testés

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #514.

## Ce qui reste non couvert

Le #514 n'a testé que la couche contextuelle du **#502** (mots-clés dans une
fenêtre). Trois couches sous-jacentes, utilisées par toute la série
**#500-#514**, n'ont **jamais** subi de témoin :

- **D500** — l'extraction du **#500** : une chaîne publiée est un
  « emprunt candidat » si elle contient **à la fois** une référence `#NNN`
  et un nombre en gras ;
- **D501** — la confirmation du **#501** : une valeur est « retrouvée » si
  elle apparaît **en gras quelque part** dans le dépôt, **sans** contrainte
  de sujet ;
- **D497-P10** — la primitive « exécution en process » du **#497** : un
  script est classé P10 s'il **importe** un module `nonml_*` **et** appelle
  `.main()` **sur l'alias de cet import précisément**.

## La méthode — un **témoin de vraisemblance (lift)**, pas une permutation

Les trois détecteurs sont des **conjonctions** (A **ET** B). Le témoin
mesure si l'exigence conjointe apporte quelque chose au-delà de ce que le
hasard prédirait à partir des fréquences de A et de B **prises séparément** :

```
lift = P(A ET B) / (P(A) × P(B))
```

- **lift ≥ 3** : la conjonction est **loin** de ce que l'indépendance
  prédirait — le détecteur discrimine.
- **lift < 3** : la conjonction est **proche ou en-dessous** de ce que le
  hasard produirait — le détecteur ne fait que recouper deux événements
  fréquents.

**Le seuil de 3 est fixé ici, avant tout calcul, et ne bougera pas.**

## Les trois populations et conditions — figées

**D500** — unité : chaque **chaîne publiée** (`chaines_publiees`, importée du
#500) sur tous les `nonml_*.py`. `A` = contient `#\d{3}` ; `B` = contient un
nombre en gras (hors champ interpolé, comme le #500 l'exige déjà).

**D497-P10** — unité : chaque **script** `nonml_*.py`. `A` = importe **au
moins un** module `nonml_*` du dépôt ; `B` = appelle `.main()` sur **n'importe
quel** objet (pas nécessairement l'alias importé). La vraie règle P10 exige
`A ET B-sur-le-même-alias` ; ce témoin vérifie si l'exigence « **le même**
alias » apporte quelque chose par rapport à « A et B quelque part dans le
script, sans lien ».

**D501** — unité : chacune des **valeurs empruntées** (recensées au #500/#501).
Pour chaque valeur `v`, un **decoy déterministe** est construit :
**complément à 9, chiffre par chiffre, sur la partie entière** (`d → 9-d`),
partie décimale inchangée. *(9-d ≠ d pour tout chiffre 0-9, donc `decoy(v) ≠
v` toujours — transformation déterministe, aucun tirage.)* **Cas
indéterminé, exclu et compté séparément** : si le chiffre de tête du decoy
vaut `0`. Le test compare le taux « `v` trouvée en gras quelque part » au taux
« `decoy(v)` trouvée en gras quelque part ».

## Ce qui est mesuré

1. Pour **D500** et **D497-P10** : `P(A)`, `P(B)`, `P(A∩B)` observé, `P(A)×P(B)`
   attendu, **lift**, verdict au seuil de 3.
2. Pour **D501** : le taux « valeur réelle trouvée » contre le taux
   « decoy trouvé », le **rapport des deux taux**, verdict au seuil de 3.
3. Les cas **indéterminés** de D501, comptés.
4. Un résumé : combien des **trois** détecteurs discriminent.

## Critère de succès — chiffré

1. Les trois définitions (A, B, decoy) citées verbatim.
2. Les trois lifts/rapports publiés avec leurs effectifs.
3. Le verdict rendu pour **chacun** des trois au seuil de 3.
4. Les indéterminés de D501 comptés et non ignorés silencieusement.
5. **Aucun script exécuté**, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.
> **Le PASS ne dépend pas du succès des détecteurs testés** — seulement de
> la publication honnête de leur verdict, quel qu'il soit (leçon du #513).

## Prédictions — falsifiables

1. **D500** discrimine (lift ≥ 3).
2. **D497-P10** discrimine (lift ≥ 3).
3. **D501** **ne** discrimine **pas** (rapport < 3) — c'est la faiblesse que
   le #501 avait déjà soupçonnée en séparant confirmations « fortes » et
   « faibles » sans jamais la chiffrer par un témoin.

Si les trois prédictions sont vérifiées, le bilan de la série change de
nature : deux couches structurelles (D500, D497) tiennent, la couche de
confirmation brute (D501) ne tient que grâce au filtre contextuel ajouté au
#502 — ce qui expliquerait *pourquoi* le #502 était nécessaire.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script, ne **modifie** aucun rapport antérieur.
- Il ne **retranche** rien aux conclusions déjà publiées : un détecteur qui
  échoue ici n'invalide pas rétroactivement un cycle qui l'utilisait *en
  combinaison* avec la couche contextuelle du #502 (déjà testée au #514) —
  la portée de ce cycle est **la couche testée, pas la chaîne complète**.
- Il ne **se compte pas lui-même** — auto-exclusion (règle #447).

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, **y compris si les trois échouent**.
2. Définitions, decoy et seuil de 3 **inchangés** après mesure.
3. Les trois verdicts publiés côte à côte, jamais les seuls favorables.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
