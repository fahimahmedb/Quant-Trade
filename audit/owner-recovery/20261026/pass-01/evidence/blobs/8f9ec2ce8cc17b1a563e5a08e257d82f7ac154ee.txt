# Builder CP035 — canonical identity before scientific hashing

STATUS=PROVEN_CONTRACT_GAP_BEFORE_CODE
BASE=965ae24f65c6baf586c309e6d21c0d23ac13ed62
ORACLE_HEAD=fb236c284c1ace9aaf154bab0e832712477c6db9
NORTH_STAR_SHA=a328b4e6d7d71dafd532938888ebf9818b1b610f (Git blob)

DONE: CP034 exact code passed 688 configured tests and 190 local V2 tests,
full local workflow/policy/claim ceiling/qualification/real read-only GitHub dry-run.
Hosted qualification remains separate. Move upstream after frozen-runner packages.

FOUND: build_candidate accepts None independently for hypothesis_id,
generation_id, research_trial_id and research_epoch_id and hashes the resulting
object. _require checks only key presence. Epoch/trial constructors use the same
presence-only required-field pattern. Canonical identities cannot be null or
semantic UNKNOWN while claiming attributed scientific state. Family-extension
scientific unknowns and root parent_epoch_id=None have different semantics.

DECISION=HARDEN explicit principal identifiers at epoch, trial and candidate
construction. Require nonblank, non-sentinel strings; preserve raw valid IDs,
candidate hashes, family-specific unknowns and nullable root ancestry. Do not
infer missing IDs, rewrite historical artifacts or add another identity registry.
Qualify all four families and actual pipeline/worker adapters after the change.

HISTORY: reuse current v2_core contracts, not an alternate schema. Compare fresh
Oracle core before editing and preserve concurrent autonomous commits.
NEXT_BEST_WORK: targeted null/type/sentinel and valid-root/unknown-extension
regressions, whole V2 and configured suite, durable implementation checkpoint.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
