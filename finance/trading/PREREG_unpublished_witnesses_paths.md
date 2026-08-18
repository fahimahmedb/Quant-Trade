# Pré-enregistrement — les **témoins non publiés** : que faudrait-il ?

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #493.

## La dette à caractériser

Quatre cycles consécutifs — **#487, #489, #490, #491** — ont dû écrire la même
phrase :

> **Le témoin est dans le code, pas encore dans le rapport.**

Les scripts patchés n'ont pas été relancés parce qu'ils ont des **effets de
bord** : l'un exécute d'autres scripts du dépôt, un autre écrit un rapport qui
n'est pas le sien. **Personne n'a établi ce qu'il faudrait** pour que ces
témoins paraissent. Ce cycle l'établit — **sans rien exécuter**.

## La population — dérivée mécaniquement, pas recopiée

Un script est **porteur d'un témoin non publié** si :

1. son code contient une **ligne d'écriture de témoin** — repérée par son
   préfixe littéral, celui des patchs des #487/#489/#491 ; **et**
2. la **chaîne correspondante est absente** de son rapport publié dans
   `results/`.

Les préfixes sont figés ici :

```
- rapports ayant **perdu** l'encart du #439
- PASS qui sont des **stratégies**
- rapports classés « indéterminé » par la règle unifiée
- incohérences prose/compte exposées par le rafraîchissement
```

## Ce qui est mesuré pour chacun

Établi par **AST et lecture de motifs**, sans exécution :

1. **exécute-t-il un autre script du dépôt** ?
   (`subprocess.run([sys.executable, …])`) ;
2. **combien de fichiers écrit-il**, et lesquels ne sont pas le sien ?
3. **touche-t-il l'arbre git** (`git checkout`, `git add`) ?
4. **son rapport est-il idempotent** au sens du #463 — question **non
   mesurable ici** puisqu'elle exigerait de l'exécuter ; elle est donc
   **déclarée hors de portée**, pas contournée.

## Les trois classes — fixées avant de regarder

- **A. Exécutable sans danger** — n'écrit que son propre rapport, n'exécute
  rien, ne touche pas l'arbre.
- **B. Exécutable avec effets à annuler** — écrit d'autres fichiers ou touche
  l'arbre, mais n'exécute aucun script tiers : une restauration suffirait.
- **C. Non exécutable en l'état** — exécute d'autres scripts du dépôt ; le
  relancer déclencherait une cascade dont ce projet n'a pas le contrôle.

## Critère de succès — chiffré, il porte sur le procédé

1. Population **dérivée par code**, effectif publié, préfixes **cités
   verbatim**.
2. Les **quatre mesures** publiées pour chaque script.
3. Chacun rangé dans **une** des trois classes, et **ce qu'il faudrait** énoncé
   précisément pour chacun.
4. **Aucune exécution**, **aucun rapport modifié** — vérifié par `git status`.
5. La question d'idempotence **déclarée hors de portée**, jamais tranchée par
   supposition.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. La population compte **4** scripts — et non 3, comme la file du #493
   l'annonce.
2. Les 4 se répartissent en **au moins 2 classes** distinctes.
3. **Aucun** ne peut publier son témoin **sans être exécuté** : il n'existe pas
   de voie détournée honnête.

Si la prédiction 1 est réfutée et qu'il n'y en a que 3, alors **la file du #493
avait raison et j'ai mal compté** en écrivant ce pré-enregistrement. Si elle
donne davantage, la dette est plus large qu'annoncée dans quatre entrées
successives.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script, ne **régénère** aucun rapport.
- Il ne **modifie** aucun code : il ne fait qu'établir ce qu'il faudrait.
- Il n'**écrit à la main** dans aucun rapport — publier un témoin en l'éditant
  serait **falsifier une sortie de programme**, et c'est exclu d'avance.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que la dette est plus large
   qu'annoncée.
2. Préfixes, classes et population **inchangés** après mesure.
3. **Aucune exécution**, et l'arbre vérifié propre à la fin.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
