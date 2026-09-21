# BLUE — GATE B EVIDENCE SCHEMA FALSE-PASS REPAIR SPEC — 2026-09-21

## 0. Scope

`REPAIR_SCOPE = GOVERNANCE_EVIDENCE_SCHEMA_ONLY`

This is NOT a frozen-V4 production-code repair.

Do not modify:
- `src/`;
- `tests/` except schema-specific governance validation tests if an already
  established governance-test location exists and Blue explicitly accepts it;
- target host;
- runtime release/state;
- Gate-B production candidate.

Primary defect:

`GATE_B_EVIDENCE_SCHEMA_FALSE_PASS = REAL_DEFECT`

Exact defective authoritative schema blob:

`649cb5093930651c0fbdc810563f491084cab896`

Path:

`governance/TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_2026-09-21.json`

## 1. Independent reproduction facts

The current PASS conditional does not constrain:
- `independent_review`;
- `sub_artifacts`.

Current structural weaknesses:
- independent review verdict is arbitrary nonempty text;
- independent review CI list is optional;
- PASS can coexist with UNKNOWN/REAL_DEFECT/MISSING_PROOF sub-artifacts;
- restricted reference is optional;
- duplicate sub-artifacts are not structurally rejected.

## 2. Required repair properties

A repaired schema successor MUST fail closed for overall PASS.

At minimum:

### S1 — independent review

When `overall_verdict = PASS`:

- `independent_review.verdict` MUST equal an explicit accepted PASS value;
- `independent_review.ci_runs` MUST exist and contain at least one positive run ID;
- review HEAD remains exact 40-hex SHA.

### S2 — sub-artifact admissibility

When `overall_verdict = PASS`:

- every sub-artifact classification MUST NOT be `UNKNOWN`;
- every sub-artifact defect classification MUST NOT be
  `REAL_DEFECT`, `TEST_DEFECT`, or `MISSING_PROOF`;
- every sub-artifact MUST carry a retrievable restricted reference unless Blue
  explicitly defines an allowed self-contained exception;
- exact duplicate sub-artifact objects MUST be structurally rejected.

Do not claim JSON Schema alone proves global run uniqueness or digest
retrievability.

### S3 — preserve existing fail-closed controls

Repair MUST preserve rejection of:
- mandatory domain FAIL;
- mandatory domain MISSING_PROOF;
- real SEC request count > 0 for the default synthetic campaign;
- `t0_declared = true`;
- wrong candidate SHA/tree/input-tree.

### S4 — no silent proof inflation

Schema repair must not turn TARGET_HOST_ONLY or operational MISSING_PROOF into
repository PASS.

F2-F6 from Astra remain separate operational-proof items unless this repair
directly and truthfully closes a structural part.

## 3. Mandatory discriminants

Provide reproducible schema-validation fixtures/tests.

The repaired schema MUST reject:

D1. `overall_verdict=PASS` + `independent_review.verdict=FAIL`.

D2. PASS + missing `independent_review.ci_runs`.

D3. PASS + sub-artifact
`classification=UNKNOWN`.

D4. PASS + sub-artifact
`defect_classification=REAL_DEFECT`.

D5. PASS + sub-artifact
`defect_classification=MISSING_PROOF`.

D6. PASS + required sub-artifact lacking its restricted reference, unless the
exact schema/spec defines and exercises a narrow allowed exception.

D7. PASS + exact duplicate sub-artifact objects.

Existing negative controls MUST remain RED:
- mandatory domain verdict FAIL;
- missing mandatory domain;
- real SEC request count 1;
- `t0_declared=true`;
- wrong candidate identity.

Positive control:
one complete synthetic structurally valid PASS fixture must validate.

Synthetic fixtures are schema tests only, never Gate-B evidence.

## 4. Non-goals

This repair does NOT by itself close:
- cross-run uniqueness/history;
- activation consumption registry;
- V3->V4 mount transition proof;
- synthetic reservoir isolation;
- evidence retention;
- actual target-host semantics;
- Gate B;
- t0.

These stay for Blue/Lane A/operator proof.

## 5. Delivery

Builder must provide:
- exact repaired schema path/blob;
- exact diff;
- discriminant runner/fixtures in a governance-appropriate non-production
  location;
- results for D1-D7 + controls + positive fixture;
- no production-code changes;
- final handoff.

Required Builder status:

`GATE_B_SCHEMA_REPAIR = READY_FOR_INDEPENDENT_RECHECK`

Builder may not certify final correctness.

After exact-head CI, Blue will dispatch a targeted Astra recheck.

Throughout:

```text
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
```
