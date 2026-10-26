# Builder CP017 — content identity survives source renames

STATUS=IMPLEMENTED_FOCUSED_TESTS_PASS
BASE=2be3fbf85e00f4601c626d57376ef68a6814d927
HEAD=commit containing this checkpoint
NORTH_STAR_SHA=a328b4e6d7d71dafd532938888ebf9818b1b610f (Git blob)
ORACLE_HEAD=21bec213b756d7ca0338849eba0e47e300d5b325

DONE: adapted existing CP005/006 planner; immutable packet, record and blob
identities are consumed per frontier independently of filename. Paths remain
provenance. No new registry, scheduler, data acquisition or runtime activation.

EVIDENCE: 11 planner tests PASS, including three new adversarial/integration
tests (multiple subcases): each bound identity prevents rename reuse; changed
versions and other frontiers remain eligible; copied evidence cannot create a
refill task. Combined core/worker/planner suite: 39 PASS, cp017-focused.log in
local setup logs. Full/hosted qualification pending subsequent stable code.

CURRENT_ARCHITECTURE_IMPACT: consumed evidence → future search hardened;
BLOCKED/UNEXECUTED remains distinct from falsified. Legacy tasks without any
content binding retain conservative path-only behavior; unknown historical
bytes are not reconstructed from current content.

FOUND/NEXT_BEST_WORK: worker verification checks optional input hashes, but
does not compare to derivation.source_binding. Reproduced acceptance of a
different source path after removing the input hashes while retaining the
original derivation binding. This breaks the intended CP005 selection→producer
connection. Reuse the existing source-binding validator before source reads;
preserve explicitly unbound historical tasks. Active Oracle worker differs
from Builder (source-aware refill is not yet integrated there); no deployment
or automatic import is intended. Reacquire heads before editing.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
