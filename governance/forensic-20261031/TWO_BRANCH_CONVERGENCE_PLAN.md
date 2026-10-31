# Quant-Trade — plan de convergence vers deux branches

STATUT : `PLAN_READY_NOT_EXECUTED`

Objectif Owner : réduire la surface active à **une branche code** et **une branche projet/gouvernance**, sans perdre les capacités déjà convergées ni réécrire l'historique scientifique.

Ce plan est non destructif. Il ne supprime, ne force-push, ne merge et ne promeut aucune branche par sa seule publication.

## Principe

Ne pas choisir une branche entière par récence.

Les preuves Git montrent :

- Wave2 C2 `ebc72b9fd14f91420c37e0b7607f9bfb584a289a` et le default Blue actuel divergent depuis `09ba64b8bee1419076ec8a30f8d75a916932c2ba` ;
- Wave2 C2 et PR46 `afedfd57986aa042e9e97aa53b9db53b4619764f` divergent depuis le même merge-base ;
- Wave2 contient environ 1 221 commits de lignée que Blue/PR46 ne portent pas par ascendance ;
- Blue/PR46 portent des deltas récents de gouvernance/autonomie absents de Wave2.

Donc : **Wave2-derived base + selective qualified ports**.

## Destinations proposées

Noms provisoires, à créer seulement au moment de l'exécution :

1. `code/canonical` — produit/runtime/tests/workflows réellement retenus.
2. `project/canonical` — mémoire de projet, preuves, décisions, authority state, ledgers, handoffs, inconnus et prochaine action.

Les noms sont moins importants que les contrats. Il ne doit exister qu'un owner canonique par capacité.

## Branche 1 — CODE

### Base provisoire

Ancre de départ : Wave2 C2 `ebc72b9fd14f91420c37e0b7607f9bfb584a289a`.

Raison : c'est la fermeture de convergence la plus forte retrouvée, intégrant W1/Mega A/B/D0/C0/E et Multi-Source avec ports/adaptations vérifiés. Le default Blue et PR46 sont trop divergents pour être pris wholesale comme remplaçants.

### Passes de convergence

#### C1 — Seal exact base

- créer la candidate depuis l'exact SHA `ebc72b9f…` ;
- enregistrer arbre, SHA et inventaire de tests avant mutation ;
- aucune outcome/science/capital authority ouverte.

Critère : candidate reproductible, aucun port encore appliqué.

#### C2 — Importer uniquement les hardenings post-Wave2 démontrés

Comparer les descendants GIGA et post-challenge au niveau capability/file/test, puis :

- `NO_CHANGE_REQUIRED` si équivalent déjà présent ;
- `CONNECT` si propriétaire canonique existe mais seam manque ;
- `REPAIR` seulement pour un invariant démontré absent ;
- ne jamais importer un module parce que son nom de branche paraît plus récent.

Hardenings déjà identifiés comme candidats : source/task budgets, clock blockers, qualification runtime legacy, fédération durable de seeds, corrections C0/membrane.

#### C3 — Porter le delta autonome PR46, pas la branche PR46

Source candidate exacte : `afedfd57986aa042e9e97aa53b9db53b4619764f`, hosted run `41203216122` success.

Port scope initial borné :

- `scripts/gpt_oss_orchestrator.py` ;
- `src/autonomous_research/codex_adapter.py` ;
- `src/autonomous_research/codex_policy.py` ;
- tests correspondants ;
- workflow/state refresh uniquement si encore nécessaires après intégration.

Avant port, comparer leurs interfaces aux owners Wave2. Interdiction de remplacer `research/research_os/discovery_chain.py`, `discovery_engine.py` ou leurs gates simplement parce qu'ils sont absents à leur ancien chemin dans PR46.

Critères :

- tests focused du delta ;
- suite canonique Wave2 ;
- exact-head hosted qualification ;
- semantic review distincte du simple self-pass ;
- aucune modification de science/protocol/authority par effet de bord.

#### C4 — Oracle / source provenance

Évaluer CP057 (`fecd09e0…`) contre le candidat : importer la provenance exacte de release/qualification seulement si elle apporte un invariant absent. `CI_SOURCE != SCIENTIFIC_STATE` doit rester vrai.

#### C5 — Observability et UX

Live Lab / 3D n'entre que si :

- il projette l'état canonique sans devenir source de vérité ;
- le reducer/state machine reste déterministe ;
- aucune dépendance n'est nécessaire au runtime de recherche.

Sinon `PARK` comme outil externe/optionnel.

#### C6 — Qualification système

Le code branch n'est pas `READY` parce qu'il compile ou parce que chaque sous-lane a un green historique.

Minimum avant promotion :

1. exact-head suite complète ;
2. tests des invariants causaux/idempotents/replay ;
3. tests d'autorité fail-closed ;
4. duplicate/stale-head/recovery ;
5. qualification du loop réel sur VM : `GPT-OSS -> Codex result -> GPT-OSS next decision` sur plusieurs wakes sans routage humain ;
6. `REAL_CAPITAL_AUTHORIZED=false`, `LIVE_TRADING_AUTHORIZED=false` inchangés.

Sans #5 : état `ENGINEERING_QUALIFIED_NOT_AUTONOMOUS_RUNTIME_PROVEN`.

## Branche 2 — PROJECT / GOVERNANCE

Cette branche ne doit pas être un deuxième produit exécutable.

### Contenu vivant minimal

- `CURRENT_PROJECT_STATE.md` — routeur courant ;
- `NEXT_ACTION.md` — une prochaine action bornée ;
- `CAPABILITY_REGISTRY` — stable IDs, owner canonique, code SHA, statut ;
- `AUTHORITY_STATE` — science/outcome/capital/live/deploy ;
- `DECISIONS` — décisions Owner avec portée/date/preuve ;
- `EVIDENCE_INDEX` — exact SHA/run/artifact/PR/issue ;
- `UNKNOWN_AND_BLOCKED` — seulement inconnus qui changent une décision ;
- `NEGATIVE_AND_SUPERSEDED` — familles rejetées, blocks, contaminations, résultats supersédés ;
- `HANDOFF` — dernier checkpoint de reprise ;
- historique forensic 2026-10-31 conservé en lecture/référence.

### Ce qui ne doit plus être vivant simultanément

- multiples `CURRENT_*` concurrents ;
- snapshots de mission présentés comme autorité actuelle ;
- prompts Builder historiques comme routeurs actifs ;
- duplication d'une même décision dans 5 fichiers ;
- résultats scientifiques recopiés sans stable ID/SHA ;
- commentaires d'agents assimilés à décision Owner.

Les anciens documents restent accessibles par Git SHA, tags/archives ou dossier historique, mais ne routent plus le projet.

## Données générées et contrainte « seulement deux branches »

Aujourd'hui `data-feeds` utilise une branche dédiée pour snapshots append-only. La supprimer immédiatement casserait une capacité active.

État : `PARK_UNTIL_STORAGE_REPLACEMENT_PROVEN`.

Avant fermeture de cette branche, déplacer les outputs vers un store durable approprié (artifact/object storage/dataset store) avec : provenance, immutabilité, hash, timestamp et reprise. Le code/workflow reste dans `code/canonical`; la branche générée n'est supprimée qu'après preuve de remplacement et replay.

Tant que ce remplacement n'existe pas, la cible « exactement deux branches » est un objectif de convergence, pas une excuse pour perdre des données.

## Ce qui est retiré de la surface active

Après qualification des deux destinations et seulement après inventaire final :

- `restaurant-stock/` hors périmètre Quant ;
- branches CI-only/review/challenger/handoff dont les preuves sont référencées ;
- anciennes branches d'expériences closes/rejetées ;
- branches GIGA/Mega/Wave anciennes devenues ancêtres documentés du code canonique ;
- branches de snapshots de mission devenues historiques ;
- doublons automatiques/wakes qui ne sont pas des owners de capacité.

`RETIRE_FROM_ACTIVE_SURFACE` ne signifie pas effacer les preuves. Avant suppression : tag/ref durable ou registre SHA + preuve d'intégration/port.

## Séquence d'exécution recommandée

1. **FREEZE** — ancrer remote heads, capability registry et authority state.
2. **BUILD CODE CANDIDATE** — exact Wave2 C2, sans autre mutation.
3. **DIFF/PORT** — GIGA/hardenings puis PR46/Oracle, un capability port à la fois.
4. **QUALIFY** — exact-head CI + semantic review + regression Wave2.
5. **VM PROOF** — déployer seulement le candidat qualifié dans l'enveloppe autorisée et prouver le multi-wake loop non économique.
6. **BUILD GOVERNANCE CANDIDATE** — condenser les routeurs/mémoires ; aucun code runtime propriétaire.
7. **RECONCILE** — code SHA inscrit dans governance ; governance ne redéfinit pas le code.
8. **SHADOW PERIOD** — utiliser uniquement les deux candidats pour les nouvelles missions ; anciennes branches read-only.
9. **FINAL INVENTORY** — démontrer que chaque capacité active a un owner dans l'une des deux destinations ou un statut PARK explicite.
10. **CLEANUP** — seulement alors fermer/supprimer les branches redondantes, avec décision Owner explicite pour la mutation destructive.

## Gates d'arrêt

Stopper la migration concernée, pas relancer un audit global, si :

- un port change une sémantique scientifique gelée ;
- un descendant possède une capability non équivalente dont la nécessité n'est pas tranchée ;
- un exact-head gate échoue ;
- le VM E2E ne produit pas de receipt causal ;
- une suppression ferait perdre la seule copie d'une donnée/preuve ;
- un unknown devient décisionnel.

Résultats autorisés : `NO_CHANGE_REQUIRED`, `BLOCK`, `PARK`, `UNKNOWN`.

## Ce qui n'est pas autorisé par ce plan

- nouveau Research OS ;
- deuxième scheduler/daemon intelligent ;
- réouverture d'une famille scientifique rejetée ;
- outcome access pour « tester que ça marche » ;
- capital réel/live trading ;
- gros merge de toutes les branches ;
- sélection du default actuel comme code canonique sans récupérer Wave2 ;
- suppression de 275 branches avant preuve de port/retirement.

## Décision finale de planification

**CODE_BASE_PROVISIONAL = Wave2 C2 `ebc72b9f…`.**

**GOVERNANCE_BASE_PROVISIONAL = état Control Tower Blue actuel, à condenser en branche projet non exécutable.**

**AUTONOMY_DELTA_SOURCE = PR46 `afedfd579…`, selective port only.**

**DESTRUCTIVE_CLEANUP = NOT_AUTHORIZED_BY_THIS_AUDIT.**

**NEXT_ACTION = créer/qualifier la candidate code depuis `ebc72b9f…`, puis exécuter C2→C6 sans ouvrir de nouveau chantier scientifique.**
