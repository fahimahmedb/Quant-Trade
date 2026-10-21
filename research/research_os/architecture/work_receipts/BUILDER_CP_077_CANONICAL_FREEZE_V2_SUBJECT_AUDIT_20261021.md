# CP077 — Valid canonical freeze and valid V2 sidecar can refer to different subjects

Reacquired Builder 6f2d328e9448788e6f760880fdd6edc9af3f8d30; qualified executable
24f5efabf57c50baf840702b985898cc53aec2ab. Fresh Oracle 31d693184d7a3c9819c9de4f73f4e9a70fe9693e
has only wake-receipt deltas since integrated d2e58a7. Site stays d14b96c.
Blue 9026e4d is the historical CP12 routing head; its original North Star blob
8295041 is older than Owner expansion 8b1ff1d. Preserve the later explicit Owner
scope and current a328b4e6d7d71dafd532938888ebf9818b1b610f North Star.
No skipped network/production action or authority change.

## Before-code reproduction

In a disposable actual Git remote, use the existing V2 real-worker harness to
complete all five producer stages first for fundamental A, then for event/document
B with the captured declared document packets. Each creates its actual canonical
V1 freeze, V2 frozen candidate, generation trial and validation handoff. No base
executor, source parser, source reconstruction or independence verdict is mocked.
The reasoning backend is the explicitly local test double, not a real model.

In a distinct Python interpreter with a fresh Git snapshot, run the real native
independent-validation stage on A's handoff. Baseline frozen/Validator subject is
DOC-FUND-9219d7f488ada3c2 on both sides. Then change only the in-memory task's
frozen_hypothesis reference and V1 lineage to B's actual handoff, leaving A's V2
candidate/trial/epoch references intact. Native validation still returns CONTINUE,
calls the test model once and emits a V2 Validator for DOC-FUND-9219d7f488ada3c2,
while its canonical frozen subject is DOC-EVENT-d8d19dbf0b1291ce.

Both scientific decisions are BLOCK, not PASS: this is evidence of a wrong-subject
verdict/provenance join, not a claim of demonstrated economic promotion or a
production exploit. Outcomes remain unaccessed and all authorities FALSE.

## Audit / history / reuse

CP073 reconstructs the supplied V2 object from its own source. CP075 verifies its
own trial and active epoch. Canonical `_frozen` verifies the supplied V1 lineage
and engine output. None compares those two independently valid subjects before
`adapt_existing_validation_to_v2` binds the V1 decision to the V2 hash. The pure
pipeline's coherent input bundle does not prove this native cross-format edge.
CP044's post-verdict candidate binding cannot repair a misattributed verdict at
creation. This is the composed audit explicitly requested by CP076.

Reuse `_frozen` and the existing full source-candidate hash; compare canonical
V1 output identity to the V2 manifest before retrieval/model work. Emit a binding
receipt in the existing stage artifact rather than a new store. Also retain exact
falsification_scope and decision_map from the engine output: the native freeze
copies six scientific fields, while `_frozen` currently compares only IDs,
mechanism and claim. A stored rule must not silently replace its frozen source rule.

Next: complete native unit fixtures with coherent canonical freezes; test the
actual two-producer/separate-process path, wrong subjects, changed scientific
fields, missing source bindings, and all challenge stages. Preserve documentary
BLOCK/R0 limits, valid replay and old immutable records. No dataset, economic
experiment, semantic independence claim or duplicate scientific registry.
