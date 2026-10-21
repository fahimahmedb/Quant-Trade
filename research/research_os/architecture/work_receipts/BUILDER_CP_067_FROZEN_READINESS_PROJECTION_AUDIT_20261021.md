# CP067 — Audit frozen protocol to independent readiness projections

CP066 source 49e5f5c0e25895ead87285b1970593402c129d0b passes configured root
778, core V2 287, broader Research OS 268, shared Python 2/JS 57 locally.
Every local V2 workflow step passes; hosted status is tracked separately.
Owner-skipped network/configuration/production tasks remain excluded.

## Fresh reproducible gap

Capture a deep copy of the actual bundle supplied by economic_test_readiness to
its real independent Validator; the capture wrapper invokes the real Validator,
not a stubbed verdict. Baseline is READY. Change only bundle.clock.data_cutoff
from 10:00 to 10:10; or change expression instrument and rehash its spec; or
replace cost model ID/declaration hash. All three still return READY although
the unchanged frozen protocol contains the original clocks/expression/costs.
Only synthetic metadata is involved, no outcomes or provider requests.

Wrapper replay checks protect that wrapper's frozen package, but are not a
substitute for the independent entrypoint's own frozen input checks. History
CP021/CP034/CP036 contains plan/envelope/receipt and candidate binding work;
current Validator binds candidate and protocol digests but not these additional
projections to the frozen source/protocol body.

## Reuse/integrate decision before code

Reuse the existing frozen envelope and its dataset_provenance sources/protocol,
existing route qualification, and existing scientific declaration shapes. Require
independent readiness projections to be reconstructed from that frozen body:
source manifest/snapshots/PIT rows, clock, universe, expression, declared costs/
capacity, multiplicity, trials, decision/entry/exit mappings. Bind the existing
implementability declaration into the envelope when this readiness path freezes
it; preserve default envelope behavior for other existing callers.

Do not add a second freeze authority, registry, runner or economic test. Add an
explicit FROZEN_INPUT_BINDING_FAILED check; keep hash validity, source admission
and other scientific checks distinct. A missing frozen declaration is a block,
not permission to invent it. Upgrade direct synthetic fixtures to express the
complete frozen contract, without rewriting previous persisted receipts/results.
Test mutations whose local hashes have been rebound and prove unchanged freeze/
reproducibility hashes alone do not establish projection integrity. Reassess.
