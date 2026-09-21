# BUILDER — GATE B EVIDENCE SCHEMA FALSE-PASS FIX — 2026-09-21

## 0. Status

`GATE_B_SCHEMA_REPAIR = READY_FOR_INDEPENDENT_RECHECK`

Return owner:
`BLUE / MISSION CONTROL`

This delivery repairs the authoritative Gate-B evidence schema only. It does not
declare Gate B PASS, authorize target-host mutation, or declare t0.

## 1. Provenance and scope

Authorized branch:
`builder/gate-b-evidence-schema-false-pass-fix-2026-09-21`

Verified starting HEAD:
`8d87f7ae1dde6ab0e8fa9cd249b33756e86f6315`

The mission file still records predecessor HEAD
`2ee9e1d2d84b7c0ded400a56f64ad7d9e2a60651`; the verified starting HEAD is its
direct dispatch descendant and is the owner-specified current mission HEAD.

Normative repair authority:
`governance/BLUE_GATE_B_EVIDENCE_SCHEMA_FALSE_PASS_REPAIR_SPEC_2026-09-21.md`

Defective authoritative schema blob:
`649cb5093930651c0fbdc810563f491084cab896`

Repaired authoritative schema blob:
`993279ed89bffd19cec514b84dea7e5b44a15389`

Repair domain:
`GOVERNANCE_EVIDENCE_SCHEMA_ONLY`

No frozen V4 production code, target-host state, systemd, mounts, runtime,
`src/`, Product code, or P0 state was modified.

## 2. Changed paths

Exactly these delivery paths are changed relative to the verified starting HEAD:

1. `governance/TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_2026-09-21.json`
2. `governance/run_gate_b_evidence_schema_discriminants_2026-09-21.py`
3. `governance/fixtures/gate_b_evidence_schema_positive_pass_2026-09-21.json`
4. `handoff/BUILDER_GATE_B_EVIDENCE_SCHEMA_FALSE_PASS_FIX_2026-09-21.md`

Blob identities:

- repaired schema: `993279ed89bffd19cec514b84dea7e5b44a15389`
- discriminant runner: `8646f69481b698677e161d96c979e282ac204d5c`
- positive synthetic fixture: `0e56a647d67361ebeb0497c3787c633d83c649d2`

## 3. Exact schema delta

The authoritative schema is advanced from structural version
`gate-b-evidence-v2` to `gate-b-evidence-v3`.

Exact semantic changes:

- `$id` and title advance from v2 to v3;
- `properties.schema_version.const = "gate-b-evidence-v3"`;
- `properties.independent_review.properties.ci_runs.minItems = 1`;
- `properties.sub_artifacts.uniqueItems = true`;
- when `overall_verdict = PASS`:
  - `independent_review.verdict` is constrained to `PASS`;
  - `independent_review.ci_runs` is required and must contain at least one
    positive integer run ID;
  - every sub-artifact `classification` is restricted to
    `FACT | CLAIM | INFERENCE | RECOMMENDATION`, excluding `UNKNOWN`;
  - every sub-artifact `defect_classification` is restricted to
    `TARGET_HOST_ONLY | NON_ISSUE | NONE`, excluding
    `REAL_DEFECT | TEST_DEFECT | MISSING_PROOF`;
  - every sub-artifact must include `restricted_reference` as a non-empty
    string containing at least one non-whitespace character.

The restricted-reference constraint is structural only. JSON Schema does not
prove that the referenced bytes are actually retrievable.

## 4. Reproducible discriminant runner

Command:

```bash
python3 governance/run_gate_b_evidence_schema_discriminants_2026-09-21.py
```

The runner uses Draft 2020-12 validation with format checking and mutates one
complete synthetic PASS fixture. Synthetic fixture data is deliberately not
Gate-B evidence.

The exact committed schema/runner/fixture blob bytes were the bytes used for the
local discriminant execution. Local validator version:
`jsonschema 4.26.0`.

## 5. Discriminant and control results

| Case | Expected | Observed | Result |
| --- | --- | --- | --- |
| D1 PASS + independent review FAIL | REJECTED | REJECTED | PASS |
| D2 PASS + missing independent review CI runs | REJECTED | REJECTED | PASS |
| D3 PASS + sub-artifact classification UNKNOWN | REJECTED | REJECTED | PASS |
| D4 PASS + sub-artifact REAL_DEFECT | REJECTED | REJECTED | PASS |
| D5 PASS + sub-artifact MISSING_PROOF | REJECTED | REJECTED | PASS |
| D6 PASS + missing restricted reference | REJECTED | REJECTED | PASS |
| D7 PASS + exact duplicate sub-artifact object | REJECTED | REJECTED | PASS |
| C1 mandatory domain verdict FAIL | REJECTED | REJECTED | PASS |
| C2 mandatory domain MISSING_PROOF | REJECTED | REJECTED | PASS |
| C3 missing mandatory domain | REJECTED | REJECTED | PASS |
| C4 real SEC request count = 1 | REJECTED | REJECTED | PASS |
| C5 t0_declared = true | REJECTED | REJECTED | PASS |
| C6 wrong candidate SHA | REJECTED | REJECTED | PASS |
| C7 wrong candidate git tree | REJECTED | REJECTED | PASS |
| C8 wrong verified input-tree digest | REJECTED | REJECTED | PASS |
| P1 complete synthetic structurally-valid PASS fixture | ACCEPTED | ACCEPTED | PASS |

Runner terminal result:

`SCHEMA_DISCRIMINANT_SUITE = PASS`

## 6. Boundaries preserved

This schema repair does NOT prove:

- global Gate-B run uniqueness;
- cross-run history or terminal-run consumption;
- digest/reference retrievability;
- actual target-host observations or semantics;
- V3-to-V4 transition safety;
- synthetic reservoir isolation;
- evidence retention;
- Gate B;
- t0.

Those remain separate operational proof domains under Blue/Lane A/operator
authority.

Safety state remains:

```text
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
```

## 7. Builder disposition

The authoritative schema false-PASS defect is repaired to the Blue specification
and the requested structural discriminants are reproducible.

Builder does not independently certify final correctness.

`GATE_B_SCHEMA_REPAIR = READY_FOR_INDEPENDENT_RECHECK`

`RETURN_CONTROL_TO = BLUE`
