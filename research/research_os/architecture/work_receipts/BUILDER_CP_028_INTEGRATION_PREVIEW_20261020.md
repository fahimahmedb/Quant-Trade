# Builder CP028 — pinned integration feasibility / Integrator handoff

STATUS=STATIC_INTEGRATION_PREVIEW_COMPLETE_NO_REF_OR_CHECKOUT_CHANGE
BASE=ed947dc61b4631bb45b487953e1fbb46a246e9af
QUALIFIED_CODE_HEAD=ca3bd859e0fc48c2b8004b906f603b52b55ecac5
ORACLE_HEAD=d46116b31f3a217fdf418fe08aa2c4820d5d93c0
COMMON_BASE=7e2a6de231939f4b559a63fac3ea7eee28d81e1f
NORTH_STAR_SHA=a328b4e6d7d71dafd532938888ebf9818b1b610f (Git blob)

DONE: git merge-tree preview of exact Builder and Oracle heads, preserving both
histories. Git objects were created locally; no ref, index, checkout, task state,
VM, Site or deployed release changed. No merge was performed on either branch.
Preview tree 4dc0e6e0cc8cbf8d880e0d99db93821b4d03973e has two conflicts only:

- .github/workflows/oracle-v2-core.yml: Integrator must reconcile coverage/branch
  routing, retaining both streams' required modules/tests and gates.
- STATE.md: regenerate with official status_artifacts.py after reconciliation;
  do not choose a side's test inventory by hand.

EVIDENCE: all 24 changed Python modules compile syntactically in the preview
(no import/execution). All 48 Oracle-only receipt/runtime-evidence blobs checked
against common base survive byte-identically. All 23 existing Live Lab files
retain Oracle blob identities. This does not prove merged runtime behavior.
No native-observer Python module was found by name in the Oracle tree; receipt
commits do not establish its VM-installed configuration. That remains Integrator
proof. No installed observer preservation claim is inferred from a code scan.

PREREQUISITE DELTA: complete Builder import also carries CP005's one additional
Institutional Flow allowed-action line in RESEARCH_FRONTIER.json, permitting the
already-existing bounded mechanism stage. This predates this mission's six
patches. Reconcile it explicitly rather than treating a whole-branch import as
code-only. No four-authority or epoch/policy change is proposed.

DECISION=HANDOFF, do not apply this preview or perform Closure 4. Git text
auto-merge of runtime files is weaker than integration qualification. Import
prerequisite-complete changes, regenerate reports, run union tests/CI, then the
Integrator's controlled canary/natural wake/Site/recovery gates on the exact
chosen release. Reacquire Oracle HEAD first; autonomous writes may advance.

Machine proof: BUILDER_CP_028_INTEGRATION_PREVIEW_20261020.json.
NEXT_BEST_WORK: final hosted SEC outcome on qualified code, durable receipt and
compact session/resume checkpoint. No unfinished source modification remains.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
