# Pré-enregistrement — détecteur d'auto-inclusion, **deuxième essai**

**Écrit et committé AVANT toute mesure.** **`n_trials = 2`** — voir ci-dessous.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #466.

## Le compte d'essais, d'abord

Le #466 a construit un détecteur, l'a calibré, et il a échoué (rappel 1/2).
**Ce cycle est le deuxième essai de la même hypothèse.** Le protocole
anti-snooping impose de le déclarer et de le compter : **`n_trials = 2`**, et
non 1 comme les cycles précédents.

## Le problème que la calibration ne peut plus résoudre

> **Je connais maintenant la cause de l'échec.** Le #466 a établi que
> `six_reports_regeneration` énumère par `git status` et non par un glob.
> Élargir la règle à cette forme, puis la recalibrer sur les **mêmes 18 cas**,
> c'est **ajuster une règle sur les données qui serviront à la juger.**

La calibration sur la vérité terrain du #463 sera donc **contaminée par
construction**, et un rappel de 2/2 n'y prouvera **rien** : je l'aurai obtenu en
regardant la réponse. Je le publie d'avance pour ne pas pouvoir m'en prévaloir
après.

**D'où un second volet, hors échantillon, qui est le vrai test de ce cycle.**

## La règle élargie — énoncée mot pour mot

Un script est **exposé** s'il réunit les deux conditions :

1. il **écrit** un rapport sous `results/` — `write_text(` sur une variable de
   sortie ;
2. il **prend connaissance** de l'état de `results/`, par **l'une** de ces
   formes :
   - `RESULTS.glob(`, `.iterdir()`, `glob.glob(` ;
   - `ls-tree` ou `ls-files` portant sur `results/` ;
   - **`git status`** ou **`git diff --name-only` / `--name-status`** *(la forme
     que le #466 avait manquée)* ;
   - l'**exécution d'un autre script** (`subprocess` lançant un `.py` du dépôt)
     suivie d'une lecture de `results/`.

**Protégé** s'il porte l'un des signes déclarés au #466 : `unlink(` sur sa
sortie, exclusion nominale, ou filtre sur son propre `<nom>`.

**Exposé et non protégé ⇒ signalé.**

## Le second volet — la validation **hors échantillon**

Puisque la calibration est contaminée, le détecteur est jugé sur des scripts
**qu'aucune vérité terrain ne couvre** :

- univers : les scripts **nouvellement signalés**, inconnus du #463 ;
- échantillon : les **6 premiers par ordre alphabétique** — règle déterministe,
  fixée ici, sans aucun regard préalable sur la liste ;
- chacun est **exécuté deux fois**, empreintes comparées, budget **300 s** par
  exécution ;
- l'arbre est **restauré** après (`git checkout -- results/`), comme au #463.

**C'est la seule mesure de ce cycle qui ait valeur de preuve.**

## Critère de succès — chiffré, il porte sur le procédé

1. **319/319** scripts classés, ou écartés **avec leur raison**.
2. Calibration sur les 18 publiée, **accompagnée de la mention qu'elle est
   contaminée**.
3. Les **6** scripts hors échantillon exécutés, avec leurs **deux empreintes**
   chacun, ou écartés avec leur raison.
4. Arbre **vérifié propre** sous `results/` après restauration.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **Rappel 2/2** sur la vérité terrain. **Cette prédiction ne vaut rien** et je
   l'écris quand même : si elle échouait, la règle élargie serait fausse même
   sur le cas qui l'a motivée.
2. **Au moins 2** des **6** scripts hors échantillon se révèlent réellement non
   idempotents. **C'est la prédiction qui engage.**
3. Les faux positifs sur les 16 sains **restent ≥ 8** — la règle élargie signale
   *plus*, donc elle ne peut pas devenir plus précise sur cet échantillon.

Si la prédiction 2 est réfutée — **0 ou 1** sur 6 —, alors le détecteur
**sur-signale** et sa liste de suspects n'a **pas** de valeur de priorité. Je
devrai l'écrire, et la piste « détection statique » devra être déclarée close
plutôt que retentée une troisième fois.

## Ce que ce cycle ne fait pas

- Il ne **répare** aucun script.
- Il ne **commite** aucun rapport régénéré par la validation.
- Il ne **prétend pas** que « signalé » vaut « défectueux » ailleurs que sur les
  6 réellement exécutés.

## Engagements

1. Résultat rapporté tel quel, y compris si la validation hors échantillon
   condamne le détecteur.
2. Règle et échantillon **inchangés** après mesure. **Aucun troisième essai ne
   sera lancé sans que ce cycle soit publié.**
3. La contamination de la calibration est rappelée **dans le rapport final**.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
