# Pré-enregistrement — **dater** le basculement forme / mesure

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #509.

## L'état de la question

Le **#506** a mesuré que **95 %** de ses 20 derniers scripts à verdict
n'ouvrent **aucune donnée**, alors que le dépôt entier est à **28 %**. Son
audit a montré que la population figée n'était **pas représentative** et que
**72 %** des **346** rapports à verdict sont produits par un script qui lit
réellement des données.

**Constater un écart entre la queue et l'ensemble ne date rien.** Il reste à
savoir **quand** le dépôt a changé de nature — ou s'il n'a jamais changé et
que la queue n'est qu'une fluctuation.

## La population — celle de l'**audit** du #506, pas celle de son backtest

Tous les scripts `nonml_*_backtest.py` dont le rapport porte un verdict
`PASS`/`FAIL`, **en gras ou non**. C'est la population **élargie**, celle qui
s'est révélée représentative.

**Classement par les appels d'ouverture**, route de l'audit du #506 : un
script est **de mesure** s'il **ouvre** effectivement un `.txt`, `.npz` ou
`.csv` — *nommer un fichier n'est pas l'ouvrir*.

## La règle de datation — **figée ici**

1. Les scripts sont ordonnés par **premier commit d'ajout**
   (`git log --diff-filter=A --reverse`).
2. Pour chaque coupure possible entre deux scripts consécutifs, on calcule la
   part de **« sans données »** **avant** et **après**.
3. Le **basculement** est la coupure qui **maximise le contraste**
   `part_après − part_avant`.
4. Chaque côté doit compter **au moins 20** scripts — sinon la coupure est
   ignorée. Ce plancher est **figé ici** et empêche qu'un maximum trivial en
   bout de série soit retenu.

**Aucun seuil n'est ajusté après mesure.** Le point de coupure n'est pas
choisi : il est **calculé**.

## Ce qui est mesuré

1. La **date** du basculement, avec les deux parts et le **contraste**.
2. La **chronologie par tranches** — le lecteur doit pouvoir juger sur pièce
   plutôt que sur un seul point.
3. La **part avant** et la **part après**, en effectifs comme en pourcentage.
4. Le **deuxième meilleur** point de coupure et son contraste — si un second
   maximum presque aussi bon existe ailleurs, **la date n'est pas nette** et
   il faut le dire.

## Critère de succès — chiffré, il porte sur le procédé

1. La règle de coupure et son **plancher de 20** cités verbatim.
2. Population élargie, taille publiée, classement par **appels d'ouverture**.
3. Date, deux parts et contraste publiés.
4. Chronologie par tranches **et** deuxième meilleur point publiés.
5. **Aucun script exécuté**, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Le basculement est daté **après le 13/08/2026** — la date de naissance de
   la convention d'auto-déclaration établie au #483 et confirmée au #498.
2. Le contraste au maximum est **≥ 40 points**.
3. Avant le basculement, la part de « sans données » est **≤ 20 %**.

Si la prédiction 2 est réfutée et que le contraste reste faible, alors **il
n'y a pas de basculement** — seulement une dérive continue, ou une queue
atypique. Je devrai l'écrire ainsi et retirer le mot « basculement », que ce
pré-enregistrement emploie **par hypothèse et non par constat**.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script, n'en **modifie** aucun.
- Il ne **juge pas** qu'un verdict rendu sans données soit moins bon. Il date
  un **changement d'activité**, pas une perte de qualité.
- Il ne **se compte pas lui-même** : ce script serait, une fois de plus, un
  script à verdict qui n'ouvre aucune donnée. **Auto-exclusion déclarée**
  (règle du #447), rappelée dans le rapport.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris s'il **n'y a pas de basculement**.
2. Règle de coupure, plancher et population **inchangés** après mesure.
3. Le **deuxième meilleur** point publié même s'il affaiblit la conclusion —
   surtout s'il l'affaiblit.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
