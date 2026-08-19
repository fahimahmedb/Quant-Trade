# Pré-enregistrement — le régime postérieur au basculement : **procédé** ou **grandeur** ?

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #515.

## La question laissée par le #510 et le #512

Le **#510** a daté un basculement — **13/08/2026 21:51** — après lequel les
scripts à verdict cessent d'ouvrir des données de marché (régime
« sans données », **0 exception** sur les 62 scripts postérieurs mesurés à
l'époque). Le **#512** a montré, sur un cas précis, qu'un cycle peut
**satisfaire tous ses critères de publication tout en produisant une mesure
sans valeur** — un PASS purement **procédural**.

> **Combien, dans ce régime postérieur, sont des PASS qui portent sur une
> vraie grandeur du dépôt, et combien ne sont que des confirmations de
> procédure ?**

## La règle de classement — **figée ici**, textuelle et vérifiable

**Date pivot, reprise du #510 sans recalcul** : **13/08/2026 21:51:00 UTC**
(`1755553860`). *(Recalculer le basculement ici referait le travail du
#510 sur une population qui a bougé depuis — la date déjà auditée est
reprise telle quelle.)*

**Population** : tous les `nonml_*_backtest.py` dont le rapport porte un
verdict `PASS`/`FAIL` (en gras ou non, comme au #506 après correction de
son audit) **et** dont la date d'introduction (`git log --diff-filter=A`)
est **≥** la date pivot.

**Classement, par script, sur son verdict final `PASS`** *(les `FAIL` sont
comptés à part — un `FAIL` peut aussi porter sur une grandeur ou non, mais
la question du #510 visait les PASS)* :

- **PROCÉDURAL** : le rapport contient la phrase **« porte sur le
  procédé »** (verbatim, insensible aux emojis/gras environnants) ;
- **SUBSTANTIEL** : `PASS` sans cette phrase.

Cette phrase est employée comme **auto-déclaration constante** depuis le
#496 dans cette série précisément pour distinguer les deux cas — ce cycle
ne l'invente pas, il la **compte**.

## Ce qui est mesuré

1. La population des scripts du régime postérieur, et le nombre de `PASS`.
2. Le compte **PROCÉDURAL** vs **SUBSTANTIEL** parmi les PASS.
3. Pour les **SUBSTANTIEL** (s'il y en a) : nommés un par un, avec un
   extrait de leur grandeur publiée.
4. Le compte des `FAIL` du régime, pour situer le total.

## Critère de succès — chiffré

1. La règle de classement citée verbatim, date pivot rappelée.
2. Population et compte PASS/FAIL publiés.
3. Compte PROCÉDURAL/SUBSTANTIEL publié, **même si SUBSTANTIEL = 0**.
4. Les SUBSTANTIEL nommés individuellement (ou l'absence explicitement dite).
5. **Aucun script exécuté**, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.
> **Le PASS de CE cycle ne dépend pas du résultat trouvé** — seulement de
> la publication honnête du compte, procédural compris (leçon du #513).

## Prédictions — falsifiables

1. **≥ 90 %** des PASS du régime sont PROCÉDURAL.
2. **SUBSTANTIEL = 0** — aucune exception.
3. Le nombre total de scripts du régime postérieur est **≥ 62** (le #510 en
   comptait 62 à sa date ; ce fil (#496-#515 et ce cycle) en a ajouté
   depuis).

Si la prédiction 2 est réfutée, les exceptions substantielles seront
nommées — ce serait la première mesure concrète du régime postérieur qui
ne soit pas une auto-référence.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script.
- Il ne **recalcule pas** le basculement du #510 — la date est reprise
  telle quelle, en confiance dans l'audit déjà fait.
- Il ne **juge pas** qu'un PASS procédural soit un défaut en soi — c'est
  le mode de fonctionnement déclaré de cette série depuis le #513.
- Il ne **se compte pas lui-même** — auto-exclusion (règle #447) ; ce
  cycle serait, par sa propre règle, PROCÉDURAL.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si **100 %** sont procéduraux.
2. Règle et date pivot **inchangées** après mesure.
3. Les SUBSTANTIEL, s'il y en a, publiés avec extrait — jamais juste comptés.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
