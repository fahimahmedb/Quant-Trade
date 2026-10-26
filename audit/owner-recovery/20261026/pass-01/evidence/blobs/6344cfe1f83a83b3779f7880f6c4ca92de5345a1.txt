# BLUE — Integration Readiness Plan — 2026-09-20

## 0. Purpose

This document is Blue's executable integration contract while the active Claude branches continue to evolve.

It exists to prevent local progress from creating a disconnected system or invalidating P0 evidence. It does **not** authorize real capital, declare `t0`, start the 14-day P0 continuity window, or grant scientific authority that does not already exist.

North Star governing test:

> Does this move Quant closer to a persistent autonomous system that can discover, select and monetize real edge while preserving state and learning from outcomes?

Terminal objective remains net economic gain / long-run real wealth growth after real frictions. `NO_TRADE` remains valid when economically superior.

---

## 1. Live branch snapshot at drafting time

Repository: `fahimahmedb/Quant-Trade`

| Mission | Branch | HEAD | Current status |
|---|---|---|---|
| P0 / Astra | `astra/p0-deep-adversarial-pre-t0` | `dbbdbe565defc869411f3d4a60a0cd974a5b2d86` | exact-head SEC P0 gate run `35476344734` still in progress |
| Economic V2 | `parallel/claude-economic-v2-2026-09-20` | `6bc38c71a2bd9d6d54f17d7e479a900bb0318d5b` | 3 commits ahead of Wave 1; no exact-head GitHub Actions run |
| Forward Data | `parallel/claude-forward-data-2026-09-20` | `61ba4c85e74b5603d5e306eaaf004c673c766973` | 4 commits ahead of Wave 1; no exact-head GitHub Actions run |
| Wave 1 base | `parallel/claude-wave1-economic-system-2026-09-19` | `b17b381a8fa1f6a24e6cd6f92a090b40627bfe78` | common product integration base |

Current diff shape from Wave 1:

- Economic V2 currently changes only `src/quant/economics/**`, its tests/fixtures and handoff.
- Forward currently changes only `src/quant/dataplane/forward_*.py`, its tests and handoff.
- P0 has diverged substantially and touches `clock.py`, `state.py`, `scripts/quant.py`, SEC acquisition code, systemd/supervisor, workflows and status surfaces.

This means P0 is **not** a safe product merge base. Its qualifying runtime must be managed as a separately pinned deployment target.

---

## 2. Integration topology

### 2.1 Two distinct lines must stay separate

**Line A — Qualifying P0 runtime**

Purpose: preserve acquisition integrity, PIT reconstructability, firewall properties and future continuity evidence.

- exact pinned P0 code tree;
- exact fingerprint;
- exact systemd definition;
- persistent SEC operational state;
- no unrelated Economic/Forward development deployed into this tree during qualifying continuity.

**Line B — Product integration runtime**

Purpose: evolve the whole Quant system toward the North Star.

Base:

`parallel/claude-wave1-economic-system-2026-09-19`

Receives, after acceptance:

1. Forward Data final branch;
2. Economic V2 final branch;
3. Blue Forward → Clock integration patch;
4. Blue Economic → Desk/Risk/Book integration patch;
5. end-to-end closure tests;
6. Astra whole-system review later.

These two lines can share repository history but must not share a mutable deployed code tree during P0 qualification.

---

## 3. Required integration order

### Gate 0 — P0 deployment isolation decision

Before any future qualifying `t0`:

- define the exact immutable P0 release/worktree that will occupy `/opt/quant`;
- ensure active development occurs elsewhere;
- prove the service starts from the exact pinned tree;
- prove fingerprint equality against that deployed tree;
- prove systemd effective configuration matches the fingerprinted contract;
- record exact commit/tree/fingerprint/runtime/service identity in the deployment evidence.

Do not merge P0 wholesale into the product integration line merely to make repository history look unified.

### Gate 1 — Receive Forward Data as a leaf capability

Receive only after Forward publishes a final handoff and satisfies Section 4.1.

Why first:

- forward observations have irrecoverable time value;
- its current code is largely isolated from Clock/Desk;
- landing the leaf capability early reduces future lost observation time;
- it can still remain dormant until the Clock patch is accepted.

### Gate 2 — Receive Economic V2 as a leaf capability

Receive only after Economic V2 publishes a final handoff and satisfies Section 4.2.

This merge alone does **not** mean economic controls are system guarantees. Until Desk consumes them, they are capability, not enforcement.

### Gate 3 — Blue Forward → Clock patch

Only after Forward's callable contract is final.

The patch must add one Control-Plane-owned scheduling seam without a second scheduler or queue.

### Gate 4 — Blue Economic → Desk/Risk/Book patch

Only after Economic V2 contract is final.

The live chain must become:

`Research evidence → economic assessment → capital/order eligibility → SIZE → RISK → FILLS → BOOK`

with durable identity linking each booked action back to the assessment that permitted it.

### Gate 5 — End-to-end closure

Run the integration matrix in Section 6.

Only after this gate should Astra Mission #3 perform the whole-system closure audit.

---

## 4. Branch reception criteria

### 4.1 Forward Data acceptance

Required before landing the Forward branch:

- final committed handoff exists;
- no `src/quant/clock.py` modification in the Forward mission branch;
- no `src/quant/dataplane/sec/**` modification;
- no second scheduler, loop, service, thread or competing Control Plane;
- `ForwardCaptureRequest`, `ForwardCaptureTaskState`, `due(...)` and `execute_forward_capture(...)` are stable enough for a caller contract;
- every capture attempt is durably accounted for on success and failure;
- observation recorder is idempotent across restart;
- conflicting second writes remain visible as conflict rather than silently replacing history;
- coverage ledger exposes exactly the required semantics:
  `EXPECTED / ATTEMPTED / OBSERVED / VALID / CONFLICT / MISSING / UNKNOWN`;
- `MISSING != ZERO` and `UNKNOWN != MISSING`;
- time provenance does not pretend local clock time is external publication truth;
- UseLedger/admissibility integration is complete;
- manual runner uses the exact same callable path intended for Clock;
- at least one real live capture has been attempted and truthfully recorded;
- complete local suite green;
- after integration, run the repository's integration CI/test suite on the exact merged head.

Current useful contract already present at drafting time:

`due(task, request, now) -> bool`

`execute_forward_capture(request, recorder, journal, task_store, adapter, timebase, attempt_id=None) -> ForwardCaptureResult`

Do not code the Clock patch against fields not yet committed in the final Forward head.

### 4.2 Economic V2 acceptance

Required before landing Economic V2:

- final committed handoff exists;
- explicit capital/order eligibility remains distinct from a raw mechanical `CONTINUE`;
- `RECIPE_PROVISIONAL` cannot silently become portfolio/order authority;
- research/execution consistency must be verified for top eligibility;
- unresolved required clustering provenance cannot be treated as resolved;
- no arbitrary rewrite of scientific constants merely to make economics look favorable;
- declared cost shape is mechanically checked against the functional behavior;
- all required journal/provenance/idempotence work defined by the mission is complete;
- same-id / different-input-fingerprint conflict fails closed if the assessment journal supports persistent reuse;
- complete local suite green;
- after integration, run the repository's integration CI/test suite on the exact merged head.

Important:

**Receiving Economic V2 is not sufficient for system acceptance.**

A library that Desk can bypass is not an economic control.

### 4.3 P0 acceptance for final rodage

Separate from product integration.

Required before Blue considers P0 ready for final target-runtime rodage:

- exact-head CI successful;
- Astra says `READY_FOR_FINAL_RODAGE = TRUE`;
- no open blocker affecting capture integrity, PIT reconstructability or visibility firewall;
- qualifying runtime deployed from exact pinned immutable code content;
- materialized fingerprint equals runtime fingerprint;
- effective systemd definition matches the expected acquisition-critical contract;
- lifecycle evidence is exact and attributable;
- stop/start, failure and supervisor/child semantics are proven sufficiently for the target runtime;
- no `t0` declared merely because code/tests are green.

---

## 5. P0 immutable/pinned deployment plan

The current P0 service intentionally expects:

- `WorkingDirectory=/opt/quant`
- supervisor at `/opt/quant/deploy/quant_sec_supervisor.py`
- `--root /opt/quant`
- qualifying fingerprint derived from the deployed tree.

Blue should avoid changing this topology merely to gain aesthetic release paths before `t0`.

### 5.1 Recommended pre-t0 deployment shape

Keep `/opt/quant` as the qualifying path, but make the mounted content an exact immutable release.

Suggested operator layout:

`/opt/quant-releases/<git-sha>/` — immutable release source

`/opt/quant` — mount/bind view of the selected release

`/var/lib/quant-p0/` — persistent writable operational state

`/opt/quant/var` — writable bind mount backed by `/var/lib/quant-p0/`

Properties:

- code/data/repository content visible through `/opt/quant` is read-only;
- only `/opt/quant/var` is writable;
- development branches/build trees live elsewhere;
- changing GitHub branches does nothing to the qualifying runtime;
- a future intentional P0 release replacement is an explicit deployment event and therefore can be bound to the deployment authority/fingerprint process;
- the same SEC state survives process restart and release mount preparation as intended.

### 5.2 Release record

Before target-runtime rodage, persist an operator-facing release record containing at minimum:

- repository;
- commit SHA;
- Git tree SHA;
- acquisition fingerprint;
- service unit digest/effective-unit digest;
- Python version;
- OpenSSL version;
- host boot identity where relevant to existing P0 evidence;
- deployment authorization identity/time where relevant;
- exact release directory;
- exact persistent state root;
- CI run proving the code head;
- audit result after service start.

### 5.3 Freeze rule

During a qualifying continuity window:

- no mutation of the code mounted at `/opt/quant`;
- no service-unit semantic change;
- no Python/OpenSSL runtime replacement without treating it as a new qualifying deployment;
- no Economic/Forward/Product integration deployment into `/opt/quant`;
- GitHub development may continue freely elsewhere.

Repository motion is not continuity reset by itself.
Deployed acquisition-critical motion is.

---

## 6. End-to-end integration test contract

These tests should be implemented only after the final Claude contracts are stable.

### E2E-01 — Forward due scheduling

Given a due Forward task:

- one Clock tick selects Forward capture;
- exactly one capture attempt is journaled;
- accepted observations are recorded;
- task state advances;
- no research/desk work steals priority from a genuinely due irrecoverable capture.

### E2E-02 — Forward not-due fairness

Given Forward capture not due:

- Clock does not poll it;
- research/desk/learning work remains eligible;
- no busy-loop or phantom blocked queue entry is created.

### E2E-03 — Forward restart/idempotence

Crash/restart after a completed or partially completed capture cycle:

- accepted observation is not duplicated;
- attempt history remains reconstructable;
- task bookkeeping can recover without changing immutable observation truth;
- next due calculation remains correct.

### E2E-04 — Conflict and missing semantics

Inject:

- a conflicting value for an already accepted key;
- a genuinely missing expected cell;
- an unknown/non-expected cell.

Assert:

- conflict is visible and not silently downgraded to VALID;
- missing is not converted to zero;
- unknown is not treated as missing;
- inadmissible cells cannot become research evidence.

### E2E-05 — Admissible Forward → Research boundary

A VALID forward observation with valid provenance becomes eligible for the intended research/data-consumer path.

A CONFLICT/MISSING/UNKNOWN observation does not.

The test must prove the actual consumer path, not merely call the coverage classifier in isolation.

### E2E-06 — Economic fail-closed before exposure

Build a research opportunity that would otherwise create target weights but whose economic assessment is:

- `DEVELOPMENT_SIGNAL_ONLY`, or
- `NOT_ELIGIBLE`.

Assert:

- no capital order is produced;
- no fill is created;
- persistent Book does not change;
- ticket/journal records the exact economic reason.

### E2E-07 — Positive eligible shadow path

Use a fully eligible paper/shadow candidate.

Assert:

`SCAN → VET → ECONOMIC ELIGIBILITY → SIZE → RISK → FILLS → BOOK`

with one traceable identity chain.

The positive test must not weaken real-capital boundaries.

### E2E-08 — Economic size consistency

Create a case where economic capacity is lower than the raw Desk entitlement.

Assert final requested exposure never exceeds the economically permitted size.

Then create a portfolio-risk scaling case and assert final booked exposure does not exceed either economic capacity or Risk approval.

### E2E-09 — Crash between durable intent and Book

Crash after execution intent/fills become durable but before all Book effects are committed.

After restart:

- same intent resumes;
- same operation ids are replay-safe;
- no duplicate economic action;
- no fresh bankroll;
- final Book is equivalent to one successful application.

### E2E-10 — Realized economics traceability

For a filled shadow action:

- realized commission/shortfall/fill information points back to the assessment and opportunity that authorized it;
- the system can compare assumed versus realized implementation loss later;
- this linkage survives restart.

### E2E-11 — Learning is causal, not archival

After a negative realized/shadow result or repeated rejection:

- durable learning state is written;
- at least one future research prioritization/search decision demonstrably changes because of that state.

Merely writing a lesson string is insufficient.

### E2E-12 — P0 isolation regression

While the product integration tree advances:

- the mounted qualifying P0 code tree remains byte-identical;
- P0 fingerprint remains unchanged;
- product branch HEAD motion cannot mutate `/opt/quant`;
- no product test/deploy writes into P0 persistent state.

---

## 7. Forward → Clock contract before implementation

The patch must be intentionally small.

### 7.1 Ownership

Clock owns **when** Forward capture runs.

Forward Data owns **how one capture attempt executes**.

Do not insert Forward capture into the existing `PersistentQueue` unless that queue is explicitly generalized later. Today it dispatches research work, and a fake research task would be misleading.

### 7.2 Minimum Clock additions after the Forward contract freezes

Expected shape only; exact names follow the final Forward API.

1. Construct one Forward request/configuration from committed system configuration.
2. Construct persistent recorder / attempt journal / task store under the existing Quant root.
3. Adapt the existing Clock `Timer` to Forward's injectable timebase rather than creating another clock.
4. Add a private `_run_due_forward_capture()` method.
5. In `tick()`, call it in an explicit priority location.

Priority recommendation:

1. due P0 acquisition work;
2. due Forward acquisition work;
3. Research queue;
4. Desk session;
5. Learning;
6. idle.

Rationale:

- both acquisition lanes can lose irrecoverable observations;
- P0 currently has stronger frozen qualification constraints and remains first;
- replayable research/desk work may wait.

If final Forward semantics show a different urgency model, re-evaluate with evidence rather than copying this order blindly.

### 7.3 Clock behavior requirements

- one call performs at most one bounded Forward capture cycle;
- no internal Forward loop/sleep/thread;
- failure returns a truthfully journaled result and does not look like successful idle;
- repeated source failures do not starve the entire system forever;
- task state and attempt state survive restart;
- component/status projection must not claim DATA healthy when Forward is durably blocked/stale/conflicted;
- status surfaces must derive from actual persisted state.

---

## 8. Economic → Desk integration contract before implementation

The intended enforcement point is before SIZE can turn raw strategy desire into exposure.

Minimum rule:

A candidate may continue toward capital sizing only when the exact economic assessment for the exact candidate/input fingerprint says:

`capital_order_eligibility == PORTFOLIO_CONSIDERATION_ELIGIBLE`

The raw `verdict == CONTINUE` is insufficient.

Required traceability:

`opportunity_id ↔ research evidence identity ↔ economic assessment identity/fingerprint ↔ size/risk decision ↔ fills ↔ Book operations`

Fail closed on:

- missing assessment;
- stale assessment;
- same assessment id with different input fingerprint;
- unresolved mandatory provenance;
- failed research/execution consistency;
- provisional recipe where final portfolio authority is not allowed;
- Book application not traceable to the authorized opportunity.

Do not let Economic V2 replace portfolio Risk. Economics and Risk answer different questions and both remain required.

---

## 9. Divergence monitoring rules

Blue should inspect current remote HEADs before every integration action.

### Alert if Economic touches

- `src/quant/desk/**`
- `src/quant/clock.py`
- `src/quant/state.py`
- `src/quant/paths.py`
- Forward files
- SEC/P0 files

unless the mission explicitly announces that integration scope changed.

### Alert if Forward touches

- `src/quant/clock.py`
- `src/quant/desk/**`
- `src/quant/economics/**`
- SEC/P0 files
- a new scheduler/service loop

unless explicitly coordinated.

### P0 special rule

Any P0 changes to shared files such as `clock.py` or `state.py` are **not** automatically merged into product integration.

They must be reviewed semantically and selectively ported later if product runtime needs them.

### Before accepting a branch

Record:

- exact HEAD;
- compare against its declared base;
- changed-file list;
- final handoff SHA/content;
- full test result claimed;
- exact-head CI status when available;
- unresolved blockers/non-authorities;
- whether any file ownership boundary was crossed.

---

## 10. Blue trigger conditions

### Trigger Astra Mission #1

When the current P0 exact-head CI finishes and after reading the result.

Purpose: final P0 architecture/proof closure and immutable deployment decision.

### Trigger Economic integration work

When Economic V2 publishes a final handoff and stops moving.

### Trigger Forward → Clock implementation

When Forward publishes a final handoff and its manual runner / UseLedger / admissibility contract is committed.

### Trigger Astra Mission #2

After the actual Desk path consumes economic eligibility and bypass tests exist.

### Trigger Astra Mission #3

Only after:

- Forward → Clock is connected;
- Forward admissibility reaches a real research consumer;
- Economic → Desk/Risk/Book is connected;
- E2E closure tests are green on one integration head.

---

## 11. Explicit non-goals now

Do not, merely to create parallel work:

- invent a third scheduler;
- redesign the Research Factory;
- rewrite P0 import closure before evidence shows it is worth the risk;
- merge P0 wholesale into Wave 1;
- invent D07/D08/D19 scientific authority;
- manufacture positive research results;
- authorize real capital;
- optimize UI before the state path exists;
- code Forward → Clock against an API still changing.

---

## 12. Current Blue conclusion

The highest-value parallel work is coordination, not another subsystem.

The shortest coherent path from the current state is:

`P0 isolated and pinned`

in parallel with

`Forward final → Forward received → Forward→Clock`

and

`Economic V2 final → Economic received → Economic→Desk/Risk/Book`

then

`E2E closure → Astra adversarial integration audit`.

The acceptance criterion for the integrated system remains:

**new admissible observation → persistent economic decision → realized/shadow result → durable feedback that changes future search.**
