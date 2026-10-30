# WP2 independent exact-head review contract

TARGET_IMPLEMENTATION_SHA=d40053bd112164826273a866199e2941259919b0
BASE_SHA=13721384fe5b94b0136fb4548192e05d5e34e605
REVIEW_MODE=READ_ONLY_INDEPENDENT_CHALLENGE
TARGET_PR=39
SOURCE_REVIEW_ISSUE=40

This branch was created directly from TARGET_IMPLEMENTATION_SHA. This file is the only intentional review-branch delta and exists solely to give the reviewer an exact local checkout of the implementation that issue #40 could not fetch because of environment HTTP 403.

The reviewer must inspect the parent implementation objects directly and must not modify implementation code.

Required decision: exactly one of INDEPENDENT_WP2_PASS, REQUEST_CHANGES_NARROW, WP2_REPAIR_INVALID, BLOCK_EVIDENCE, UNKNOWN.

Mandatory challenges include:
- whether SyntheticWP2Binding closes the historical single-lineage seam or merely creates a test-only alternate path;
- whether its custom sink path and wp2-causality-receipt.v1 obey REUSE > CONNECT > REPAIR > BUILD;
- whether DryRunExperimentRunner.verify_bindings satisfies evaluator semantics;
- whether custom executor injection into ResearchOSWorker proves the intended causal lineage without implying canonical activation;
- whether the causality receipt is sufficiently durable and identity-complete;
- exact-head receipt hash integrity, copy/alias behavior, retry/recovery, duplicate publication and fail-closed behavior;
- exact lineage from BASE_SHA to TARGET_IMPLEMENTATION_SHA and affected-dependency requalification.

Run independent tests against the exact implementation checkout. Distinguish tests planned, executed and passed. Do not inherit builder test claims.

Forbidden: implementation edits, merge, promotion, deployment, runtime activation, WP1 reopening, C1-C4, real science, live data, capital or trading.

SELF_PASS != INDEPENDENT_PASS.
CANONICAL_ACTIVATION != SYNTHETIC_CAUSALITY_PROOF.
GLOBAL_JOIN=NOT_ADMISSIBLE while WP1 remains blocked.