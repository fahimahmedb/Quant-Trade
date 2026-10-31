# Reconstruction terminée — carte de capacités et plan de convergence prêts

STATUT : `FORENSIC_SURFACE_AND_CAPABILITY_RECONCILIATION_COMPLETE_PLAN_READY`.

La chronologie quotidienne de surface de la photographie initiale est terminée et la réconciliation de capacités est désormais publiée. **Ne pas recommencer la revue jour-par-jour ni relancer un audit global** sauf contradiction précise qui change une décision de capacité, d'autorité ou de réutilisation.

## Preuves durables

- 6 393 / 6 393 commits de la photographie initiale rattachés et parcourus selon la méthode de surface ;
- 71 journées actives revues jusqu'au 31 octobre 2026 inclus ;
- 111 journées calendaires indexées ;
- 13 471 occurrences de sources ;
- 969 occurrences sans date exploitable conservées `UNKNOWN` ou à associer par SHA sans inventer d'heure ;
- checkpoint final : `surface/CHECKPOINT_2026-10-29_2026-10-31.md` ;
- carte canonique : `CAPABILITY_MAP.md` ;
- plan de convergence : `TWO_BRANCH_CONVERGENCE_PLAN.md`.

`SURFACE_COMPLETE` ne signifie pas lecture profonde de chaque diff/document. La passe a reconstruit les principales identités, constructions, corrections, ports, échecs, qualifications et changements d'autorité suffisamment pour arrêter le recommencement et décider la convergence.

## Décision de topologie

Wave2 C2 est scellé à `ebc72b9fd14f91420c37e0b7607f9bfb584a289a`.

Les comparaisons Git fraîches démontrent que le default Blue actuel et PR #46 divergent de Wave2 depuis le même merge-base `09ba64b8bee1419076ec8a30f8d75a916932c2ba`. Chacun porte des deltas récents, mais ne porte pas par ascendance environ 1 221 commits de la lignée Wave2.

Décision :

- `CODE_BASE_PROVISIONAL = ebc72b9fd14f91420c37e0b7607f9bfb584a289a` ;
- `GOVERNANCE_BASE_PROVISIONAL = current Blue Control Tower state`, à condenser en surface projet non exécutable ;
- `AUTONOMY_DELTA_SOURCE = afedfd57986aa042e9e97aa53b9db53b4619764f`, selective port only ;
- aucun merge massif de branches ;
- aucun nettoyage destructif autorisé par cet audit.

## Ce qui est déjà récupéré

Le travail horizontal / vertical / transversal n'a pas disparu en bloc. W1/Mega A/B/D0/C0/E et Multi-Source ont des ports, adaptations ou re-exports vérifiés vers Wave2 et ses descendants. Les GIGA se classent principalement comme hardenings/extensions de cette lignée, pas comme produits autonomes.

Les branches récentes d'autonomie apportent cependant des deltas utiles qui ne sont pas dans Wave2 par ascendance, notamment Issue #44 / PR #46. Elles doivent être portées capability par capability, avec tests et qualification, pas substituées à Wave2.

## Autorité et limites inchangées

- `REAL_CAPITAL_AUTHORIZED = FALSE` ;
- `LIVE_TRADING_AUTHORIZED = FALSE` ;
- PR #46 `afedfd579…` possède un hosted exact-head PASS (`41203216122`) mais n'est pas prouvé déployé sur la VM ;
- la vraie boucle multi-wake `GPT-OSS -> Codex -> GPT-OSS` sans routage humain reste non démontrée ;
- WP1 real-science reste `PARK/BLOCKED_PRE_EXPOSURE` ;
- les résultats rejetés, supersédés et contaminations restent mémoire négative et ne doivent pas être recréés.

## Prochaine action exacte

**Ne plus auditer globalement.**

Construire de manière non destructive une candidate code depuis l'exact Wave2 C2 `ebc72b9f…`, puis :

1. comparer/porter uniquement les hardenings post-Wave2 nécessaires ;
2. porter sélectivement le delta PR #46 / autonomie ;
3. qualifier exact-head + régressions Wave2 + revue sémantique ;
4. prouver ensuite le vrai loop VM multi-wake non économique ;
5. condenser la gouvernance Blue dans une branche projet/gouvernance unique ;
6. seulement après période shadow et inventaire final, demander une décision Owner pour le cleanup destructif.

La branche de données générées reste `PARK_UNTIL_STORAGE_REPLACEMENT_PROVEN` : ne pas perdre les snapshots append-only pour satisfaire artificiellement la cible de deux branches.

## Lois de reprise

`REUSE > CONNECT > REPAIR > BUILD`.

`BRANCH_NAME/DATE != AUTHORITY/TIME`.

`PATH_ABSENCE != CAPABILITY_LOSS`.

`CI_GREEN != DEPLOYMENT_OR_SCIENTIFIC_AUTHORITY`.

`HISTORICAL_NOT_QUALIFIED` n'est pas réécrit par une réparation ultérieure.

`BLOCK`, `UNKNOWN`, `PARK`, `NO_CHANGE_REQUIRED` sont valides.

`FRONTIER_EXHAUSTED -> NOOP`.

`SELF_PASS != INDEPENDENT_PASS`.
