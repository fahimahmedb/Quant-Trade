# CP083 — Frozen expression -> identity -> portfolio, before code

Reacquired Builder a71317b, Oracle 7d50a63 (only wakes since integrated d2e58a7),
Site d14b96c and historical Blue 9026e4d. Owner North Star blob a328b4e remains
controlling; September routing does not narrow the expanded whole-system scope.

Reproduction uses the existing metadata-only fixture in
research/research_os/tests/test_economic_readiness_integration.py, without adding
market data, outcomes, real-primary declarations or authorization. The actual
economic_test_readiness entrypoint returns READY_FOR_AUTHORIZED_ECONOMIC_TEST.
Its frozen economic expression declares SYNTHETIC_TEST_INSTRUMENT,
SYNTHETIC_ELIGIBLE_UNIVERSE, an entry/exit rule and one declared clock interval.
Its structural identity instead returns UNKNOWN instrument/universe/timing_clock,
the candidate's different 'one interval' horizon and UNKNOWN candidate_hash.
The expression is present and hash-bound upstream but lost at this consumer edge.

History/reuse: B8/724e4c0 composed the interfaces; CP044/d6557df binds exports;
CP068/77c8ffb binds readiness projections; CP081/5b90a8a preserves documentary
fact/thesis ceilings. None transfers an explicitly frozen expression into the
current identity/portfolio path. The existing standalone structural_identity
already accepts explicit generic declarations. Reuse that identity/projection and
the existing frozen envelope; no second identity registry or portfolio authority.

Build the bounded declaration bridge: retain the complete original envelope as
an immutable input basis, verify its content hash and exact candidate/implementation
join, expose instrument/universe/entry clock/horizon with DECLARED_ONLY evidence,
and carry protocol/candidate hashes into structural field provenance. Documentary
issuer facts and thesis support must remain distinct and reconstructible. No alias
from directional semantics to factor exposure, or capacity model to bottleneck.
Missing/foreign/tampered freeze inputs must fail closed. Existing callers without
an envelope must retain their prior contract and golden output. Test actual
composition, portfolio consumption, source ceilings, tampering and input ownership.

Broader coverage must be reassessed against all eight Section 15 criteria and
actual executable tests, with explicit V1/V2/production/economic limits. A source
coverage result cannot establish final canonical Quant, real-primary READY,
semantic independence or deployment. Four authorities remain FALSE. The Owner's
skipped network/production task, Oracle science and outcome stores remain untouched.
