# BLUE — ANTIGRAVITY HIGH-VALUE PRODUCT PRESTAGE ALLOCATION — 2026-09-21

## 0. Status

`ANTIGRAVITY_HIGH_VALUE_PRESTAGE = AUTHORIZED / NON_AUTHORIZING`

Architectural authority:
`QUANT_NORTH_STAR.md`

This allocation supersedes the idea of using Antigravity primarily as a duplicate Gate-B reviewer.
The formal Gate-B run-authority recheck remains an Astra responsibility.

Antigravity is instead allocated to the highest-value parallel Product-prestage problem that can
advance without contaminating the P0/Gate-B/t0 critical path.

Current safety boundary remains:

```text
PRODUCT_INTEGRATION = PAUSED
TARGET_HOST_TOUCHED = FALSE
P0_RUNTIME_MUTATION = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
t0 = NOT_DECLARED
```

## 1. Why this is the highest-value auxiliary task

The completed post-P0 interface map establishes that most required vertical mechanisms already exist.
The remaining value is not another horizontal subsystem. The two highest-value unresolved seams are:

1. exact semantic mapping from validated Research evidence into the frozen Economic coordinate
   (`ResearchTicket / StrategyDefinition -> EffectEstimate / EconomicAssessment`) without changing
   the scientific claim;
2. exact authority ordering for
   `RESEARCH VALIDATION -> ECONOMIC ELIGIBILITY -> SHADOW PROMOTION -> SIZE -> RISK -> FILL`,
   including reconciliation of Economic margin-based sizing with the current Desk sizing path.

A third cross-cutting seam must be specified with them:

3. one immutable provenance chain from Forward observation through Research, Economic assessment,
   Desk journal, persistent Book and Learning/Memory.

Closing these design ambiguities before implementation prevents another expensive build/audit repair loop.

## 2. Exact authorities

Blue Product integration spine:
`cbf30c1bb38dd69c11fb64c523c3aec694116b9c`

Canonical Forward:
`parallel/claude-forward-data-2026-09-20@83521dbfdd90027c90d04adfb7d814593c2355c5`

Canonical Economic:
`parallel/claude-economic-v2-2026-09-20@35dff27b8fac53618da434ee6d31febbddcc0e69`

Completed interface map:
`builder/post-p0-vertical-interface-map-2026-09-21@8d40af1f2333474d8f26509b61cb257d96f8772d`

Existing governing plans:
- `governance/BLUE_POST_P0_VERTICAL_SHADOW_LOOP_PRESTAGE_PLAN_2026-09-21.md`
- `governance/BLUE_WORK_ALLOCATION_PRE_GREEN_TO_ECONOMIC_LOOP_2026-09-21.md`
- `handoff/BUILDER_POST_P0_VERTICAL_INTERFACE_MAP_2026-09-21.md`

## 3. Antigravity mission

Authorized branch:

`parallel/antigravity-post-p0-vertical-shadow-loop-design-2026-09-21`

Mission type:

`READ_ONLY_ANALYSIS + INTEGRATION_CONTRACT + BUILDER_MISSION_PREP`

Antigravity must NOT implement Product code yet.

It must produce an exact, code-ready integration contract for the first vertical shadow loop.

## 4. Required decisions to prepare for Blue

Antigravity must not silently make policy decisions that belong to Blue.
For each unresolved decision it must present:

- exact current competing semantics;
- concrete failure mode if left ambiguous;
- smallest viable options;
- consequences for provenance/economics/restart behavior;
- one recommended option with rationale;
- explicit `BLUE_DECISION_REQUIRED` marker.

At minimum:

### D1 — Research -> Economic coordinate

Define the exact mapping from current research evidence into `EffectEstimate` and related Economic inputs.

Must prove:
- estimator/claim semantics are unchanged;
- sample provenance remains exact;
- PIT/forward timing is not strengthened or laundered;
- confidence / interval / clustering provenance has one authoritative origin;
- unavailable fields fail closed rather than being invented.

### D2 — promotion authority ordering

Resolve the desired state machine conceptually:

`RESEARCH_VALIDATED`
-> `ECONOMIC_ASSESSMENT_ELIGIBLE`
-> economic verdict/eligibility
-> `SHADOW` or `NO_TRADE`

Current automatic research `VALIDATED -> SHADOW` must not remain an implicit bypass around Economic authority.

### D3 — SIZE composition

Reconcile:
- Economic V2 margin/capacity sizing;
- current Desk lifecycle/capital_fraction sizing;
- Desk portfolio Risk veto.

Specify one authority ordering with zero-size as a valid outcome.
Do not build a second sizing engine.

### D4 — execution-model consistency

Specify which model:
- supplies research/economic cost assumptions;
- produces the actual shadow fill;
- records expected-vs-realized implementation shortfall.

No duplicated booking/execution authority.

### D5 — durable provenance chain

Define stable identifiers/digests carried through:

`ForwardObservation`
-> `ResearchTicket / StrategyDefinition`
-> `EconomicAssessmentJournal`
-> `OpportunityTicket`
-> `DeskJournal`
-> `Ledger operation_id / fill`
-> `LearningStore`

The chain must support deterministic restart/replay and distinguish rejection, NO_TRADE and fill.

## 5. Required first-loop acceptance contract

Prepare one deterministic acceptance test specification for:

```text
one PIT source observation
-> one research ticket / explicit hypothesis
-> one scientific VET disposition
-> one economic assessment
-> one size/risk decision
-> one shadow fill OR NO_TRADE
-> one persistent Book result
-> one durable Learning/Memory record
```

The fixture must include BOTH:
- a legitimate NO_TRADE path;
- a positive-size shadow path where all gates allow it.

It must test:
- restart/idempotence;
- exact provenance continuity;
- lookahead/PIT bypass rejection;
- friction omission rejection;
- economic ineligibility cannot reach fill;
- Risk veto;
- Book double-apply prevention;
- Learning records rejection and fill outcomes.

This is an implementation contract, not current production proof.

## 6. Integration strategy deliverable

Antigravity must produce a selective-composition plan.

Forbidden:
- wholesale merge of the Forward leaf;
- wholesale merge of the Economic leaf;
- second scheduler;
- second Book;
- second execution engine;
- second economics engine.

For every required source path classify:

`REUSE_AS_IS | ADAPT | COPY_SEMANTICS_ONLY | NEW_GLUE | DEFER | BLUE_DECISION_REQUIRED`

Give exact source SHA/path and intended destination/integration point.

## 7. Output

Required handoff:

`handoff/ANTIGRAVITY_POST_P0_VERTICAL_SHADOW_LOOP_DESIGN_2026-09-21.md`

Required contents:
- exact authorities/SHAs;
- end-to-end contract diagram;
- D1-D5 analysis;
- exact object/field mapping;
- state-machine ordering;
- provenance chain;
- minimal changed-path forecast;
- deterministic E2E acceptance-test design;
- selective integration plan;
- explicit Blue decisions;
- post-Gate-C Builder mission proposal;
- opportunity-cost note.

Allowed status:

`ANTIGRAVITY_VERTICAL_PRESTAGE = READY_FOR_BLUE_REVIEW`

or a precise blocker.

## 8. Hard boundary before Gate C

Until Blue explicitly advances the phase:

Antigravity may read all pinned repository objects and create its handoff only.

It may NOT:
- modify `src/`, tests, scripts, schemas or workflows;
- merge/cherry-pick Forward/Economic code;
- touch the qualifying host;
- alter P0 runtime/state;
- authorize real capital.

After Gate-B PASS/t0 and when Blue declares Gate-C isolated Product implementation prep open,
Blue may dispatch a separate Builder mission using this design as input.

## 9. Economic selection rule

Every proposed code change must answer:

`WHAT ECONOMIC UNCERTAINTY DOES THIS CLOSE?`

The first slice exists to produce reproducible economic learning, not architectural elegance.
