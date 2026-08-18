# Pré-enregistrement — réparer le **seul candidat actionnable**

**Écrit et committé AVANT toute mesure et avant toute modification.**
`n_trials = 1`.

**Cycle de MODIFICATION**, première piste de la file ouverte au #510.

## La cible

`nonml_battery_backfill_lot_audit.py` est, après le #507, le **seul des 13
« réparables » qui soit à la fois candidat committable et sans dépendance à
`sys.argv`**. Le #485 lui reproche deux chiffres en dur :

- l. 131 : « son overlay **0,00 %** du temps » ;
- l. 168 : « reste **1** candidat hors de portée de l'outil (schéma panier) ».

## Ce que j'ai constaté **avant** d'écrire ce pré-enregistrement

**J'ai lu le code de la cible pour concevoir un geste borné** — comme au #499.
Cette lecture a montré une chose que je dois déclarer **maintenant**, et qui
ne sera **pas** comptée comme une prédiction :

> Le script **ne lit aucun `.npz`**. Sa seule source est `read_battery()`, qui
> relit des rapports `.md`. **Le « 0,00 % » n'est donc dérivable par aucune
> donnée qu'il possède** — contrairement à ce qu'affirme la justification du
> #485 (« il lit les `.npz` d'activation »). En revanche, `SET_ASIDE` est un
> dictionnaire du module, et le nombre de candidats écartés **pour schéma
> panier** en est directement dérivable.

**Une prédiction dont je connais déjà la réponse n'est pas une prédiction.**
Ce constat sera **publié comme mesure**, pas crédité comme anticipation.

## Le périmètre de réparation — **délimité ici**

- **Réparé** : le « **1** » de la l. 168, remplacé par un compte dérivé de
  `SET_ASIDE` sur le motif **panier**.
- **Non réparé** : le « **0,00 %** » de la l. 131. **Aucune donnée du script
  ne le produit** ; l'interpoler exigerait d'aller lire une source qu'il
  n'ouvre pas, ce qui n'est plus « une interpolation » mais un cycle distinct.

## La règle du geste borné — reprise du #489/#499, appliquée telle quelle

1. La **classe** de la cible est réétablie **par AST** : **0** primitive
   d'exécution (règle du #497, **importée**), **0** balayage de `scripts/` ou
   `results/`, **0** appel `git`, **0** `sys.argv` — les trois causes du #507
   plus son angle mort.
2. Le script est exécuté **une fois**.
3. Le **diff de son rapport** doit se réduire à la **ligne réparée**. Toute
   autre ligne modifiée fait **échouer** le cycle.
4. En cas d'échec : **restauration ciblée**, **rien n'est committé**, FAIL
   publié.
5. **En cas de succès, la réparation EST committée.** C'est la différence avec
   le #499 : si le geste est borné, il doit aboutir, sinon le mot
   « actionnable » du #507 ne veut rien dire.

## Ce qui est mesuré

1. Les **quatre causes de non-committabilité**, toutes à zéro ou non.
2. Le **diff du `.py`**, publié.
3. Le **diff du rapport**, publié en entier.
4. La **valeur calculée** face au littéral **1**.
5. Le sort du « 0,00 % » : **justification du #485 confrontée au code**.

## Critère de succès — chiffré

1. Les **quatre causes** mesurées et publiées.
2. Diff du `.py` **limité** à la ligne réparée et à ce qu'elle exige.
3. Diff du rapport **réduit à la ligne réparée** — **0** autre ligne.
4. Valeur calculée publiée face au littéral.
5. Justification du #485 sur le « 0,00 % » **confrontée au code et tranchée**.

> **PASS** = les cinq points, **et la réparation est committée**.
> **FAIL** = un seul manque, **et tout est restauré**.

## Prédictions — falsifiables, et sur ce que j'ignore

1. Le diff du rapport est **vide ou limité à la ligne réparée** — je ne sais
   pas si ce rapport a dérivé depuis sa dernière écriture.
2. La valeur calculée vaut **1**, comme le littéral.
3. Les **quatre causes** valent **0** — la classe C du #507 tient encore.

Si la prédiction 1 est réfutée, alors **aucun des 13 « réparables » n'est
committable**, et le compte du #485 ne décrira **rien d'actionnable du tout**.

## Ce que ce cycle ne fait pas

- Il ne touche **pas** au « 0,00 % », ni à aucun autre script.
- Il ne touche **pas** aux données (`data/`).
- Il ne **régénère** aucun autre rapport.

## Simulation 300 € et robustesse

**Sans objet** : cycle de réparation, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, **FAIL et restauration compris**.
2. Périmètre **inchangé** après mesure.
3. Le constat sur le « 0,00 % » **n'est pas compté comme une prédiction**.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
