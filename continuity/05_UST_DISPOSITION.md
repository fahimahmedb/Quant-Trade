# UST forensic disposition

## Witness

Primary lineage: `FLOW-UST-PRIMARY-DEALER-AUCTION-001`, generation `G1`.

Frozen protocol: `7b843ddd551c6770c0ff5941cf5cb1ffb74b8452`.

Post-freeze checkpoint: `ac3b32ffa8ff4d768525c6da2a7ae3f9e2cdddc7`.

## Recovered factual state

The independent validation artifact reports `PASS_TO_TEST_DESIGN_BOUNDED`, but explicitly closes economic experiment, prospective observation, real-capital and live-trading authority and says outcome/price-return data had not been accessed at that validation point.

The subsequently committed frozen protocol preserves `outcome_accessed=false` and contains text that bounded economic outcome access becomes authorized only after the protocol file is committed. The post-freeze checkpoint then records a scoped conversation-owner authorization and labels the current stage as authorized outcome acquisition/execution.

The current Wave2 engineering base used by this mission globally closes economic experiment and prospective observation authority. No primary normative artifact has been proven that resolves the precedence, effective-time, scope or revocation relationship between the historical scoped grant and the current broader denial.

Those facts are preserved together. The mission does not rewrite the historical scoped grant as nonexistent, and it does not choose the historical grant over the current closed state.

## Authority resolution

`AUTHORITY_STATUS=UNRESOLVED`

Because the contemplated next action requires protected outcome access, unresolved authority is a mandatory stop.

No protected outcome was opened by this mission. The frozen question was not retuned.

## Expected continuation obligation

The frozen lineage had an intended next obligation: determine whether the exact frozen screen may lawfully execute under current applicable authority, and execute it only if such authority is explicit, current, scoped to the protocol and non-contradictory.

No lawful existing descendant or historical execution receipt has been proven for this obligation in this mission. That absence is **not** reinterpreted as proof that the scheduler failed.

## Durable closure

A machine-readable `RECOVERY_ARTIFACT` is committed at:

`continuity/evidence/UST_RECOVERY_ARTIFACT.json`

It is explicitly not an original historical receipt and does not fabricate a historical task. It declares one obligation and one `BLOCK` closure with:

- reason `AUTHORITY_UNRESOLVED`;
- exact claim/authority/data/source scope;
- the missing normative condition;
- an observable reopen predicate;
- an idempotency key;
- a content-bound closure hash.

The block may reopen only after a repository-committed current authority artifact explicitly resolves scope, precedence, effective time and revocation for this exact protocol and permits the protected action. Reopen must append an event and preserve the historical block.

## Gate 3

`UST_STATUS=LAWFUL_DURABLE_AUTHORITY_UNRESOLVED_BLOCK`

`UST_EXECUTION_REQUIRED_FOR_PASS=FALSE`

`UST_SILENT_ORPHANING=FALSE`

`HISTORICAL_RECEIPT_FABRICATED=FALSE`

`HISTORICAL_TASK_FABRICATED=FALSE`

`OUTCOME_ACCESSED=FALSE`

`AUTHORITY_CHANGED=FALSE`
