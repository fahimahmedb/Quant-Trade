# BLUE — GATE B RUN AUTHORITY ASTRA RECEPTION — 2026-09-21

## 0. Decision

Blue receives the independent Astra review of the Gate-B run-authority mechanisms and accepts its blocker classifications without dilution.

Audited Builder delivery:

`builder/gate-b-run-authority-mechanisms-2026-09-21@845dfa3609a9bbb2f81b76cd4375189a30ec2232`

Builder exact-head CI:

`35585585066 = COMPLETED / SUCCESS`

Independent Astra review:

`astra/gate-b-run-authority-mechanisms-independent-review-2026-09-21@02432fae0ceb6440d2aec2182d06756f7151c648`

Astra exact-head CI:

`35588182384 = COMPLETED / SUCCESS`

Astra verdict:

`ASTRA_GATE_B_RUN_AUTHORITY_REVIEW = BLOCKED_REAL_DEFECTS_M1_DURABILITY_M2_FRESHNESS_BINDING_M4_GIT_INDIRECTION`

Blue disposition:

```text
CURRENT_RUN_AUTHORITY_DELIVERY_ACCEPTED_AS_ACTIVATION_AUTHORITY = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
```

Green Builder/Astra workflow execution does not override the independently reproduced defects.

## 1. Exact received defect matrix

| ID | Classification | Blue reception |
| --- | --- | --- |
| A1 | REAL_DEFECT | Registry/receipt short writes may be reported successful. Repair required. |
| A2 | REAL_DEFECT | Required containing-directory durability/fsync is missing. Repair required. |
| A3 | REAL_DEFECT | Consume freshness time is captured before lock acquisition. Repair required. |
| A4 | REAL_DEFECT | Future `issued_at_utc` and chronology invariants are not enforced. Repair required. |
| A5 | REAL_DEFECT | Evidence binding does not prove equality to the activation actually consumed; ordinal typing is weak. Repair required. |
| A6 | REAL_DEFECT | `.git/objects` symlink/foreign object-store indirection can pass M4 locality checks. Repair required. |
| A7 | REAL_DEFECT | Git replace refs can poison authoritative `ls-tree` reads while preserving apparent expected identifiers. Repair required. |
| A8 | TEST_DEFECT | Existing “exact frozen tree” positive control does not exercise the frozen candidate/tree. Test repair required. |
| A9 | MISSING_PROOF | Cross-process flock and mandatory R1/R2 negative controls are not all reproduced. Proof repair required. |
| A10 | MISSING_PROOF | M4 has unresolved pathname-race/TOCTOU assumptions; repository hardening required, irreducible post-verification immutability remains host-only. |

Blue does not reinterpret any of A1-A10 as closed merely because CI is green.

## 2. Non-reopened work

This reception explicitly does not reopen:

### F1 evidence-schema false-PASS

Already repaired, independently rechecked and promoted by Blue.

`F1_REOPENED = FALSE`

### F5 Route-1 host feasibility

Target-host evidence already supports:

`PASS_ROUTE1_FEASIBLE`

Authoritative operator closure:

`operator/gate-b-f5-route1-host-evidence-closure-2026-09-21@17d692beaa8013101670c0c0164c9bb204f471d9`

`F5_REOPENED = FALSE`

### V4 materialization / activation prestage

Completed at:

`builder/gate-b-v4-materialization-activation-prestage-2026-09-21@478735d5924df8bc79777b837e710c9083817512`

Exact-head CI already recorded as:

`35581739682 = COMPLETED / SUCCESS`

`V4_PRESTAGE_REOPENED = FALSE`

## 3. Blue repair authority

Blue created the repair dispatch branch:

`blue/gate-b-run-authority-repair-dispatch-2026-09-21`

Exact dispatch HEAD:

`58b559767ddbb965c1ab6448dd7ec89dc46ec821`

The dispatch descends directly from the audited Builder delivery and adds only governance/mission authority:

- `governance/BLUE_GATE_B_RUN_AUTHORITY_REPAIR_SPEC_2026-09-21.md`
- `handoff/BUILDER_GATE_B_RUN_AUTHORITY_M1_M3_REPAIR_MISSION_2026-09-21.md`
- `handoff/BUILDER_GATE_B_DEPLOYED_BYTE_VERIFIER_M4_REPAIR_MISSION_2026-09-21.md`

No implementation file is modified on the dispatch branch.

The mission files identify their exact starting authority as the dispatch self-commit from which the Builder branches are created. A literal self-SHA is not embedded inside those files because a Git commit cannot truthfully contain its own hash; this Blue reception is the durable external attestation of the exact dispatch SHA.

## 4. Repair lanes dispatched

### R1 — M1/M2/M3

Branch:

`builder/gate-b-run-authority-m1-m3-repair-2026-09-21`

Exact starting HEAD:

`58b559767ddbb965c1ab6448dd7ec89dc46ec821`

Scope:
- A1;
- A2;
- A3;
- A4;
- A5;
- M1/M2/M3 portions of A9.

Implementation ownership:

`scripts/quant_gate_b_runctl.py`

R1 must not modify M4 implementation.

### R2 — M4 deployed-byte verifier

Branch:

`builder/gate-b-deployed-byte-verifier-m4-repair-2026-09-21`

Exact starting HEAD:

`58b559767ddbb965c1ab6448dd7ec89dc46ec821`

Scope:
- A6;
- A7;
- A8;
- M4 portions of A9;
- A10 hardening plus explicit residual host-only boundary.

Implementation ownership:

`scripts/verify_gate_b_deployed_bytes.py`

R2 must not modify M1/M2/M3 implementation.

The two lanes are intentionally disjoint and may proceed in parallel after this dispatch.

## 5. Acceptance policy

A Builder may return only:
- `READY_FOR_INDEPENDENT_REVIEW`; or
- a precise blocker.

A Builder may not self-certify:
- independent defect closure;
- Gate B safety;
- Gate B PASS;
- production readiness;
- t0 readiness.

After both lanes are complete and exact-head CI is actually observed green, Blue must integrate them into one candidate and dispatch a fresh independent Astra recheck.

No repair is accepted as activation authority until that independent recheck is received.

## 6. Target-host and remaining boundaries

This Blue reception performs no target-host operation.

Repository repair does not by itself prove:
- installation/digest of the authority consumer on the target host;
- actual external registry/receipt roots and their permissions/persistence;
- active-run/resume state required by final activation design;
- F6 evidence-root/journald/headroom observations;
- M4 execution against the real frozen target release;
- release immutability across the verification-to-first-mutation window;
- exact host/boot/mount bindings;
- Blue sealing/consumption of one concrete activation;
- Gate-B execution or reception;
- t0.

## 7. Current governance state

```text
ASTRA_AUDIT_RECEIVED = TRUE
DEFECTIVE_RUN_AUTHORITY_DELIVERY_REJECTED_FOR_ACTIVATION = TRUE
REPAIR_DISPATCH_HEAD = 58b559767ddbb965c1ab6448dd7ec89dc46ec821
R1_DISPATCHED = TRUE
R2_DISPATCHED = TRUE
F1_REOPENED = FALSE
F5_REOPENED = FALSE
V4_PRESTAGE_REOPENED = FALSE
TARGET_HOST_TOUCHED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
RETURN_CONTROL_TO = BUILDERS_R1_R2
```
