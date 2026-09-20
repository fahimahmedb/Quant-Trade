# ASTRA GATE A V4 INDEPENDENT AUDIT — FINAL HANDOFF — 2026-09-21

Role: independent Astra / Red Team auditor.
Decision authority remains Blue / Mission Control.

## 0. Repository verdict

AUDIT_GATE_A_V4 = PASS_REPOSITORY_CORRECTION

This verdict is limited to the repository correction at:

blue/p0-gate-a-v4-frozen-2026-09-20@4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072

It does not declare target-host readiness, t0, P14D, Gate B, Product integration, scientific/economic readiness, or real-capital authority.

## 1. Lineage and immutable object

Frozen candidate:
4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072

Astra mission commit:
b636a04b6f8f7786679907d01a4fa22bdfc4e329

Independent-probe commit:
b3b9ceae2958bf06cd08d0b6ae50623308fcdd8b

Audit-workflow artifact-name correction:
1744a897d57dddef524a880d317557c660a17897

Final Astra HEAD:
resolve the live head of astra/p0-gate-a-v4-independent-audit-2026-09-20 after this handoff commit. A Git commit cannot truthfully embed its own SHA.

Verified before this handoff:
- merge-base(candidate, Astra) = 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072;
- Astra at 1744a897... was exactly three commits ahead of the candidate;
- no candidate production file was edited by Astra.

Audit-only delta before this handoff:
- handoff/ASTRA_GATE_A_V4_MISSION_2026-09-20.md
- audit/astra_gate_a_v4_independent_probe.py
- .github/workflows/astra-gate-a-v4-independent-audit.yml

This checkpoint/handoff commit adds documentation only.

## 2. Authorities read

Before the verdict Astra read:
1. QUANT_NORTH_STAR.md
2. current Blue governance state
3. Blue Gate A v4 reception
4. Blue target-host REAL_DEFECT finding
5. Builder v4 mission
6. Builder v4 final handoff
7. P0 qualifying deployment contract
8. target-host rodage entrance contract
9. Astra v4 mission

Blue/Builder conclusions were evidence inputs, not Astra conclusions.

## 3. A1 — independent historical-defect reproduction

Astra reconstructed the old raw-property hash behavior without using the corrected canonicalizer as oracle.

Same semantic command; only transient ExecStart observations changed.

Independent raw-property digest:
- before: 0d3ed6dcb46c9b86ef8cf358781a6d556649c3d030725dbffc90f0de21f54d6a
- after: 13388a4c4f722efa454bb5efa35d91f3dbfbee14c7024c7155f8e614c1207ad1

A1_old_raw_execstart_digest_moves = PASS

FACT: raw ExecStart hashing is unstable under runtime-only metadata.
INFERENCE: the historical target-host failure mechanism is independently reproducible repository-side.

## 4. A2 — transient stability

Each of start_time, stop_time, pid, code and status was changed independently.

Every variant produced:
sha256:dc2e5d9fbd1d9da63a2f8e5033d87e9f46ccf9afc039daf98c707f8a91a50da7

Result: PASS.

## 5. A3 — real command drift

Attacked:
- executable path
- Python interpreter argv
- supervisor path
- root flag
- root value
- added acquisition-relevant argv
- removed -I
- removed qualifying flag

Observed:
- removal of --qualifying is rejected;
- every other accepted tested semantic drift has a digest different from baseline;
- no tested semantic drift collided with baseline.

Result: PASS.

This matches the frozen contract: semantic drift must be rejected or fingerprint-changing, never normalized into equality.

## 6. A4 — parser fidelity

Verified:
- field reordering and delimiter whitespace canonicalize identically;
- no-struct malformed input fails closed;
- unknown stable fields remain bound;
- repeated structs change the digest rather than disappearing.

Five parser limitations were deliberately surfaced:
1. duplicate stable keys are last-write-wins;
2. literal semicolon inside argv is not round-trippable by the simple split parser;
3. internal argv whitespace can move the digest;
4. duration parsing accepts trailing noncanonical text;
5. equivalent duration text representations can move the digest.

Classification for the frozen current unit:
NON_ISSUE / HYPOTHETICAL_FUTURE-UNIT_LIMITATION

Reason:
the frozen service is Type=simple, declares exactly one ordinary ExecStart, has no semicolon-bearing or embedded-space argument, and no current-unit reachable false equality or fail-open path was reproduced from these representations.

Actual v4 target-host serialization remains TARGET_HOST_ONLY.

## 7. A5 — exact qualifying authority

Attacked:
- removed token
- prefix lookalike
- suffix lookalike / --qualifying-disabled
- value-like token
- duplicate exact token

All lookalikes were rejected. Duplicate exact token was not normalized to baseline; it changed the digest.

Result: PASS.

## 8. A6 — existing systemd contract

Independently attacked:
- fragment byte mismatch
- non-empty DropInPaths
- WorkingDirectory
- EnvironmentFiles
- Restart
- RestartUSec
- StartLimitIntervalUSec
- StartLimitBurst
- KillMode
- KillSignal
- TimeoutStopUSec
- unavailable systemctl
- malformed/incomplete systemctl property output

Every tested current-contract drift failed closed.

Result: PASS.

## 9. A7 — digest binding

Verified:
- equivalent ExecStart field order => same digest;
- unknown stable field value change => different digest;
- all accepted tested semantic command drifts => distinct non-baseline digests;
- transient observations => no digest movement.

No tested semantic collision was found.

Result: PASS.

## 10. A8 — materialization / authority / child launch

Independent discriminants verified:
- consumed deployment authority cannot be replayed, including nonce recreation against the ledger;
- stale materialized fingerprint fails closed;
- materialization validation failure occurs before CHILD_LAUNCH_AUTHORIZED and before Popen/child creation;
- existing Phase5 authority tests still require consumed deployment authority and external restart witness.

Result: PASS.

The v4 ExecStart correction does not weaken these boundaries.

## 11. A9 — Builder-test falsification

One Builder test is over-named:

test_materialize_authorize_then_qualifying_start_is_not_invalidated_by_metadata_change

FACT:
its body calls _effective_environment() twice against mocked pre/post ExecStart output and compares the effective-unit digest.

It does not:
- create deployment authority;
- consume deployment authority;
- call materialize_if_absent();
- execute launcher.main();
- create a child with Popen().

Classification:
TEST_DEFECT / NON_BLOCKING

The test is valid digest-stability evidence but is not end-to-end lifecycle evidence by itself.

Astra closes that proof gap independently through A8 plus the existing Phase5 authority campaign. Therefore this test defect does not block the repository correction.

## 12. A10 — second-order search

Inspected:
- _effective_systemd_definition
- _canonicalize_exec_start
- _effective_environment
- current_fingerprint
- materialize_if_absent
- deployment-authority write/consume and replay ledger
- effective_service_configuration
- supervisor_manifest
- acquisition fingerprint manifest construction

FACT:
the surrounding requested systemd properties are configuration properties; the historical target-host runtime observations are the five excluded ExecStart keys.

FACT:
unknown stable ExecStart fields remain bound.

FACT:
QUANT_SEC_EFFECTIVE_UNIT_DIGEST remains bound into effective_service_configuration and therefore the acquisition-critical fingerprint.

FACT:
materialization validates active fingerprint and does not silently rewrite stale evidence.

FACT:
deployment authority binds fingerprint + host boot + nonce and checks a durable consumed-nonce ledger.

Result:
NO_SECOND_ORDER_REPOSITORY_BYPASS_FOUND

## 13. Independent execution evidence

Workflow:
Astra Gate A v4 independent audit

Exact evidence HEAD:
1744a897d57dddef524a880d317557c660a17897

Run:
35544664445 = COMPLETED / SUCCESS

The run:
- verified frozen-candidate ancestry;
- executed independent A1–A10 probe;
- recorded zero probe failures;
- replayed Phase5 + Phase7 + Phase8;
- focused replay = 22 tests, OK;
- uploaded the independent probe artifact.

Artifact:
astra-gate-a-v4-independent-probe-1744a897d57dddef524a880d317557c660a17897
artifact id: 10616800129
uploaded ZIP SHA-256:
61f8e11f3bab7164829f0bd2e1e28403b500f8f5bb9ad99fb1e0b18e8d46e278

SEC P0 pre-t0 gate on evidence HEAD:
run 35544664469.

At handoff authoring, its schema/status freshness, full unit suite, SEC P0 lane suite and V1 end-to-end regression steps had all completed successfully; its exact-head verification-artifact step was still executing.

The final handoff commit triggers both workflows again. A commit cannot embed its own SHA, and the workflow run ID does not exist until after push. Therefore the final exact-head SHA and final run IDs are resolved externally from the live branch after push and reported to Blue. This is an explicit self-reference cut, not proof transfer.

## 14. Classification summary

REAL_DEFECT:
- none reproduced in the v4 frozen candidate.

TEST_DEFECT:
- Builder lifecycle-named Phase8 test overstates its authority-lifecycle coverage; independently compensated by Astra A8 + Phase5.

MISSING_PROOF:
- no repository blocker after final exact-head CI closes;
- repository evidence cannot substitute for real target-host execution.

TARGET_HOST_ONLY:
- actual v4 execution against the real systemd host;
- confirmation of real post-invocation ExecStart serialization under v4;
- runtime-image, mount, durable-state-root, single-writer, reboot and fault semantics required by the entrance contract.

NON_ISSUE:
- the five parser representation limitations listed under A4 for the frozen current unit, absent evidence those representations are reachable on that unit/target.

## 15. Proof boundary

Repository PASS does not establish:
- target-host correctness
- target-host entrance PASS
- t0
- P14D continuity
- Gate B
- Product integration
- scientific/economic readiness
- real-capital authority

The historical restricted v3 target-host defect artifact remains historical evidence only. It is not presented as a v4 target-host result.

## 16. Independent repository verdict

The historical failure mechanism is independently reproduced.
V4 removes the five transient observations from the effective digest.
Stable configuration remains bound.
Tested semantic command drift cannot collide with baseline.
Existing systemd semantic checks remain fail-closed.
Materialization and one-use authority boundaries remain intact.
No new current-unit repository bypass was found.

AUDIT_GATE_A_V4 = PASS_REPOSITORY_CORRECTION

After final exact-head CI is observed, Astra stops and returns control to Blue.
