# BLUE — WORK ALLOCATION PLAN: PRE-GREEN -> P0 EXIT -> ECONOMIC LOOP — 2026-09-21

## 0. Status

`WORK_ALLOCATION_PLAN = PREPARED / ACTIVE_FOR_NON_AUTHORIZING_WORK`

`ASTRA_FINAL_CI_GATE = 35551073229 -> COMPLETED / SUCCESS REQUIRED`

This plan allocates the minimum useful parallel work while preserving the
critical P0 proof path and the North Star.

Highest architecture authority:
`QUANT_NORTH_STAR.md`

North Star blob:
`8295041a8d253636d8f8aab941b811dce64939d9`

The terminal objective remains long-run real net economic gain after real
frictions through repeatable discovery, selection, sizing, execution,
monitoring, retirement and replacement of genuine edge.

## 1. Operating principle

The project must NOT turn the remaining P0 calendar/proof waiting time into
another horizontal infrastructure program.

Use two rails only:

```text
RAIL A — CRITICAL P0
Blue -> promotion -> Gate B -> t0 -> Gate C -> Gate D -> P0 EXIT

RAIL B — ECONOMIC PRESTAGE
interface mapping -> first vertical shadow-loop plan -> isolated Product prep
```

Rail B may never mutate or contaminate Rail A.

## 2. Concurrency cap

Maximum active substantial workstreams before P0 exit:

`2`

1. Blue/Mission Control on the P0 critical path.
2. One Product prestage Builder on a fully separate branch.

A target-host read-only preflight may occur as a short operator task but is not
a third development workstream.

Do NOT launch multiple Builders against the same files/surfaces.

Do NOT spend Astra on routine implementation or code review.

## 3. NOW — before Astra exact-head CI turns green

### Workstream A — Blue / Mission Control

Owner:
`BLUE`

Branch:
`blue/master-v2-2026-09-20`

Status:
active now.

Tasks:
1. preserve exact Astra/Builder refs;
2. keep final Blue reception prefilled;
3. keep final consistency precheck ready;
4. keep atomic promotion package ready;
5. keep Gate-B activation presealing non-authorizing;
6. monitor exact Astra run `35551073229`.

Deliverables already prepared:
- `handoff/BLUE_ASTRA_RESTART_BURST_FINAL_RECEPTION_2026-09-21.md`
- `governance/BLUE_HYBRID_PROMOTION_FINAL_CONSISTENCY_PRECHECK_2026-09-21.md`
- `governance/BLUE_HYBRID_PROMOTION_ATOMIC_DRY_RUN_2026-09-21.md`
- `governance/BLUE_GATE_B_ACTIVATION_PRESEAL_2026-09-21.md`
- `governance/BLUE_P0_POST_ASTRA_GREEN_EXECUTION_CONTROL_PLAN_2026-09-21.md`

Forbidden before green:
- hybrid promotion;
- Gate-B activation;
- target-host mutation;
- t0 declaration;
- Product integration merge.

### Workstream B — Product Integration Scout / Builder

Owner:
`BUILDER / CODEX`

Recommended branch:
`builder/post-p0-vertical-interface-map-2026-09-21`

May start NOW.

Mission type:
`READ_ONLY_ANALYSIS + HANDOFF_ONLY`

No production implementation.

Mandatory exact sources:
- North Star;
- Blue current routing;
- canonical Forward:
  `parallel/claude-forward-data-2026-09-20@83521dbfdd90027c90d04adfb7d814593c2355c5`;
- canonical Economic:
  `parallel/claude-economic-v2-2026-09-20@35dff27b8fac53618da434ee6d31febbddcc0e69`;
- current Research/Book surfaces on Blue.

Questions to answer:
1. What exact Forward output object can feed Research?
2. What exact Research ticket/hypothesis object can feed VET?
3. What is currently missing for VET?
4. Which fields feed the economic engine?
5. Where are fees/spread/slippage/financing/capacity applied?
6. What object carries SIZE/RISK?
7. Is there already a shadow-fill abstraction?
8. What Book transition API exists?
9. How does Learning/Memory consume rejects/fills/errors/decay?
10. What is the minimum glue required for one end-to-end shadow slice?

Required classification for every component:
- `REUSE_AS_IS`;
- `ADAPT`;
- `MISSING_GLUE`;
- `DEFER`;
- `CONFLICT / BLUE_DECISION_REQUIRED`.

Required handoff:
`handoff/BUILDER_POST_P0_VERTICAL_INTERFACE_MAP_2026-09-21.md`

The handoff must contain:
- exact source SHAs;
- exact compared paths;
- data-contract diagram;
- minimum vertical slice;
- smallest implementation delta;
- no architecture expansion unless a concrete blocker requires it;
- no profit/edge claim.

Acceptance:
`PRODUCT_PRESTAGE_INTERFACE_MAP = READY_FOR_BLUE_REVIEW`

Forbidden:
- changing Product code;
- merging canonical leaves;
- modifying P0 runtime;
- changing scientific claims;
- opening capital authority.

## 4. Optional short task NOW — target-host read-only preflight

Owner:
`OPERATOR / CODEX UNDER BLUE INSTRUCTIONS`

This is optional because it must not become a new workstream.

Execution:
real target host, READ ONLY only.

Purpose:
detect obvious host drift before Gate-B activation without consuming or creating
qualification authority.

Allowed reads:
- current boot id;
- UTC/time/NTP state;
- mount inventory;
- persistent-state identity;
- installed Python/OpenSSL/runtime versions;
- systemd unit/drop-in text and show output;
- filesystem free space/inodes;
- resource baseline;
- proxy/network/TLS environment;
- current service state;
- evidence-retention path availability.

Forbidden:
- start/stop/restart;
- daemon-reload;
- reboot;
- mount/remount;
- create/delete/modify release or state;
- synthetic fault setup;
- real SEC requests;
- materialize V4 release;
- consume activation authority.

Output:
a timestamped READ-ONLY snapshot for Blue.

This snapshot is diagnostic only and MUST be recollected/rebound at actual
Gate-B activation time.

## 5. TRIGGER G — Astra exact-head CI becomes green

Trigger:

`35551073229 = COMPLETED / SUCCESS`

and exact Astra branch remains:

`61facacdcdc499bd3e6680644c75c97fcff22656`

### Blue actions — immediate, sequential

G1. Finalize Astra reception:
```text
FINAL_INDEPENDENT_FAULT_MATRIX_REVIEW = PASS
UNRESOLVED_REPOSITORY_MISSING_PROOF = 0
```

G2. Run final consistency check against live blobs.

G3. If PASS, execute atomic hybrid promotion.

G4. End promotion with:
```text
P0_CONTINUITY_QUALIFICATION = HYBRID_EVENT_BASED_V1
P14D = HISTORICAL / SUPERSEDED_FOR_FUTURE_QUALIFICATION
TARGET_HOST_READY = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
PRODUCT_INTEGRATION = PAUSED
REAL_CAPITAL_AUTHORIZED = FALSE
```

These actions remain BLUE-only.
Do not delegate final authority transitions to Builder or Astra.

## 6. AFTER promotion — Gate-B activation

### Blue

Create one concrete sealed Gate-B activation artifact.

Bind:
- hybrid amendment ref/digest;
- authoritative Gate-B contract/runbook/schema/materialization refs/digests;
- exact V4 candidate identity;
- unique `GATE_B_RUN_ID`;
- actual host snapshots;
- explicit mutation permissions.

Default deny every mutation not required.

### Operator

Execute only the authoritative runbook and only the explicitly authorized
mutations.

No improvisation.

First mandatory failure makes the run terminal.
A retry needs a new run ID and new Blue activation.

### Builder

IDLE for P0 unless Gate B reproduces a concrete implementation defect.

### Astra

IDLE unless:
- Gate B exposes an ambiguous high-impact defect;
- Blue needs an independent reproduction that can alter the P0 decision.

## 7. Gate-B PASS -> t0 -> Gate C

After Blue receives Gate-B PASS:

1. Blue seals t0 precommit.
2. One-use qualifying launch establishes t0.
3. Gate C watches real required events.

During Gate C, P0 runtime is frozen except by the authoritative reset/invalidation
rules.

## 8. DURING Gate C — use calendar wait economically

This is where Rail B may move from analysis to isolated implementation prep.

Prerequisite:
- Product Integration Scout handoff accepted by Blue;
- no mutation of qualifying P0 runtime.

### Builder Product Integration mission

Recommended branch:
`builder/post-p0-first-vertical-shadow-loop-2026-09-21`

Base:
selected by Blue after reviewing the interface-map handoff.

Mission:
implement ONLY the minimum isolated vertical slice needed to demonstrate:

```text
one source observation
-> one research ticket/hypothesis
-> one VET disposition
-> one economic assessment
-> one SIZE/RISK result
-> one shadow fill OR NO_TRADE
-> one persistent Book transition
-> one Learning/Memory record
```

Allowed:
- isolated Product branch;
- synthetic/historical fixtures;
- tests;
- glue code;
- shadow-only execution abstractions.

Forbidden:
- merge to qualifying P0 runtime;
- deployment to P0 target release;
- real capital;
- live-order submission;
- architecture expansion not required by the slice.

Required acceptance test:
one command/test must replay the full slice and leave durable, inspectable
artifacts for every transition.

## 9. Independent review policy for the Product slice

Do NOT run a giant Astra audit by default.

First:
Builder -> Blue technical/economic reception.

Use Red Team for:
- provenance break;
- lookahead/PIT bypass;
- friction omission;
- unrealistic fill;
- Book inconsistency;
- NO_TRADE bypass;
- restart/state-loss defect.

Use Astra only if a decision is frontier-worthy, for example:
- research/economic semantics are ambiguous enough to alter weeks of work;
- capital-risk architecture is disputed;
- scientific validity cannot be resolved cheaply;
- a major architecture choice could lock the system into the wrong topology.

Astra is not a routine test runner.

## 10. Gate D -> explicit P0 EXIT

After Gate D PASS, Blue creates a durable P0 exit.

Required:
```text
P0_QUALIFICATION = CLOSED
P0_POST_QUALIFICATION_SURVEILLANCE = ACTIVE
PRODUCT_INTEGRATION = UNPAUSED
NEXT_PRIMARY_OBJECTIVE = FIRST_END_TO_END_ECONOMIC_SHADOW_LOOP
REAL_CAPITAL_AUTHORIZED = FALSE
```

From this point:
P0 becomes maintenance/surveillance.

## 11. First post-P0 Product sequence

Do not restart from architecture.

Sequence:

1. Blue reviews Product Interface Scout handoff.
2. Qualify exact canonical Forward leaf.
3. Qualify exact canonical Economic leaf.
4. Decide integration baseline.
5. Reimplement/cherry-pick only semantically valid pieces.
6. Complete missing VET / fill / Book / Learning glue.
7. Run the first end-to-end shadow test.
8. Independently attack its economic false-positive channels.
9. Start repeated shadow runs.
10. Let observed economic bottlenecks choose the next work.

## 12. Mission-selection rule after P0

Before allocating Builder time, require:

`WHAT ECONOMIC UNCERTAINTY DOES THIS CLOSE?`

Good:
- signal survives forward timing;
- edge survives friction;
- capacity is sufficient;
- size should be zero/nonzero;
- risk veto is correct;
- shadow fill model is realistic;
- Book state is coherent;
- learning detects decay/replacement.

Bad:
- cleaner architecture;
- more agents;
- generalized framework;
- nicer abstraction without a current consumer.

## 13. Capital boundary

All work in this plan remains:

`REAL_CAPITAL_AUTHORIZED = FALSE`

Capital path remains:
scientific evidence -> capturability/cost/capacity -> repeated forward shadow ->
capital readiness -> explicit owner authorization -> tiny real capital -> scaling
-> monitoring -> decay -> retirement/replacement.

## 14. Allocation summary

```text
NOW
Blue        : wait/receive/promote critical P0 path
Builder #1  : Product interface-map handoff only
Operator    : optional read-only host snapshot
Astra       : idle
Builder #2+ : do not launch

AFTER GREEN
Blue        : reception -> consistency -> promotion
Operator    : only after sealed Gate-B activation
Builder     : idle unless concrete defect
Astra       : idle

DURING GATE C
Blue        : monitor P0
Builder #1  : isolated first vertical shadow-loop implementation
Operator    : P0 runtime only per authoritative rules
Astra       : reserve for high-value decisions

AFTER P0 EXIT
Blue        : unpause Product / select integration baseline
Builder     : finish vertical economic loop
Red Team    : targeted falsification
Astra       : only if frontier-worthy
```
