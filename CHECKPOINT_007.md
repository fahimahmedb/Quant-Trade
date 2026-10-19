# Forensic Audit Continuation — Checkpoint 007

Date: 2026-10-19
Audit branch: `audit/forensic-checkpoint-20261019`
Parent audit head: `1ff248ed54a7b5d479b169de430d512f4c40207e`
Status: `PARTIAL_IN_PROGRESS`

## Scope

This checkpoint closes the next item from CP6: test whether current economic-identity / Portfolio handling would prevent the demonstrated ASML current-lineage collision from being treated as an independent candidate.

This is an audit-only checkpoint. No operational Research OS, Oracle/OCI, hypothesis, validation, task, queue, authority, or Legacy state is modified.

## 1. Real current-lineage collision: two ASML freezes on the same day

Economic snapshot reviewed:

`ac3b32ffa8ff4d768525c6da2a7ae3f9e2cdddc7`

Frozen lineage A:

`research/research_os/hypotheses/FUND-ASML-CAPACITY-SERVICE-001.json`

- hypothesis id: `FUND-ASML-CAPACITY-SERVICE-001`
- generation id: `G1`
- frozen at: `2026-10-15T13:14:30Z`
- mechanism core: stated 2027-2028 demand above planned ASML supply + Installed Base Management productivity upgrades; scarcity plus installed-base monetization may sustain revenue/margin economics.

Frozen lineage B:

`research/research_os/hypotheses/FUND-ASML-CAPACITY-PRICING-001.json`

- hypothesis id: `FUND-ASML-CAPACITY-PRICING-001`
- generation: `1`
- frozen at: `2026-10-15T19:14:00Z`
- thesis core: stated 2027-2028 demand above planned ASML supply + installed-base productivity-upgrade demand; scarcity plus installed-base monetization may support pricing/mix and medium-term revenue/margin durability.

Chronology:

`SERVICE` existed first; `PRICING` was frozen approximately six hours later.

The second lineage's own falsification contract says it should be rejected if duplicative of Legacy, but neither its frozen hypothesis nor its independent validation identifies the already-frozen `SERVICE` lineage.

Forensic classification:

`ASML_CURRENT_LINEAGE_NEAR_DUPLICATION = PROVEN`

This classification is semantic/economic, not a claim that the two JSON objects are byte-identical.

## 2. Independent validation did not reconcile the two ASML lineages

Service assessment:

`research/research_os/assessments/VALIDATE-FUND-ASML-CAPACITY-SERVICE-001.json`

Decision:

`PASS_BOUNDED_BUSINESS_MECHANISM_WITH_BLOCK_CLAIM_LEVEL`

Pricing assessment:

`research/research_os/assessments/VALIDATE-FUND-ASML-CAPACITY-PRICING-001.json`

Verdict:

`PASS_BOUNDED_CAPACITY_SCARCITY_MECHANISM_WITH_BLOCK_CLAIM_LEVEL`

Both validators independently preserve essentially the same bounded economic mechanism: ASML planned supply scarcity plus installed-base productivity-upgrade monetization, with stronger pricing/margin/return extensions blocked.

The later `PRICING` validation does not cite or reconcile `FUND-ASML-CAPACITY-SERVICE-001`.

Therefore the validator layer did not operate as a current-frozen-lineage deduplication gate in this real case.

## 3. The two frozen hypotheses do not share one canonical schema

The real frozen objects are not represented with a common candidate schema:

`SERVICE` uses fields including:

- `generation_id`
- `mechanism`
- `claim`
- `decision_map`
- `freeze_status`

`PRICING` uses fields including:

- `generation`
- `thesis`
- `causal_chain`
- `test_contract`
- `status`
- `source_artifact`

This is not merely cosmetic. The current economic-identity constructor in:

`research/research_os/expansion/final_shape.py`

expects an `engine_output` object containing:

`engine_output["candidate"]`

and directly reads canonical candidate fields such as:

- `candidate["hypothesis_id"]`
- `candidate["generation_id"]`
- `candidate["mechanism"]`

Therefore the two frozen ASML JSON documents cannot simply be supplied as-is to `economic_identity_v1()` and compared by Portfolio v2.

In the canonical paths reviewed for this audit, no contract was found that first enumerates all frozen hypothesis JSON files and normalizes these heterogeneous historical/current schemas into peer economic identities before readiness.

Forensic classification:

`CURRENT_FROZEN_HYPOTHESIS_SCHEMA_UNIFIED_FOR_PORTFOLIO = FALSE`

`CURRENT_FROZEN_SET_AUTO_NORMALIZED_TO_PEER_IDENTITIES = NOT_PROVEN`

## 4. Economic readiness does not load the current frozen hypothesis set

Canonical composition reviewed:

`research/research_os/expansion/economic_test_readiness_v1.py`

The readiness function receives:

`economic_test_readiness(package, *, legacy, frozen=None, peer_identities=(), ...)`

Its identity/portfolio path is:

1. read the current package's `engine_output`;
2. build the current identity with `economic_identity_v1(output, ...)`;
3. call:
   `portfolio_diagnostics_v2([identity, *deepcopy(list(peer_identities))])`.

It does not itself enumerate:

`research/research_os/hypotheses/`

and does not itself transform all already-frozen hypotheses into `peer_identities`.

Therefore current-lineage collision detection depends on the caller/worker supplying a complete and correctly normalized peer set.

Forensic classification:

`ECON_READINESS_CURRENT_FROZEN_SET_AUTOLOAD = FALSE`

`PEER_IDENTITY_COMPLETENESS_CALLER_DEPENDENT = TRUE`

## 5. Queue replenishment does not populate Portfolio peers

`research/research_os/queue_replenisher.py`:

- derives at most one bounded producer task;
- requires `legacy_gate_required = true`;
- preserves closed authority;
- prevents duplicate derivation keys.

It does not:

- enumerate existing frozen hypotheses;
- build economic identities;
- create Portfolio peer identities;
- enforce semantic deduplication against the current frozen set.

A duplicate derivation key protects deterministic task derivation, not economic-thesis uniqueness.

Therefore:

`QUEUE_DERIVATION_DEDUP_EQUALS_ECONOMIC_DEDUP = FALSE`

## 6. Scheduled-worker protocol states the responsibility but not the binding

`research/research_os/runtime/SCHEDULED_WORKER_PROTOCOL.md` assigns the `integrator_portfolio` lane responsibility for:

- economic identity;
- overlap mapping;
- Portfolio Map;
- shadow readiness.

However, the reviewed protocol does not specify a deterministic contract that every integration wake must:

1. enumerate the complete current frozen hypothesis set;
2. normalize every supported schema/version;
3. bind that normalized set/hash into the readiness package;
4. supply every other relevant current lineage as `peer_identities`;
5. fail closed if any frozen lineage cannot be normalized.

Thus responsibility exists, but completeness is not mechanically bound by the reviewed readiness interface.

Forensic classification:

`INTEGRATOR_PORTFOLIO_PEERSET_COMPLETENESS_CONTRACT = NOT_PROVEN`

## 7. Portfolio v2 overlap detection is diagnostic, not a readiness blocker

Modern Portfolio implementation reviewed:

`research/research_os/expansion/portfolio_v2.py`

`structural_pair()` can emit:

`HIGH_STRUCTURAL_OVERLAP_REVIEW`

and:

`same_exposure_review_required = True`

for sufficiently overlapping structural identities.

`portfolio_diagnostics_v2()` exposes those pairs in:

`same_exposure_review_pairs`

but it does not raise/block on their presence. Its explicit hard duplicate check only rejects multiple selected generations carrying the same exact `hypothesis_id`.

The more important integration fact is in:

`research/research_os/expansion/economic_test_readiness_v1.py`

After Portfolio is computed:

`portfolio = portfolio_diagnostics_v2(...)`

readiness is determined by:

`ready = not reasons`

No Portfolio overlap/review condition is appended to `reasons` before that decision.

Therefore even a peer pair that Portfolio successfully marks for same-exposure review does not, by itself, make economic readiness return `BLOCK`.

Forensic classification:

`PORTFOLIO_OVERLAP_REVIEW_BLOCKS_ECONOMIC_READINESS = FALSE`

## 8. Tests confirm warning semantics rather than blocking semantics

`research/research_os/tests/test_economic_identity_portfolio_readiness.py` explicitly verifies that a same payer + same mechanism + same timing clock pair emits:

`HIGH_STRUCTURAL_OVERLAP_REVIEW`

with:

`same_exposure_review_required = True`

The suite verifies detection, provenance, absence of empirical-correlation fabrication, and authority closure.

It does not assert that such a review blocks portfolio construction.

`research/research_os/tests/test_economic_readiness_integration.py` separately verifies that readiness can remain:

`READY_FOR_AUTHORIZED_ECONOMIC_TEST`

while a supplied structural peer shares the current candidate's mechanism/payer information. The Portfolio output remains diagnostic and does not enter the readiness blocker set.

This is consistent with the source-level control flow above.

## 9. Exact ASML end-to-end replay limitation

A literal executable call of the form:

`portfolio_diagnostics_v2([ASML_SERVICE_FROZEN_JSON, ASML_PRICING_FROZEN_JSON])`

would not be a valid replay of the canonical interface because the frozen documents are heterogeneous hypothesis records, not both canonical `economic_identity_v1` outputs.

This checkpoint therefore does **not** fabricate a normalized ASML pair and does not claim a repository execution that was not performed.

Instead, the stronger architectural fact is recorded:

- the real collision exists in frozen state;
- the canonical readiness path does not auto-load that state;
- the real frozen objects are not schema-unified for direct identity construction;
- peer completeness is caller-dependent;
- even a detected Portfolio review is not wired into `reasons` and therefore is not a readiness blocker.

Consequently the current architecture cannot prove that the later ASML lineage would have been blocked by Portfolio.

## 10. Current verdict

- `ASML_CURRENT_LINEAGE_NEAR_DUPLICATION = PROVEN`
- `ASML_SECOND_FREEZE_AFTER_FIRST = PROVEN`
- `ASML_SECOND_VALIDATION_RECONCILED_FIRST_LINEAGE = FALSE`
- `CURRENT_FROZEN_HYPOTHESIS_SCHEMA_UNIFIED_FOR_PORTFOLIO = FALSE`
- `CURRENT_FROZEN_SET_AUTO_NORMALIZED_TO_PEER_IDENTITIES = NOT_PROVEN`
- `ECON_READINESS_CURRENT_FROZEN_SET_AUTOLOAD = FALSE`
- `PEER_IDENTITY_COMPLETENESS_CALLER_DEPENDENT = TRUE`
- `QUEUE_DERIVATION_DEDUP_EQUALS_ECONOMIC_DEDUP = FALSE`
- `INTEGRATOR_PORTFOLIO_PEERSET_COMPLETENESS_CONTRACT = NOT_PROVEN`
- `PORTFOLIO_OVERLAP_REVIEW_BLOCKS_ECONOMIC_READINESS = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`
- `ORACLE_AUTONOMOUS_ACTIVATION_SAFE = FALSE`

## 11. Required remediation acceptance criteria — audit proposal only

Before autonomous Oracle candidate production can be considered scientifically restart-safe, a future implementation should prove at minimum:

1. **Current-state corpus binding**
   - enumerate every frozen/current CandidateHypothesis lineage from a canonical registry or manifest;
   - bind the corpus hash/snapshot into the worker/readiness receipt.

2. **Schema normalization or fail-closed behavior**
   - canonicalize every supported hypothesis schema into one economic-identity input contract;
   - block new freeze/integration if any relevant frozen lineage cannot be normalized.

3. **Legacy + current-frozen screening**
   - screen new candidates against both the reconciled historical Legacy corpus and the current frozen corpus;
   - exact ID checks are insufficient.

4. **Economic-mechanism normalization**
   - compare canonical mechanism/actor/payer/instrument/clock/exposure fields rather than relying only on exact prose equality;
   - preserve provenance and never invent missing evidence.

5. **Unresolved same-exposure review must be gating**
   - a `HIGH_STRUCTURAL_OVERLAP_REVIEW` or equivalent unresolved same-exposure finding must prevent an independent-lineage `READY_FOR_AUTHORIZED_ECONOMIC_TEST` result;
   - continuation should require either a documented same-lineage/new-generation relation or an explicit, auditable distinctness resolution.

6. **ASML regression fixture**
   - the real `SERVICE` / `PRICING` pair should become a regression fixture proving that semantically overlapping current lineages cannot independently pass unnoticed.

7. **Authority closure remains unchanged**
   - none of this authorizes outcome access, prospective observation, capital allocation, orders or live trading.

These are acceptance criteria only. This audit checkpoint intentionally does not implement them on operational branches.

## Next forensic work

1. Convert the remediation criteria above into a precise audit-only acceptance/test matrix (CP8).
2. Audit Oracle/OCI branches for the proven Legacy materialization preflight and current-frozen peer-set handling.
3. Build an audit-only Legacy-v2/PR#1 crosswalk without mutating historical verdicts.
4. Only after those checks, return to the Oracle recovery branch and implement CP1/CP2 against the proven contracts.
