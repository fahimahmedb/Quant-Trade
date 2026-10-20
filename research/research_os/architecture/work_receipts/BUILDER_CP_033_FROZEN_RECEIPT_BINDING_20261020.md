# Builder CP033 — frozen plan → exact receipt → closed replay

STATUS=IMPLEMENTED_FOCUSED_TESTS_PASS_FULL_QUALIFICATION_PENDING
BASE=5a31b07936c07d970f67609a9db7e5b942065abc
HEAD=commit containing this checkpoint
ORACLE_HEAD=fb236c284c1ace9aaf154bab0e832712477c6db9
NORTH_STAR_SHA=a328b4e6d7d71dafd532938888ebf9818b1b610f (Git blob)

FOUND: three metadata-only reproductions returned REPLAY_MATCH for a foreign
plan's intact receipt, a deleted frozen receipt and a rehashed receipt declaring
live authority true. No actual policy/authority was changed. This extended the
CP032 frozen-runner investigation; fresh Oracle runner had no intervening edits.

DONE: receipt self-hash is followed by exact experiment/plan/protocol/binding,
version and ready-status checks. Frozen v1 plans require their protocol and
receipt; deleting both cannot downgrade to legacy. Root experiment identity is
checked against hashed plan payload. Receipt authority must explicitly contain
all four false flags; closed-state validation rejects any opened flags elsewhere.
Actual legacy plans retain their prior format and deterministic fingerprints.

EVIDENCE: 19 focused tests PASS (six new runner/accounting/receipt tests plus
original 13-test frozen runner suite). Adversarial subcases cover transplant,
rehashing changed identifiers, versions, statuses, hashes, missing components,
all four true/missing/invalid authority values and replay/rebinding. Valid frozen
and legacy plans still replay. Pyflakes/whitespace PASS. New tests added to V2 CI.

ARCHITECTURE_IMPACT: Experiment Infrastructure → durable receipt → reconstructable
replay now verifies common identity and explicit pre-outcome authority, rather
than trusting separate self-consistent objects. No economic execution, source
acquisition, runtime/Site deployment or global convergence.

NEXT_BEST_WORK: full qualification and the next proven upstream connection gap:
altering envelope.protocol_payload.candidate.claim while retaining its declared
old protocol_hash still yields a fresh READY plan and REPLAY_MATCH. The runner
binds those inconsistent references independently. Check envelope integrity and
candidate/hypothesis/generation linkage at freeze without changing legacy mode.
CP030 remains a prior handoff checkpoint, not the mission's terminal state.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
