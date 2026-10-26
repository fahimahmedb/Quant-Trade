# CHECKPOINT 010 — CP7–CP9 reconciliation against qualified Oracle V1

Recorded 2026-10-20 (Europe/Paris).

## Scope and non-interference rule

This checkpoint updates the 2026-10-19 forensic conclusions against the current qualified Oracle H24 implementation. It is observation/audit only. It does **not** modify the live Oracle branch, runtime, scheduler, scientific state, authority, task queue, hypotheses, receipts or deployment.

Audit input branch:

- `audit/forensic-checkpoint-20261019`
- input audit HEAD: `df27181887dfa3a0998e54bf1a88cc41cd8047d6`

Observed live Oracle branch:

- `builder/oracle-economic-loop-recovery-20261019`
- observed Oracle HEAD: `14479dc7649c6126420a9627ad8fec2147e2c335`
- observed tree: `d5e69acd43ae90eb6dab6c63f9e06f6992499b36`
- observed latest transition: `Research OS independent_validation VALIDATE-DOC-FUND-9219d7f488ada3c2-g1-b081ffda6505 [skip ci]`

Qualified V1 release remains documented as:

- `f3943830e20b05d926d3013501573b8b21fdace7`
- classification: `ORACLE_H24_V1_OPERATIONALLY_QUALIFIED`

The Oracle branch can advance autonomously after this checkpoint. This document binds only the exact observed HEAD above plus already-durable V1 qualification evidence.

## Permanent authority boundary

No audit finding changes authority. These remain CLOSED:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

Operational qualification, validator PASS, a frozen hypothesis, a model response or an audit result grants none of these authorities.

## Executive reconciliation

CP7–CP9 correctly identified the pre-V1 scientific and deployment gaps. V1 subsequently closed many of the implementation/runtime gaps without invalidating the forensic conclusions that remain about scientific identity and historical coverage.

Current classification:

- `V1_OPERATIONAL_QUALIFICATION_VALID = TRUE`
- `CP9_ORACLE_RUNTIME_IMPLEMENTATION_GAPS = OBSOLETE_HISTORICAL`
- `LEGACY_FAIL_CLOSED_BOOTSTRAP = CLOSED_FIXED`
- `CURRENT_CORPUS_DETERMINISTIC_NORMALIZATION = CLOSED_FIXED`
- `ASML_CURRENT_LINEAGE_OVERLAP_DETECTION = CLOSED_FIXED`
- `NEW_CANDIDATE_CURRENT_CORPUS_SCREEN = CLOSED_FIXED`
- `PORTFOLIO_OVERLAP_BLOCKS_ECONOMIC_READINESS = CLOSED_FIXED`
- `COMPLETE_PEER_SET_IN_WORKER_READINESS_PATH = CLOSED_FIXED_FOR_CURRENT_WORKER_PATH`
- `VALIDATOR_CURRENT_LINEAGE_SCREEN = CLOSED_FIXED_FOR_WORKER_CHALLENGE_PATH`
- `GLOBAL_WORKER_PREFLIGHT_BLOCKS_ANY_PREEXISTING_UNRESOLVED_CORPUS_OVERLAP = FALSE`
- `GLOBAL_PREFLIGHT_OVERLAP_POLICY = OPEN_V2_GOVERNANCE_GAP`
- `LEGACY_RECONCILIATION_COMPLETE = FALSE`
- `LEGACY_RECONCILIATION_STATUS = PARTIAL_WITH_EXPLICIT_GAPS`
- `EMPIRICAL_CORRELATION_WITHOUT_ADMISSIBLE_RETURN_HISTORY = UNAVAILABLE`
- `MARGINAL_PORTFOLIO_CONTRIBUTION_WITHOUT_ADMISSIBLE_RETURN_HISTORY = NOT_ESTIMATED`
- `FORWARD_FARM = CLOSED_BY_AUTHORITY`
- `ECONOMIC_OUTCOME_ACCESS = CLOSED_BY_AUTHORITY`

The remaining global-overlap preflight gap does **not** retroactively invalidate V1 operational qualification. V1 proves scheduling, recovery, persistence and fail-closed authority behavior. It does not claim scientific completeness or economic edge.

---

## CP8 acceptance matrix — current disposition

### A. Legacy bootstrap

**Disposition: `CLOSED_FIXED`, with historical coverage limitation preserved.**

Current worker preflight:

1. requires the source manifest;
2. requires materialized `LEGACY_RESEARCH_LEDGER.imported.json`;
3. recomputes the Git blob identity and requires an exact manifest match;
4. requires schema equality;
5. requires historical-result immutability in both manifest and ledger;
6. requires real-capital and live-trading authority false in both manifest and ledger;
7. requires a non-empty record list;
8. loads the real `LegacyKnowledgeBase` and requires the loaded-record count to match the actual ledger records.

This corrects the old fail-open Oracle bootstrap concern from CP6/CP9.

Important preserved distinction: `historical_research_items_found = 33` in the manifest is a reconciliation census, not a required equality to the imported ledger record count. The qualified V1 evidence loaded 20 actual records. Do not rewrite this as `20 == 33` or claim complete historical reconciliation.

Legacy remains explicitly `PARTIAL_WITH_EXPLICIT_GAPS`. Historical PR #1 and later backlog cycles must not be silently reclassified as completely captured merely because runtime bootstrap is now fail-closed.

### B. Current frozen corpus

**Disposition: `CLOSED_FIXED`.**

`worker_preflight.py` now deterministically enumerates and normalizes the current hypothesis corpus and binds a snapshot hash. Tests assert no silent omission by requiring the normalized IDs to equal the hypothesis filenames.

Heterogeneous historical schemas are normalized fail-closed. Unsupported generation/schema cases block rather than silently dropping an item.

The real ASML pair is a regression fixture:

- `FUND-ASML-CAPACITY-SERVICE-001`
- `FUND-ASML-CAPACITY-PRICING-001`

It is detected as `HIGH_CURRENT_EXPOSURE_OVERLAP_REVIEW`.

### C. Economic distinctness / anti-redetection

**Disposition: `CLOSED_FIXED_FOR_NEW_CANDIDATES`; existing historical overlap still requires explicit governance.**

Current candidate screening:

- blocks exact current IDs;
- blocks unresolved high current-exposure overlap;
- does not interpret UNKNOWN identity as proof of distinctness;
- binds the screen to the current corpus snapshot hash;
- retains a machine-readable list of matching peers and reason codes.

The worker producer path invokes this current-corpus screen before research progression, again during disconfirmation, and again immediately before freeze. Legacy screening is also combined into the stage-level screen.

Therefore the CP7 failure mode where an ASML-like rewording could simply become a second new frozen hypothesis is now covered for the current worker producer path.

This does not erase the historical ASML pair already present. Historical evidence remains immutable.

### D. Portfolio / economic readiness

**Disposition: `CLOSED_FIXED` for the current canonical worker/readiness path.**

The old CP7 defect is repaired: unresolved portfolio overlap is no longer merely diagnostic. `economic_test_readiness_v1.py` adds `BLOCK_UNRESOLVED_CURRENT_EXPOSURE_OVERLAP` when `same_exposure_review_pairs` is non-empty.

Current worker readiness calls bind peer identities derived from the full normalized current corpus excluding only the focal hypothesis. The integrator also recomputes the current-corpus screen and can only make readiness more restrictive.

Preserved scientific limits:

- structural similarity is not empirical correlation;
- absent admissible return histories, empirical correlation remains `UNAVAILABLE`/unknown;
- marginal portfolio contribution remains `NOT_ESTIMATED`;
- readiness does not authorize an experiment or economic claim.

### E. Validator / red team current-lineage context

**Disposition: `CLOSED_FIXED_FOR_WORKER_CHALLENGE_PATH`, not a claim that every standalone validator API automatically loads repository context.**

The canonical worker independent-challenge path:

1. loads the immutable frozen hypothesis;
2. verifies producer lane/generation/engine-output binding;
3. screens the focal frozen hypothesis against the fresh current corpus with only self excluded;
4. persists the screen in the independent-validation artifact;
5. adds `BLOCK_PORTFOLIO_DUPLICATION` when the screen blocks;
6. supplies complete peer identities to economic readiness when a readiness package exists;
7. passes portfolio duplication state into the red-team context;
8. prevents integration unless claim restrictions are empty, red-team status is PASS, the current screen passes, and explicit machine-readable integration authorization exists.

The standalone `validator_economic_readiness_v3()` API remains focused on its supplied readiness bundle and does not independently crawl the repository. Repository/current-lineage context is therefore a responsibility of the canonical worker orchestration path, not an intrinsic property of every validator function call. V2 should preserve or strengthen this separation explicitly rather than assume context magically exists.

### F. Worker / Oracle runtime

**Disposition: mostly `CLOSED_FIXED`; one acceptance wording remains intentionally unresolved.**

Closed since CP9:

- scheduler implemented and operationally qualified;
- exact content-addressed release identity;
- real Legacy bootstrap in worker preflight;
- deterministic current-corpus snapshot in worker preflight;
- current-candidate anti-redetection in stage execution;
- fresh GitHub state before claim and critical transitions;
- claim/lease/generation fencing;
- process-crash/expired-lease recovery without duplicate lineage/stages/receipts;
- durable receipts/events/artifacts;
- actual service/timer, genuine reboot and natural post-reboot wake proven for V1;
- scheduler invokes the canonical `oracle_worker` rather than a separate scientific execution architecture;
- the worker runs preflight before selection, during selection, after claim/lease verification and again before final publication;
- all four authorities remain closed.

The scheduler therefore cannot bypass the canonical scientific worker merely by waking it.

#### Remaining CP8-F mismatch: global overlap at startup

CP8 literally required startup preflight to include `no unresolved duplicate`.

Current `run_worker_preflight()` computes:

- corpus snapshot;
- overlap map;
- `review_count`;
- `review_pairs`;

but returns `status = PASS` even when `review_count > 0`.

This behavior is demonstrated by the qualified V1 corpus, which retained the historical ASML overlap while operational wakes were allowed. Tests explicitly require ASML overlap detection and candidate blocking, but do not require `run_worker_preflight()` itself to fail solely because the repository already contains an unresolved historical overlap.

This creates an important policy distinction:

- **execution-global policy:** current runtime may continue operating while a historical unresolved pair exists;
- **candidate/lineage policy:** a new or challenged candidate that collides with the current corpus is blocked;
- **economic-readiness policy:** unresolved structural overlap blocks readiness.

The implementation is therefore internally coherent, but it does not literally satisfy the strongest wording of CP8-F.

Classification: `OPEN_V2_GOVERNANCE_GAP`, not `V1_RUNTIME_FAILURE`.

V2 must decide explicitly whether a historical unresolved overlap should:

A. block the entire autonomous research runtime;
B. quarantine only the affected exposure/lineages while unrelated research continues; or
C. be resolved by a canonical lineage/duplicate-resolution registry before V2 activation.

Recommended V2 direction: **B + C**. Global shutdown wastes safe unrelated research; silently permitting the affected exposure is too weak. Quarantine the affected exposure and require a durable resolution state (`CANONICAL`, `SUPERSEDED`, `RELATED_DISTINCT_WITH_RATIONALE`, or `UNRESOLVED_BLOCKED`) before that exposure can progress toward readiness.

---

## CP7 conclusions — supersession map

| CP7 conclusion | 2026-10-20 disposition |
| --- | --- |
| ASML current-lineage near duplication proven | `STILL_TRUE_HISTORICAL_EVIDENCE` |
| second freeze occurred after first | `STILL_TRUE_HISTORICAL_EVIDENCE` |
| second historical validation did not reconcile first | `STILL_TRUE_HISTORICAL_EVIDENCE` |
| frozen hypothesis schema not unified | `MITIGATED_BY_FAIL_CLOSED_NORMALIZATION` |
| current set not auto-normalized | `CLOSED_FIXED` |
| readiness current set autoload absent | `CLOSED_FIXED_IN_CANONICAL_WORKER_PATH` |
| peer completeness caller-dependent | `GENERIC_API_STILL_CALLER_DEPENDENT; WORKER_PATH_FIXED` |
| portfolio overlap did not block readiness | `CLOSED_FIXED` |
| correlation must not be fabricated | `STILL_REQUIRED_AND_PRESERVED` |

No historical finding is deleted; it is superseded only where current code/evidence repairs the defect.

## CP9 conclusions — supersession map

| CP9 conclusion | 2026-10-20 disposition |
| --- | --- |
| wholesale old OCI merge unsafe | `STILL_TRUE_AS_HISTORICAL_MIGRATION_RULE` |
| old OCI scientific state stale | `STILL_TRUE_HISTORICALLY` |
| useful OCI deployment primitives existed | `PORTED/REPLACED_IN_CURRENT_RAIL` |
| VM autonomy implementation missing | `OBSOLETE; V1 QUALIFIED` |
| real Legacy Oracle preflight missing | `CLOSED_FIXED` |
| current-frozen dedup Oracle preflight missing | `CLOSED_FIXED_FOR_DETECTION/SCREENING; GLOBAL_REVIEW_POLICY_OPEN` |
| scheduler missing/not enabled | `OBSOLETE; V1 QUALIFIED` |
| ORACLE_CP1 NOT_COMPLETE | `SUPERSEDED_BY_QUALIFIED_V1` |
| ORACLE_CP2 NOT_COMPLETE | `SUPERSEDED_BY_QUALIFIED_V1` |

The old OCI branch must still not be wholesale merged into V2 merely because its historical purpose has been superseded. Cleanup must first classify unique commits/evidence and preserve anything not represented in canonical current history.

---

## Cleanup implications

No branch deletion is authorized by this checkpoint alone.

The next audit stage must inventory every branch and classify it using evidence, ancestry and unique content, not age or naming:

- `KEEP_CANONICAL`
- `KEEP_LIVE`
- `RETAIN_EVIDENCE`
- `MERGE_OR_PORT`
- `ARCHIVE_OR_TAG`
- `DELETE_CANDIDATE`
- `UNKNOWN_REVIEW`

A branch can become a `DELETE_CANDIDATE` only after proving one of:

1. it has no unique commits relative to a retained canonical descendant; or
2. all unique useful implementation/evidence has been intentionally ported and its historical identity is durably referenced elsewhere; or
3. it is a disposable generated branch with no unique scientific/economic result or governance evidence.

Never delete merely because a branch is old, abandoned, failed, negative, superseded or visually redundant. Negative research and failed experiments are part of the anti-redetection memory.

Before any destructive cleanup, create a separate machine-readable or tabular cleanup manifest binding each branch name, current tip SHA, ancestry/uniqueness evidence, disposition and preservation target.

## V2 carry-forward requirements from this audit

1. Preserve V1 exact qualified release as an operational baseline while V2 is separate.
2. Preserve deterministic current-corpus normalization and candidate screens.
3. Preserve full peer binding on canonical readiness paths.
4. Preserve structural-overlap blocking of readiness.
5. Add a canonical overlap-resolution/quarantine state rather than relying indefinitely on unresolved review pairs.
6. Preserve Legacy fail-closed bootstrap while separately completing historical reconciliation.
7. Keep validator/red-team producer independence and explicit integration authority.
8. Preserve fresh-state/CAS/lease/idempotency/restart guarantees.
9. Do not convert structural similarity into empirical correlation.
10. Keep Forward Farm/economic outcomes/capital/live trading closed until separate Owner authority exists.

## Audit verdict

`CP7_CP9_RECONCILIATION = COMPLETE_AT_OBSERVED_ORACLE_HEAD`

`V1_OPERATIONAL_BASELINE = PRESERVE`

`SCIENTIFIC_CLEANUP_REQUIRED_BEFORE_V2_CONVERGENCE = TRUE`

`DESTRUCTIVE_BRANCH_CLEANUP_AUTHORIZED_BY_THIS_CHECKPOINT = FALSE`

Next gate: exhaustive branch inventory and preservation manifest before any deletion/archive operation.
