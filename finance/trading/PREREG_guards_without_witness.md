# Pré-enregistrement — les **gardes sans témoin inconditionnel**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #480.

## La question, telle que le #478 l'a posée

Le #478 a compté **58** titres de section écrits sous une garde, dans **31**
scripts, et a conclu que le comptage n'était pas la bonne mesure :

> **La ligne de partage n'est pas « section conditionnelle ou non », mais
> « la garde a-t-elle un témoin inconditionnel ».**

Une section gardée dont l'**effectif est publié sans garde** juste avant ne
disparaît pas silencieusement : le lecteur voit « divergents : **0** » puis pas
de section « Divergents », et comprend. Une section gardée **sans** ce témoin
s'efface sans laisser de trace — c'est la forme qui a coûté **trois cycles**
(#469, #472, #475).

Le #478 l'a établi **à la main sur cinq scripts** et a écrit qu'il ne pouvait
pas l'extrapoler. **Ce cycle le mesure sur toute la population.**

## La règle — fixée ici, avant de regarder

Pour chaque titre de section conditionnel (repéré par **AST**, comme au #478) :

1. remonter à sa **garde la plus interne** ;
2. si elle est de la forme `if <var>:` ou `if not <var>:`, retenir `<var>` ;
3. chercher, **dans la même fonction**, une ligne d'écriture
   (`append`/`write`/`print`) **sous aucune garde** qui mentionne `<var>`.

Classement :

- **AVEC TÉMOIN** — une telle ligne existe : la disparition est **signalée** ;
- **SANS TÉMOIN** — aucune : la section s'efface **silencieusement** ;
- **GARDE NON NOMMÉE** — la garde n'est pas de la forme `if <var>:` (condition
  composée, test de valeur, boucle). **Ma règle ne sait pas la traiter** : ces
  cas sont comptés **à part** et **jamais présentés comme fautifs**.

## Ce que « sans témoin » n'est PAS

**Ce n'est pas une faute.** Une section peut légitimement n'exister que dans un
cas particulier sans que rien ne manque au lecteur — un développement
supplémentaire, une remarque annexe. Le défaut du #475 est plus étroit : la
section gardée portait **l'unique mention de son sujet**, si bien que son
absence était **indiscernable** d'un sujet inexistant.

**Ma règle mécanique ne distingue pas les deux** : elle mesure une
**prévalence**, pas une culpabilité, et le rapport devra le dire à l'endroit du
chiffre.

## L'examen à la main — DÉCLARÉ ICI, avant mesure

Le **#480** a classé mécaniquement, découvert après coup que sa règle avait mal
lu, et a dû refuser le reclassement parce qu'aucun examen n'avait été déclaré.
**La leçon est appliquée ici :**

**Jusqu'à 5 cas « sans témoin »** — pris dans l'ordre alphabétique du script,
puis par numéro de ligne croissant — sont **lus un par un**, et chacun reçoit un
verdict **écrit à la main** :

- **MASQUANT** — la section gardée est la **seule** mention de son sujet dans le
  rapport ; son absence est indiscernable d'un sujet inexistant (forme #475) ;
- **ANODIN** — le sujet est mentionné ailleurs, ou la section est un
  développement dont l'absence ne cache rien.

Ce verdict **fait partie du résultat pré-enregistré**, pas d'un constat
post-hoc.

## Critère de succès — chiffré, il porte sur le procédé

1. Tous les titres conditionnels classés, effectif publié, **écart au #478
   signalé**.
2. **Chaque « sans témoin » nommé** avec son script, son numéro de ligne et sa
   garde **verbatim**.
3. Les **gardes non nommées** comptées à part, et **explicitement** exclues de
   tout total présenté comme une dette.
4. **Jusqu'à 5 « sans témoin » examinés à la main**, chacun avec son verdict.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **≥ 30** des titres conditionnels ont un **témoin inconditionnel**.
   *(Fondement : le #478 en a trouvé dans 4 cas sur 5 lus.)*
2. **≤ 15** sont **sans témoin**.
3. Sur les **≤ 5** examinés, **≥ 1** est **MASQUANT** — donc le cas du #475 a au
   moins un frère dans le dépôt.

Si la prédiction 3 est réfutée — **aucun masquant parmi les examinés** — alors
le cas du #475 est **isolé**, la piste ouverte depuis le #478 se referme, et je
devrai l'écrire sans chercher à la prolonger.

## Ce que ce cycle ne fait pas

- Il ne **corrige** aucun script ni aucun rapport.
- Il n'**exécute** aucun script du dépôt : lecture du disque, **aucun effet de
  bord**.
- Il ne **rouvre** pas le cas du #475, tranché, ni les verdicts du #478.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique à perturber.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que le cas du #475 est
   isolé.
2. Règle, classement et taille d'échantillon **inchangés** après mesure.
3. **Aucun total présenté comme un compte de fautes**, et les gardes non nommées
   jamais fondues dedans.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
