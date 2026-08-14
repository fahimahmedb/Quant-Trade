# Pré-enregistrement — trancher le sort du **citeur du #451**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #471.

## La question laissée ouverte

Le **#451** avait compté, dans son propre tableau, **« 1 rapport qui cite
l'encart sans le porter »**. Le **#469**, appliquant le croisement
rapport ↔ script émetteur **au dépôt d'aujourd'hui**, n'a trouvé **0 citeur
établi**.

Le #469 a refusé de trancher, et a écrit pourquoi :

> Soit son citeur a **disparu du dépôt** depuis, soit **ma règle le classe
> porteur à tort**. Trancher exigerait de remonter à son commit — **non déclaré
> ici**.

**Ce cycle le déclare et le fait.**

## Le protocole — au commit du #451, épinglé

Le commit introducteur de l'entrée #451 est retrouvé par `git log -S` sur son
titre, occurrence la plus ancienne — **même méthode qu'aux #461, #462, #465**.

À ce commit, et **uniquement à ce commit** :

1. lister les rapports de `results/` dont le texte contient
   `Rapport dépendant du dépôt` ;
2. pour chacun, remonter au script producteur par la convention de nommage
   (`_result.md` → `_backtest.py`, `_audit.md` → `_audit.py`,
   `_robustness.md` → `_robustness.py`) ;
3. classer **PORTEUR** si le script **écrit** la marque — une ligne
   `append`/`write`/`print` contenant la chaîne littérale — **CITEUR** sinon.

C'est la règle **corrigée** du #469, celle qui distingue *écrire* de *contenir*.
Sa faiblesse est connue et rappelée ci-dessous.

## L'angle mort, dit d'avance

Le #469 a établi qu'un script qui écrit la marque **par variable** est invisible
à cette règle : `selfref_reports_marking` (le script du #439) en est le cas
type, et il avait produit **un faux citeur** qu'un examen individuel avait dû
retirer.

**Le même examen sera conduit ici, sur chaque citeur trouvé, avant tout
décompte.** Un citeur non examiné ne sera pas compté.

## Ce qui est confronté

Le rapport du #451 lui-même est relu **au même commit**, pour voir s'il **nomme**
le rapport qu'il comptait. Trois issues possibles, toutes publiables :

- il le nomme, **et ma règle trouve le même** → la question est close ;
- il le nomme, **et ma règle en trouve un autre ou aucun** → **ma règle est en
  défaut**, et je le publie ;
- il ne le nomme pas → la comparaison reste **partielle**, et je le dis.

## Critère de succès — chiffré, il porte sur le procédé

1. Le commit du #451 **retrouvé et publié**.
2. **100 %** des rapports contenant la marque à ce commit classés.
3. **Chaque citeur examiné individuellement** avant décompte.
4. Le rapport du #451 relu, et **l'issue des trois ci-dessus explicitement
   nommée**.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **Exactement 1 citeur établi** au commit du #451.
2. Le rapport du #451 **ne nomme pas** le rapport en question — auquel cas la
   comparaison sera partielle. *(Je le prédis parce que le #465 avait cité son
   tableau sans y voir de nom.)*
3. Le citeur trouvé **n'en est plus un aujourd'hui**, ce qui expliquerait le
   0 du #469 **sans mettre ma règle en cause**.

Si la prédiction 1 donne **0**, alors **ma règle manquait déjà le citeur à
l'époque**, et l'explication « il a disparu depuis » tombe : c'est ma méthode
qui serait en cause, et je devrai l'écrire.

## Ce que ce cycle ne fait pas

- Il ne **corrige** aucun rapport ni aucun script.
- Il n'**exécute** rien : lecture d'objets git, aucun effet de bord.
- Il ne **réécrit** aucun verdict.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que ma règle était déjà
   fautive au #469.
2. Protocole et commit **inchangés** après mesure.
3. Chaque citeur **examiné**, jamais seulement compté — leçon des #462, #464,
   #465 et #469.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
