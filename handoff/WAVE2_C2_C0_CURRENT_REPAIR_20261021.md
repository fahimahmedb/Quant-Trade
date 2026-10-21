# WAVE 2 CONVERGENCE #2 — C0 CURRENT REPAIR CONTRACT

Date: 2026-10-21
Owner role: Integration Foreman / pre-convergence accelerator
Status: SOURCE-LANE FINAL CLAIM CHALLENGED — CANONICAL ACCEPTANCE BLOCKED

## Canonical law

- `WAVE2_IMMUTABLE_BASE_SHA=2b99d8aeb8a342f1ef32544247d366cb8a26037e`
- historical parent `97165db2faa3300cef1f23de0045ed93d25eb9cb` is **not** the Wave-2 immutable base.
- C0 source branch: `builder/mega-c0-scientific-adjudication-20261021`
- observed documentary FINAL head at preparation time: `6dc84f35e80aec709e67e3d5d3ce0cdcfaee3bcf`
- source FINAL material-code head: `66bdd16085a57e324f92cab4346362acf52d6f93`
- source code/test qualified head named by the sibling FINAL: `be9124f6699e76dc606de6c35a73885212930d78`

This handoff does not modify C0, does not integrate it, and does not emit `WAVE2_INTEGRATED_SHA`.

## Finding 1 — source FINAL is bound to the wrong Wave-2 base

The source C0 module still declares:

`WAVE2_IMMUTABLE_BASE_SHA = "97165db2faa3300cef1f23de0045ed93d25eb9cb"`

The sibling exact-head workflow also exports the same historical SHA as `WAVE2_IMMUTABLE_BASE_SHA` and therefore proves ancestry against the wrong anchor. Its green runs are valid source-lane evidence only; they are not canonical sealed-base qualification.

The sibling FINAL document itself records `BASE_SHA=97165db2...` while claiming `SAFE_TO_INTEGRATE=TRUE`. The foreman does not accept that claim for Convergence #2.

Required repair for canonical use:

```diff
-WAVE2_IMMUTABLE_BASE_SHA = "97165db2faa3300cef1f23de0045ed93d25eb9cb"
+WAVE2_IMMUTABLE_BASE_SHA = "2b99d8aeb8a342f1ef32544247d366cb8a26037e"
```

The exact-head workflow / receipt must likewise name and verify `2b99d8...`, or canonical convergence must perform this as an explicit controlled semantic rebind and requalify the resulting exact tree.

Historical C0 checkpoints and receipts must not be rewritten to pretend they originated from `2b99d8...`.

## Finding 2 — C0-A02 producer self-validation is accepted

The foreman sealed-base challenge injected a Validator receipt with:

`producer_id == validator_id`

Acceptance law requires `BLOCK`. Current `bind_validator_ref()` accepted the receipt.

This violates the C0 Acceptance Pack requirement that producer and Validator identities differ and weakens the existing W1 Validator independence law.

Required semantic repair at the C0 receipt boundary:

1. a Validator receipt must carry a non-empty producer identity;
2. a Validator receipt must carry a non-empty validator identity;
3. `producer_id == validator_id` must fail closed;
4. the bound ValidatorRef must retain both identities, or retain sufficient immutable provenance to re-prove inequality;
5. adversarial tests must prove equal identity blocks and distinct identity passes;
6. no fallback may infer independence merely from a validator label.

The repair must reuse the qualified W1 Validator law; it must not introduce a second Validator implementation.

## Finding 3 — test placement creates avoidable convergence inventory debt

C0 currently owns:

`tests/test_mega_c0_scientific_adjudication.py`

The sealed base exact-head root inventory is `799`. MEGA E already demonstrated the safer pattern: module-specific Wave-2 tests can live under `research/research_os/tests/` so they extend the Research OS suite without silently changing the root inventory contract.

Canonical-port recommendation:

`tests/test_mega_c0_scientific_adjudication.py`
→ `research/research_os/tests/test_mega_c0_scientific_adjudication.py`

This relocation is packaging/qualification hygiene only; it must not alter C0 semantics. The current-head foreman simulation explicitly tests this layout before any canonical mutation.

## Semantic-independence hardening retained

The late C0 repair at `66bdd160...` is directionally correct and must be preserved:

- structural independence alone does not count as semantic independent confirmation;
- `independent_confirmation_count=1` requires structural independence, `PRIMARY_SOURCE_RECONSTRUCTION`, and `PROVEN_INDEPENDENT_SEMANTIC_REVIEW`;
- duplicate / wrapper-equivalent / unknown support does not count.

This hardening does not repair Finding 1 or Finding 2.

## Acceptance after repair / controlled port

Before C0 may be marked canonically acceptable, one exact sealed-base-derived tree must prove all of the following together:

- module bound to `2b99d8aeb8a342f1ef32544247d366cb8a26037e`;
- current C0 focused suite green (`34` tests at the current semantic frontier);
- C0-A02 producer self-validation blocks;
- Factory / Validator / Red Team differential remains green;
- W1 ECON differential remains green;
- sealed-base three repair blobs remain byte-identical;
- root suite remains exact and green;
- Research OS suite remains green with C0 tests included under its namespace if relocation is used;
- authority flags all false;
- `OUTCOME_ACCESSED=FALSE`;
- canonical branch remains untouched during simulation.

Only after that proof may the foreman upgrade C0 from `SOURCE_FINAL_PORT_BLOCKED` to `SEALED_BASE_PORT_PROVEN`.

## Current disposition

`C0_SOURCE_FINAL=OBSERVED`

`C0_SOURCE_SAFE_TO_INTEGRATE_CLAIM_ACCEPTED=FALSE`

`C0_CANONICAL_BASE_BINDING=FAIL`

`C0_A02_PRODUCER_VALIDATOR_INDEPENDENCE=FAIL`

`C0_SEMANTIC_INDEPENDENCE_HARDENING=PRESERVE`

`READY_FOR_CANONICAL_CONVERGENCE2=FALSE`

`WAVE2_INTEGRATED_SHA=NOT_AUTHORIZED_TO_EMIT`
