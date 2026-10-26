# Edge Discovery Method — Time-to-Edge

Status: methodological handoff only. This document records the current research method; it does **not** modify the worker, scheduler, Site, validation gates, or capital permissions.

## Objective

Optimize for one thing: **reduce expected time to a real, capturable, still-live edge**.

Do not optimize for number of files, frameworks, audits, tests, Sharpe estimates, or governance sophistication. Engineering is justified only when it unlocks multiple economic tests, protects result integrity, or restores a broken end-to-end capability.

## Core doctrine

**Search widely → filter cheaply → test economically → promote rarely → freeze → observe prospectively → validate severely.**

The main probabilistic lever is the number of **causally distinct mechanisms** that reach a first clean economic look per unit of time, not the number of parameter variants.

## Research funnel

### L0 — ultra-light mechanism/data triage

Purpose: eliminate obvious dead ends before expensive formalization, without reading economic outcomes.

A candidate should fit in roughly six fields:

- `MECHANISM`
- `WHO_PAYS`
- `WHY_PERSIST`
- `CHEAP_DATA_NOW`
- `CHEAP_EXPRESSION`
- `FATAL_PROBLEM`

Allowed outcomes:

- `L1_NOW`
- `PARK_DATA`
- `PARK_ECONOMICS`
- `DUPLICATE`

L0 is **not** an economic verdict. It must not inspect signal→future-return/PnL outcomes.

### L1 — V4.2 frozen economic test

Only L0 survivors receive the existing V4.2 contract discipline before the first economic look:

- exact expression;
- asymmetric inference rights (`TEST_CAN_KILL`, `TEST_CAN_SUPPORT`, `TEST_CANNOT_SAY`);
- adequacy conditions;
- known biases;
- fixed economic units/frictions;
- one predeclared adversarial check;
- no post-outcome retuning presented as fresh evidence.

A single economic look should answer one decision question cheaply.

### After a positive

One cheap predeclared red-team only. If it survives, **freeze the expression**.

Do not respond to a positive by launching a parameter search or a family of nearby backtests.

### Passive forward OOS incubation

A sufficiently frozen survivor should accumulate genuinely prospective evidence while Search continues elsewhere.

The OOS record must keep fixed:

- signal rules;
- universe;
- timing;
- data availability semantics;
- evaluation metrics;
- invalidation rules.

Any material post-freeze change creates a new linked variant, not a reinterpretation of the old OOS record.

### V3 strict validation

V3 remains the strict validation/capturability lane. It receives only survivors worth paying the cost of PIT reconstruction, survivorship-safe data, executable prices, rolls, CTD/DV01, fills, costs, capacity, etc.

Discovery never validates an edge and never authorizes real/live capital.

## Breadth: what counts as a new chance

Prefer **mechanism breadth**, not parameter breadth.

Use these dimensions to compare candidates, without pretending they form a precise independence score:

- `WHO_PAYS`
- `INEFFICIENCY_SOURCE`
- `INFORMATION_SOURCE`
- `MARKET_STRUCTURE`
- `MONETIZATION_PATH`
- `TIME_HORIZON`

Two variants that differ only by horizon/threshold/window are usually one research chance. Two hypotheses in the same asset class may still be meaningfully distinct if their causal signatures differ.

## Multiplicity / exposure accounting

Keep the complete history, but distinguish exposure types:

1. `IDEA_GENERATED` — no economic outcomes read.
2. `DATA_FEASIBILITY` — source/schema/rights/coverage only.
3. `ECONOMIC_LOOK` — signal→future-return/PnL observed.
4. `POST_OUTCOME_VARIANT` — material change after outcomes.

Statistical/selection concern should primarily increase with economic looks and post-outcome variants, not with harmless idea generation or API feasibility checks.

Closed/rejected families remain closed; renaming is not a fresh test.

## Throughput and autonomy

The system should maintain three simple inventories:

- `IDEA INVENTORY`: many untested causal mechanisms;
- `READY INVENTORY`: a small queue of L0 survivors ready for L1;
- `OOS INVENTORY`: frozen survivors accumulating prospective evidence.

The operational goal is to avoid `READY INVENTORY = 0` while plausible accessible mechanisms remain.

While one economic look is active, the system should still be allowed to:

- generate new mechanisms;
- run L0 triage;
- qualify sources and rights;
- prepare the next frozen L1.

Do **not** rush to concurrent economic writes yet. Keep one economic look active until a real ready-queue bottleneck demonstrates that parallel economic execution is worth the state/CAS complexity.

## Multi-agent use

Do not spend several strong models repeatedly auditing the same mechanism.

Use agents on deliberately different causal territories, for example:

- forced flows / institutional mechanics;
- information diffusion / event-driven;
- market structure / low-capacity rents.

A single L0 selector removes duplicates and sends only the best testable survivors to L1.

## Small-actor advantage

Do not optimize only for large scalable institutional alpha. Our search prior should explicitly include edges large funds may rationally ignore because of:

- low capacity;
- operational nuisance;
- fragmented public data;
- irregular events;
- small markets;
- high fixed research cost relative to deployable institutional capital.

`WHY_NOT_ARBITRAGED` can validly be: the opportunity is too small or operationally unattractive for large capital but meaningful for us.

## What not to build now

Unless it directly unlocks research, avoid:

- another V5/V6 governance layer;
- numeric pseudo-precision for “effective breadth”;
- a Bayesian prioritization engine;
- a large hidden-benchmark infrastructure;
- elaborate dashboard work;
- concurrent economic execution before a demonstrated queue bottleneck;
- historical reconstruction work that does not change the next economic decision.

A researcher-quality benchmark for false kills / false promotions is valuable later, after enough fresh decisions exist to calibrate it without becoming a governance project itself.

## End-to-end infrastructure rule

Site and automation are not “method versions”. They are binary product capabilities with end-to-end acceptance tests.

`AUTONOMY_E2E = PASS` only if a scheduled run can be traced from trigger → unique run → fresh HEAD/control read → useful research decision/action → durable publication, without human intervention.

`SITE_E2E = PASS` only if the public Site is actually deployed, returns successfully, and displays telemetry corresponding to the expected fresh HEAD/timestamp.

Unit tests, YAML correctness, fresh `LIVE.json`, or a declared session are not substitutes for those end-to-end proofs.

When either capability is broken, repair the root cause and verify the real external behavior. Do not create a new governance version around the failure.

## Decision rule for any proposed work

Before spending time, ask:

> **What new economic information can this action produce, or how many future economic tests does it directly unblock?**

If the answer is “none” and it mainly creates cleaner organization, refuse it unless it is required for integrity or an end-to-end repair.

## Immediate research posture

The next useful research cycle should be aggressive on economic work:

1. derive the old funnel baseline only from already-saved metadata if cheap;
2. source a fresh set of causally distinct mechanisms;
3. L0-triage them rapidly without outcomes;
4. keep several L1-ready candidates prepared;
5. execute L1 economic looks sequentially without idle gaps;
6. freeze/promote rare survivors into passive OOS;
7. send only justified survivors to V3.

The target is **maximum decision-relevant economic learning per hour**, with the smallest amount of machinery needed to preserve scientific integrity.