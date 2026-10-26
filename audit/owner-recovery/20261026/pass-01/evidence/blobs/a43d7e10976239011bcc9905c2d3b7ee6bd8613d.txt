# B4 `MACRO-TSMOM-001` — pre-execution record (Builder, 2026-10-08)

Status: `HARNESS_FROZEN_NOT_EXECUTED` at the time of writing. This file does not change the pre-registration or the harness.

## Frozen objects
- Pre-registration: `PREREGISTRATION_2026-10-08.md`, SHA-256 `11f77332f9551028dc6b19f91a1fc939513511f0e1c2188d6fdffef83d9c7c5d` (verbatim from PR #22 comment `6057499890`).
- Erratum 1: `ERRATUM_1_2026-10-08.md`, SHA-256 `e561a9c684d041b0bb0f66fed914e865726e6fe42dc1d7e4220ab953e074637b`. Its own status line still reads `PROPOSED_BY_BUILDER_PENDING_ORCHESTRATOR_ACCEPTANCE` because the file is the verbatim proposal; it was ACCEPTED without amendment (E1, E2, E3) by the orchestrator in PR #22 comment `6057563728`.
- Harness: `run_b4.py` at commit `20d7568ef4ee9935922b89d9055d9ac3677e981c`, blob `644bdefb26ddbe4827c1b2563ba8865f58f760ba`, SHA-256 `30ede2a379d0f72c2349df37ec96854d8fdd129f523777b3589c8c3631a30706`; 40 synthetic-data tests green, also on a clean detached worktree.

## Review trail (before any observation)
- Orchestrator automated code reviews of `7657a0f`, `bfb81f2`/`451cc59`, `7ed3c7f`: six real defects found and fixed (raw-line filter before the CSV parser, dataset-metadata gate, registry-vs-STATE.md conflict, tie rule measured from the maximum, invalidation of the persisted result after a late filesystem change). All fixed before execution.
- Orchestrator review capacity ended at 2026-10-08T10:24Z (`usage limits for code reviews`, comments `6057811519`, `6058258054`); mentions after that returned only the same notice. No manual orchestrator reading of `20d7568e` exists.
- Substitute: one independent fresh-context reviewer (no repository history, forbidden from touching real data) read the harness against the pre-registration and erratum: no BLOCKING defect. Non-blocking observations, accepted as pre-resolved conventions and to be disclosed in the reading of the result:
  1. For L = 252 the first common-intersection row is charged entry turnover from zero, while L = 21/63/126 carry position continuity from earlier rows (L = 252 cannot have an earlier position). Effect: at most 5 bp on one row; disadvantages L = 252 marginally in selection.
  2. Calendar year for criterion 6 = year of the exit date (the pre-registration is silent).
  3. Only `InvalidInput` is caught: an unexpected exception aborts without writing a result (no outcome risk).
  4. Pre-registration/erratum hashes are reported but not verified at run time (both match today).

## Decision
No blocking objection exists and the orchestrator cannot respond (usage limit). Per the rule announced in PR #22 comment `6058253274`, after 2026-10-08T11:01Z the harness is executed once from a clean detached worktree at `20d7568e`, unchanged, and the result is published verbatim. `CHALLENGE_STATUS[H7] = NON_REPONDU` (accepted risk: an undetected defect, bounded by 40 tests, six fixed defects and one independent read).

```text
DISCOVERY_CLAIM = FALSE
INDEPENDENT_VALIDATION_CLAIM = FALSE
SHADOW_BAR_ANALYSED = FALSE
TRADABLE_STRATEGY = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
```
