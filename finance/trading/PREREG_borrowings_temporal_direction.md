# Pré-enregistrement — la **direction temporelle** des 21 emprunts « B tiers »

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #508.

## L'enjeu

Le #508 a classé **26** emprunts en **B** — sourcés au sujet, mais **ailleurs**
que dans le cycle qu'ils citent. **5** sont circulaires (contexte trouvé dans
le rapport du script lui-même) ; il en reste **21 « tiers »**.

Un emprunt qui cite le #449 mais dont le contexte vit au #465 est-il une
**erreur de citation**, ou une **reprise légitime** par un cycle ultérieur ?

Le **#503** a déjà tranché ce point une fois : **une source postérieure ne
prouve rien**, parce que ce registre reprend ses chiffres vers l'avant. Le
même test n'a jamais été appliqué aux **B tiers**.

## La règle de datation — **figée ici**

Les dates sont des **premiers commits d'ajout**, jamais l'état courant :

```
git log --diff-filter=A --reverse --format=%ct -- <chemin>
```

- **date du cycle cité `#NNN`** : celle de son `PREREG_<nom>.md`, où `<nom>`
  est extrait de sa section par la règle du **#504** (`PREREG_([a-z0-9_]+)\.md`,
  à défaut `nonml_([a-z0-9_]+)_(?:result|audit|backtest)`) ;
- **date de la source** : celle du **fichier** où le contexte a été trouvé —
  le rapport lui-même, ou le `PREREG_` du cycle si la source est une section
  du registre.

## Les trois classes

| Classe | Condition |
|---|---|
| **postérieure** | date de la source **>** date du cycle cité |
| **antérieure** | date de la source **<** date du cycle cité |
| **indatable** | l'une des deux dates est introuvable |

## Ce que chaque classe permet de conclure — **dit d'avance**

- **postérieure** : **rien**. Le chiffre a simplement été **repris plus tard**,
  ce qui est le fonctionnement normal d'un registre où chaque cycle commente
  les précédents. Leçon du #503, appliquée telle quelle.
- **antérieure** : le chiffre **existait au sujet avant** le cycle cité. C'est
  un **candidat sérieux d'erreur de citation** — le bon cycle serait
  l'antérieur. **Candidat**, pas verdict.
- **indatable** : rien non plus, et il faudra le compter.

> **Le résultat utile de ce cycle est le compte des antérieures.** S'il vaut
> zéro, alors les 21 « tiers » s'expliquent **entièrement** par la reprise
> vers l'avant, et la classe B du #508 ne désigne **aucune** erreur.

## Ce qui est mesuré

1. Les **21** emprunts « B tiers », classés par les trois classes.
2. Les **antérieures**, nommées avec **les deux dates** et l'écart en jours.
3. Ce qui **reste** après retrait des postérieures et des indatables.
4. Le **rappel chiffré** de ce que la classe B du #508 vaut après ce filtre.

## Critère de succès — chiffré, il porte sur le procédé

1. La règle de datation et la **commande** citées verbatim.
2. Les **21** classés, **trois classes** publiées avec leur compte.
3. Les **antérieures** nommées avec leurs deux dates.
4. La conclusion « postérieure ne prouve rien » **rappelée et chiffrée**.
5. **Aucun script exécuté**, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **≥ 15** des 21 sont **postérieures**.
2. **≥ 1** est **antérieure** — il subsiste au moins un candidat d'erreur de
   citation.
3. Les **indatables** sont **0**.

Si la prédiction 2 est réfutée et qu'aucune source antérieure n'existe, alors
**neuf cycles d'enquête sur les emprunts se terminent sans un seul candidat
d'erreur**, et la conclusion de toute la série sera que ce canal, bien que
réel, **n'a jamais produit de faute repérable**. Je l'écrirai ainsi.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script, ne **corrige** aucune citation.
- Il ne **déclare fausse** aucune citation : « antérieure » ouvre un soupçon
  fondé, il ne le clôt pas. Une même grandeur peut légitimement apparaître
  dans deux cycles.
- Il ne **reclasse pas** les 5 circulaires du #508 — ils restent hors de cette
  population, comme le #508 les a laissés.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris s'il **clôt la série sans rien
   trouver**.
2. Règle de datation et population **inchangées** après mesure.
3. Le mot **« candidat »** ne sera pas durci après coup.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
