# Pré-enregistrement — **réparer** les deux scripts auto-inclusifs

**Écrit et committé AVANT toute modification et toute mesure.** `n_trials = 1`.

**Cycle de RÉPARATION** — le premier de cette série. Première piste de la file
ouverte au #467.

## Pourquoi c'est un cycle à part

Le #463 a trouvé **2** scripts non idempotents par auto-inclusion et **ne les a
pas réparés** : l'engagement depuis le #450 est de *publier et inscrire, pas
réparer au passage*. Le #466 a refusé pour la même raison.

**Réparer est légitime — dans un cycle qui ne fait que ça, et qui le déclare.**
Ce qui était interdit, c'est de mêler la découverte d'un défaut à sa correction,
parce qu'on ne sait plus alors ce que la mesure a vu.

## Les deux défauts, localisés à la ligne

**D1 — `nonml_verdict_rule_propagation_backtest.py`**
```
rapports = sorted(RESULTS.glob("nonml_*_result.md"))
```
Le glob inclut **sa propre sortie**. Au second passage, le rapport se compte et
s'ajoute à sa propre table de reclassement, avec un verdict `PASS → FAIL`
inexistant au premier.

**D2 — `nonml_six_reports_regeneration_backtest.py`**
```
modifs = [ln[3:] for ln in git("status", "--short", ...) ... if ln.startswith(" M")]
```
Son corpus est **l'état du dépôt**, pas un dossier. Au second passage, son
propre rapport figure parmi les fichiers modifiés. C'est la forme que le
détecteur du #466 avait manquée.

## Le régime de modification — déclaré avant, à la ligne près

- **une seule expression modifiée par script** : la compréhension de liste
  reçoit une condition d'exclusion de la sortie du script lui-même ;
- des **lignes de commentaire** expliquant la correction et citant ce cycle ;
- **aucun `import` ajouté** — `Path` et les objets nécessaires sont déjà là ;
- **aucune autre ligne touchée**, dans aucun autre fichier.

**Toute ligne modifiée hors de ce régime vaut échec du cycle.** Le diff est
mesuré contre le commit de ce pré-enregistrement, **épinglé** — leçons #445 et
#451, où une base lue sur le disque avait produit un résultat vide.

## La régénération — assumée, et bornée

Réparer oblige à réexécuter. `six_reports_regeneration` **écrit 7 rapports qui
ne sont pas le sien** (#463). Ils seront donc réécrits pendant la mesure.

**Décision, prise ici :** ces 7 sont **restaurés** après mesure, et le commit ne
contient que **les 2 scripts corrigés et leurs 2 rapports**. Committer les 7
autres mêlerait l'effet de la correction à la dérive du dépôt — précisément ce
que le #450 a payé cher.

## Ce qui est mesuré

1. **Idempotence après correction** : chaque script rejoué **trois fois**,
   empreintes comparées. Trois, pas deux — le #467 a montré qu'une dérive de
   période 2 échappe à deux passages.
2. **L'effet de la correction** sur le contenu des deux rapports, diff publié.
3. **Le diff du code**, confiné au régime déclaré.
4. **L'état de l'arbre** après restauration.

## Critère de succès — chiffré

1. Les **2** scripts idempotents sur **3** passages.
2. Diff de code **confiné** au régime déclaré : 2 fichiers, aucune autre ligne.
3. Effet sur les 2 rapports **publié avec son diff**.
4. Arbre propre hors des **4** fichiers du commit (2 scripts, 2 rapports).

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Les deux deviennent idempotents sur 3 passages.
2. Leurs compteurs **baissent d'exactement 1** : le rapport cesse de se compter.
3. **Aucun autre fichier suivi** ne reste modifié après restauration.

Si la prédiction 1 est réfutée, la correction est **insuffisante** et je devrai
publier que l'auto-inclusion n'était pas la seule cause — ce qui invaliderait le
diagnostic du #463 autant que ma réparation.

## Ce que ce cycle ne fait pas

- Il ne **touche** à aucun autre script, même signalé par le #466 : ces
  signalements sont **sans valeur démontrée** (#467, 0/6).
- Il ne **committe** aucun rapport tiers régénéré.
- Il ne **réécrit** aucun verdict de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si la correction échoue.
2. Régime de modification **inchangé** après mesure.
3. Les diffs des deux rapports sont publiés **en entier ou tronqués avec leur
   longueur**, jamais résumés en prose seule.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
