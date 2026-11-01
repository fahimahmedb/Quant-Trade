# Point de reprise canonique — convergence code qualifiée, preuve VM bloquée sur accès host

STATUT : `CANONICAL_CODE_ENGINEERING_QUALIFIED_VM_MULTI_WAKE_BLOCKED_EXTERNAL_HOST_ACCESS`.

## Ne pas recommencer

La reconstruction forensic globale est terminée pour convergence : **6 393 / 6 393 commits**, **71 journées actives**, jusqu’au 31 octobre 2026. Les 969 occurrences non datables restent `UNKNOWN` ou rattachées seulement par SHA. Ne pas relancer un audit global, CP par CP, branche par branche ou discussion par discussion sauf contradiction primaire précise susceptible de changer une décision `REUSE / CONNECT / REPAIR / PARK / RETIRE`.

Les preuves détaillées restent sous `governance/forensic-20261031/`, notamment `SURFACE_RESUME.md`, `resume.json`, `CAPABILITY_MAP.md` et `TWO_BRANCH_CONVERGENCE_PLAN.md`.

## Autorités canoniques

- code : `code/canonical`;
- projet / gouvernance : `project/canonical`.

`BRANCH_DELETION_AUTHORIZED=FALSE`
`BRANCH_RETIREMENT=PARK`
`ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE`
`PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE`
`REAL_CAPITAL_AUTHORIZED=FALSE`
`LIVE_TRADING_AUTHORIZED=FALSE`
`PRODUCTION_DEPLOYMENT_AUTHORIZED=FALSE`

## Code canonique actuel

Base Wave2 C2 : `ebc72b9fd14f91420c37e0b7607f9bfb584a289a`.

Head actuel qualifié :
`6039cfd7a8502e0a4727a6928a4ef4cb75a3bb6e`.

Qualification exact-head :
- workflow : `Canonical Code Qualification`;
- run : `41264501411`;
- conclusion : `SUCCESS`;
- CP099 carried-hardening regressions : `22/22 PASS`;
- PR46 autonomy regressions : `16/16 PASS` + `GPT_OSS_LAUNCHER_ISOLATION=PASS`;
- Wave2 non-regression sample : `48/48 PASS`;
- GIGA-Q focused recovery challenge : `110/110 PASS` + `44 subtests PASS`;
- `CANONICAL_AUTHORITY_CLOSED=PASS`;
- clean checkout : PASS.

## Chaîne de challenge à conserver cumulativement

1. `fd3f8ce77d3a2f20cc5954c184c4487b44dac1d3` : qualification antérieure run `41216401503` SUCCESS, avant challenge GIGA-Q renforcé.
2. `1d5d76c8450b14481cc73eec4d4588698184c3a2` : run `41218076177` FAILURE au challenge GIGA-Q ; les contrôles CP099, PR46 et Wave2 précédents avaient passé.
3. `583a86589e502c8659a8886edd0c81a05b494f69` : récupération sélective des hardenings GIGA-Q non chevauchants ; run `41263645798` FAILURE limité au challenge GIGA-Q, `31 failed / 79 passed / 44 subtests passed`. Défauts reproduits : identités/hash non idempotents après sérialisation et mémoire négative insuffisamment fail-closed.
4. `6039cfd7a8502e0a4727a6928a4ef4cb75a3bb6e` : réparation minimale de `v2_core.py` seulement. Diff : retrait des anciens champs de hash avant recalcul pour epoch/trial/negative-memory/export, plus validations fail-closed de la mémoire négative. Run `41264501411` SUCCESS.

Ne pas réinterpréter les étapes 2–3 comme une panne globale : elles ont servi de challenge adversarial puis de preuve de correction.

## Claim ceiling actuel

`ENGINEERING_CODE_CANDIDATE_QUALIFIED=TRUE`
`CANONICAL_PROJECT_AUTHORITY_ESTABLISHED=TRUE`
`ACTUAL_VM_MULTI_WAKE_AUTONOMY_PROVEN=FALSE`
`CURRENT_HOST_STATE=UNKNOWN`
`HOST_ACCESS_IN_THIS_SESSION=BLOCKED_EXTERNAL`
`VM_MULTI_WAKE_PROOF=NOT_EXECUTED`
`SOFTWARE_GAP_REQUIRING_NEW_BUILD=FALSE`
`RUNBOOK_MISSING=FALSE`
`LEGACY_BRANCHES_RETIRED=FALSE`
`DEFAULT_BRANCH_SWITCHED=FALSE`

Le CI démontre la qualification engineering du code courant. Il ne démontre pas un déploiement ni l’utilisation réelle sur VM. Les reçus historiques d’activation Oracle et de wakes ne démontrent pas l’état actuel du host ni une boucle réelle `GPT-OSS -> Codex -> GPT-OSS` sur le candidat canonique.

## Blocker runtime borné

La réconciliation post-qualification a établi que la prochaine preuve ne manque plus de code ou de procédure : elle manque d’un canal authentifié vers le host réel.

Preuves à conserver :
- checkpoint VM historique `8a1bdadc9bc52c4889ee19d0472bcee61fe24318` : à ce point, service VM non implémenté/non activé ;
- installateur OCI historique `35d3b8a9faba2015b05b54477f61fff7268d7d20` : installation seule, `scheduler_started=false` ;
- rail de réparation OCI jusqu’à `6e8ea155b05086f8e5eabcf830a5f835d3e3d09c` : fail-closed tant que la livraison agent n’est pas confirmée ;
- Control Tower du 31 octobre : activation historique du modèle/timer et 29 wakes réussis, mais santé VM actuelle `UNKNOWN` ;
- PR46 `afedfd57986aa042e9e97aa53b9db53b4619764f` : bridge hosted-qualified, mais déploiement VM et boucle réelle multi-wake explicitement non prouvés ;
- `deploy/ORACLE_H24_RUNBOOK.md`, blob `5b00ba9955deb35716c0f3447e8f2a830db84a36` : procédure existante d’inventaire, qualification/rebind, canary, activation, journald, preuve multi-wake/restart et rollback.

Décision :
- ne pas construire un autre scheduler, daemon ou workflow de déploiement ;
- ne pas relancer l’audit forensic/global ;
- ne pas transformer les wakes historiques ou la CI en preuve de runtime actuel ;
- conserver `VM_MULTI_WAKE_PROOF=BLOCK_EXTERNAL_HOST_ACCESS` jusqu’à accès host authentifié.

## Prochaine action

Dès qu’un canal authentifié OCI Run Command ou SSH vers la VM existante est disponible, exécuter **le runbook existant**, dans cet ordre :

1. inventorier release V1/V2 active, unités/timer, configuration, modèle, principal GitHub et SHA réellement déployé ;
2. rebind uniquement le timer/hook existant vers la release canonique qualifiée si l’inventaire prouve que c’est nécessaire et autorisé ;
3. lancer un canary synthétique non économique ;
4. démontrer au moins deux wakes automatiques consécutifs, sans relance/routage humain, avec un résultat Codex réellement lié causalement puis consommé par la décision GPT-OSS suivante ;
5. lier `task_id / dispatch_id / attempt / expected_head_sha / result_sha` et les preuves exact-head CI/review ;
6. exercer restart / duplicate / stale-head / retry-PARK en fail-closed ;
7. vérifier que l’état scientifique protégé n’a pas changé et que toutes les autorités ci-dessus restent `FALSE` ;
8. publier les receipts host assainis dans GitHub.

Tant que ce canal host n’existe pas, la bonne action est `BLOCK_EXTERNAL_HOST_ACCESS`, pas un nouveau build, pas une nouvelle architecture et pas un nouvel audit.
