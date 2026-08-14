# Pré-enregistrement — donner un `.npz` à `tom_decomposition_overlay` et le soumettre au balayage

**Écrit et committé AVANT toute modification et toute mesure.** `n_trials = 1`.

**Cycle de MODIFICATION**, huitième après les #445 → #451. Premier depuis
longtemps à toucher une **stratégie** et non un instrument.

## Le problème, établi au #446

`tom_decomposition_overlay` est une **stratégie portant un PASS** (variante A,
fin de mois seule, 4/5 marchés) qui **ne produit aucun `.npz`**. Elle est donc
**invisible au balayage de doublons** — le mécanisme même qui existe pour éviter
que le décompte d'hypothèses testées soit gonflé par des essais qui n'en font
qu'un.

Or le **#8** (`tom_overlay`, ToM complet — union des deux sous-fenêtres) est
**PASS lui aussi** et **possède** son `.npz`. La variante A est l'une des deux
sous-fenêtres de cette union. Si les deux séries étaient très proches, deux
« essais » n'en seraient qu'un, et le DSR de la famille s'en trouverait faussé.

**Cette question n'a jamais pu être posée**, faute de série sauvegardée.

## La modification — régime annoncé

**Une seule insertion** dans `nonml_tom_decomposition_overlay_backtest.py` :
un `np.savez` de la **variante A sur NDX**, placé dans la boucle de `main()`,
immédiatement après le calcul du marché courant.

Le choix de **NDX** n'est pas libre : c'est la **convention #416** du dépôt, qui
sauvegarde la branche NDX des stratégies multi-marchés. La variante **A** est
celle qui porte le PASS ; la B est FAIL et n'est pas sauvegardée.

Schéma **indiciel** standard : `pos`, `r_asset`, `dates`, `cost_bps` — celui que
le balayage lit sans conversion.

Toute ligne touchée hors de cette insertion vaut **échec du cycle**.

## Critère de succès — chiffré, et il peut échouer

1. **Diff confiné** à l'insertion annoncée.
2. **Les chiffres publiés du rapport ne bougent pas.** Ajouter une sauvegarde ne
   calcule rien de neuf : le rapport régénéré doit être **identique** à sa
   baseline épinglée. Toute différence est un effet de bord et fait échouer le
   cycle.
3. **Concordance** : le Sharpe reconstruit depuis le `.npz` par la formule
   indicielle apparaît dans le rapport (axe des #442-#443).
4. **Le balayage voit désormais la série**, et son classement est publié :
   doublon exact, quasi-doublon, ou isolée.

> **PASS** = les quatre points. **FAIL** = un seul manque.

**Le verdict du cycle ne dépend pas de ce que le balayage trouve.** Qu'elle soit
doublon ou isolée, le résultat est publié tel quel — c'est le fait de pouvoir
enfin poser la question qui est l'objet du cycle.

## Prédiction — falsifiable, et je ne connais pas la réponse

La variante A (fin de mois, 4 derniers jours) est une **sous-fenêtre** du ToM
complet du #8 (union fin + début de mois). Les deux positions coïncident donc
sur une partie des séances et diffèrent sur l'autre.

- J'attends une corrélation **élevée mais inférieure au seuil de 0,9999** : les
  deux séries partagent l'essentiel de leur exposition mais pas les jours de
  début de mois. **Si elle dépasse le seuil**, alors deux PASS de la famille ToM
  n'en font qu'un, et **ce serait le résultat le plus important du cycle** — à
  publier en tête, avec la conséquence sur le décompte d'essais.
- Je **n'exclus pas** l'inverse : que la corrélation soit modeste, auquel cas la
  décomposition du ToM aura bien isolé deux effets distincts.

Je n'ai **pas** mesuré cette corrélation avant d'écrire ces lignes.

## Ce que ce cycle ne fait pas

- Il ne **recalcule aucun verdict** : ni celui de la variante A, ni celui du #8.
- Il ne **retire rien** du décompte d'essais, même si un doublon est trouvé :
  requalifier une famille est un cycle à part, à déclarer.
- Il ne touche **pas** la variante B (FAIL).

## Engagements

1. Résultat rapporté tel quel, y compris un **FAIL**.
2. Aucune ligne hors de l'insertion annoncée.
3. La corrélation trouvée est publiée **quelle qu'elle soit**, et son
   interprétation ne sera pas ajustée après coup.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
