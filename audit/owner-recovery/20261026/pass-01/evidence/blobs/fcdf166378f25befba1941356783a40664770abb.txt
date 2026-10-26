# WAVE 2 CONVERGENCE #2 — C0 CURRENT SEALED-BASE PORT PROOF

Date: 2026-10-21
Role: Integration Foreman / pre-convergence accelerator
Status: TECHNICAL PORT CLEAN — CANONICAL ACCEPTANCE BLOCKED

## Canonical anchor

- `WAVE2_IMMUTABLE_BASE_SHA=2b99d8aeb8a342f1ef32544247d366cb8a26037e`
- historical parent `97165db2faa3300cef1f23de0045ed93d25eb9cb` is not the Wave-2 immutable base.

## Pinned C0 source

- branch: `builder/mega-c0-scientific-adjudication-20261021`
- documentary FINAL head: `6dc84f35e80aec709e67e3d5d3ce0cdcfaee3bcf`
- material code head: `66bdd16085a57e324f92cab4346362acf52d6f93`
- source code/test qualified head named by the sibling FINAL: `be9124f6699e76dc606de6c35a73885212930d78`

The source FINAL is historically rooted at `97165db2...`. Its own exact-head workflow also names `97165db2...` as `WAVE2_IMMUTABLE_BASE_SHA`; that source-lane green proof is therefore not accepted as sealed Wave-2 ancestry.

## Foreman challenge

Workflow:

`.github/workflows/wave2-convergence2-c0-current-final-challenge.yml`

Foreman checkpoint:

`9ba8c565c3ea88524985250291b32148bf183ce1`

Run:

`39663523425`

Job:

`119442432630`

Artifact:

`wave2-c0-current-final-challenge-9ba8c565c3ea88524985250291b32148bf183ce1`

Artifact ID:

`12377320983`

Artifact SHA-256:

`acfe9f8aec4981de7f0ee693f08cbcaa3f62f33530ee30c36ddd41dc1179a2e8`

## Construction

The challenge did not mutate the canonical branch or the C0 sibling branch. It created detached ephemeral worktrees from exact `2b99d8...` and:

1. applied only the C0 semantic module and C0 tests from the pinned source FINAL;
2. rebound the C0 embedded Wave-2 base constant from historical `97165db2...` to canonical `2b99d8...`;
3. relocated `tests/test_mega_c0_scientific_adjudication.py` to `research/research_os/tests/test_mega_c0_scientific_adjudication.py` in the ephemeral port only;
4. excluded sibling workflows and documentary FINAL material from the semantic port;
5. proved the three sealed-base repair blobs remained byte-identical;
6. ran C0, W1 Factory/Validator/Red Team, W1 ECON, root and Research OS qualification;
7. executed the foreman C0-A02 adversarial probe;
8. kept authority and outcome membranes closed.

## Positive proof

Exact results:

```text
C0_CURRENT_SEMANTIC_PORT_APPLIED=TRUE
C0_REBOUND_TO_SEALED_BASE=TRUE
C0_TEST_RELOCATED_TO_RESEARCH_OS=TRUE
SOURCE_WORKFLOW_DOCS_EXCLUDED=TRUE
SEALED_BASE_REPAIR_PRESERVED=TRUE

C0_FOCUSED_34=PASS
FACTORY_VALIDATOR_RED_TEAM_DIFFERENTIAL=63_PASS
W1_ECON_DIFFERENTIAL=86_PASS
ROOT_UNIT_SUITE=799_PASS
RESEARCH_OS_SUITE=457_PASS

C0_AUTHORITY_MEMBRANE=CLOSED
OUTCOME_ACCESSED=FALSE
C0_PROMOTION_TARGET=ECONOMIC_IDENTITY_ONLY
AUTHORITY_OPENED=FALSE
CANONICAL_BRANCH_MUTATED=FALSE
WAVE2_INTEGRATED_SHA_EMITTED=FALSE
```

The test relocation is therefore proven convergence hygiene: it preserves the sealed root inventory at exactly `799` while extending the Research OS suite from `423` to `457` with the `34` C0 tests.

The controlled base rebind is also technically clean: no Factory/Validator/Red Team or W1 ECON differential regression was introduced.

## Failing acceptance case — C0-A02

Expected law:

A producer may not validate its own candidate. `producer_id == validator_id` must fail closed.

Observed receipt:

```json
{
  "acceptance_case": "C0-A02",
  "acceptance_pass": false,
  "actual": "ACCEPTED",
  "error": null,
  "expected": "BLOCK",
  "producer_self_validation_blocked": false
}
```

This is the sole semantic acceptance failure observed in the current sealed-base port challenge.

The workflow itself completed successfully because the foreman intentionally records acceptance failures as evidence instead of hiding them behind an infrastructure-red job. The scientific receipt remains `BLOCK`.

## Final receipt

```text
SOURCE_FINAL_CANONICAL_BASE_BOUND=FALSE
CONTROLLED_REBIND_SIMULATED=TRUE
C0_FOCUSED_TESTS=34
FACTORY_VALIDATOR_RED_TEAM_TESTS=63
W1_ECON_TESTS=86
ROOT_TESTS=799
RESEARCH_OS_TESTS=457
C0_A02_ACCEPTANCE_PASS=FALSE
CANONICAL_ACCEPTANCE=BLOCK
SEALED_BASE_PORT_PROVEN=FALSE
AUTHORITY_OPENED=FALSE
OUTCOME_ACCESSED=FALSE
CANONICAL_BRANCH_MUTATED=FALSE
WAVE2_INTEGRATED_SHA_EMITTED=FALSE
```

## Required repair before canonical acceptance

C0 must fail closed at the Validator receipt boundary when producer and Validator identities are equal, while preserving the existing W1 Validator law and the later C0 semantic-independence hardening.

The detailed repair contract is:

`handoff/WAVE2_C2_C0_CURRENT_REPAIR_20261021.md`

After repair, the same current-head challenge must be rerun against the repaired exact source head. Only an exact receipt with C0-A02 `BLOCK` as expected may upgrade C0 to `SEALED_BASE_PORT_PROVEN`.

## Current disposition

`C0_SOURCE_FINAL=OBSERVED`

`C0_CONTROLLED_SEALED_BASE_REBIND=TECHNICALLY_CLEAN`

`C0_TEST_LAYOUT_RELOCATION=PROVEN`

`C0_A02_PRODUCER_VALIDATOR_INDEPENDENCE=FAIL`

`C0_CANONICAL_ACCEPTANCE=BLOCK`

`C0_SEALED_BASE_PORT_PROVEN=FALSE`

`READY_FOR_CANONICAL_CONVERGENCE2=FALSE`

`WAVE2_INTEGRATED_SHA=NOT_AUTHORIZED_TO_EMIT`
