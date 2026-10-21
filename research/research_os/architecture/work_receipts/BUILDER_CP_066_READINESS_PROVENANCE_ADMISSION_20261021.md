# CP066 — Source/time/actor provenance admission for future-test readiness

CP065 audits the reproduced joins. Reuses existing composition, route qualification,
independent Validator checks and frozen plan/replay. No new engine, data loader,
network work, orchestration truth or scientific-state migration.

Each source PIT row now includes its exact snapshot digest and qualified-route
availability, alongside the unchanged supplied snapshot availability. Independent
Validator requires exact multiset coverage of all declared source references and
checks both explicit timezone-aware clocks at data cutoff. Snapshot aliases remain
aliases, not independent trials. Missing/extra/mismatched rows cannot qualify.
Offsets compare as instants; input clock strings are not rewritten.

Producer and Validator identities must be explicit non-null literal strings and
distinct. The independent Validator no longer invents a default identity. This
proves only the declared structural identity property, not cognitive independence.
The direct valid fixture now states its snapshot/time joins explicitly; no
persisted historical receipt or former result is overwritten.

Additional source-provenance falsification before repair: a source digest beginning
with plus or whitespace was accepted by int(value,16), despite being unaddressable
as a 64-hex digest. The independent Validator now checks only ASCII hex characters,
retaining already accepted upper/lower hex forms without rewriting them.

A further synthetic-only reproduction accepted fixture routes after the producer
marker was set False/None/string/zero. The composition now requires a boolean
producer scope and literal True for SYNTHETIC_FIXTURE or FIXTURE_ONLY sources;
returned metadata preserves the scope. A qualified fixture does not silently
become real research evidence. No acquisition or economic calculation occurs.

Five new adversarial tests (37 affected tests PASS) cover post-cutoff route with
older snapshot, missing/invalid clocks, independently hash-rebound extra sources,
wrong/extra/missing PIT joins, malformed hashes, explicit actors, offset equality,
alias accounting and fixture/producer scope. All unrelated freeze/reproducibility
checks remain PASS in the extra-source attack; the new source guard is what blocks.
Inputs remain unchanged, four authorities remain False, no outcome is accessed.
Broader/exact-source results are recorded after execution. Configured target: 778.

Owner's skipped task stays skipped: no network configuration retry, Site/API probe,
VM action or deployment. Reassess independent pre-outcome depth after qualification.
