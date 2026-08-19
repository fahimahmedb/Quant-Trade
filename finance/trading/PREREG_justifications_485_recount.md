# Pré-enregistrement — le compte « 3 justifications du #485 jamais vérifiées » tient-il ?

**Écrit et committé AVANT toute mesure.** `n_trials` continue le compte
global (aucune remise à 1 pour un fil déjà ouvert). **Cycle de
VÉRIFICATION**, première piste de la file ouverte au #516.

## Ce qui est répété sans être ré-établi

Depuis le **#511**, chaque « Dette restante » du backlog répète, verbatim
ou presque : *« 2 justifications du #485 sur 5 sont tombées (#493, #511) ;
3 n'ont jamais été vérifiées »*. Cette phrase apparaît inchangée dans **15
cycles consécutifs** (#511 → #516 compris), **sans jamais nommer les 3
restantes**. Un examen préliminaire de son propre texte (autorisé avant le
PREREG — même précédent que le #511 pour son constat sur `battery_backfill`,
qui n'était pas compté comme prédiction) montre deux faits qui **ne
s'accordent pas évidemment avec la phrase** :

1. Le **#493** a explicitement relu et jugé **les 4 justifications
   restantes** du tableau des 5 irréparables du #485 (`protocol_inventory_audit`,
   `marker_emitted_by_scripts`, `pnl_persistence_exposed_pass_audit`,
   `reproducibility_campaign_v3_lot2_audit`), en plus de celle du **#488**
   (`pnl_duplicate_sweep_audit`). **Les 5 lignes du tableau original ont
   chacune reçu un verdict cité sur pièce.**
2. Le fait cité par le **#511** (le « 0,00 % » de
   `nonml_battery_backfill_lot_audit.py`) ne porte sur **aucun** des 5 noms
   de ce tableau — c'est une justification de **classification RÉPARABLE**,
   pas une des 5 justifications IRRÉPARABLES d'origine.

Si ces deux faits sont exacts, la phrase répétée depuis le #511 confond
**deux populations distinctes** : les 5 justifications du tableau
« IRRÉPARABLE » (toutes relues dès le #493) et les justifications des 12-13
figures classées RÉPARABLE (dont une seule, celle du #511, a été relue).
**Ce cycle vérifie mécaniquement, sans se fier à cette lecture**, laquelle
des deux lectures est correcte.

## Ce qu'il faut établir — mécaniquement, sans lecture manuelle du sens

1. **Extraire par script** (pas par relecture) les 5 noms du tableau
   « Irréparable | Pourquoi » du #485, depuis la section `## Backlog #485`
   du backlog.
2. **Pour chacun des 5**, chercher dans les sections `## Backlog #488` et
   `## Backlog #493` une occurrence du nom de script accompagnée d'un
   marqueur de verdict (`EXACTE`, `FAUSSE`, `exacte`, `confirmée`, etc.) —
   déterminer combien des 5 ont reçu un verdict écrit sur pièce dans l'un
   de ces deux cycles.
3. **Vérifier** si le nom de script cité par le #511
   (`nonml_battery_backfill_lot_audit.py`) figure dans la liste des 5 —
   réponse binaire, par simple appartenance à un ensemble.
4. **Compter** les occurrences verbatim de la phrase « jamais vérifiées »
   ou « n'ont jamais été vérifiées » associée à « justifications du #485 »
   dans les sections #511 à #516, pour mesurer depuis combien de cycles la
   phrase est recopiée sans être ré-établie.

## Critère de succès — chiffré, porte sur le procédé

1. Les **5** noms du tableau du #485 extraits par script et publiés.
2. Pour chacun, le verdict trouvé (ou son absence) dans #488/#493, publié
   avec la ligne de texte qui le fonde.
3. Le statut d'appartenance du script du #511 à cet ensemble des 5,
   publié.
4. Le nombre de cycles ayant recopié la phrase sans la ré-établir, publié.
5. **Si les 5 sont tous couverts par #488+#493** : la phrase « 3 jamais
   vérifiées » est publiée comme **imprécise/obsolète**, et une
   reformulation correcte de la dette réelle est proposée (elle ne sera
   pas appliquée rétroactivement aux cycles passés — seulement à la
   dette de CE cycle).

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **Les 5 noms du tableau du #485 reçoivent chacun un verdict écrit dans
   #488 ou #493** — c'est-à-dire **0** justification du tableau des 5
   irréparables reste non vérifiée à ce jour.
2. Le script cité par le #511 (`nonml_battery_backfill_lot_audit.py`)
   **n'appartient PAS** à l'ensemble des 5 noms du tableau du #485.
3. La phrase « 3 jamais vérifiées » (ou équivalent) apparaît **au moins 10
   fois** depuis le #511 sans jamais nommer les 3 en question.

Si la prédiction 1 est réfutée (un des 5 n'a pas de verdict écrit dans
#488/#493), alors la phrase répétée était **correcte pour une mauvaise
raison apparente**, et ce cycle le publiera tel quel plutôt que de forcer
la conclusion inverse.

## Ce que ce cycle ne fait pas

- Il ne **rejuge** aucun verdict d'irréparabilité ou de réparabilité —
  seulement la **bibliographie interne** du backlog (qui a vérifié quoi,
  et où).
- Il ne **répare** rien, ne modifie aucun script de stratégie.
- Il n'**exécute** aucun script de marché : lecture du disque et du texte
  du backlog uniquement, **aucun effet de bord**.
- Il ne **tranche pas** la question `n_trials` (#421) ni la batterie au
  schéma panier (#432).

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification bibliographique, aucune position,
aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si la phrase répétée s'avère
   correcte et que ce cycle se trompe en la questionnant.
2. Population, protocole et forme des verdicts **inchangés** après mesure.
3. **Chaque verdict adossé à la ligne de texte citée**, jamais à une
   impression.
4. **Relecture intégrale du rapport produit avant commit** (engagement
   #414).
