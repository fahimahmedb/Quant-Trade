# CP5 — R1 closed; R2 repair deployment required before cold reboot

Verified 2026-10-20 after Codex quota exhaustion and ChatGPT project-lead reacquisition.

## Fresh durable state

Working branch: `builder/oracle-economic-loop-recovery-20261019`.
Fresh branch HEAD before this checkpoint write: `a4913df277181be1e5d81dfdadd27970a12eecec`.

Oracle advanced autonomously after the first ChatGPT handoff. The current task
`FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003` is still `READY`, now at lease generation 2,
with both `legacy_duplicate_check` and `document_or_fundamental_research` persisted.
Its current execution `release_sha` remains
`f138c980c94eea313fd77532c20857da5c02d3fe`. All four authority flags remain false.

Automatic generation-2 commits observed before this checkpoint include:

- claim: `8945589e5b9fc9cb7de2550aa154a06431efd535`
- `document_or_fundamental_research`: `255b4e0e865620c8c26f2e6ace630221c3278279`

This is further evidence that the scheduler can continue durable work without Codex.
It is not a substitute for cold-reboot qualification.

## R1 — CLOSED PASS

Repair SHA: `f3943830e20b05d926d3013501573b8b21fdace7`.

Both relevant exact-SHA CI paths are complete and successful:

- Oracle Economic Loop Recovery CI run `39346723653`: SUCCESS. Its
  `cp1-static-and-regression` job completed successfully, including compilation,
  Oracle recovery unit tests, local-backend/fresh-Git/atomic-lease/crash-recovery tests,
  Research OS regressions, scheduler-absence assertion, and exact-head CI receipt.
- SEC P0 pre-t0 gate run `39346723807`: SUCCESS. Its `gate` job completed successfully,
  including fail-closed SEC identity check, schema drift, status freshness, full unit suite,
  SEC P0 lane suite, V1 end-to-end regression, exact-head verification artifact, and clean tree.

R1 exit criterion is satisfied.

## R2 — deployment decision

The repair MUST be installed before the real VM cold-reboot qualification.

Reason: the currently executing release `f138c980...` contains a target-host compatibility
defect in daily Git maintenance. A real automatic wake can publish its durable GitHub
transition and then fail during `git gc` because Ubuntu 24.04 Git 2.43 does not support
`git gc --no-detach`. The bounded repair at `f394383...` removes only that incompatible
option and retains synchronous explicit GC, the stable cache lock, two-week prune policy,
and once-daily maintenance marker.

Qualifying reboot resilience on the known-defective old release would not satisfy V1's
healthy-runtime claim. The correct sequence is therefore:

1. install exact release `f394383...` using the existing scheduler-free exact-SHA installer;
2. prepare the worker configuration while stopping the old timer before pointer change;
3. run the canonical live Oracle canary for the repaired release;
4. activate the timer only if that canary is `PASS_PRE_ACTIVATION` with all authorities false;
5. capture the pre-reboot state;
6. perform one genuine VM reboot;
7. prove services/model/timer recover and then wait for a natural scheduled wake.

The existing `deploy/oracle_v1_host_prepare.py` and
`deploy/oracle_scheduler_install.py` already enforce these release/config/canary boundaries.
No new deployment architecture is required.

## Safety invariants

Remain CLOSED:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

## Next gate

Owner/VM access is now the only material blocker. Use one bounded Owner intervention to
install/requalify/reactivate the repaired release, then perform the real reboot. Do not use a
manual worker wake as post-reboot evidence. After the VM returns, reacquire fresh GitHub HEAD
before interpreting the first natural timer transition.
