# ANTIGRAVITY — POST-P0 VERTICAL SHADOW LOOP HIGH-VALUE PRESTAGE — 2026-09-21

ROLE:
Auxiliary Product Integration Architect / Builder-prestage.

REPOSITORY:
fahimahmedb/Quant-Trade

WORK ONLY ON:
parallel/antigravity-post-p0-vertical-shadow-loop-design-2026-09-21

MISSION TYPE:
READ_ONLY_ANALYSIS + INTEGRATION_CONTRACT + BUILDER_MISSION_PREP

Do not create another branch.

## 0. Authority

Read first, in full:

1. QUANT_NORTH_STAR.md
2. governance/BLUE_ANTIGRAVITY_HIGH_VALUE_PRODUCT_PRESTAGE_2026-09-21.md
3. governance/BLUE_POST_P0_VERTICAL_SHADOW_LOOP_PRESTAGE_PLAN_2026-09-21.md
4. governance/BLUE_WORK_ALLOCATION_PRE_GREEN_TO_ECONOMIC_LOOP_2026-09-21.md
5. handoff/BUILDER_POST_P0_VERTICAL_INTERFACE_MAP_2026-09-21.md

Pinned comparison authorities:

Blue Product spine:
cbf30c1bb38dd69c11fb64c523c3aec694116b9c

Forward:
parallel/claude-forward-data-2026-09-20
@83521dbfdd90027c90d04adfb7d814593c2355c5

Economic:
parallel/claude-economic-v2-2026-09-20
@35dff27b8fac53618da434ee6d31febbddcc0e69

Interface-map delivery:
builder/post-p0-vertical-interface-map-2026-09-21
@8d40af1f2333474d8f26509b61cb257d96f8772d

Before analysis, verify all pinned SHAs still exist.

Do not replace pinned authorities with moving branch tips.

## 1. Objective

Prepare the exact code-ready contract for:

FIRST_END_TO_END_ECONOMIC_SHADOW_LOOP

Do not redesign the whole system.

The target chain is:

SOURCE / FORWARD DATA
-> RESEARCH CANDIDATE
-> SCIENTIFIC VET
-> ECONOMIC ASSESSMENT
-> SIZE
-> RISK
-> SHADOW FILL or NO_TRADE
-> PERSISTENT BOOK
-> LEARNING / MEMORY
-> RESCAN / RETIRE / REPLACE

The terminal output may legitimately be NO_TRADE.

## 2. Highest-value questions

Deeply resolve the following seams.

### D1 Research -> Economic semantic mapping

Trace exact current types/functions and produce a field-level mapping from:

ForwardObservation / ForwardRecorder.as_of(...)
-> Research input
-> ResearchTicket / StrategyDefinition
-> EffectEstimate / EconomicAssessment inputs

For every field state:
- source path/SHA;
- source semantic meaning;
- target semantic meaning;
- whether mapping is exact, derived, unavailable, or forbidden;
- provenance/digest that must survive;
- PIT/time authority;
- fail-closed behavior when unavailable.

Do not invent statistics or convert missing scientific authority into a default.

### D2 Promotion authority

Inspect exact current transitions.

Design the minimum state-machine change needed so that:

RESEARCH VALIDATED

does NOT automatically imply SHADOW/tradable eligibility before Economic authority.

Produce the desired ordering and enumerate all current bypass paths that would need to be closed by a future Builder.

### D3 SIZE composition

Compare exact current sizing semantics in:
- Blue Desk;
- Economic V2;
- capacity;
- Risk.

Propose the smallest single authority chain.

Requirements:
- zero size is first-class;
- economic ineligibility cannot be overridden by Desk;
- portfolio Risk remains an independent veto;
- no duplicated sizing engine;
- no hidden rescaling that changes the scientific/economic coordinate.

### D4 Execution consistency

Trace:
- research cost assumptions;
- economic modeled execution/frictions;
- actual Blue shadow ExecutionModel;
- Book fill application.

Specify exactly one execution authority for actual shadow fills and one consistency contract tying modeled assumptions to it.

### D5 Durable provenance / restart chain

Specify exact stable IDs/digests for:

ForwardObservation
-> ResearchTicket
-> StrategyDefinition
-> EconomicAssessmentJournal
-> OpportunityTicket
-> DeskJournal
-> Ledger operation/fill
-> LearningStore

Show how replay/restart:
- avoids duplicate economic assessment;
- avoids duplicate fill/book mutation;
- preserves NO_TRADE/rejection reasons;
- retains upstream evidence identity.

## 3. Exact code inspection

Inspect exact pinned versions of all relevant surfaces, including at minimum:

Forward:
- src/quant/dataplane/forward_contracts.py
- src/quant/dataplane/forward_capture.py
- src/quant/dataplane/forward_recorder.py
- src/quant/dataplane/forward_admissibility.py

Blue Product:
- src/quant/factory/workers.py
- src/quant/factory/evaluate.py
- src/quant/factory/strategies.py
- src/quant/desk/desk.py
- src/quant/desk/opportunity.py
- src/quant/desk/risk.py
- src/quant/desk/execution.py
- src/quant/desk/journal.py
- src/quant/book/ledger.py
- src/quant/learning/store.py
- src/autonomous_research/ticket.py

Economic:
- src/quant/economics/decision.py
- src/quant/economics/journal.py
- src/quant/economics/sizing.py
- src/quant/economics/capacity.py
- src/quant/economics/consistency.py
- src/quant/economics/opening.py
- src/quant/economics/frictions.py
- src/quant/economics/value.py

Follow dependencies when needed.

## 4. Selective composition

Do NOT recommend whole-branch merge/cherry-pick.

For each required piece classify:

REUSE_AS_IS
ADAPT
COPY_SEMANTICS_ONLY
NEW_GLUE
DEFER
BLUE_DECISION_REQUIRED

For every ADAPT/NEW_GLUE item give:
- exact current path;
- exact proposed integration point;
- expected changed-path surface;
- reason;
- economic uncertainty closed;
- principal failure modes;
- tests needed.

## 5. First-loop acceptance test design

Prepare a single deterministic E2E test contract.

It must exercise BOTH:

A. legitimate NO_TRADE

B. positive-size SHADOW path

Required assertions:

- exact PIT source provenance survives;
- no lookahead;
- research claim remains unchanged;
- failed scientific VET cannot reach Economics;
- Economic ineligibility cannot reach SIZE/FILL;
- omitted/understated execution friction is rejected;
- capacity can force zero/reduce size according to authority;
- Risk can veto independently;
- one actual shadow ExecutionModel creates the fill;
- Ledger mutation is idempotent/restart-safe;
- duplicate replay cannot double-book;
- Learning records rejection/no-trade/fill with upstream refs;
- restart between Economic journal and Desk resumes deterministically;
- restart between Desk intent and Book commit does not duplicate outcome.

Specify exact synthetic/historical fixtures and durable artifacts.

Do not run real capital or live orders.

## 6. Blue decision packet

For each policy ambiguity requiring Blue, output:

- DECISION_ID;
- competing options;
- exact code paths affected;
- economic consequences;
- integrity/provenance consequences;
- recommended option;
- why;
- what remains uncertain.

At minimum cover:
- D1 estimator/effect mapping authority;
- D2 SHADOW promotion point;
- D3 sizing authority/composition;
- D4 execution model authority.

Do not silently decide them in code.

## 7. Future Builder mission

Draft, inside the handoff, a bounded future Builder mission for:

builder/post-p0-first-vertical-shadow-loop-2026-09-21

Do NOT create that branch now.
Do NOT implement now.

The draft must specify:
- exact base selection rule;
- exact paths allowed;
- explicit forbidden paths;
- tests;
- final acceptance;
- no real capital;
- no P0 runtime mutation.

Blue will activate that mission only in the appropriate post-Gate-B/t0/Gate-C phase.

## 8. Hard safety boundary

You may inspect repository objects and run local/read-only analysis.

Do NOT modify:
- src/
- tests/
- scripts/
- schemas/
- workflows
- production config
- P0 runtime
- target host
- Blue/Builder/Astra branches

Do NOT merge or cherry-pick canonical Forward/Economic leaves.

You may commit ONLY your final handoff to THIS branch.

## 9. Required output

Write:

handoff/ANTIGRAVITY_POST_P0_VERTICAL_SHADOW_LOOP_DESIGN_2026-09-21.md

Final status exactly:

ANTIGRAVITY_VERTICAL_PRESTAGE = READY_FOR_BLUE_REVIEW

or a precise blocker.

Include:
- exact SHAs verified;
- field-level contracts;
- state-machine diagram;
- sizing/execution authority proposal;
- durable provenance chain;
- E2E acceptance test;
- minimal changed-path forecast;
- Blue decision packet;
- future Builder mission draft;
- opportunity-cost assessment.

No profit claim.
No capital authorization.
No t0 claim.

Proceed independently and deeply.
