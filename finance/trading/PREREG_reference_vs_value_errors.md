# Pré-enregistrement — **erreur de référence** ou **erreur de valeur** ?

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #502.

## L'état de la question

Le #502 laisse **29 emprunts suspects** : **14 sur-crédités** (le nombre est
dans la section citée, mais pas au même sujet) et **15 absents** (le nombre
n'est pas en gras dans la section citée).

**On ne sait pas de quoi ils souffrent.** Deux maladies très différentes se
confondent sous ce mot de « suspect » :

- **erreur de référence** — le chiffre est juste, mais il vient d'**un autre
  cycle** que celui qui est cité ;
- **erreur de valeur** — le cycle cité est le bon, mais le **nombre** ne s'y
  trouve pas.

## Les définitions — **figées ici**

- **magnitude** d'un nombre : le **nombre de chiffres de sa partie entière**
  (`113` → 3). Deux nombres sont « de même grandeur » s'ils ont la même
  magnitude ;
- **section candidate** : une section `## Backlog #MMM` **autre** que celle
  citée, où le nombre apparaît **en gras** **et** avec **≥ 2 mots-clés** de
  l'emprunt dans une fenêtre de **±200 caractères** — c'est-à-dire la règle
  contextuelle du **#502, reprise sans modification** ;
- **grandeur présente** : la section **citée** contient au moins un nombre en
  gras de **même magnitude** que le nombre emprunté.

**Classes** :

| Classe | Condition |
|---|---|
| **référence probable ailleurs** | ≥ 1 section candidate |
| **valeur suspecte** | 0 section candidate, **et** grandeur présente dans la section citée |
| **indéterminé** | 0 section candidate, **et** aucune grandeur de ce rang dans la section citée |

Les paramètres du #502 (**6 lettres**, **±200 caractères**, **2 mots-clés**)
sont **repris tels quels**. Les retoucher ici reviendrait à régler un
détecteur sur la population qu'il doit juger.

## Ce qui est mesuré

1. Les **29 suspects** classés, par les trois classes.
2. Le détail par origine — **sur-crédités** vs **absents**, séparément :
   rien ne dit qu'ils souffrent de la même chose.
3. Les **« référence probable ailleurs »** nommés, avec leurs sections
   candidates et **combien** ils en ont.
4. Ceux dont la section candidate est **unique** — les seuls pour lesquels une
   correction serait **nommable**.

## Critère de succès — chiffré, il porte sur le procédé

1. Les **trois définitions** citées verbatim, paramètres du #502 **inchangés**.
2. Les **29** suspects classés, **trois classes** publiées avec leur compte.
3. Le détail **sur-crédités / absents** publié **séparément**.
4. Les « référence probable ailleurs » nommés, avec le **nombre** de sections
   candidates, et ceux à candidate **unique** distingués.
5. **Aucun script exécuté**, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Les **« référence probable ailleurs »** sont **≥ 5** sur 29.
2. Les **absents** et les **sur-crédités** se répartissent **différemment** :
   la part de « référence probable ailleurs » diffère d'au moins **20 points**
   entre les deux groupes.
3. **Au moins 1** suspect a une section candidate **unique**.

Si la prédiction 2 est réfutée, alors les deux groupes du #502 souffrent de la
même chose et **la distinction sur-crédité / absent ne recouvre rien** — ce
qui affaiblirait rétrospectivement la lecture du #502.

## Ce que ce cycle ne fait pas — et c'est essentiel

- Il ne **corrige** aucune référence : « probable » n'est pas « établi ».
- Il ne **déclare faux** aucun nombre. Une section candidate peut parler du
  même sujet **par hasard** — le dépôt répète ses thèmes d'un cycle à l'autre,
  et c'est précisément ce qui rend cette méthode faillible.
- Il n'**exécute** aucun script.

> **Le mot « probable » n'est pas une précaution de style** : la méthode
> produit des **hypothèses de correction**, pas des corrections.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si **tout** tombe en « indéterminé »
   et que le cycle ne sépare rien.
2. Définitions, paramètres et population **inchangés** après mesure.
3. Les deux groupes publiés **séparément**, jamais fondus en un total qui
   masquerait leur différence.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
