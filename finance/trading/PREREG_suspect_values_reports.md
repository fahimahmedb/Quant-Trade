# Pré-enregistrement — chercher les **13 valeurs suspectes** dans les **rapports**, pas dans le registre

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #503.

## Pourquoi elles restent seules

Le #503 a expliqué **15** des 29 suspects par un **artefact de méthode** — leur
chiffre est simplement **repris plus tard**, ce qu'un détecteur aveugle au
temps prenait pour une erreur d'attribution. **Les 13 « valeurs suspectes » ne
sont expliquées par rien.**

Mais les #501 à #503 n'ont interrogé **qu'une source** : la section
`## Backlog #NNN` du registre. **Un cycle publie aussi un rapport**, et c'est
même là que ses chiffres naissent. **Le registre en est le résumé, pas
l'original.**

> Chercher un chiffre dans le résumé et conclure qu'il n'existe pas est une
> faute de méthode que trois cycles ont commise sans la voir.

## La règle de correspondance cycle → rapport — **figée ici**

Pour un cycle `#NNN` :

1. sa **section** de registre est lue ;
2. le **nom de stratégie** en est extrait par `PREREG_([a-z0-9_]+)\.md` ;
   à défaut, par `nonml_([a-z0-9_]+)_(?:result|audit|backtest)` ;
3. ses **rapports** sont tous les `results/nonml_<nom>_*.md` existants.

**Classes** (règle contextuelle du **#502 reprise sans modification** —
**6 lettres**, **±200 caractères**, **2 mots-clés**) :

| Classe | Condition |
|---|---|
| **confirmé au rapport** | le nombre est en gras dans un rapport du cycle cité, **avec** ≥ 2 mots-clés dans la fenêtre |
| **présent sans contexte** | en gras dans un rapport, **< 2** mots-clés |
| **absent du rapport** | pas en gras dans ses rapports |
| **rapport introuvable** | aucun nom de stratégie extractible, ou aucun fichier |

Les paramètres du #502 sont **repris tels quels**. Les retoucher ici serait
régler un détecteur sur la population qu'il doit juger — refusé au #503, refusé
encore.

## Ce qui est mesuré

1. Les **13** valeurs suspectes classées par les quatre classes.
2. La **correspondance** cycle → rapport, publiée cycle par cycle : quel nom,
   combien de fichiers.
3. La **couverture comparée des deux sources** : combien de ces 13 le
   **registre** confirmait (par construction **0**) contre combien le
   **rapport** confirme.
4. Les **résidus** — absents des deux sources — nommés un par un.

## Critère de succès — chiffré, il porte sur le procédé

1. La règle de correspondance citée verbatim, paramètres du #502 **inchangés**.
2. Les **13** classées, **quatre classes** publiées avec leur compte.
3. La correspondance cycle → rapport publiée **cycle par cycle**.
4. Les **résidus** nommés individuellement.
5. **Aucun script exécuté**, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **≥ 6** des 13 sont **confirmés au rapport** — le registre était la
   mauvaise source pour au moins la moitié d'entre eux.
2. **≥ 1** cycle cité a un **rapport introuvable** par cette règle.
3. **≥ 1** résidu subsiste — absent du registre **et** de ses rapports. Toutes
   les valeurs suspectes ne s'expliquent pas par la source consultée.

Si la prédiction 3 est réfutée et que **tout** s'explique par le changement de
source, alors les quatre cycles #500-#503 n'auront mesuré que **les limites de
leur propre lecture**, et aucun emprunt douteux ne subsistera. Ce serait un
résultat net, et je devrai l'écrire sans le nuancer.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script, ne **corrige** aucun emprunt.
- Il ne **déclare faux** aucun nombre : un résidu reste un **soupçon**, et la
  liste des sources consultées n'est **toujours pas exhaustive** — un chiffre
  peut vivre dans un `PREREG_`, un commentaire de code ou un message de commit.
- Il ne **modifie** pas les classes du #503.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que **trois cycles ont
   interrogé la mauvaise source**.
2. Règle, paramètres et population **inchangés** après mesure.
3. Les deux sources comparées **côte à côte**, jamais la seule favorable.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
