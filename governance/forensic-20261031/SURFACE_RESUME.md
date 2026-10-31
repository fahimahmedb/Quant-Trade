# Historique de surface terminé — reprise vers la carte de capacités

STATUT : `SURFACE_CHRONOLOGY_COMPLETE_NEXT_CAPABILITY_MAP`.

La chronologie quotidienne de surface de la photographie initiale est terminée. **Ne pas recommencer la revue jour-par-jour.** Revenir à une journée uniquement pour résoudre une contradiction précise qui change une décision de capacité, d'autorité ou de réutilisation.

## Couverture durable

- 6 393 / 6 393 commits de la photographie initiale rattachés et parcourus selon la méthode de surface ;
- 71 journées actives revues jusqu'au 31 octobre 2026 inclus ;
- 111 journées calendaires indexées ;
- 13 471 occurrences de sources ;
- 969 occurrences sans date exploitable conservées `UNKNOWN` ou à associer par SHA sans inventer d'heure ;
- dernier checkpoint : `surface/CHECKPOINT_2026-10-29_2026-10-31.md`.

`SURFACE_COMPLETE` ne signifie pas lecture profonde des 6 393 diffs ou des 6 465 versions documentaires. Cela signifie que la chronologie active, les principales constructions, corrections, ports, échecs, qualifications et changements d'autorité ont été reconstruits suffisamment pour passer à la réconciliation des capacités.

## Ce que la chronologie change

Le dépôt ne contient pas 275 architectures indépendantes. La dispersion vient surtout de :

1. lignées successives de recherche et résultats négatifs/blocked ;
2. branches de rôle Builder/Astra/Owner/reviewer autour d'une même capacité ;
3. campagnes W1/Mega/Wave2/GIGA avec ports sélectifs, adaptations et re-exports ;
4. snapshots data, CI, wakes et receipts automatiques qui gonflent les compteurs sans créer de nouveaux modules ;
5. branches longues dont le head actuel a bougé après l'événement historique ;
6. couches récentes d'autonomie/orchestration encore séparées de l'autorité scientifique et du runtime réellement unattended.

## Invariants réutilisables

- `restaurant-stock/` est hors périmètre Quant.
- `SCHEDULED_DATA_COLLECTION` est une seule capacité ; les snapshots de feed ne sont pas des architectures.
- W1/Mega A/B/D0/C0/E et Multi-Source ont des ports/adaptations vérifiés vers Wave2 ; l'absence d'un ancien chemin ne prouve pas une perte.
- Wave2 C2 est scellé à `ebc72b9fd14f91420c37e0b7607f9bfb584a289a`, sans implication de production/capital.
- Le one-shot historique reste `NOT_QUALIFIED` ; les réparations C0/membrane ultérieures ne réécrivent pas son verdict.
- C0 final : `13721384fe5b94b0136fb4548192e05d5e34e605`, run `40437918834` success.
- WP2 exact head : `8f8df47d184f0f1594280bec7e9e7941962cf1c5`, run `41069767444` success, claim ceiling = autonomie engineering synthétique.
- Issue #44 / PR #46 : candidat `afedfd57986aa042e9e97aa53b9db53b4619764f`, run `41203216122` success ; vraie boucle VM unattended non prouvée.
- `REAL_CAPITAL_AUTHORIZED = FALSE`; `LIVE_TRADING_AUTHORIZED = FALSE`.

## Lois à ne plus redécouvrir

`REUSE > CONNECT > REPAIR > BUILD`.

`BRANCH_NAME/DATE != AUTHORITY/TIME`.

`PATH_ABSENCE != CAPABILITY_LOSS`.

`CI_GREEN != DEPLOYMENT_OR_SCIENTIFIC_AUTHORITY`.

`HISTORICAL_NOT_QUALIFIED` n'est pas réécrit par une réparation ultérieure.

`BLOCK`, `UNKNOWN`, `PARK`, `NO_CHANGE_REQUIRED` sont valides.

`FRONTIER_EXHAUSTED -> NOOP`.

`SELF_PASS != INDEPENDENT_PASS`.

## Prochaine action exacte

**Ne plus poursuivre la chronologie.** Construire maintenant la carte de capacités/lignées depuis les checkpoints existants, `capability-lineages.csv`, `w1-mega-a-lineages.csv`, les receipts CP et les preuves exact-head. Pour chaque famille : `REUSE / CONNECT / REPAIR / PARK / RETIRE`.

Puis proposer deux destinations seulement :

- une branche **code** pour l'implémentation intégrée ;
- une branche **projet/gouvernance** pour mémoire, preuves, décisions, inconnus et prochaines actions.

Aucune suppression/fusion destructive avant validation de cette carte.
