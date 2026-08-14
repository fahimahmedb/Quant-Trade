# Pré-enregistrement — idempotence : **épuiser la famille capable**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #470.

## Ce que le #470 a appris, et qui change la cible

Le #470 a éprouvé 10 scripts tirés **par ordre alphabétique** et n'a rien
trouvé — puis a constaté que **aucun des dix n'énumérait `results/`**, donc
qu'aucun ne pouvait porter l'auto-inclusion cherchée.

> Le pré-enregistrement protège contre le choix des cas **après coup**. Il ne
> protège pas contre le choix des **mauvais cas**.

Ce cycle vise donc la **bonne population**, et il se trouve qu'elle est petite
assez pour être **épuisée**.

## La population — définie ici

Un script est **capable** du défaut s'il **énumère l'état de `results/`** :
`RESULTS.glob(`, `.iterdir()`, `glob.glob(`, ou un `git status`. Sans cela, il
ne peut pas se compter lui-même.

**Vérifié avant d'écrire ce pré-enregistrement** (inventaire de structure,
aucune mesure d'idempotence) : **22** scripts capables sur **323**, dont
**19 déjà éprouvés** aux #463, #467 et #470. **Il en reste 3.**

Ce cycle éprouve **les 3**, donc porte la couverture de la famille capable à
**22/22**.

## La faiblesse de cette définition, dite d'avance

Ma règle « capable » est la condition d'énumération du détecteur du **#466** —
détecteur dont le #467 a démontré qu'il était **inutilisable comme prédicteur de
défaut** (0/6 en validation).

**Ici elle ne prédit rien : elle délimite une population.** C'est un usage
différent et légitime. Mais sa faiblesse demeure :

- un script qui **construirait** son énumération autrement (variable, appel
  indirect) échapperait à la règle — le #469 a montré exactement ce cas sur la
  détection d'émission ;
- « épuiser la famille capable » **ne veut donc pas dire** « épuiser les scripts
  qui peuvent s'auto-inclure ».

**Le rapport devra énoncer les deux couvertures** : celle de la famille (élevée)
et celle du dépôt entier (basse). Publier la première seule serait trompeur.

## Le protocole

Chacun des 3 est **exécuté deux fois**, empreintes SHA-256 comparées, budget
**300 s** par exécution. Arbre restauré **après la dernière exécution** (leçon
du #468), résidus vérifiés ensuite.

## Critère de succès — chiffré, il porte sur le procédé

1. **3/3** scripts traités ou classés **avec leur raison**.
2. Les **deux empreintes** publiées pour chacun.
3. Tout non idempotent publié **avec son diff**.
4. **Les deux couvertures publiées** — famille capable **et** dépôt entier.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **0 non idempotent** parmi les 3. Fondement : dans la famille capable, 2
   défauts sur 19 éprouvés (~10 %), soit ~0,3 attendu sur 3. **Une prédiction
   de zéro est faible ; trouver un défaut la réfute nettement.**
2. Les **3** tiennent dans le budget.
3. La couverture de la **famille capable** atteint **100 %**, celle du **dépôt**
   reste **sous 12 %**.

Si la prédiction 1 est réfutée, tant mieux : un défaut trouvé vaut mieux qu'un
lot vide, et il ira au cycle de réparation comme au #468.

## Ce que ce cycle ne fait pas

- Il ne **répare** rien : tout défaut est publié et inscrit.
- Il ne **committe** aucun rapport régénéré.
- Il ne **prétend pas** clore la question de l'auto-inclusion dans le dépôt :
  seulement dans la famille **telle que je la définis**.

## Engagements

1. Résultat rapporté tel quel.
2. Population, échantillon et budget **inchangés** après mesure.
3. **Les deux couvertures sont publiées côte à côte**, jamais la favorable
   seule.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
