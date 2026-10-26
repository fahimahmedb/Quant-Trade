# WAVE 2 — CONVERGENCE #2 PORT ORDER

This is a recommended semantic port order for the canonical integrator. It is not an integration action and does not authorize this foreman to merge, seal, rebase siblings or emit `WAVE2_INTEGRATED_SHA`.

Formal base observed: `2b99d8aeb8a342f1ef32544247d366cb8a26037e` — **seal unproven**.

## Decision criteria

The order is optimized for:

1. dependency direction;
2. schema/identity stabilization before consumers;
3. smallest conflict surface first;
4. immediate focused qualification after each port;
5. earliest detection of authority/invariant violations;
6. rollback/localization of failures;
7. postponement of high-risk runtime/global-truth reconciliation until scientific contracts are stable.

## Recommended order

`RECOMMENDED_PORT_ORDER=Multi-Source -> MEGA B -> MEGA C0 -> MEGA D0 -> MEGA E`

This is not a blind restatement of the conceptual DAG. It follows the observed deltas and ownership surfaces.

## Gate 0 — prove canonical starting base

Before Port 1, canonical Convergence #2 must identify/publish durable evidence for the Wave-2 immutable base. The foreman observes branch head `2b99…` but does not possess independent seal authority.

If the formally sealed base differs from `2b99…`:

- do not rewrite foreman history;
- retain this preparation as Phase-A diagnostic evidence;
- repeat semantic delta analysis against the actual sealed base;
- recompute textual/semantic base conflicts before any port.

## Port 1 — Multi-Source Ideation

### Why first

- direct descendant of current observed formal base;
- upstream producer of ideation/proposal semantics consumed by B;
- substantial identity/provenance/staleness/claim behavior must be frozen before B seam qualification;
- does not own Candidate or operational task truth.

### Entry gate

Do not port the moving branch merely because implementation exists. Require:

- durable exact-head final manifest;
- `FINAL_SHA` no longer pending;
- `SAFE_TO_INTEGRATE=TRUE` or equivalent qualified lane result;
- exact-head CI/clean-tree proof;
- all authority/outcome flags false.

Current blocker: manifest still says `PENDING_EXACT_HEAD` / `PENDING_EXACT_HEAD_CI`.

### Port method

Because Multi is rooted directly at `2b99…`, semantic port should be low conflict. Still inspect every lane-owned addition and exclude documentary/test artifacts that assert global truth beyond lane authority.

### Immediate qualification

Run Multi focused suite plus S1 preliminary identity/provenance/no-READY checks.

Rollback boundary: base/head before Multi port.

## Port 2 — MEGA B Discovery

### Why second

- B consumes the ideation/RI boundary and produces the canonical Candidate facts that C0 adjudicates;
- B Candidate/discovery semantics must stabilize before C0 is adapted;
- B is scientific and scheduler-neutral, so it is safer to integrate before runtime/global surfaces.

### Base issue

B was qualified on `97165…`; canonical convergence must port the semantic delta onto the authorized base rather than merge/rebase the sibling branch.

Qualified code identity observed: `7ef088bb30ece88cf96f4514e8c581a95ca4b091`.

Documentary branch head observed: `bfc9fad9c36790abce71f80aead2485d6e022cdb`.

### Immediate qualification

- B focused suite;
- base-repair preservation;
- Multi→RI→B seam;
- canonical Candidate identity/no duplicate schema;
- no task READY/control-plane mutation;
- Data/PIT clock/provenance checks.

Rollback boundary: post-Multi exact qualified head.

## Port 3 — MEGA C0 Scientific Adjudication

### Why third

- C0 consumes exact Candidate + Factory identity from B;
- its verdict identity must be stable before D0/economic lifecycle binding;
- C0 shares canonical Validator/Red Team/Factory surfaces and therefore benefits from a fully stabilized upstream Candidate seam.

### Base issue

C0 was qualified on `97165…`; semantic replay is required on the authorized base.

Qualified head: `be9124f6699e76dc606de6c35a73885212930d78`.

Material code head: `66bdd16085a57e324f92cab4346362acf52d6f93`.

Documentary branch head: `6dc84f35e80aec709e67e3d5d3ce0cdcfaee3bcf`.

### Immediate qualification

- C0 focused suite `34/34` equivalent;
- B→Factory→C0 seam;
- upstream Factory/Validator/Red Team differential;
- semantic-vs-structural independence tests;
- no outcome/economic/runtime authority.

Rollback boundary: post-B exact qualified head.

## Port 4 — MEGA D0 Economic Lifecycle

### Why fourth

- D0 is strictly downstream of qualified science + existing W1 Economic Identity/Portfolio Readiness;
- integrating it before C0 would force the integrator to guess the scientific disposition binding;
- D0 carries a known embedded old-base identity and is therefore intentionally isolated after science contracts stabilize.

### Base issue and required adaptation

D0 was qualified on `97165…`. Its qualified code/test head is `84aa0f5f78aad9a5dfd50a20d34022b31d2fcdd9`; documentary branch head `4262462e0c853d917f32e8f87c2423f93a313167`.

Canonical convergence must explicitly rebind the base identity to the authorized Wave-2 base without changing W1 economic semantics. This adaptation must be documented as an integration repair.

### Immediate qualification

- D0 focused `33/33` equivalent;
- C0→W1 ECON→D0 seam;
- W1 ECON regression;
- exact EconomicIdentityRef/PortfolioReadinessRef binding;
- no prospective observation/outcome creation;
- lifecycle state != task state.

Rollback boundary: post-C0 exact qualified head.

## Port 5 — MEGA E Runtime

### Why last despite lane-local readiness

E is the only currently observed lane already qualified directly on `2b99…`, but it touches the highest-risk operational/global surfaces:

- canonical task/queue/lease authority;
- capabilities/blockers;
- runtime worker launch/recovery;
- events/receipts/outbox;
- Live Lab projection;
- global operational truth.

Porting it last keeps runtime regression attribution clean: if a scientific port fails, E is not involved; if E fails after stable science, the blast radius is localized to the operational seam.

Qualified head: `2d5ff9d3cbfd7c6cbd71f54bb71095b46edb2e42`.

Documentary branch head: `82da975878eb9b525e1845103fe7b35e7aeca404`.

### Immediate qualification

- E runtime focused suite;
- canonical Control Plane/task/lease ownership scan;
- science→operational admission seam;
- event/receipt/outbox/recovery tests;
- E→Live Lab factual projection tests;
- no second scheduler/queue/authority registry/Oracle.

Rollback boundary: post-D0 exact qualified head.

## Why E is not ported first

Technically E could be ported independently because it is already based on `2b99…`. That would optimize short-term green tests but worsen convergence diagnostics: subsequent B/C0/D0 base replay could then fail against a runtime-modified tree and obscure ownership. The selected order prioritizes causal attribution and scientific schema stabilization over convenience.

## Why D0 is not before C0

D0 consumes EconomicIdentityRef/PortfolioReadinessRef downstream of scientific qualification. Its code can be replayed independently for rehearsal, but canonical order should not commit the lifecycle contract before the C0 exact-subject scientific seam is proven.

## Why B is not before Multi

B itself can be qualified without Multi, and the foreman already has B evidence. But final convergence must consume the **final** Multi intake semantics. Porting Multi first allows the B port to run the real S1 seam once, rather than port B then modify its intake assumptions later.

If Multi remains externally blocked while every other lane becomes ready, canonical owner may choose a consciously documented partial-order exception, but that would not constitute full Wave-2 Convergence #2 and cannot emit the final integrated seal under this mission law.

## Parallelizable qualification inside the serial port order

After each semantic port, independent regressions may run in parallel:

- upstream non-regression suites;
- authority/outcome scans;
- schema/generated-contract consistency;
- documentary/global-truth drift scan.

The semantic port commits themselves should remain serial and rollback-addressable.

## Port receipt requirements

For every port capture:

```text
LANE=
SOURCE_BRANCH_HEAD=
SOURCE_QUALIFIED_HEAD=
SOURCE_BASE_SHA=
TARGET_PARENT_SHA=
PORT_SHA=
SEMANTIC_FILES=
INTEGRATION_ADAPTATIONS=
FOCUSED_TESTS=
SEAM_TESTS=
UPSTREAM_REGRESSION=
AUTHORITY_STATUS=CLOSED
OUTCOME_ACCESSED=FALSE
ROLLBACK_SHA=
```

No receipt may claim canonical FINAL until the whole system exact-head qualification has passed.

## Final post-port sequence

After Port 5:

1. reconcile integrator-owned global files/registries;
2. generate convergence-owned schema/contract indexes;
3. run all Level-2 seams again on the same exact head;
4. run Level-3 full system regression;
5. verify clean tree and remote exact-head equality;
6. verify no material commit after qualification;
7. only the canonical integrator may decide whether to emit `WAVE2_INTEGRATED_SHA`.

## Current gate state

`PORT_1_MULTI=BLOCKED_PENDING_EXACT_HEAD_SEAL`

`PORT_2_B=READY_FOR_SEMANTIC_REPLAY_AFTER_PORT_1`

`PORT_3_C0=READY_FOR_SEMANTIC_REPLAY_AFTER_PORT_2`

`PORT_4_D0=READY_FOR_BASE_REBIND_REPLAY_AFTER_PORT_3`

`PORT_5_E=READY_LANE_LOCAL_AFTER_PORT_4`

`READY_TO_START_CANONICAL_PORT_SEQUENCE=FALSE`

Reason: durable base seal proof and final Multi exact-head seal remain unresolved.

## Authority

`ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE`

`PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE`

`REAL_CAPITAL_AUTHORIZED=FALSE`

`LIVE_TRADING_AUTHORIZED=FALSE`

`OUTCOME_ACCESSED=FALSE`

`WAVE2_INTEGRATED_SHA_EMITTED=FALSE`
