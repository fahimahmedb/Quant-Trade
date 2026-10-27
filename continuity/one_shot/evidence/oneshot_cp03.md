# CP03 retrospective admissibility: product revert recommended

FACT: Comparison anchors are W2 `ebc72b9fd14f91420c37e0b7607f9bfb584a289a`, CP03 `acec18f007b079701ee55a620cf913ac960bdcfa`, resume `40c590189e1389502d179e63f6e0925df8513d2c`, V3 `0691a4c1c905c8cfa1e68d521b12d66655ec4dd3`, F `79329f15bbf02c25fa61e5d5ef6028e5abfb1493`.

RECOMMENDATION: Revert all three CP03 product files by a new commit. Preserve its historical commit, rationale, original tests and source semantics as evidence/replay only. V3_FINAL_STATUS=NOT_PORTED_W2_OWNERSHIP_RETAINED; F_FINAL_STATUS=NOT_PORTED_NO_REQUIRED_ROOT_EXPOSURE_GAP_PROVEN_FOR_THIS_MISSION.

## W2 equivalence and limits

FACT: W2 already implements passive admission in `research/research_os/multi_source_ideation.py:intake` (lines 272-279), strengthened `multi_source_ideation_hardening.py:qualify_for_discovery` (194-213), `DurableProposalLedger` (110-191), frozen proposal/provenance identity (21-36), explicit ancestry (39-59), semantic duplicate checks (`multi_source_ideation.py:247-262`), qualified memory lineage (`227-244`), and light implementability (`265-269`). The strengthened path rejects stale context, exact negative/superseded memory, exact/ancestry duplicates, UNKNOWN/review-required duplicate classification and inadmissible implementability. It explicitly creates no Candidate/task. Proposal Ledger enforces passive status, recursive operational-key prohibition and unobserved-truth firewall. W2 remains the surviving owner.

FACT: W2 `research_intelligence.py:93-115,159-212` already normalizes semantic identity and preserves qualified scientific memory relations, mismatched and UNKNOWN dimensions, evidence identity and claim ceiling. This is available under a different path from CP03; CP03 does not establish that native path was inadequate for the UST forensic witness.

UNKNOWN: This audit does not prove W2 has a complete cross-cohort canonical root/exposure denominator. W2 does not have CP03's `root_hypothesis_id` and `cumulative_exposure_ids` schema at this admission seam. Absence of that optional schema is not proof of a required current safety gap. The primary witness is forensic read-only disposition and does not enroll a root/proposal or access protected outcomes. A future mission must prove a concrete counterexample under the existing canonical path before choosing an identity mapping owner. Historical denominator completeness remains UNKNOWN.

## Direct semantic comparison

FACT: CP03 `ideation_intake.py:180-278` is another admission writer over the reused storage class. Sharing storage does not make its admission policy identical to W2's owner. Eligibility at line 250 depends only on critical-root presence and same-variant rejection. It takes no qualified-memory, current-context or implementability argument and never invokes W2 `qualify_for_discovery`. Thus it cannot inherit W2's negative/superseded memory and stale-context protections merely by using `DurableProposalLedger`.

FACT: Immutable V3 `ideation_intake.py:_classify_novelty` (599-665), `_novelty_rejections` (668-678), and `ProposalLedger.admit` (883-915) require frozen source bindings, qualified-memory comparison, ambiguity rejection, parent/claim/falsifiability checks and rejection of parameter variants/previously explored proposals. CP03 omits several of these and explicitly admits parameter variants (`test_verified_continuity_admission_identity.py:test_parameter_variant_keeps_root_and_charges_prior_exposure`). CP03 is neither a wholesale V3 port nor evidence V3 is the required owner.

FACT: Immutable F `idea_feed/contracts.py:seed` (64-101) validates exact seed schema, source clocks, prior_exposure_state UNKNOWN/KNOWN_EXPOSURE/CONTAMINATED and immutable provenance; `registry.py:register` assigns roots using parent identity or seed ID (101-110), while `expose`/`exposure_state` (147-166) journal source/known exposure and contamination. CP03's newly introduced semantic-hash roots (`idea_feed/primitives.py:36-75`) and `cumulative_exposure_ids` (`ideation_intake.py:207-235`) are a distinct derived identity scheme. They do not import F's journal lineage/history or contamination denominator and cannot be treated as recovered historical exposure truth.

INFERENCE: CP03 is ~451 lines across three new product files, introduces a parallel policy entry point and newly derived root/exposure identities, and has no production call sites. The only current Python imports found are CP03 admission tests, CP06 renewal tests, and the new module's own internal primitive import. The forensic UST witness uses neither. It fails the small/local/no-new-owner/required-invariant conjunction for safety-critical retention. Reverting it cannot break the primary read-only witness.

## Frozen review inputs and authority

FACT: `f503b5f:audit/owner-recovery/20261026/pass-01/README.md` explicitly calls the audit INCOMPLETE and its reports frozen projections, not operational state. `e97bb38:audit/owner-recovery/20261026/architecture-delta-01/DELTA_ARCHITECTURAL_MINIMAL.md` recommends reuse and bounded continuation but states FUNCTIONAL_RECOMMENDATION_NOT_A_BUILD, no product mutation, no permission grant, and no new Proposal Ledger or second denominator. Its proposed F/V3 topology is recommendation rather than proof of production lineage. `642b551:architecture-review/03_CAPABILITY_OVERLAP_MATRIX.csv` identifies duplicate proposal ownership and calls for selecting one versioned contract; `13_FINAL_DECISION_DIGEST.md` says omit repairs when recovery finds equivalent controls and preserves authority/root-denominator unknowns. None is code/promotion authority.

FACT: Historical `continuity/03_IDENTITY_OWNERSHIP.md` chose V3 admission and F primitive ownership without the required W2 gap proof. Preserve the historical file and append a CORRECTION event in current evidence stating MISSION_PRESELECTED_V3_MUTATION_OWNER=FALSE and MISSION_PRESELECTED_F_MUTATION_OWNER=FALSE. No production object mutation is authorized.

## Explicit reduction instructions

RECOMMENDATION: Remove `research/research_os/ideation_intake.py`, `research/research_os/idea_feed/__init__.py`, `research/research_os/idea_feed/primitives.py` from the target with new commit(s). These files were absent at W2, so removal restores W2 ownership. Retain all CP01-CP06 commits in ancestry. Do not alter W2 MultiSource files.

RECOMMENDATION: Preserve exact original bytes of `tests/test_verified_continuity_admission_identity.py` under `continuity/one_shot/replay_tests/CP03_test_verified_continuity_admission_identity.py.replay` (or an equally explicit non-Python replay suffix). Record original path, exact CP03 commit/blob hash and byte SHA256 in a replay index. Remove original test from ordinary `tests/` discovery because it imports intentionally removed modules. Use `git archive acec18f...` into an isolated temporary directory and replay its exact original test there; capture COMMAND/ENVIRONMENT/HEAD_SHA/START_TIME/END_TIME/RESULT/log. Label HISTORICAL_REPLAY_ONLY=TRUE, TARGET_PRODUCT_QUALIFICATION=FALSE, SYNTHETIC=TRUE, PRODUCTION_SCIENCE=FALSE. No dynamic resurrection of historical modules inside target tests and no skip-as-pass substitution. CP06 test also imports `idea_feed.primitives`; archive it with CP06 if renewal is removed.

RECOMMENDATION: Re-run W2 MultiSource v2 tests, late/adversarial MultiSource tests, Research Intelligence tests and ordinary Research OS regression on target. Do not count CP03 historical replay as target identity/exposure qualification. Current F root integration remains a separate mission if concrete production need is proven.

## Self-challenge answers

FACT: No exact W2 gap requiring CP03 has been proved for UST. Existing admission/lineage protection has native W2 paths. Neither sunk cost nor recency justifies retention. The historical tests prove properties of optional new code, not its necessity. Evidence/test-only archival achieves all current forensic needs. Reversion introduces no mutation owner, no fixture production state and no conversion of historical UNKNOWN. There is no primary-witness dependency on any of the three files.

UNKNOWN: Future canonical root/exposure mapping requirements, complete historical denominator, and comparative source productivity remain unresolved; no conclusion here converts them to FALSE.
