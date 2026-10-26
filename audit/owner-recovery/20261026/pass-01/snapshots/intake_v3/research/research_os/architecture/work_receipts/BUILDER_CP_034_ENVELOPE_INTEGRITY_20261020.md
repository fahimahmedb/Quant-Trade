# Builder CP034 — declared freeze hash → actual candidate envelope

STATUS=IMPLEMENTED_FOCUSED_TESTS_PASS_FULL_QUALIFICATION_PENDING
BASE=7878fecc1f4ab38ef4c787db9c8acd37b1496fa1
HEAD=commit containing this checkpoint
ORACLE_HEAD=fb236c284c1ace9aaf154bab0e832712477c6db9
NORTH_STAR_SHA=a328b4e6d7d71dafd532938888ebf9818b1b610f (Git blob)

FOUND: changing protocol_payload.candidate.claim without changing protocol_hash
still produced a new READY plan and REPLAY_MATCH. Independent object hashes did
not prove the upstream envelope's declared freeze matched its actual payload.
CP033 records this reproduction before the present modification.

DONE: frozen v1 creation requires payload hash equality and matching outer/inner
hypothesis/generation identities. Rehashed but misidentified candidates BLOCK.
Rebinding retains existing specific generation/candidate mismatch diagnostics
before the stricter envelope integrity gate; malformed inputs remain bounded
FrozenExperimentBindingError rather than unexpected attribute failures.
Legacy opaque-envelope mode retains its existing lower capability ceiling.

EVIDENCE: 22 focused tests PASS (three new envelope tests, six accounting/receipt
tests and original 13 frozen-runner tests). Existing identity-mutation diagnostics,
frozen replay/bindings and legacy fingerprints preserved. Invalid payload shapes
and stale/rehashed mismatches tested; inputs not mutated. Pyflakes/whitespace PASS.
Full/hosted qualification pending stable exact code; suite added to V2 CI.

PREVIOUS PACKAGE: exact 7878fec passed 685 configured tests and 187 local V2
tests, policy/claim ceiling, exact-code qualification and real read-only GitHub
dry-run. Source/epoch/authority and runtime/Site remain untouched.

ARCHITECTURE_IMPACT: canonical candidate → frozen experiment → exact receipt →
replay now preserves common scientific identity across the connections, not
merely separately valid hashes. No economic execution or inferred validation.

NEXT_BEST_WORK: qualify stable exact implementation; reassess canonical trial/
candidate identity contracts before moving further upstream. A targeted
reproduction already showed build_candidate accepts None independently for
hypothesis_id, generation_id, research_trial_id and research_epoch_id and hashes
the result. This is an identity contract question, not a reason to rebuild family
extensions or require empirically known mechanism fields. Do not treat this
checkpoint or green tests as completion of the open-ended Owner mission.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
