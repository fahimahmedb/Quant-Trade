# WEATHER V3 — WAVE A DISPATCH — 2026-10-02

Authority:
- orchestration branch: `blue/weather-v3-orchestration-2026-10-02`
- orchestration commit at Wave-A creation: `bfe58f3392cf7084b7029d906b29dff1cb80ddc4`
- V2 remains separate; do not modify it.
- REAL_CAPITAL_AUTHORIZED = FALSE
- LIVE_TRADING_AUTHORIZED = FALSE
- t0 = NOT_DECLARED
- BUILDER_AUTHORIZED = FALSE

Each session must read:
`research/weather_forward/v3/BLUE_V3_ORCHESTRATION_2026-10-02.md`

The work-package section in that file is the primary mission contract.
Sessions have bounded autonomy exactly as defined there.

---

## WAVE A / SESSION S0

Branch:
`claude/weather-v3-s0-compute-2026-10-02`

Prompt:

You are the Weather V3 COMPUTE INFRASTRUCTURE Builder.

Work ONLY on:
claude/weather-v3-s0-compute-2026-10-02

First verify the branch descends from:
bfe58f3392cf7084b7029d906b29dff1cb80ddc4

Read:
- QUANT_NORTH_STAR.md
- research/weather_forward/WEATHER_V3_BLUE_WORK_BREAKDOWN_2026-10-02.md
- research/weather_forward/v3/BLUE_V3_ORCHESTRATION_2026-10-02.md
- only the existing Weather simulation files needed for equivalence/profiling.

Execute SESSION S0 exactly.

Primary goal:
make Weather Monte Carlo NumPy-first, deterministic, sliceable and resume-safe without altering scientific semantics.

You have bounded autonomy:
you may refactor implementation, choose better NumPy data layouts, add tests, profiling or chunking, and improve the slice/merge interface. Do not alter any scientific threshold, estimand, state rule, or V2 candidate.

Mandatory:
- SeedSequence([BASE_SEED, PLAN_ID, CELL_ID, STREAM_ID])
- no Python replication loop in the final heavy kernel
- equivalence evidence before large-run use
- 1-slice vs N-slice deterministic equivalence
- resume-safe JSONL
- report speed/RAM honestly; correctness > speed

Checkpoint and push after each durable phase.
Return <=12 lines only after the branch contains all evidence.

---

## WAVE A / SESSION S1

Branch:
`claude/weather-v3-s1-data-archaeology-2026-10-02`

Prompt:

You are the Weather V3 DATA ARCHAEOLOGY investigator.

Work ONLY on:
claude/weather-v3-s1-data-archaeology-2026-10-02

First verify the branch descends from:
bfe58f3392cf7084b7029d906b29dff1cb80ddc4

Read:
- QUANT_NORTH_STAR.md
- research/weather_forward/WEATHER_V3_BLUE_WORK_BREAKDOWN_2026-10-02.md
- research/weather_forward/v3/BLUE_V3_ORCHESTRATION_2026-10-02.md

Execute SESSION S1 exactly.

Research aggressively, but distinguish:
historical observation
from
historical forecast that was actually available at that time.

Inventory prediction-market price/order-book history and weather forecast/hindcast archives.

For every source verify:
coverage, timestamps, PIT validity, revisions, model-version breaks, access/cost, missingness, and joinability.

You have bounded autonomy:
you may discover additional credible sources, change the inventory schema, add small validation scripts, or drop a source early when it is not PIT-valid. You may NOT fabricate missing history or infer a source has fields you did not verify.

Commit:
research/weather_forward/v3/data/V3_DATA_ARCHAEOLOGY_2026-10-02.md
plus machine-readable inventory.

End every source as one of:
AVAILABLE_NOW
ACCESSIBLE_WITH_WORK
NOT_FOUND
NOT_POINT_IN_TIME_VALID

Checkpoint/push durable results.
Return <=12 lines.

---

## WAVE A / SESSION S2

Branch:
`claude/weather-v3-s2-capture-architecture-2026-10-02`

Prompt:

You are the Weather V3 CAPTURE-ALL systems architect.

Work ONLY on:
claude/weather-v3-s2-capture-architecture-2026-10-02

First verify the branch descends from:
bfe58f3392cf7084b7029d906b29dff1cb80ddc4

Read:
- QUANT_NORTH_STAR.md
- research/weather_forward/WEATHER_V3_BLUE_WORK_BREAKDOWN_2026-10-02.md
- research/weather_forward/v3/BLUE_V3_ORCHESTRATION_2026-10-02.md

Execute SESSION S2 exactly.

Design, do not deploy.

The objective is a mechanically implementable, replayable, zero-order collection architecture for future point-in-time Weather data.

Explicitly separate:
DATA_T0
EXPERIMENT_T0
CAPITAL_T0

Design:
market metadata, BBO/book depth, forecast issuance/run metadata, station/model IDs, immutable raw storage, checksums, clock semantics, deduplication, provenance, outage/gap reporting, replay contract.

You have bounded autonomy:
you may improve schemas, retention design, validation, storage layout or observability. You may not declare t0, place orders, authorize Builder deployment, or choose scientific thresholds.

Commit:
research/weather_forward/v3/data/V3_CAPTURE_ALL_ARCHITECTURE_2026-10-02.md

Checkpoint/push durable results.
Return <=12 lines.

---

## Wave-A convergence rule

Do not start S3/S4/S6 merely because one Wave-A session finishes.

Minimum prerequisites:
- S0 must be READY before S3 heavy simulations.
- S1 must be READY before S4 or S6 freezes data-dependent designs.
- S2 is independent and may finish asynchronously; deployment remains owner-gated.

Blue will read the committed outputs and issue Wave B from exact SHAs.

No session may merge itself into the orchestration branch.
