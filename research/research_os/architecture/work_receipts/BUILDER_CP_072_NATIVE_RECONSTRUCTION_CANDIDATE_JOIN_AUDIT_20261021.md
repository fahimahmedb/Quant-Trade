# CP072 — Independent source reconstruction does not yet bind its V2 projection

Base: CP071, 1f2f0ff. No network/production task, active state edit or outcome read.
All four authorities stay FALSE.

## Reproduce before code

Use `V2WorkerIntegrationTests.real_worker()` and two actual bounded wakes against
its disposable local Git remote. Read its actual candidate_draft sidecar. Start a
fresh Python interpreter with a separate GitHubStateStore cache pointing to that
local remote, acquire a fresh snapshot and call the actual `independent_context`.
No process-identity mock or replacement independence verdict is used.

Baseline reconstruction succeeds. Then change each of claim,
mechanism_statement, universe, clock and economic_expression in memory, separately,
and call the actual `build_candidate` so every modified object has a valid new
candidate hash. Keep its original source path/blob/source_candidate_hash.
All five modified objects still receive all four independence axes TRUE and the
same reconstructed V1 candidate hash:
7fffefe81dbb1514d71254510ff81408bc97a9d07ad2616bf99fd7dbc03f4da6.

This is a bounded local documentary/Git/process test, not a fresh publisher fetch,
semantic review or economic experiment. Its cognitive scope is explicitly
R0_DETERMINISTIC_STRUCTURAL_CHECKS_ONLY throughout.

## Audit / history / reuse

`v2_independence.independent_context`, introduced with native provenance at
8af3ac7, verifies distinct process, fresh exact source blob, registered parser and
the reconstructed V1 candidate's manifest hash. It does not compare the rebuilt
V2 projection to the object receiving the proof. Native `independent_validation`
then binds its V2 Validator result to that supplied object's candidate_hash.
Existing CP044 candidate-to-Validator/export binding prevents reusing an old
Validator after a change; it does not protect this earlier proof-creation edge.

Do not add another parser or promote model commentary into source evidence.
Reuse `adapt_engine_output_to_v2_candidate` on independently reconstructed output,
preserving the envelope's trial/epoch/producer/disconfirmation coordinates but
deriving all source-driven fields again. Forward only the three native source
binding keys; copying the whole supplied manifest would also copy altered source
facts and undermine reconstruction. Require actual and declared candidate hashes
to match the fresh projection before emitting independence proof.

Next tests: all native producer families; correctly rehashed source-field changes;
manifest/extension and stale-digest changes; actual separate-process Git retrieval;
native executor refusal before base reasoning/validation or writes. Preserve
unknown fields and legitimate per-task envelope coordinates. No second scientific
store, new authority, semantic PASS or change to persisted historical candidates.
