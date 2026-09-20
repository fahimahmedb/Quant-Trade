# BLUE → WORK HANDOFF — 2026-09-20

## Purpose

This file transfers Blue's current long-horizon work into a fresh ChatGPT Work conversation without depending on chat memory.

Repository evidence is authoritative. Read the exact branches and files below before making recommendations or changes.

## Mandatory first reads

1. `QUANT_NORTH_STAR.md`
2. `governance/BLUE_LONG_HORIZON_EXECUTION_PROTOCOL_2026-09-20.md`
3. `governance/BLUE_P14D_CHALLENGE_2026-09-20.md`
4. `governance/BLUE_P0_COMPRESSED_QUALIFICATION_PROTOCOL_2026-09-20.md`
5. `handoff/ASTRA_P0_CHECKPOINT.md` on `astra/p0-deep-adversarial-pre-t0`
6. `governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md` on the Astra branch
7. `handoff/BLUE_INTEGRATION_READINESS_2026-09-20.md` on `blue/integration-readiness-2026-09-20`

## North Star constraint

Quant is a persistent autonomous quantitative system, not a search engine/backtester/strategy collection.

Target topology:
HUMAN/CONTROL → ROOT/CLOCK → DATA/RESEARCH/BUILD → OPPORTUNITIES → SCAN→VET→SIZE→RISK→FILLS→BOOK → REAL/SHADOW FEEDBACK → LEARNING/MEMORY → SEARCH.

Terminal objective: long-run net wealth growth after real frictions. Risk, drawdown, Sharpe, activity and architecture elegance are instrumental.

Before important recommendations, check coherence with `QUANT_NORTH_STAR.md`.

## Long-horizon execution method

Use the six-pass protocol already persisted by Blue:

1. Planner
2. Investigator
3. Builder
4. Red Team
5. Verifier
6. Integrator

Do not pretend these are independent agents unless actual separate agents/tools are used.
Persist important conclusions in GitHub.
Prefer hypothesis → discriminating test → reproduce/falsify → minimal fix → exact-head verification → checkpoint.

## Current branches / verified heads at handoff creation

### Astra / P0 repository closure
Branch:
`astra/p0-deep-adversarial-pre-t0`

HEAD:
`643deacdf5bbbdb1d2410c762eb20f72aff16bbf`

Exact-head CI:
GitHub Actions run `35478796506` = **COMPLETED / SUCCESS**

Prior tested code candidate:
`88566cb4fb08bdf01561ffcbfe18fd391e57c572`

Candidate exact-head CI:
`35478291920` = **COMPLETED / SUCCESS**

Astra final repository-side conclusion:
- no known open repository defect in capture integrity / PIT reconstructability / anti-selection-firewall classes;
- one real raw directory durability defect was found and fixed;
- repository Phase 7 should stop;
- remaining work is target-runtime-specific.

Current status:
`READY_FOR_FINAL_RODAGE = FALSE`

Reason: target-host evidence is absent, not because Astra wants more abstract repository work.

Still:
`t0 = NOT DECLARED`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

### Blue long-horizon research
Branch:
`blue/long-horizon-research-2026-09-20`

Known commits:
- `7d81dd3a2ae0ed7b35bdf8cd2a00758f7b940e38` — long-horizon execution protocol
- `3155fc2f7525678f80d7fd57f5b234f9045fb337` — initial evidence-based P14D challenge
- `023dd3aa53c03479bd6ba0500cb13e2314da2f78` — red-team P14D against calendar / SEC source closure
- `28a7bacaf97813ed54410942784592c2fc0d6cd1` — compressed P0 qualification protocol

At handoff creation, CI for `28a7bac...` had already passed:
- setup
- schema drift
- status freshness
- full unit suite
- SEC P0 lane
- V1 E2E

and was generating the exact-head verification artifact. Refresh before relying on final conclusion.

### Blue P0 continuity qualification research
Branch:
`blue/p0-continuity-qualification-2026-09-20`

Current HEAD at handoff creation:
`a9dd68457397e7c392c3866ccefdef2b9bd22910`

Parent research commit:
`8350dd214943a547af23294b8801cff98037896d`

Purpose:
test whether the old fixed P14D rule is carrying real unique evidence, or whether most of it can be replaced by stronger accelerated/fault-injected evidence plus a shorter event-based live source window.

Important: this branch is **research/qualification evidence**, not the authoritative P0 runtime branch.

`8350dd214...` added two calendar-compression tests:
- Friday → weekend → Monday reconciliation boundary;
- virtual 14-day horizon reduces to settled business-day reconciliation states.

It updated STATE inventory from 380 → 382 tests atomically.

`a9dd684...` adds two stronger tests and updates inventory 382 → 384:
1. `test_settle_delay_is_measured_after_edgar_close_not_utc_date_start`
2. `test_bootstrap_day_is_the_edgar_eastern_business_date`

These are designed to test a potentially real source-calendar bug:
current production `reconciliation_due()` derives candidate days from UTC dates and uses `now - 30h`; the new tests assert that the 30-hour settle delay should be measured from EDGAR's actual 22:00 ET business-day close, and that a 01:00 UTC bootstrap can still belong to the previous EDGAR business day.

At handoff creation, exact-head run:
`35479512122` on `a9dd684...` = **IN_PROGRESS**, at status-artifact freshness.

Do not assume these new tests pass.
If they fail for the intended discriminant, treat that as a potentially genuine P0 calendar semantics defect and investigate carefully.
If they fail because the test target/assumption is wrong, fix the test rather than manufacturing a blocker.

### Economic V2
Branch:
`parallel/claude-economic-v2-2026-09-20`

HEAD:
`3b50cd7356945c770192454a96fa05cb4f0fa2e3`

State:
- 4 commits ahead of Wave 1;
- still isolated to economics + tests;
- no Clock / Desk / Forward / P0 ownership crossing;
- full local suite reported 618 passed;
- final handoff `handoff/CLAUDE_ECONOMIC_V2_2026-09-20.md` was still absent at last check;
- no exact-head GitHub Actions run;
- Desk still does not consume `quant.economics`.

Do not integrate yet.
Astra #2 is still premature.

### Forward Data
Branch:
`parallel/claude-forward-data-2026-09-20`

HEAD:
`c2d71c4c7b71480a75ec82df8e80982be3cece26`

State:
- 5 commits ahead of Wave 1;
- UseLedger/admissibility integration done;
- full local suite reported 648 passed;
- still no Clock / Desk / P0 / Economics boundary crossing;
- manual runner `scripts/forward_capture_runner.py` absent at last check;
- final handoff `handoff/CLAUDE_FORWARD_DATA_2026-09-20.md` absent;
- next declared work: manual runner, real live capture, final deliverable.

Do not wire Forward→Clock yet.

## P14D challenge — current technical finding

The fixed rule currently lives in Blue/P0 governance:

`P0_CONTINUOUS_OBSERVATION_MIN = P14D`

plus one complete weekend and one prospectively declared source-normal silence interval.

The 14-day number is **not** in `QUANT_NORTH_STAR.md`.

The P0 governance uses the window to support:
1. unattended continuity;
2. restart durability;
3. discovery fail-closed.

Repository inspection found no internal SEC timing horizon remotely close to 14 days.
Important production horizons found:
- discovery poll: 60 s;
- idle connection recycle: 20 s;
- connect timeout: 10 s;
- read timeout: 20 s;
- total request deadline: 60 s;
- backoff ladder: 5 / 15 / 60 / 300 / 900 s;
- 429 cooldown: 300 s;
- 403 cooldown: 3600 s;
- daily-index settle: 30 h;
- restart delay: 15 s;
- restart burst window: 600 s;
- stop timeout: 30 s;
- deployment authority max age: 3600 s.

The only meaningful multi-day/calendar branch found is daily-index reconciliation:
`collector.py` uses `DAILY_INDEX_SETTLE_HOURS = 30` and skips weekend days.

Prior-art conclusion:
mature systems use deterministic simulation and fault injection to deliberately exercise failure boundaries, then retain real-host/live testing for properties simulation cannot honestly prove.

Blue's current technical recommendation (not yet governance authority):
replace fixed P14D with a hybrid qualification contract:
- Gate A: accelerated time + deliberate fault/crash coverage;
- Gate B: actual target-host mounts/filesystem/systemd/reboot/fingerprint tests;
- Gate C: prospective live event-based window across real EDGAR source closures and a complete weekend;
- Gate D: one retrospective exact-runtime proof artifact.

Current frozen P14D rule remains authoritative until an explicit amendment supersedes it.

## SEC source-calendar fact to re-check before any live gate

Current Blue research used SEC guidance that EDGAR filing acceptance is generally 06:00–22:00 Eastern Time Monday–Friday except federal holidays, with daily-index updates beginning around 22:00 ET.

Do not treat this as permanently frozen. Re-check authoritative SEC documentation immediately before live qualification.

## Immediate task queue for Work

### T1 — Refresh all moving CI/head state
Refresh:
- Astra head + run;
- Blue long-horizon CI;
- Blue continuity-qualification head/run;
- Economic/Forward heads/final handoffs.

### T2 — Resolve `a9dd684...` honestly
Inspect run `35479512122`.

If new calendar tests fail:
- establish whether production's UTC-date + 30h logic is semantically wrong relative to EDGAR business-day close;
- do not patch before discriminating the intended source semantics;
- if genuine, make the smallest P0 correction on the Blue qualification branch first, with red→green evidence;
- then decide with Blue whether it belongs in authoritative P0 before target deployment.

If tests pass unexpectedly:
- inspect why; verify they actually hit the intended boundary.

### T3 — Complete Gate A only where evidence is missing
Do not add redundant tests for already-covered:
- 429/403;
- backoff ladder;
- cooldown restart persistence;
- hidden retry;
- socket deadline;
- SIGTERM/SIGKILL;
- raw directory fsync;
- fingerprint mismatch;
- visibility proxy.

Focus only on real uncovered boundary semantics.

### T4 — Do not amend P14D yet
First finish Red Team on the compressed protocol.
Only commit a governance amendment if there is no unique P14D-only property left uncovered.

### T5 — Target-host preparation
Astra says repository expansion should stop after real repository defects close.
Target runtime needs:
- exact immutable release;
- fixed `/opt/quant` view;
- persistent `/var/lib/quant-p0`;
- mount-before-service fail closed;
- actual filesystem semantics;
- actual systemd loaded values/drop-ins;
- target interpreter/OpenSSL/config;
- private SEC identity;
- active == materialized fingerprint;
- one-use deployment authority;
- actual stop/start/kill/reboot pre-t0 checks;
- live rodage.

If Work does not have target-host access, do not fake those results. Produce the exact command/runbook/evidence schema instead.

### T6 — Continue Product integration only on trigger
Forward final + runner + real capture must arrive before Forward→Clock.
Economic final must arrive before reception; actual runtime guarantee requires later Desk enforcement.
Keep P0 qualifying runtime isolated from Product integration.

## Integration topology remains

Product line base:
`parallel/claude-wave1-economic-system-2026-09-19`

Intended order:
1. Forward final leaf reception
2. Economic V2 final leaf reception
3. Blue Forward→Clock
4. Blue Economic→Desk/Risk/Book
5. whole-system E2E
6. Astra #2 after actual economics enforcement
7. Astra #3 after coherent integrated head

Never wholesale-merge Astra P0 into Product integration.

## Blue E2E acceptance matrix still required later

- Forward due scheduling
- Forward not-due fairness
- restart/idempotence
- conflict/missing/unknown semantics
- admissible Forward→Research
- economic fail-closed before exposure
- positive eligible shadow path
- economic size consistency
- crash durable intent→Book
- realized economics traceability
- causal learning
- P0 isolation regression

## Hard non-claims

Do not claim:
- t0 declared;
- 14-day continuity proven;
- P0 target-runtime ready;
- Forward final;
- Forward live capture proven;
- Economic final;
- economics enforced by Desk;
- real capital authorized

unless freshly proven by repository/target evidence.

`REAL_CAPITAL_AUTHORIZED = FALSE`

## Work behavior requested by the user

The user wants long-project execution, task by task, with maximum care and no flattering falsehoods.
They explicitly prefer doing all available safe work rather than stopping early.
Do not ask unnecessary clarifying questions.
Keep periodic progress updates.
Do not claim asynchronous/background work.
Use GitHub as durable memory because project memory is disabled.

## First response in the new Work conversation

Do not re-explain the whole project to the user.
Read this handoff and the mandatory files, refresh the live repo state, then report:
- what moved since this handoff;
- whether the new calendar tests passed/failed and why;
- the next concrete task you are executing.
