# CP063 — Source admission from a recovered engineering lesson

Implements the independent CP062 synthetic reproduction in the existing daily
Data Plane adapter. No new provider, acquisition daemon or economic runner.

A successful chart must explicitly declare error=null, one result and supported
quote/adjusted-close structures. Missing/malformed/non-null errors and mismatched
arrays fail as DataUnavailable, allowing the existing Data -> Control -> snapshot
recovery path to continue. Empty errors no longer silently admit a price panel.
Source values/timestamps must be finite numbers, not booleans; duplicate sessions
are refused. Complete valid bars preserve their values and existing PIT caveats.
Partial prices or missing volume drop that bar; unknown volume is not invented as
zero. A declared numeric zero remains valid. No interpolation, data repair,
capacity inference or raw snapshot rewrite.

Five new tests use only synthetic HTTP JSON and temporary paths: non-null/missing
error ambiguity, malformed/numerically unsupported payloads, unchanged valid bars
and source/PIT declarations, absent volume/price without fabrication, and actual
ingest_all recovery with persistent dataset_blocked events. That integration test
mocks the unrelated missing index and snapshot loader but executes the real Yahoo
adapter and ingestion error handling; it proves control continuation and durable
WARN receipts, not real provider or snapshot contents. Existing V1 root tests
qualify actual committed snapshot/replay behavior separately.

This is a learning-to-Build-to-Data connection: historical crypto protocol
invalidation supplied a testable engineering lesson, not a strategy parameter,
economic result or new research trial. The retired recorder is not resurrected.
No Yahoo request, sealed Evaluation read, prospective capture or deployment.
All four authorities remain FALSE. Synthetic tests pass; exact-source broader and
hosted qualification are checkpointed after execution. Configured target: 773.
