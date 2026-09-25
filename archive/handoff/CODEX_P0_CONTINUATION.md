# CODEX HANDOFF — ASTRA P0 DEEP ADVERSARIAL PRE-t0

You are taking ownership of the Quant/Astra pre-t0 P0 continuous-service mission because the prior conversational agent repeatedly loses execution context. Work from the repository only.

Repository: fahimahmedb/Quant-Trade
Single branch: astra/p0-deep-adversarial-pre-t0

DO NOT create another branch.
DO NOT merge PR #17.
DO NOT declare t0.
DO NOT claim the 14-day continuity window is proven.
DO NOT inherit uncommitted/local state.

Start by verifying the remote branch, then read:
1. handoff/ASTRA_P0_CHECKPOINT.md
2. handoff/ASTRA_PRE_T0_FINDINGS.md
3. QUANT_NORTH_STAR.md
4. governance/P0_RAW_CAPTURE_CRITICAL_PATH_RECLASSIFICATION_2026-09-18.md
5. governance/BLUE_P0_RAW_CAPTURE_CHECKPOINT_ADDENDUM_2026-09-18.md
6. governance/P0_ACQUISITION_CRITICAL_FINGERPRINT_V1.md
7. NEXT_BUILD_MISSION.md
8. handoff/BLUE_CHECKPOINT_2026-09-18_P0_CONTINUITY.md
9. full PR #17 conversation, especially all Blue reviews

Current durable branch head at this handoff:
5fc663ca1d68657dfd627d09c34ef69722e196a7

Phase-6 red-test code head:
d737eabee8f502e30852b3594972c5bcbbde2dbd

Baseline initial audit:
8d5dbb41559c4716e94d5290b6ae979a8b96143c

Blue base:
c1a955316055aaf6c1b28853e21ed07e36e55f6a

PR: #17

t0 = NOT DECLARED
P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS

## Immediate confirmed open blockers

Exact phase-6 GitHub Actions run:
35471064118

It executed 371 tests and produced exactly 3 genuine phase-6 failures plus 1 invalid-test error.

1. GLOBAL_MAX_CONCURRENCY_NOT_HELD_FOR_NETWORK_WINDOW
Classification: BLOCKS_CAPTURE_INTEGRITY
Reproduction: two processes sharing SecTrafficBudget overlap their actual HTTP request windows; local server observed maximum concurrency 2 while frozen policy says max_concurrency=1.
Required direction: serialize the complete cross-process network request lifetime, not only reserve(). Preserve crash-safety and rate-limit semantics. Any authority/lock that changes request emission belongs in the acquisition fingerprint.

2. QUALIFYING_MISSING_FINGERPRINT_AUTO_MATERIALIZATION_ATTEMPT
Classification: BLOCKS_CAPTURE_INTEGRITY
Reproduction: qualifying supervisor materialize_if_absent() invokes scripts/quant.py sec-fingerprint when acquisition_fingerprint.json is absent.
Required direction: qualifying launch validates an already-created pre-t0 materialization and fails closed if absent. Materialization creation must be an explicit pre-t0 action, distinct from service startup.

3. READINESS_WEAKER_THAN_EXTERNAL_AUTHORITY_AUDIT
Classification: BLOCKS_CAPTURE_INTEGRITY
Reproduction: delete deployment_authorities.jsonl after an otherwise qualifying run; lifecycle audit rejects it but t0_readiness() still returns instrumentation_ready=true.
Required direction: readiness and audit must use the same consumed external deployment-authority contract.

## Do NOT promote this yet

STATUS_ARTIFACT_TEST_INVENTORY_FALSE_GREEN is only a hypothesis.

The intended phase-6 test errored because the regex is malformed:
r'Proof inventory: **(\d+) unit tests discovered'
=> re.error: multiple repeat.

Repair only the test harness/regex, preserve the intended assertion, rerun, and promote only if it then fails because published inventory differs from authoritative package discovery.

Circumstantial evidence: the status freshness step passed while the phase-6 full suite discovered 371 tests and committed STATE.md had previously reported 310.

## Phase-5 status

Phase-5 six blockers were red-proven at run 35469598503:
- AUTOMATIC_RESTART_EXTERNAL_WITNESS_MISSING
- DEPLOYMENT_AUTHORITY_CONSUMPTION_UNBOUND
- EFFECTIVE_SYSTEMD_POLICY_MISMATCH_ACCEPTED
- BLUE_T0_WINDOW_NOT_PLUMBED_TO_OPERATOR_CLI
- SIGHUP_CLEANLY_STOPS_QUALIFYING_SERVICE
- EXACT_VERIFICATION_SHA_NOT_ENFORCED

Production fix:
eefd544dd9ad2a2b545362cb21d6402f7c733624

Test-only repair commits:
4d9b89b4106e9d5b796ea7a37c5f59810e9b1605
a82f749463f797a3352549dbc2581004c569f25e

On exact phase-6 full-suite run 35471064118 all six phase-5 discriminants pass. Treat phase-5 as red→green CLOSED unless a new falsifier appears.

Run 35470924225 on a82f749 also has Status freshness, Full unit suite, SEC P0 lane and V1 end-to-end green; exact verification-artifact generation was still in progress at last observed checkpoint.

## Method

Do not try to prove the system works. Try to manufacture a false proof.

For every new defect:
- stable id
- scenario
- reproduction
- one classification only:
  BLOCKS_CAPTURE_INTEGRITY
  BLOCKS_PIT_RECONSTRUCTABILITY
  BLOCKS_ANTI_SELECTION_OR_VISIBILITY_FIREWALL
  BLOCKS_ONLY_LATER_INFERENCE_OR_ECONOMICS
- red test
- minimal correction
- green test
- fingerprint impact
- rodage impact

Never mark CLOSED without prior red reproduction and discriminating green.

After every materially significant step update and push:
handoff/ASTRA_P0_CHECKPOINT.md

Checkpoint must contain:
- timestamp UTC
- branch
- exact HEAD SHA
- parent/base SHA
- t0 status
- P0_CONTINUOUS_SERVICE_STATE
- defects CONFIRMED OPEN
- defects CONFIRMED CLOSED
- hypotheses NOT YET REPRODUCED
- red tests
- green tests
- full-suite status
- CI run id/status
- active fingerprint
- materialized fingerprint
- manifest schema/version
- rodage exact artifact/status
- readiness
- audit
- firewall
- acquisition-critical files changed
- next unique action
- exact reproduce/resume commands

## Immediate next action

1. Verify current remote head and inspect anything after 5fc663ca.
2. Fix only the 3 confirmed phase-6 blockers.
3. Repair only the malformed inventory-test regex and rerun it.
4. Push to the SAME branch.
5. Obtain exact-head full-suite + SEC P0 + V1 + exact-verification CI.
6. Promote inventory hypothesis only if the repaired test fails for the intended reason.
7. Update ASTRA_P0_CHECKPOINT.md.
8. Continue adversarially until final exit criteria, without incremental Blue review.

## Remaining campaign after phase 6

Do not duplicate already-covered tests. Materially open:
- restart-limit exhaustion, SIGTERM/systemctl stop-start semantics, supervisor SIGKILL child-death behavior
- exact loaded systemd RestartUSec, StartLimitIntervalUSec, KillSignal, TimeoutStopUSec validation beyond already-tested Restart mismatch
- truly concurrent/interrupted materialization
- deeper budget/state journal failure ordering not already covered
- remaining PIT crash boundaries not already covered by raw→envelope→ack, ENOSPC, torn JSONL, rollback/missing-history tests
- remaining public/protocol proxy leaks
- exact final evidence binding: exact commit SHA, tree digest, acquisition fingerprint, manifest schema, effective runtime config, effective service definition digest, CI run id, timestamp, lifecycle provenance
- final exact-head rodage
- readiness TRUE only when active/materialized fingerprint match and all authority checks pass
- final coherent audit

Do not start final rodage while acquisition-critical code or fingerprint membership is still changing.

## Exit criteria

Return to Blue only when:
- no known blocker class 1–3 remains
- full suite green
- production-path tests green
- CI attached to exact final SHA
- active fingerprint == materialized fingerprint
- final manifest exact
- final evidence bound to exact commit/tree/fingerprint/runtime/service definition
- final rodage executed on exact final state
- firewall clean
- readiness true
- audit coherent
- t0 still NOT DECLARED

Even then:
P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS

The rodage never proves the 14 days, weekend, or silence interval.
