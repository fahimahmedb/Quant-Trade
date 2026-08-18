# Pré-enregistrement — confronter les **31 emprunts** à leur source

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #500.

## Ce que le #500 s'est explicitement interdit

Le #500 a recensé **31 emprunts** dans **24 scripts** — des nombres en gras
attribués à un autre cycle et **retapés** plutôt que relus. Il l'a dit dans son
rapport : *« il mesure une exposition, pas une erreur »*.

**Ce cycle mesure l'erreur.** Chaque emprunt est relu dans la source qu'il
cite.

## La règle de confrontation — **figée ici**

Pour un emprunt porté par le script `S`, citant le cycle `#NNN`, avec le
nombre en gras `x` :

- **la source** est la section `## Backlog #NNN` du fichier
  `NONML_STRATEGY_BACKLOG.md` — le registre publié de ce cycle ;
- **confirmé** : `x` apparaît **en gras** dans cette section ;
- **retrouvé ailleurs** : `x` n'y est pas, mais apparaît **en gras** dans une
  autre section du backlog ou dans un `results/*.md` ;
- **non retrouvé** : `x` n'apparaît en gras **nulle part** ;
- **non vérifiable** : la section `## Backlog #NNN` **n'existe pas**.

## La faiblesse de cette règle, déclarée d'avance

Un nombre à un ou deux chiffres se retrouve **par hasard** : « **5** » figure
dans presque toutes les sections. **Une confirmation sur un petit nombre ne
prouve donc presque rien.**

> Les confirmations sont **comptées séparément** selon que le nombre a
> **1-2 chiffres** (*faible*) ou **≥ 3 chiffres** (*forte*). Publier un taux de
> confirmation global sans cette coupure serait fabriquer une assurance que la
> méthode ne donne pas.

**Et l'absence n'est pas la fausseté** : un « non retrouvé » signale un
emprunt **invérifiable par cette méthode**, pas un chiffre faux. Ce cycle
produit donc une **liste de suspects**, pas un verdict d'erreur.

## Ce qui est mesuré

1. Les **31 emprunts**, chacun avec son script, son cycle cité, son nombre et
   sa classe.
2. Les **quatre classes**, comptées.
3. Les confirmations **fortes** vs **faibles**.
4. Les **non retrouvés**, nommés un par un — la liste de suspects.

## Critère de succès — chiffré, il porte sur le procédé

1. La **règle de confrontation** citée verbatim, ses **quatre classes**
   publiées avec leur compte.
2. **Tous** les emprunts recensés au #500 confrontés — **aucun écarté**.
3. Confirmations **fortes** et **faibles** comptées **séparément**.
4. Les **non retrouvés** nommés individuellement.
5. **Aucun script exécuté**, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Les emprunts **confirmés** (dans la section citée) sont **≥ 20** sur 31.
2. **Au moins 1** emprunt est **non retrouvé** — le canal a produit au moins
   un chiffre orphelin.
3. La **majorité** des confirmations sont **faibles** (nombre à 1-2 chiffres),
   donc de faible valeur probante.

Si la prédiction 3 est vérifiée, la conclusion honnête n'est pas « les
emprunts sont exacts » mais **« la méthode ne sait pas les départager »** — et
il faudra l'écrire ainsi, sans convertir une faiblesse de mesure en satisfecit.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script, ne **corrige** aucun emprunt.
- Il ne **déclare faux** aucun chiffre : la méthode ne peut pas l'établir.
- Il ne **réécrit** aucun rapport — le #499 a montré qu'ils ne sont plus
  committables.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si **tout** est confirmé et que le
   cycle ne trouve rien.
2. Règle, classes et population **inchangées** après mesure.
3. La coupure **forte / faible** publiée **même si elle affaiblit** le
   résultat — surtout si elle l'affaiblit.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
