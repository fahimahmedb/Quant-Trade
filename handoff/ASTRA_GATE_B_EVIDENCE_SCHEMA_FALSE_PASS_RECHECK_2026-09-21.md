# ASTRA — GATE B EVIDENCE SCHEMA FALSE-PASS RECHECK — 2026-09-21

## 0. Disposition

`ASTRA_GATE_B_SCHEMA_RECHECK = PASS_REPOSITORY_EVIDENCE`

Return owner:

`BLUE / MISSION CONTROL`

This is a targeted repository-evidence recheck of the Gate-B evidence-schema
false-PASS repair only. It does **not** declare Gate B PASS, authorize target-host
mutation, close target-host/operational proof items, or declare t0.

## 1. Audit object and activation checks

Assigned Astra branch:

`astra/gate-b-evidence-schema-false-pass-recheck-2026-09-21`

Mission starting checkpoint:

`b73d8a012af643027b4931cff10232dd685b1353`

Direct parent of that checkpoint:

`12a666fde821d80f7323f527c64c96ff1c290058`

Audited Builder branch:

`builder/gate-b-evidence-schema-false-pass-fix-2026-09-21`

Audited Builder delivery:

`12a666fde821d80f7323f527c64c96ff1c290058`

Remote Builder branch was independently resolved at recheck time and still pointed
exactly to the audited SHA.

Builder exact-head workflow run:

`35579909353`

Observed GitHub run state:

- branch: `builder/gate-b-evidence-schema-false-pass-fix-2026-09-21`;
- head SHA: `12a666fde821d80f7323f527c64c96ff1c290058`;
- status: `completed`;
- conclusion: `success`;
- event: `push`.

Therefore the mission activation condition was satisfied.

Tooling note: this execution environment had no direct outbound git transport from
the local shell, so remote refs were refreshed/resolved directly against GitHub's
repository API instead of relying on a stale local checkout. No local checkout was
used as authority.

## 2. Authorities read

Astra read and applied:

1. `QUANT_NORTH_STAR.md`;
2. `handoff/ASTRA_GATE_B_EVIDENCE_SCHEMA_FALSE_PASS_RECHECK_MISSION_2026-09-21.md`;
3. `governance/BLUE_GATE_B_EVIDENCE_SCHEMA_FALSE_PASS_REPAIR_SPEC_2026-09-21.md`;
4. `handoff/BUILDER_GATE_B_EVIDENCE_SCHEMA_FALSE_PASS_FIX_2026-09-21.md` at the exact audited SHA;
5. the original Astra finding at
   `aff6b7a2ca6355f518578c0ddbcac72fb49a356c`,
   `handoff/ASTRA_GATE_B_V4_TRANSITION_PREACTIVATION_REVIEW_2026-09-21.md`.

The original F1 finding was:

`REAL_DEFECT` in the governance evidence schema, not a frozen-V4 runtime defect.
The defective PASS conditional failed to constrain `independent_review` and
`sub_artifacts`, allowing structurally misleading PASS artifacts.

## 3. Scope and changed-path review

Builder base:

`8d87f7ae1dde6ab0e8fa9cd249b33756e86f6315`

Builder delivery is exactly one commit ahead of that base.

Exactly four paths changed:

1. `governance/TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_2026-09-21.json`
2. `governance/fixtures/gate_b_evidence_schema_positive_pass_2026-09-21.json`
3. `governance/run_gate_b_evidence_schema_discriminants_2026-09-21.py`
4. `handoff/BUILDER_GATE_B_EVIDENCE_SCHEMA_FALSE_PASS_FIX_2026-09-21.md`

No `src/`, production runtime, target-host, state, systemd, mount, or frozen-V4
production path is changed by the audited delivery.

Exact relevant blobs:

- defective schema: `649cb5093930651c0fbdc810563f491084cab896`;
- repaired schema: `993279ed89bffd19cec514b84dea7e5b44a15389`;
- Builder discriminant runner: `8646f69481b698677e161d96c979e282ac204d5c`;
- positive fixture: `0e56a647d67361ebeb0497c3787c633d83c649d2`.

## 4. Independent recheck method

Astra did not accept the Builder conclusion as proof.

The exact committed repaired schema and positive fixture bytes were fetched from
the audited SHA. Astra independently implemented the subset of Draft 2020-12
semantics exercised by this schema and these discriminants, including:

- `$ref`;
- `type`;
- `const`;
- `enum`;
- `required`;
- `properties`;
- `additionalProperties`;
- `items`;
- `minItems`;
- `uniqueItems`;
- `minimum`;
- `minLength`;
- `pattern`;
- `allOf`;
- `if/then/else`;
- date-time format sanity for the positive fixture.

Astra then independently mutated the exact positive fixture for every required
discriminant/control and evaluated the result against the exact repaired schema.
This replay did not invoke Builder's conclusion or reuse Builder's result table.

## 5. Required discriminants

| Case | Expected | Astra observed | Result |
| --- | --- | --- | --- |
| D1 PASS + independent review FAIL | REJECTED | REJECTED | PASS |
| D2 PASS + missing independent review CI runs | REJECTED | REJECTED | PASS |
| D3 PASS + sub-artifact classification UNKNOWN | REJECTED | REJECTED | PASS |
| D4 PASS + sub-artifact REAL_DEFECT | REJECTED | REJECTED | PASS |
| D5 PASS + sub-artifact MISSING_PROOF | REJECTED | REJECTED | PASS |
| D6 PASS + missing restricted reference | REJECTED | REJECTED | PASS |
| D7 PASS + exact duplicate sub-artifact | REJECTED | REJECTED | PASS |

Observed first rejecting constraints were respectively:

- D1: `independent_review.verdict: const PASS`;
- D2: `independent_review.ci_runs: required`;
- D3: PASS sub-artifact `classification` enum;
- D4: PASS sub-artifact `defect_classification` enum;
- D5: PASS sub-artifact `defect_classification` enum;
- D6: PASS sub-artifact `restricted_reference: required`;
- D7: `sub_artifacts: uniqueItems`.

## 6. Negative controls and positive fixture

| Case | Expected | Astra observed | Result |
| --- | --- | --- | --- |
| C1 mandatory domain verdict FAIL | REJECTED | REJECTED | PASS |
| C2 mandatory domain MISSING_PROOF | REJECTED | REJECTED | PASS |
| C3 missing mandatory domain | REJECTED | REJECTED | PASS |
| C4 real SEC request count = 1 | REJECTED | REJECTED | PASS |
| C5 t0_declared = true | REJECTED | REJECTED | PASS |
| C6 wrong candidate SHA | REJECTED | REJECTED | PASS |
| C7 wrong git tree | REJECTED | REJECTED | PASS |
| C8 wrong verified input-tree digest | REJECTED | REJECTED | PASS |
| P1 complete synthetic PASS fixture | ACCEPTED | ACCEPTED | PASS |

Terminal replay result:

`ASTRA_INDEPENDENT_SCHEMA_REPLAY = PASS`

The positive fixture is synthetic structural test data only and is not Gate-B
evidence.

## 7. Additional adversarial edge checks

Astra also tested fail-closed edges not individually named in Builder's D1-D7
table but required by the Blue repair semantics:

| Case | Astra observed |
| --- | --- |
| empty independent-review CI list | REJECTED |
| independent-review CI run = 0 | REJECTED |
| duplicate independent-review CI run IDs | REJECTED |
| PASS sub-artifact TEST_DEFECT | REJECTED |
| empty restricted reference | REJECTED |
| whitespace-only restricted reference | REJECTED |
| null restricted reference | REJECTED |

These results close obvious boundary variants of S1/S2 rather than merely matching
the Builder's exact mutations.

## 8. Old-to-new differential reproduction

Astra replayed representative original F1 false-pass constructions against both
schema generations.

| Construction | Defective blob 649cb5… | Repaired blob 993279… |
| --- | --- | --- |
| PASS + failed independent review / no review CI evidence | ACCEPTED | REJECTED |
| PASS + UNKNOWN / REAL_DEFECT sub-artifact without restricted reference | ACCEPTED | REJECTED |
| exact duplicate sub-artifact | ACCEPTED | REJECTED |

This independently confirms that the audited change removes the reproduced F1
false-PASS acceptance surface rather than only changing labels or fixtures.

## 9. Repair-property assessment

### S1 — independent review

Satisfied for repository schema evidence:

- PASS requires `independent_review.verdict = PASS`;
- PASS requires non-empty `ci_runs`;
- CI IDs remain positive integers and unique;
- review HEAD remains a 40-hex SHA under the base object schema.

### S2 — sub-artifact admissibility

Satisfied for repository schema evidence:

- PASS excludes `UNKNOWN` classification;
- PASS excludes `REAL_DEFECT`, `TEST_DEFECT`, and `MISSING_PROOF`;
- PASS requires a non-empty, non-whitespace `restricted_reference`;
- exact duplicate sub-artifact objects are rejected.

### S3 — existing fail-closed controls

Preserved by independent replay for mandatory-domain failure/missing proof,
missing mandatory domain, real SEC request count 1, t0=true, and wrong
candidate/tree/input-tree identities.

### S4 — no proof inflation

Preserved. This recheck does not reinterpret operational or target-host proof
gaps as repository PASS.

## 10. Explicit boundaries

This PASS is **repository evidence for the F1 schema repair only**.

It does not prove or close:

- global Gate-B run uniqueness/history;
- activation reservation/consumption history;
- digest or restricted-reference retrievability;
- actual target-host observations;
- exact V3→V4 mount/state transition safety;
- synthetic reservoir isolation;
- evidence retention;
- target-host runtime binding;
- Gate B as a whole;
- t0.

Those remain outside this targeted recheck and under Blue/Lane-A/operator
authority as applicable.

Astra performed no target-host operation and no audited-object mutation.

```text
TARGET_HOST_MUTATION_PERFORMED = FALSE
AUDITED_BUILDER_OBJECT_MODIFIED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
ASTRA_GATE_B_SCHEMA_RECHECK = PASS_REPOSITORY_EVIDENCE
RETURN_CONTROL_TO = BLUE
```
