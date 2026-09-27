# BLUE LONG-HORIZON CHECKPOINT — 2026-09-20

## Purpose

Durable checkpoint for the ongoing Blue P0/P14D qualification work.

From this point onward:
- every meaningful technical step is committed to its working branch;
- every phase transition gets a checkpoint on the Blue long-horizon branch;
- chat memory is never treated as authority.

## Global status

`t0 = NOT DECLARED`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

`READY_FOR_FINAL_RODAGE = FALSE` at the authoritative Astra checkpoint because target-host evidence is still absent.

`REAL_CAPITAL_AUTHORIZED = FALSE`

## Astra repository baseline

Branch:
`astra/p0-deep-adversarial-pre-t0`

HEAD:
`643deacdf5bbbdb1d2410c762eb20f72aff16bbf`

Exact-head CI:
`35478796506 = SUCCESS`

Prior code candidate:
`88566cb4fb08bdf01561ffcbfe18fd391e57c572`

Candidate CI:
`35478291920 = SUCCESS`

Astra's repository-side Phase-7 work is closed. Remaining authoritative rodage blockers are target-runtime-specific.

## New Blue work since Astra closure

### CAL-001 — EDGAR settlement anchored to wrong calendar

Red branch evidence:
`a9dd68457397e7c392c3866ccefdef2b9bd22910`

CI:
`35479512122 = FAILURE`

Exactly two intended tests failed:
- EDGAR bootstrap source date must be America/New_York, not UTC;
- 30-hour daily-index settlement must start from 22:00 ET close, not UTC date truncation.

Minimal fix:
`5b5489edef620080df3410d93e9b213c7e6c66bf`

Final coherent corrected branch:
`blue/p0-continuity-qualification-2026-09-20`

HEAD:
`3dfc54a4219f1b31374ff4a007f1d9a2dfc0ec4c`

Exact-head CI:
`35479897689 = SUCCESS`

CAL-001 status:
`CLOSED_GREEN_ON_BLUE_QUALIFICATION_BRANCH`

### CAL-002 — federal holiday pins reconciliation

Red branch:
`blue/p0-calendar-holiday-red-2026-09-20`

Isolated red:
`88a871a337ab07e98a50ca1f72dfaf65c4f40abf`

CI:
`35479910327 = FAILURE`

Exactly one intended failure:
Labor Day 2026-09-07 was incorrectly treated as a normal daily-index reconciliation target.

Root issue:
the collector skips weekends but has no prospectively bound official SEC holiday calendar. A missing holiday daily index can therefore remain the oldest unresolved day and prevent later reconciliation progress.

Candidate fix:
`c1ff38596a6679d4d7e1fc3437c4e0dd22c7e2fd`

Design:
- explicit SEC EDGAR 2026 closure calendar;
- separate calendar module;
- included in acquisition-critical fingerprint;
- no inference from HTTP 404;
- future unbound calendar year fails closed.

Exact-head CI:
`35480609349 = IN_PROGRESS` at this checkpoint.

CAL-002 status:
`FIX_UNDER_CI`

### DST proof

Branch:
`blue/p0-calendar-dst-proof-2026-09-20`

HEAD:
`99a64981b7f3c5e8755782d68d52cb7c7408e764`

Purpose:
prove 30 elapsed hours remain exactly 30 elapsed hours across both spring-forward and fall-back DST boundaries.

CI:
`35480655370 = IN_PROGRESS`

Status:
`PROOF_UNDER_CI`

### Long-history audit stress

Branch:
`blue/p0-gate-a-long-history-2026-09-20`

HEAD:
`1f87bfe89deac056ae4bf3c2923009804fc63c05`

Purpose:
exercise the real audit/parser over 2,016 named obligations spanning 14 virtual days, preserving one-obligation-to-one-resolution.

CI:
`35480709558 = IN_PROGRESS`

Status:
`PROOF_UNDER_CI`

### Consolidated Gate A head

Branch:
`blue/p0-gate-a-consolidated-2026-09-20`

HEAD:
`419a0606108f0cc70a1341233eb4db459c20a40d`

Contains:
- EDGAR business-time fix;
- holiday calendar fix;
- DST tests;
- long-history stress;
- cumulative test inventory 390.

CI:
`35480731363 = IN_PROGRESS`

This is the most important current Blue validation head.

Do not promote any P0 code until this exact-head CI and the underlying holiday fix are green.

## P14D challenge

Current frozen authority still says:
`P0_CONTINUOUS_OBSERVATION_MIN = P14D`

No amendment has been made.

Blue has documented a candidate replacement:
1. Gate A — deterministic/fault-compressed repository proof;
2. Gate B — destructive target-host entrance checks before t0;
3. explicit prospective t0 declaration;
4. Gate C — live source event window beginning at that t0;
5. Gate D — retrospective closure audit.

Important governance correction already committed:
t0 must be declared **before** the qualifying live interval, never chosen retrospectively.

Relevant Blue documents:
- `governance/BLUE_P14D_CHALLENGE_2026-09-20.md`
- `governance/BLUE_P0_COMPRESSED_QUALIFICATION_PROTOCOL_2026-09-20.md`
- `governance/BLUE_P0_TARGET_HOST_RUNBOOK_2026-09-20.md`
- `governance/BLUE_P0_GATE_A_EVIDENCE_MATRIX_2026-09-20.md`
- `governance/BLUE_P0_CALENDAR_ADVERSARIAL_FINDINGS_2026-09-20.md`

Do not amend P14D until Gate A is one-head green and final Red Team finds no unique fixed-14-day property.

## Product lanes

Economic V2:
`parallel/claude-economic-v2-2026-09-20`
HEAD `3b50cd7356945c770192454a96fa05cb4f0fa2e3`
No final handoff; no Desk enforcement; no Actions.
Do not integrate yet.

Forward:
`parallel/claude-forward-data-2026-09-20`
HEAD `c2d71c4c7b71480a75ec82df8e80982be3cece26`
No final handoff; no manual runner/live capture; no Actions.
Do not wire Forward→Clock yet.

## Immediate next actions

1. Refresh `35480609349`, `35480655370`, `35480709558`, and especially consolidated run `35480731363`.
2. If consolidated head fails, inspect only the exact failing discriminants and fix the smallest cause.
3. If consolidated head succeeds, update the Gate A evidence matrix from OPEN/PENDING to exact green facts.
4. Perform one final Red Team pass over calendar authority, source closure, audit scaling, DST, and business-day failure semantics.
5. Only then decide whether to draft an explicit superseding P14D governance amendment.
6. Target-host Gate B remains unclaimable until the real host is available.
7. Product integration remains blocked on Forward/Economic final triggers.

## Working discipline from now on

Every meaningful step:
- commit code/test/docs on the relevant branch;
- do not pile uncommitted conceptual state in chat;
- update this checkpoint at phase boundaries;
- include exact branch, SHA and CI run whenever a claim depends on them.

This checkpoint is intentionally conservative: in-progress CI is not counted as proof.
