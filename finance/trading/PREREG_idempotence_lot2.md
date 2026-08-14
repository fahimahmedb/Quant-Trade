# Pré-enregistrement — idempotence, **lot 2** : dix scripts jamais éprouvés

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #469.

## Pourquoi ce cycle existe

Le **#467** a clos la piste de la **détection statique** : sur 6 scripts
signalés par l'heuristique, **0** était réellement défectueux. Ce qui reste est
coûteux et démontré — **rejouer les scripts**.

Couverture actuelle : **24** scripts éprouvés sur **320** (18 au #463, 6 au
#467). **296 n'ont jamais été exécutés deux fois.**

Ce cycle en éprouve **10 de plus**. Ce n'est pas spectaculaire, et c'est le
point : après deux tentatives de raccourci, la seule méthode qui marche
n'avance que par lots.

## L'univers et l'échantillon — fixés ici

- univers : les `nonml_*_backtest.py` **jamais éprouvés**, ni au #463 ni au
  #467 ;
- échantillon : les **10 premiers par ordre alphabétique** — règle
  déterministe, arrêtée **avant** d'avoir regardé la liste ;
- chacun est **exécuté deux fois**, empreintes SHA-256 de son rapport
  comparées ;
- budget **300 s** par exécution ; au-delà, le script est classé
  « budget dépassé » et **listé**, pas silencieusement omis.

## L'effet de bord — annulé, et vérifié après TOUTE exécution

Rejouer réécrit des rapports. L'arbre est restauré
(`git checkout -- results/`), et la vérification a lieu **après la dernière
exécution**, pas avant.

> Le #468 a montré pourquoi cette précision compte : sa restauration précédait
> sa dernière mesure, et le critère annonçait « 0 résidu » **sur un arbre
> sale**.

## Critère de succès — chiffré, il porte sur le procédé

1. **10/10** scripts traités ou classés **avec leur raison**.
2. Les **deux empreintes** publiées pour chaque script éprouvé.
3. Tout script non idempotent publié **avec le diff qui le prouve**.
4. Arbre **vérifié propre** sous `results/` après restauration finale.

> **PASS** = les quatre points. **FAIL** = un seul manque.

Un lot qui ne trouve aucun défaut et le montre proprement **réussit**.

## Prédictions — falsifiables

1. **Au moins 1** des 10 est non idempotent. Fondement : **2 sur 18** au #463,
   **0 sur 6** au #467, soit **2 sur 24** éprouvés — environ **8 %**, donc
   ~0,8 attendu sur 10. **C'est un pari, pas une certitude.**
2. **Au moins 8** des 10 tiennent dans le budget de 300 s.
3. Si un défaut est trouvé, c'est une **auto-inclusion** — le seul mécanisme
   observé jusqu'ici (#463, #468).

Si la prédiction 1 est réfutée, je ne dois **pas** en conclure que le dépôt est
sain : **10 sur 296**, c'est **3,4 %** de ce qui reste, et l'absence de défaut
dans un si petit lot est parfaitement compatible avec un taux de 8 %.

## Ce que ce cycle ne fait pas

- Il ne **répare** rien : tout défaut trouvé est **publié et inscrit**, la
  réparation revenant à un cycle dédié comme au #468.
- Il ne **committe** aucun rapport régénéré.
- Il ne **généralise** pas aux 286 scripts restants.

## Engagements

1. Résultat rapporté tel quel, y compris s'il ne trouve rien.
2. Univers, échantillon et budget **inchangés** après mesure.
3. La couverture atteinte est rappelée **en proportion**, pas seulement en
   nombre — 34 sur 320 se lit autrement que « 34 scripts éprouvés ».
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
