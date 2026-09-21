# BLUE — AUXILIARY AI BUILD / REVIEW POLICY — 2026-09-21

## 0. Purpose

This policy governs use of auxiliary AI engineering agents such as Google Antigravity CLI inside Quant's Build Plane.

Architectural authority remains `QUANT_NORTH_STAR.md`.

Auxiliary AI agents may accelerate bounded engineering and adversarial analysis, but they are not governance authorities.

## 1. Authority hierarchy

The following ordering is mandatory:

1. Quant North Star;
2. Blue governance / exact mission contract;
3. exact audited repository object and exact-head CI;
4. Builder implementation evidence;
5. independent Astra review where required;
6. auxiliary AI findings.

An auxiliary agent may discover a defect that blocks progression.
It may not promote a candidate, waive a blocker, authorize Gate B, declare Gate B PASS, or declare t0.

## 2. Allowed Antigravity roles

Antigravity may be used as:

- bounded Builder on a Blue-dispatched implementation branch;
- read-only adversarial reviewer;
- test/fuzz author on its own bounded Builder branch;
- CI/log analyzer;
- independent attack-generator before formal Astra review;
- documentation / handoff assistant when explicitly scoped.

For the current Gate-B run-authority repair, Antigravity is authorized only as an auxiliary read-only adversarial precheck.

## 3. Forbidden actions without separate Blue authority

Antigravity must not:

- write directly to `blue/master-v2-2026-09-20`;
- modify the audited integration candidate;
- modify Builder R1/R2 branches;
- modify Astra branches;
- touch frozen V4 `src/`;
- touch the target host;
- mutate systemd, mounts, firewall, P0 state, evidence roots, or network;
- merge/cherry-pick into an authoritative branch;
- reinterpret green CI as independent correctness;
- declare `PASS_REPOSITORY_EVIDENCE`;
- authorize Gate B;
- declare t0.

## 4. Current auxiliary lane

Authorized auxiliary branch:

`parallel/antigravity-gate-b-run-authority-adversarial-precheck-2026-09-21`

Audited integration candidate:

`blue/gate-b-run-authority-repair-integration-2026-09-21@644da76eb0227be275b8e3448118dac0cc7096ca`

Integration exact-head CI:

`35598077120`

Activation rule:

- the auxiliary lane may begin static/read-only analysis immediately;
- before issuing its final report it must verify the integration branch still resolves exactly to `644da76eb0227be275b8e3448118dac0cc7096ca`;
- it must verify CI `35598077120 = COMPLETED / SUCCESS`;
- if either condition is false, the report is `STALE_CANDIDATE / STOP` and must not be used for governance.

## 5. Scope of current Antigravity precheck

Antigravity should independently attack the integrated R1/R2 repairs, including A1-A10 from:

`governance/BLUE_GATE_B_RUN_AUTHORITY_REPAIR_SPEC_2026-09-21.md`

It should especially search for NEW bypasses in:

- partial/crash write and fsync semantics;
- cross-process locking;
- activation time/freshness boundaries;
- evidence binding / ordinal typing;
- recovery and terminal-state ambiguity;
- receipt collision / failure-after-consume behavior;
- canonical JSON ambiguity;
- Git environment/config authority;
- replace refs / grafts / alternates;
- object-store indirection;
- linked worktrees;
- symlink/path traversal;
- allowed-extra-prefix abuse;
- pathname races / TOCTOU;
- index or Git metadata writes.

It may run repository tests, disposable-process tests, temporary Git repositories, and additional local fuzz/adversarial scripts.

It must not alter the audited candidate.

## 6. Output semantics

Required output:

`handoff/ANTIGRAVITY_GATE_B_RUN_AUTHORITY_ADVERSARIAL_PRECHECK_2026-09-21.md`

Every finding must use one of:

`REAL_DEFECT | TEST_DEFECT | MISSING_PROOF | TARGET_HOST_ONLY | NON_ISSUE`

Allowed final auxiliary statuses:

`ANTIGRAVITY_PRECHECK = ADVISORY_NO_NEW_REPOSITORY_DEFECT_FOUND`

or

`ANTIGRAVITY_PRECHECK = ADVISORY_BLOCKER_FOUND`

or

`ANTIGRAVITY_PRECHECK = STALE_CANDIDATE`

Antigravity may never emit `PASS_REPOSITORY_EVIDENCE`.

## 7. Governance consumption

Antigravity findings are advisory but actionable.

If it finds a plausible repository defect:
- Blue receives the report;
- Blue independently verifies the mechanism;
- Blue dispatches a bounded repair if warranted;
- the formal independent Astra recheck remains required.

If it finds no new defect:
- this does not replace Astra;
- Blue still requires the formal Astra recheck before any repository-evidence promotion.

## 8. Safety state

```text
AUXILIARY_AI_AUTHORITY = ADVISORY_ONLY
TARGET_HOST_TOUCHED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
```
