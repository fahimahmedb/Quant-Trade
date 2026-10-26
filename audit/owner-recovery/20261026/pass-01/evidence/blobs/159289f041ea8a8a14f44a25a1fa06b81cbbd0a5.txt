# W1 MEMORY FINAL — 2026-10-21

STATUS: FINAL_SCOPED_FRONTIER_EXHAUSTED

BASE_SHA: `fecd09e0839f1208d9f876c311331221bde3ab7d`
PRE_FINAL_CODE_HEAD_SHA: `4e412e9d0969d0b37ad50d005eb9bf74760c1854`
FINAL_HEAD_SHA: `SELF` — this file is committed in the final metadata-only seal commit; resolve the exact SHA from `builder/w1-scientific-memory-depth-20261021`. No code changes follow this checkpoint.
MODULE_SCOPE: W1-MEMORY — archaeology -> scientific memory -> canonical reusable research knowledge.

## CAPABILITIES_QUALIFIED

- Canonical fail-closed `scientific-memory-v1` representation for NEGATIVE, BLOCKED, UNEXECUTED, POSITIVE_BUT_INSUFFICIENT, INVALIDATED_PROTOCOL, SCIENTIFIC_MEMORY_ONLY, and REVIEW_STILL_REQUIRED.
- Explicit separation of scientific disposition, epistemic status, claim ceiling, record/governance status, evidence and provenance.
- Existing `AppendOnlyHashLedger` reused as the only scientific truth store; canonical memory appends through it.
- Semantic identity and deterministic memory identity independent of branch/path names.
- Canonical-memory validation requiring sufficient semantic identity and non-Owner historical provenance.
- Query/facet retrieval for mechanism, payer, constrained actor, clock, universe, instrument, evidence identity, failure reason, protocol weakness, source family and economic exposure.
- Structural retrieval explicitly separated from empirical similarity/correlation; empirical correlation remains `UNKNOWN`.
- Proof-required supersession preserving original provenance.
- Owner governance can govern interpretation without overwriting scientific evidence.
- `LegacyKnowledgeBase` hardened so current Research OS consumers receive canonical memory semantics; raw legacy `RESULT` is retained only as non-authoritative compatibility context.
- Exact legacy duplicate anti-restart behavior remains compatible with `canonical_spine` through `BLOCK_EXACT_LEGACY_DUPLICATE`.
- Immutable provenance-only archaeology contract. Branch names alone cannot qualify history.
- Identity-safe archaeology -> memory binding that can append immutable provenance only and cannot mutate evidence/disposition/epistemic status/claim ceiling/semantic identity.
- F2 blocked-pre-look history qualified as BLOCKED / UNKNOWN, never negative.
- F1 Stage A and Stage B historical report provenance qualified as distinct immutable generations.
- Weather V2 independent re-audit qualified specifically as outcome-blind protocol-review provenance, not as economic-result evidence.

## CAPABILITIES_PARTIAL

- F1 Stage A/B canonical structured memory import: immutable reports are qualified, but no matching structured F1 record exists in the pinned legacy ledger. Manual report-to-truth reconstruction was intentionally not introduced.
- Box Office: primary result artifact unrecovered in pinned reconciliation; review-only.
- MLB/Soccer/Weather secondary replication: primary replication artifact unrecovered in pinned reconciliation; review-only. Weather protocol artifacts cannot substitute for this identity.
- EURUSD frozen quote proxy: mission-known UNEXECUTED/UNKNOWN semantics preserved, but no immutable repository artifact was recovered in bounded archaeology.
- V1 causal-timing invalidation: nearby V1-era memory exists, but the exact named causal-timing artifact was not recovered; no substitution was made.
- Institutional / Forced Flows: structural mechanism retained only as structural memory; no qualified empirical-result artifact was recovered.

## CAPABILITIES_REUSED

- `research/research_os/scientific_store.py` / `AppendOnlyHashLedger` — REUSE_CURRENT.
- Existing `LegacyKnowledgeBase` — HARDEN_EXISTING.
- Existing `negative-knowledge.schema.json` — retained for genuine negative-only knowledge; not generalized into a parallel ontology.
- Existing exact duplicate status consumed by canonical spine — REUSE_CURRENT as anti-restart control only.
- Pinned legacy reconciliation commit/blob — REUSE_CURRENT as read-only history source.
- Historical append-only memory principle — ADAPT_EXISTING into current scientific ledger.

## CAPABILITIES_IMPORTED

None as a standalone historical subsystem. Historical separate memory/learning stores were not imported because they would duplicate truth storage or mix scientific result with allocation/prioritisation behavior.

## NO_BUILD_DECISIONS

- No second scientific truth store.
- No second Candidate/Research Core.
- No new scheduler/orchestration authority.
- No empirical similarity/correlation engine in W1-MEMORY.
- No source acquisition or producer rebuild.
- Event/Documents producer logic: NO_BUILD_REQUIRED in this lane; memory only preserves the rule that public timestamp + causal transfer + reaction are required and DOCUMENT_CHANGE != EDGE.
- No manual canonicalization of unrecovered historical conclusions from Owner summaries or report prose when a structured evidence identity is absent.

## HISTORICAL_SOURCES_USED

- North Star blob `a328b4e6d7d71dafd532938888ebf9818b1b610f`.
- Pinned reconciliation commit `183ad65ff260b903a16548ce37948f54d47a9ec8`, ledger blob `ba9b165aaf96956776672df51233bb9bf1e6cbc9`.
- F1 Stage A report blob `c83a9cf0eca3edf44c81beec9c791fc99becd073`.
- F1 Stage B report blob `cceb75f9623a14e094fd6eaab19a587b480135c3`.
- Weather V2 independent re-audit blob `957d28e7e923c210729a934d61174430f78b0a58`, exact audited candidate commit `94b59348d5b79cd3c53dcba0b791ce1daeb75d60`.
- Nearby V1 `research/memory.jsonl` blob `79ab74c28c05c7cfd688ecdfe1c41dcc4c773717`, explicitly not sufficient proof for the named causal-timing history.
- Historical Research Factory memory/learning implementations reviewed and superseded as implementation sources; no parallel store imported.

## FILES_CHANGED

Added:
- `research/research_os/scientific_memory.py`
- `research/research_os/contracts/scientific-memory.schema.json`
- `research/research_os/archaeology.py`
- `research/research_os/legacy/archaeology_source_catalog.json`
- `research/research_os/memory_archaeology_bridge.py`
- `research/research_os/tests/test_scientific_memory.py`
- `research/research_os/tests/test_legacy_scientific_memory.py`
- `research/research_os/tests/test_archaeology.py`
- `research/research_os/tests/test_memory_archaeology_bridge.py`
- W1 checkpoint files and this FINAL checkpoint / integration manifest.

Modified:
- `research/research_os/legacy.py`
- `research/research_os/tests/contract-smoke.test.mjs` — baseline coverage preserved; only the scientific-memory schema was added to the contract inventory.

## SHARED_SURFACES_TOUCHED

- `research/research_os/legacy.py`: required because this is the current historical ingress used by canonical spine.
- `research/research_os/tests/contract-smoke.test.mjs`: additive schema parse coverage only.

WHY_REQUIRED: later Search/Prioritisation must consume historical truth through current Research OS contracts rather than raw strings or branch-name archaeology.

EXPECTED_CROSS_LANE_IMPACT: Search/Prioritisation can consume canonical memory and archaeology qualification. Canonical spine exact-duplicate behavior remains stable. No producer/orchestrator authority changed.

## PUBLIC_CONTRACTS_CHANGED

Additive public contract: `scientific-memory-v1` plus additive Python query/archaeology/binding APIs. No existing canonical-spine status removed or renamed.

## SCHEMAS_CHANGED

Added `research/research_os/contracts/scientific-memory.schema.json` (JSON Schema Draft 2020-12). No existing schema was weakened.

## TESTS_ADDED

34 focused/adversarial Python tests across scientific memory, legacy integration, archaeology and archaeology-memory binding.

## FOCUSED_TEST_RESULT

PASS — 34/34 tests.

Also PASS:
- Python compilation of `scientific_memory.py`, `legacy.py`, `archaeology.py`, `memory_archaeology_bridge.py`, `scientific_store.py`.
- `scientific-memory-v1` Draft 2020-12 schema validation.
- Tamper detection through existing hash ledger.

## BROADER_TEST_RESULT

PASS for the broadest practical W1 compatibility regression available in this environment:
- cumulative 34-test lane suite;
- current canonical-spine contract inspected at branch head and confirmed to consume only `legacy_screen["status"] == "BLOCK_EXACT_LEGACY_DUPLICATE"`, which remains preserved;
- baseline contract-smoke test file restored/preserved with only additive scientific-memory schema inventory change;
- base-to-head compare is linear (`behind_by=0`) with no Wave-1 merge/rebase.

Limitation: the repository-wide hosted Research OS workflows are branch-filtered to historical builder branches, and a full network clone/hosted W1 CI run was unavailable from this execution environment. No broader test result is fabricated.

## SCIENTIFIC_CLAIM_LIMITS

- This lane creates no economic result and establishes no profitability or edge.
- No prospective observation, real capital, live trading or new economic experiment is authorized.
- BLOCKED and UNEXECUTED remain epistemically UNKNOWN.
- Protocol invalidation is not converted into economic failure.
- Positive-but-insufficient history is capped at `SIGNAL_NOT_PROOF`.
- Structural mechanism is not empirical success.
- Structural overlap is not empirical similarity/correlation.
- Missing provenance remains missing; no raw historical bytes, provider identity or outcome proof were fabricated.

## DEPENDENCIES_ON_OTHER_LANES

- Search/Prioritisation may consume W1 memory/query hooks but is not implemented here.
- Source acquisition / historical recovery is required to upgrade unrecovered Box Office, MLB/Soccer/Weather, EURUSD, and named V1 artifacts.
- No dependency on another Wave-1 builder branch was introduced.

## EXPECTED_INTEGRATION_CONFLICTS

Likely shared-file conflict surfaces:
- `research/research_os/legacy.py`
- `research/research_os/tests/contract-smoke.test.mjs`

Resolution rule: preserve the W1 semantic guarantees (raw result non-authoritative, exact duplicate status compatibility, UNKNOWN fail-closed semantics) while incorporating unrelated concurrent additions. New W1 modules are otherwise additive.

## REMAINING_GAPS

1. F1 Stage A/B structured canonical memory records absent from pinned legacy ledger.
2. Box Office primary artifact unrecovered.
3. MLB/Soccer/Weather primary replication artifact unrecovered.
4. EURUSD immutable frozen-proxy artifact unrecovered.
5. Exact V1 causal-timing invalidation artifact unrecovered.
6. Forced-flow empirical evidence identity unrecovered; structural memory only.
7. Full hosted repository-wide CI on this W1 branch not available in this execution environment.

## REMAINING_GAP_CLASSIFICATION

1. F1 structured import — PARTIAL_WITH_EXPLICIT_BLOCKER / REVIEW_STILL_REQUIRED; artifact provenance qualified, but no admissible structured current record. Manual truth reconstruction rejected.
2. Box Office — PARTIAL_WITH_EXPLICIT_BLOCKER / EXTERNAL_ACCESS_REQUIRED for primary artifact recovery.
3. MLB/Soccer/Weather — PARTIAL_WITH_EXPLICIT_BLOCKER / EXTERNAL_ACCESS_REQUIRED for primary artifact recovery.
4. EURUSD — PARTIAL_WITH_EXPLICIT_BLOCKER / REVIEW_STILL_REQUIRED; further history recovery required.
5. V1 causal timing — PARTIAL_WITH_EXPLICIT_BLOCKER / REVIEW_STILL_REQUIRED; exact artifact required.
6. Forced Flows — PARTIAL_WITH_EXPLICIT_BLOCKER; structural-only until empirical artifact exists.
7. Hosted full CI — EXTERNAL_ACCESS_REQUIRED; focused/current-contract regression is green.

## AUTHORITY_STATUS

- ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
- PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
- REAL_CAPITAL_AUTHORIZED=FALSE
- LIVE_TRADING_AUTHORIZED=FALSE
- OUTCOME_ACCESSED=FALSE for new/prospective outcomes in this mission.

SAFE_TO_INTEGRATE: TRUE, subject to normal shared-file conflict resolution and the explicit broader-CI limitation above.

SAFE_TO_CONTINUE_THIS_MODULE: FALSE for autonomous W1 build under current evidence. Remaining work requires recovered external/historical artifacts, structured evidence from another source, or broader CI access; continuing to invent abstractions would violate the history-first/no-second-store constraints.
