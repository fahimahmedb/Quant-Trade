# Pré-enregistrement — les **5 résidus** dans les sources **non publiées**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #504.

## L'enjeu

Cinq cycles (#500-#504) ont réduit **39** nombres empruntés à **5 résidus** :
des chiffres attribués à un cycle, introuvables **au registre** comme **aux
rapports** de ce cycle.

Toutes les sources consultées jusqu'ici sont **publiées**. Il en reste trois
qui ne le sont pas :

- les **pré-enregistrements** (`PREREG_*.md`) ;
- les **commentaires et docstrings** du code ;
- les **messages de commit**.

> Si un résidu s'y trouve, l'emprunt est **sourcé mais mal cité**. S'il ne s'y
> trouve **nulle part**, c'est le **premier candidat sérieux** de toute la
> série — et il faudra le dire sans l'atténuer.

## Les règles d'appariement — **figées ici**, et pourquoi elles diffèrent

| Famille | Extraction | Appariement du nombre |
|---|---|---|
| `PREREG_*.md` | fichier entier | **en gras** — ce sont des documents markdown |
| commentaires / docstrings | jetons `COMMENT` de `tokenize` + docstrings par AST | **jeton nu** (`\b<val>\b`) |
| messages de commit | `git log --format=%B` sur tout l'historique | **jeton nu** |

**Le nombre nu est plus permissif que le gras** : un commentaire ou un message
de commit n'emploie pas de balisage. Pour compenser, **la contrainte de
contexte reste identique** — ≥ **2 mots-clés** de l'emprunt dans **±200
caractères**, règle du **#502 reprise sans modification**.

**Les paramètres du #502 ne bougent pas.** Refusé au #503, au #504, refusé
encore.

## Les classes — par **ordre de priorité déclaré**

1. **sourcé au `PREREG_` du cycle cité** ;
2. **sourcé dans un autre `PREREG_`** ;
3. **sourcé dans un commentaire ou une docstring** ;
4. **sourcé dans un message de commit** ;
5. **introuvable partout**.

Un résidu peut toucher **plusieurs** familles. L'ordre ci-dessus décide de sa
classe, **mais toutes ses trouvailles seront publiées** — ne montrer que la
gagnante masquerait la redondance des sources.

## Ce qui est mesuré

1. Les **5 résidus** classés par les cinq classes.
2. Pour chacun, **toutes** les familles où il est trouvé, pas seulement la
   première.
3. La **contribution de chaque famille** : combien de résidus elle explique
   seule, combien elle explique en doublon.
4. Les **introuvables partout**, nommés — avec leur extrait d'emprunt.

## Critère de succès — chiffré, il porte sur le procédé

1. Les **trois familles** et leurs règles d'appariement citées verbatim, avec
   la justification de l'appariement nu.
2. Les **5** résidus cherchés dans les **trois** familles, résultats publiés
   par famille.
3. Classement par priorité **et** liste complète des trouvailles.
4. Les **introuvables partout** nommés individuellement, avec extrait.
5. **Aucun script exécuté**, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **≥ 2** des 5 résidus sont trouvés dans au moins une source non publiée.
2. **≥ 1** reste **introuvable partout**.
3. Les **messages de commit** expliquent **le moins** de résidus des trois
   familles — au plus **1**.

Si la prédiction 2 est réfutée et que **les 5** s'expliquent, alors six cycles
d'enquête n'auront trouvé **aucun emprunt faux**, et la conclusion de la série
sera que **le canal d'erreur soupçonné au #497 n'a produit aucune erreur
détectable**. C'est un résultat net et je devrai l'écrire tel quel, sans le
présenter comme un demi-succès.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script, ne **corrige** aucun emprunt.
- Il ne **déclare faux** aucun nombre, même un introuvable : l'appariement nu
  est **permissif**, et son échec est d'autant plus significatif — mais
  l'absence de trace reste une **absence de preuve**, pas une preuve
  d'absence.
- Il ne **modifie** pas les classes des cycles précédents.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris s'il **innocente tout** et rend la
   série stérile.
2. Règles, paramètres et population **inchangés** après mesure.
3. Toutes les familles publiées, jamais la seule qui arrange.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
