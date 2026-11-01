# Point de reprise canonique — convergence code qualifiée, preuve VM suivante

STATUT : `CANONICAL_CODE_ENGINEERING_QUALIFIED_VM_AUTONOMY_NOT_PROVEN`.

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
`LEGACY_BRANCHES_RETIRED=FALSE`
`DEFAULT_BRANCH_SWITCHED=FALSE`

Le CI démontre la qualification engineering du code courant. Il ne démontre pas un déploiement ni l’utilisation réelle sur VM.

## Prochaine action

`VM_MULTI_WAKE_PROOF` : vérifier l’état réel du host/VM puis démontrer, sans capital et sans nouvelle science, une séquence causale réelle sur plusieurs wakes :

`GPT-OSS decision -> Codex dispatch/result -> GPT-OSS next decision`

avec :
- aucune relance/routage humain entre les wakes ;
- résultat Codex lié à l’identité exacte de la tâche et du head ;
- reprise après restart / duplicate / stale-head conforme ;
- autorités scientifiques, économiques, capital et trading inchangées à false.

Si le runtime ou les permissions nécessaires ne sont pas disponibles, classer précisément `BLOCK` ou `UNKNOWN` sur cette preuve runtime sans rouvrir l’architecture globale.
