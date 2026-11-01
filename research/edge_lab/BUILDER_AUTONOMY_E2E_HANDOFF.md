# BUILDER HANDOFF — AUTONOMY_E2E

## Mission

Repair and prove the existing scheduled research loop **end to end**. This is a product-capability repair, not a new governance version.

Canonical research method: `research/edge_lab/EDGE_DISCOVERY_METHOD.md`.

Success means one future scheduled trigger, with no human intervention after the test is armed, produces a useful autonomous decision and a durable receipt that can be independently tied back to that scheduled pass.

Target acceptance state:

`AUTONOMY_E2E = PASS`

Do **not** claim success from unit tests, a fresh `LIVE.json`, an enabled task, a CLI session declaration, or an unrelated GitHub commit.

---

## Known facts — do not rediscover from scratch

- Repository: `fahimahmedb/Quant-Trade`
- Research branch: `research/edge-lab-continuous`
- The scheduled ChatGPT automation exists and is enabled.
- Automation title: `Recherche Quant — Discovery V4.2`
- Automation id observed by Owner tooling: `6ac978ecda1081918fba4d76dee437f4`
- Schedule is hourly, Europe/Paris.
- Historical backend runs have been observed, including `2026-10-12T09:15:46Z` and `2026-10-12T09:34:42Z`.
- The worker historically records `delivery_verified = False` and explicitly states that a published CLI session is **not** scheduler-delivery telemetry.
- Historical defects included zero ready tasks, `IDLE`, WAIT/recovery, and V3 recovery obscuring Discovery.
- Discovery routing has since been made primary.
- A global Discovery `unfinished = running or recovery` condition can still serialize economic work. **Do not solve concurrency in this mission.**
- For now one economic look at a time is acceptable. L0/data-feasibility/L1 preparation should eventually be able to continue while an economic look is active, but that is not the acceptance test for this repair.
- `REAL_CAPITAL_AUTHORIZED = FALSE` and `LIVE_TRADING_AUTHORIZED = FALSE` remain invariant.

---

## Core hypothesis to test first

The system may be doing useful work, but there is no durable attribution chain proving:

`scheduled trigger -> actual run -> fresh authority read -> useful autonomous decision -> durable publication`

The fastest test is a **preassigned one-use canary**, not a scheduler rewrite.

---

## Phase A — observe before modifying

Before changing scheduler/worker/recovery code:

1. Read the exact remote branch HEAD.
2. Read `research/edge_lab/CONTROL.json` fresh.
3. Inspect the current scheduled-worker entry points and receipt paths.
4. Identify the smallest durable receipt surface already present or safely addable.
5. Confirm that any change you propose cannot execute an economic outcome, authorize capital, reset a prior claim, replay an economic look, or rewrite prior evidence.

Do not refactor first.

---

## Phase B — arm one canary pass

Generate exactly one unique nonce for the next scheduled test, for example:

`AUTONOMY_CANARY_20261012_<HHMM>_<8HEX>`

Requirements:

- nonce must be generated before the target scheduled run;
- it must be unique and single-use;
- no manual relaunch, prompt edit, or competing manual run is allowed between arming and observing the target scheduled pass;
- if platform scheduler history/run metadata is available, capture its reference; if no native run id is exposed, write `RUN_REFERENCE = UNAVAILABLE` rather than inventing one;
- do not require a new trigger-id subsystem merely to run the test.

The scheduled instruction for this one test must require a durable receipt containing at minimum:

- `canary` — exact nonce;
- `scheduled_for` — expected scheduled time if known;
- `observed_run_at` — timestamp the agent/run itself observes;
- `head_before` — exact remote HEAD read before action;
- `control_digest_or_summary` — enough to prove fresh control was read, without copying secrets;
- `decision` — one useful autonomous research decision/action;
- `decision_reason` — bounded explanation;
- `head_after` or durable `result_reference`;
- `scheduler_run_reference` if available, otherwise literal `UNAVAILABLE`;
- `human_intervention_after_arming = false`.

A useful autonomous decision does **not** need to be an economic result. Examples that are acceptable if real and useful:

- prepare one fresh L0 candidate;
- perform one data-feasibility qualification;
- predeclare the next admissible L1 contract without reading outcomes;
- conclude there is no admissible economic look and persist the next useful research action.

A meaningless heartbeat is not sufficient.

Prefer storing the receipt under a dedicated evidence path such as:

`research/edge_lab/e2e/autonomy/<CANARY>.json`

If an existing receipt surface is already clearly better, reuse it rather than creating parallel machinery.

---

## Phase C — independent verification

After the scheduled window passes:

1. Read the remote branch independently.
2. Locate the exact nonce.
3. Verify `head_before` existed before the receipt publication.
4. Verify `head_after` / result exists remotely and is causally compatible with the receipt.
5. Verify the canary was not present before the armed run.
6. Verify there was no human/manual intervention after arming.
7. If platform task-history metadata is accessible, reconcile the observed scheduled pass with the receipt timestamp/reference.

Classify the first missing transition, not just the final failure.

Use one of these statuses:

- `PASS`
- `SCHEDULER_TRIGGER_NOT_OBSERVED`
- `RUN_STARTED_RECEIPT_MISSING`
- `FRESH_AUTHORITY_READ_MISSING`
- `USEFUL_DECISION_MISSING`
- `PERSISTENCE_FAILED`
- `ATTRIBUTION_AMBIGUOUS`
- `EXTERNAL_PLATFORM_BLOCKER`

Do not invent a more elaborate state machine.

---

## Phase D — repair only the demonstrated broken transition

Only after the canary test localizes the break may you modify implementation.

Examples:

- if the scheduled trigger is not observed, repair scheduler/task configuration only;
- if the run starts but never persists a receipt, repair the handoff/receipt boundary only;
- if stale authority is read, repair fresh-head/control hydration only;
- if useful work is skipped despite admissible L0/data-feasibility work, repair routing only;
- if GitHub publication fails, repair the publication/CAS boundary only.

Then arm **one fresh canary** and repeat the E2E test exactly once.

Do not use the same nonce again.

---

## Hard non-goals

Do not:

- create V5/V6 governance;
- redesign Discovery V4.2;
- change research methodology;
- parallelize economic looks;
- reopen closed families;
- read/replay sealed outcomes;
- touch Site deployment;
- build a general observability platform;
- create dashboards;
- replace the scheduler if a narrow repair suffices;
- equate unit-test success with E2E success.

---

## Acceptance test

`AUTONOMY_E2E = PASS` only when one fresh scheduled canary demonstrates, without human intervention after arming:

`scheduled pass -> identifiable run/nonce -> fresh HEAD + CONTROL read -> useful autonomous decision -> durable remote result/receipt`

and an independent read verifies that exact receipt/result on the remote branch.

If a native scheduler run id is unavailable, a unique preassigned nonce + target schedule + scheduler history timestamp (when available) + no manual intervention is acceptable operational attribution. State the limitation explicitly.

---

## Required final handoff

Return only the following concise block after work is complete:

`AUTONOMY_E2E = PASS | FAIL | BLOCKED`

`CANARY =`

`SCHEDULED_FOR =`

`OBSERVED_RUN_AT =`

`HEAD_BEFORE =`

`DECISION =`

`HEAD_AFTER_OR_RESULT =`

`RUN_REFERENCE =`

`FIRST_BROKEN_TRANSITION =`

`ROOT_CAUSE =`

`FIX =`

`VERIFICATION =`

`FILES_CHANGED =`

`COMMIT =`

If blocked by platform capability, persist the evidence and exact blocker; do not fabricate PASS.