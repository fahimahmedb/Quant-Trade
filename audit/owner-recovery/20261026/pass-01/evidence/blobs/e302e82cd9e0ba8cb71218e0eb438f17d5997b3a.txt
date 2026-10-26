# Polymarket neg-risk screen — timestamp root-cause and scientific adjudication

DATE = 2026-10-08
SOURCE_WORKFLOW_RUN = 37815709390
SOURCE_ARTIFACT = polymarket-neg-risk-readonly-screen
SOURCE_ARTIFACT_DIGEST = sha256:af451db7145d31b99890791d98fa401ec0bf1dc4fa0d271784151a058b9ec38f
SOURCE_AUDIT_SHA256 = 98662a914b4d2866efe0723f2306783c9b3fcec0ba26a6860572082ca858ed9a

PRIOR_KILL_VERDICT = INVALIDATED_BY_DATA_QUALITY_GATE
TIMESTAMP_ROOT_CAUSE = API_TIMESTAMP_SEMANTICS_MISUNDERSTOOD
SAME_FROZEN_TEST_REEXECUTABLE = TRUE
ECONOMIC_SPEC_CHANGED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

## Why the prior economic verdict is invalid

The source run reported 60/600 valid event-snapshots, zero fully-valid rounds, zero evaluated routes and `DECISION=KILL`. Because the primary route statistic was never computed on any route, that KILL is not scientifically admissible. The original result files remain unchanged as provenance; this document supersedes only their economic interpretation.

## Root-cause evidence from the immutable source artifact

The 600 event-snapshot records were re-analysed without reading or selecting on net-gap outcomes.

1. For event `106981`, every change of an individual token's returned `timestamp` coincided exactly with a change of that token's returned book `hash`: 22 timestamp transitions, 22 hash transitions, 22 joint transitions, zero timestamp-only and zero hash-only transitions.
2. For event `233140`, the same relation held: 14 timestamp transitions, 14 hash transitions, all 14 joint, zero mismatches.
3. For static events such as `237722`, `250181`, `250182`, `250183`, `256576`, `256577`, `256578` and `259108`, both the timestamp vector and hash vector remained unchanged throughout repeated HTTP reads.
4. Returned timestamps normally appeared in equal pairs, consistent with the two binary token books of one component market sharing a state update/version time while different component markets updated independently.
5. Event `256577` was the sole event passing the old `<=1000 ms` cross-token timestamp rule because all six books happened to carry exactly the same state timestamp in all 60 reads. That timestamp was `1789034568908` (2026-09-10T10:02:48.908Z), about 28.3 days before the first 2026-10-08 acquisition. Therefore its zero cross-token skew cannot mean the HTTP acquisition itself was uniquely simultaneous.
6. Event `256576` demonstrated the converse: one batch response contained six current order-book summaries whose per-book timestamps differed by about 2.400 billion ms. The same timestamp vector and hash vector persisted over the ten-minute source run. This is evidence about independently aged book states, not a multi-week HTTP request.

These facts demonstrate that the field was incorrectly used as a client acquisition clock. The field identifies the timestamp of each returned order-book snapshot/state; empirically it advances with the corresponding book state/hash and may remain unchanged across later reads when the book state is unchanged.

## API contract evidence

Current Polymarket documentation for `POST /books` states that the endpoint "Retrieves order book summaries for multiple token IDs using a request body" and describes the response `timestamp` as "Timestamp of the order book snapshot". It does not define that per-book timestamp as the HTTP request-generation or receipt timestamp, nor does it promise equal timestamps across multiple books in one batch.

References:
- https://docs.polymarket.com/api-reference/market-data/get-order-books-request-body
- https://docs.polymarket.com/api-reference/market-data/get-order-book
- https://docs.polymarket.com/market-data/realtime-data

The documented batch endpoint returns all requested book summaries in one HTTP response. Server-side atomicity is not claimed. The scientifically supportable client-side simultaneity observable is therefore the monotonic request/response acquisition envelope of that single batch call, not the difference among independent book-state timestamps.

## Hypothesis adjudication

A. `timestamp` is not demonstrated to be request generation time. Source evidence is consistent with per-book snapshot/state update/version time; it changes one-for-one with book hash changes.

B. YES. One `/books` response can contain multiple component books with naturally different per-book state timestamps.

C. YES. The source runner conflated `book state freshness/version time` with `simultaneity of client acquisition`.

D. The API does not document atomic server-side snapshotting. Client-side, however, all component summaries are acquired through one HTTP request and one response. The end-to-end monotonic request duration is a conservative envelope for the acquisition operation and can be measured directly.

E. YES. The 540 invalidations were produced by the wrong measurement variable. They do not show that the HTTP collection itself took >1 second.

F. Event `256577` passed only because its six independent book-state timestamps were identical; their common timestamp was ~28.3 days old. Its special validity was therefore an artefact of the incorrect gate, not evidence that only this event was acquired synchronously.

## Measurement correction — non-economic only

The numeric synchrony bound remains exactly 1,000 ms. No economic threshold is changed.

Old invalid measurement:
`max(per_book_state_timestamp) - min(per_book_state_timestamp) <= 1000 ms`

Corrected measurement:
`single POST /books monotonic request-response span <= 1000 ms`

Per-book timestamps and hashes remain persisted for provenance and freshness diagnostics but cannot invalidate simultaneity by cross-book subtraction.

The economic collector blob remains pinned as `faffb23fc0c0fce0ad498b05681e2608d0f5b347`; route arithmetic, executable depth, fee calculation, common quantity, 0.10 pUSD / 10 bp threshold and persistence rule are unchanged. A regression test must prove corrected route arithmetic equals the frozen evaluator on synthetic payloads where the legacy timestamp gate is satisfied.

## Scientific gates for the rerun

Pipeline is fail-closed:

`RUNTIME_GATE -> DATA_QUALITY_GATE -> SCIENTIFIC_EXECUTION_GATE -> ECONOMIC_VERDICT`

No economic `KILL`, reserve or promotion may be emitted if `ROUTES_EVALUATED == 0`, `PRIMARY_STATISTIC_COMPUTABLE == FALSE`, or the primary route statistic was not materially executed. No new numerical coverage percentage is introduced because none was frozen before observation.

If the corrected acquisition measurement cannot support the screen, or if no route is evaluable, terminal state is `BLOCKED_DATA_QUALITY` and economic verdict is `NONE`.

This measurement correction is fixed before the rerun and was derived only from API semantics, book timestamp/hash behaviour and runtime validity. Net gaps were not used to choose it.
