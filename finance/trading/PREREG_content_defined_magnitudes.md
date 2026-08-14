# Pré-enregistrement — les grandeurs définies par le **contenu**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #464.

## Pourquoi ce cycle existe

Le **#462** a construit une table de référence des grandeurs du dépôt — et a
conclu, contre lui-même, que **trois des quatre faux connus lui échappaient** :

> « Consommateurs d'une règle » (#449) et « porteurs d'un encart » (#451) se
> définissent par le **contenu** des fichiers, pas par leur nom. Les six
> grandeurs comptent des **totaux**, et en ajouter une maintenant serait
> ajuster l'instrument au résultat.

Ce cycle est l'instrument qui manquait : il compte par le **contenu**, et il
est déclaré **avant** de regarder quoi que ce soit.

## Les deux grandeurs — définies ici, et la distinction qui décide

**G1 — consommateurs de la règle de verdict.** Fichiers de
`finance/trading/scripts/` dont le contenu contient `import nonml_verdict` ou
`from nonml_verdict`.

**G2 — porteurs de l'encart de dépendance.** Fichiers `.md` de
`finance/trading/results/` qui **portent** la marque, c'est-à-dire dont une
ligne, décoration retirée, **commence par** `**Rapport dépendant du dépôt**`.

> **La distinction est le cœur du cycle.** Le #451 a établi que le « 6 » du
> backlog était faux parce qu'il comptait comme marqués des rapports qui
> **parlent** de l'encart. C'est exactement le défaut du #446 sur la règle de
> verdict : *porter* n'est pas *mentionner*.

Je mesure donc **les deux** : les **porteurs** (G2) et les **mentionneurs** —
fichiers contenant la phrase sans la porter en tête de ligne. **G2 est la
grandeur ; l'écart entre les deux est le mécanisme du faux.**

## L'univers — les 18 commits épinglés

Les entrées **#443 à #460**, chacune à son commit introducteur — **le même
univers et le même épinglage qu'aux #461, #462 et #463**, pour que les quatre
cycles se comparent. Soit **36** cellules (2 grandeurs × 18 commits), plus les
mentionneurs.

Le #464 a établi que la convention `PREREG_` est **parfaitement suivie** sur cet
intervalle : l'appariement n'y est donc pas en cause.

## Ce qui est confronté — les deux faux connus

| Entrée | Ce qu'elle annonçait | Ce que le backlog dit après coup |
|---|---|---|
| #449 | **8** scripts consommateurs | « le compte de 8 était faux » — il en cite **six** |
| #451 | **6** rapports portant l'encart | « le 6 du backlog était faux » |

**Recomptés au commit de chaque entrée**, valeur vraie publiée.

## Critère de succès — chiffré, il porte sur le procédé

1. **36/36** cellules produites, ou manquantes **avec leur raison**.
2. Les **deux** faux connus recomptés, chacun avec sa valeur vraie au commit.
3. La distinction **porte / mentionne** publiée avec ses deux chiffres — pas
   seulement le total.
4. Définitions **inchangées** après mesure.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Au commit du **#449**, G1 **≠ 8** — et je précise : **= 6**, le nombre que
   l'entrée elle-même cite dans son texte de correction.
2. Au commit du **#451**, G2 **≠ 6**.
3. À ce même commit, **mentionneurs > porteurs** — c'est le mécanisme par lequel
   le « 6 » s'est formé.

Si la prédiction 1 est réfutée et que G1 vaut **8**, alors **c'est la correction
du #449 qui était fausse**, pas le compte d'origine — et je devrais le publier
tel quel, y compris si cela contredit trois cycles de dette inscrite.

## Ce que ce cycle ne peut pas faire

- Il ne couvre **que deux** grandeurs de contenu. Le faux du **#453**
  (« 13 orphelins ») est une **relation** entre deux globs, toujours hors de
  portée — et je n'ajoute rien pour lui.
- `import nonml_verdict` ne capture pas un script qui **réimplémenterait** la
  règle sans l'importer. Les #446-#448 ont montré que de telles copies ont
  existé. **G1 est donc une borne inférieure**, et le rapport le dira.

## Ce que ce cycle ne fait pas

- Il ne **corrige** aucun chiffre du backlog : publié et inscrit, pas réparé au
  passage — engagement tenu depuis le #450.
- Il ne **rejoue** aucun script : lecture seule, aucun effet de bord (#463).
- Il ne juge **aucune stratégie**.

## Engagements

1. Résultat rapporté tel quel, y compris s'il **innocente** un compte que trois
   cycles ont déclaré faux.
2. Définitions et univers **inchangés** après mesure.
3. La borne inférieure de G1 est rappelée dans le rapport final.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
