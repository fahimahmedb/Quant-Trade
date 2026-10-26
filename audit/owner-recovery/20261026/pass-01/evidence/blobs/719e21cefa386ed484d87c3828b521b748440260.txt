# CP089 — Trial proposal -> candidate -> export, before code

Reacquired Builder eaa9598, Oracle 504386d (wake-only delta since integrated
d2e58a7) and historical Blue 9026e4d. Owner North Star blob a328b4e governs.
Skipped network/production and four closed authorities remain unchanged.

Actual reproduction: load the existing oracle_v2_core_fixture.json, replace all
generated proposals with one OTHER/OTHER/a*64 proposal and clear discarded
proposals. Keep trial ID, epoch, candidate and its valid Validator unchanged.
run_pre_outcome_pipeline returns READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY and
creates export hash 5fcf9befd62d3a763746634a2ea242feded3ad566cd9b46e613c5e3bf7e64db4.
The trial hash is bbeae145b1d706073efe4e5e77403da952a31c6e437e68a7ebaf047aa40b3708.
Thus equal trial/epoch labels and a valid candidate Validator do not establish
that this trial generated the exported scientific subject. No outcomes, economic
execution or external Evaluation store were accessed; fixture metadata only.

History search: CP036 attributes trial/candidate IDs, CP044 binds validated
candidate meaning through export, CP075/24f5efa joins actual native proposals and
source packets before challenge. The pure composed pipeline checks only trial/
epoch IDs. Its positive fixture proposals P1/P2 are not scientifically attributed.
Reuse the CP075 matching rule in one core helper shared by both paths; do not
create another trial ledger or weaken native source/epoch/integrity checks.

The pure generic path must join proposal hypothesis, generation and exact V2
candidate hash. Source-adapted proposals instead refer to their original source
candidate hash: preserve that explicit distinction and require the matching
documentary packet. Missing or malformed declared source bindings must not fall
back to generic matching. Native admission must continue to require its original
literal source hashes and retain its current fail-before-model behavior.

Migrate only synthetic positive fixtures to explicit proposal references. Preserve
generated/discarded counts and all scientific candidate fields. Any fixture receipt
golden change must be explained by the newly attributed trial body and accompanied
by semantic assertions. Tests must exercise unrelated same-label proposals, changed
candidate content with a freshly bound Validator, missing/mixed source bindings,
valid generic and native source paths, deterministic replay and input immutability.
Keep source qualification, semantic independence and economic validation distinct.
