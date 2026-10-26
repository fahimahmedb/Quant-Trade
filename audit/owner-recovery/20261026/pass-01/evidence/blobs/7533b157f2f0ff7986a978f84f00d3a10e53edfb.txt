# Forensic Audit Continuation — Checkpoint 005

Date: 2026-10-19
Audit branch: `audit/forensic-checkpoint-20261019`
Parent audit head: `7fb2c653dac077c1a4176d8b33c2a80ce50dc9cd`
Status: `PARTIAL_IN_PROGRESS`

## Purpose

Freeze two findings before any Oracle/OCI runtime integration proceeds:

1. the semantic crosswalk between PR #1 scientific history and every currently frozen Research OS hypothesis visible at the UST branch head;
2. the actual runtime state of the pinned Legacy anti-restart gate.

This checkpoint is audit-only. It changes no operational Research OS state, no Legacy ledger, no workflow, no scheduler, no economic result and no authorization.

## 1. Current Research OS hypothesis set reviewed

Reference:

`builder/econ-test-flow-ust-auction-20261019`

Head:

`ac3b32ffa8ff4d768525c6da2a7ae3f9e2cdddc7`

The complete `research/research_os/hypotheses/` directory at that head contains 13 hypotheses:

1. `EVENT-DUEBILL-LARGE-DIST-001`
2. `EVENT-FDA-ADCOM-BRIEFING-CLOCK-001`
3. `EVENT-SCHEDULE13D-DISCLOSURE-CLOCK-001`
4. `EVENT-STAPLED-CVR-PRV-001`
5. `FLOW-ADR-TERM-001`
6. `FLOW-RUSSELL-RECON-CLOSE-001`
7. `FLOW-UST-PRIMARY-DEALER-AUCTION-001`
8. `FUND-ASML-CAPACITY-PRICING-001`
9. `FUND-ASML-CAPACITY-SERVICE-001`
10. `FUND-TSMC-N2-MARGIN-LEARNING-001`
11. `QUANT-CLOSE-AUCTION-IMBALANCE-001`
12. `QUANT-FORM144-SUPPLY-001`
13. `QUANT-LETF-DAILY-RESET-001`

All 13 files were read individually for this checkpoint.

A machine-readable crosswalk is frozen in:

`PR1_RESEARCH_OS_CROSSWALK.json`

at commit:

`7fb2c653dac077c1a4176d8b33c2a80ce50dc9cd`

## 2. PR #1 crosswalk result

Against the audit-side PR #1 semantic identity map:

- exact PR #1 duplicates observed: **0**
- same-mechanism/different-expression duplicates observed: **0**
- related exposure / materially different mechanism: **3**
- distinct from reviewed PR #1 families: **10**

### Related exposure / different mechanism

#### `QUANT-LETF-DAILY-RESET-001`

PR #1 has heavily spent leveraged-exposure / volatility-drag / vol-targeting surfaces. The current candidate is materially different because its causal mechanism is product-mandated daily leverage reset and associated pre-close hedge/rebalance flow rather than an overlay or portfolio-risk-targeting rule.

Classification:

`RELATED_EXPOSURE_DIFFERENT_MECHANISM`

PR #1 history is still mandatory negative/multiplicity context. The candidate must not be called a pristine first look at leveraged-exposure economics.

#### `QUANT-CLOSE-AUCTION-IMBALANCE-001`

PR #1 contains substantial close/calendar/reversal research. The current candidate instead uses exchange-published pre-cross imbalance, paired liquidity and indicative/reference-price state as the proposed treatment.

Classification:

`RELATED_EXPOSURE_DIFFERENT_MECHANISM`

Index-rebalance and month/quarter-end sessions are explicit confounders in the candidate itself, which reinforces the need to carry historical calendar/flow evidence into the identity review.

#### `FLOW-RUSSELL-RECON-CLOSE-001`

PR #1 contains calendar, month-end and cross-market/index research. The current candidate is instead a forced benchmark-membership implementation flow concentrated into an effective close.

Classification:

`RELATED_EXPOSURE_DIFFERENT_MECHANISM`

Historical calendar effects do not prove or falsify Russell reconstitution alpha, but they are part of spent close/calendar exposure context and multiplicity accounting.

### Distinct current hypotheses

The reviewed PR #1 families do not contain a material exact mechanism for:

- due-bill distribution entitlement;
- FDA advisory-committee briefing-document release clock;
- Schedule 13D control-intent disclosure clock;
- stapled CVR attached to continuing common equity;
- ADR termination residual forced sale;
- U.S. Treasury primary-dealer auction participation constraint;
- ASML company-specific lithography scarcity/service economics;
- TSMC N2 node-ramp learning/margin economics;
- Form 144 proposed affiliate-sale supply.

`DISTINCT` here means distinct from the reviewed PR #1 map. It is not a statement that all reachable repository history has been completely reconciled.

## 3. Intra-Research-OS collision: ASML

A separate issue was found inside the current 13-hypothesis set.

Members:

- `FUND-ASML-CAPACITY-PRICING-001`
- `FUND-ASML-CAPACITY-SERVICE-001`

Both are G1-style frozen ASML theses with no explicit parent-child relation. Both use the same two-channel causal core:

1. planned 2027-2028 leading-edge lithography supply below stated customer demand;
2. Installed Base Management / productivity upgrades as an additional monetization channel.

The names and some framing differ, but the economic core is highly overlapping.

Forensic classification:

`PROBABLE_SAME_CORE_LINEAGE_DUPLICATE_NEEDS_OWNER_INTEGRATOR_REVIEW`

Risk:

- count one economic thesis twice as independent discovery;
- inflate later trial/learning counts;
- overstate portfolio diversification;
- create conflicting descendants from two nominal G1 roots.

Audit action:

- do not delete, merge or rewrite either during forensic audit;
- require an explicit canonical lineage reconciliation later.

## 4. Legacy anti-restart gate code

Modern file:

`research/research_os/legacy.py`

Reference:

`d0dc70f5dd71f3e6cb8097d2f15807bb99ebc8ec`

### Exact-ID path

The gate blocks an exact candidate `hypothesis_id` matching either legacy `HYPOTHESIS_ID` or `LEGACY_ID_IF_ANY`.

This is strong for literal identity reuse.

### Non-exact path

The fallback similarity check tokenizes:

Candidate:

- `mechanism`
- `economic_tags`

Legacy record:

- `MECHANISM`
- `TITLE`
- `RESEARCH_FAMILY_ID`

It then computes plain token-set Jaccard overlap and flags review only when:

`overlap >= 0.30`

Tokens are lowercase alphanumeric strings of length >=3.

The algorithm does **not** compare normalized structural identity such as:

- payer / forced actor;
- constraint;
- instrument or base exposure;
- universe;
- clock;
- horizon;
- capacity bottleneck;
- cost structure;
- event/rule dependency;
- historical sample identity;
- parent/descendant lineage;
- trial-family membership.

Forensic classification:

`TOKEN_SIMILARITY_NOT_SUFFICIENT_FOR_SEMANTIC_ANTI_RESTART`

This is especially weak when a long candidate mechanism paragraph is compared with a short legacy title/family label: semantically related candidates can have very low or even zero literal token overlap.

## 5. More serious defect: the runtime Legacy ledger is absent

The code's default loader looks for:

`research/research_os/legacy/LEGACY_RESEARCH_LEDGER.imported.json`

If the file does not exist:

- `ledger` remains `None`;
- the constructor substitutes `{"records": []}`;
- `self.records` becomes empty;
- `self.by_id` becomes empty.

There is no fail-closed check that the number of loaded records matches the manifest.

### Tree evidence

At modern ref `d0dc70f...`, the directory:

`research/research_os/legacy/`

contains only:

`source_manifest.json`

The imported ledger file is absent.

A path-specific commit-history query for:

`research/research_os/legacy/LEGACY_RESEARCH_LEDGER.imported.json`

on the modern lineage returns no commits.

A recursive tree search at `d0dc70f...` finds no `LEGACY_RESEARCH_LEDGER*` path anywhere in that tree.

### Manifest contradiction

`source_manifest.json` declares:

- source branch `research/legacy-economic-reconciliation-20261015`
- source commit `183ad65ff260b903a16548ce37948f54d47a9ec8`
- ledger blob SHA `ba9b165aaf96956776672df51233bb9bf1e6cbc9`
- `historical_research_items_found = 33`
- `known_duplicate_or_variant_items = 17`
- `reconciliation_status = PARTIAL_WITH_EXPLICIT_GAPS`
- `prospective_validated = 0`
- `global_effective_trials = UNKNOWN`
- `import_policy = READ_ONLY_PINNED_SOURCE`

But those 33 records are not present in the modern runtime directory.

## 6. Runtime consequence

Unless a caller supplies a separate external `imported_ledger_path` that actually exists, the modern `LegacyKnowledgeBase` loads zero records.

The reviewed multi-engine pipeline constructs an imported-ledger path under the same `legacy/` directory and only passes it when it exists; otherwise the loader falls back to the same absent default path.

Therefore, for the repository-contained modern pipeline state:

`LEGACY_LOADED_RECORD_COUNT_EXPECTED_FROM_TREE = 0`

and the gate can trivially return no exact conflict because it has no records to screen.

This is **not** merely weak semantic matching. It is an unpopulated automated anti-restart gate.

Important distinction:

- some historical/current hypotheses contain durable `legacy_distinctness` notes that may reflect a human/agent reading of the external pinned 33-item ledger;
- this finding does **not** retroactively prove those manual screenings were false;
- it proves the repository-contained automated `LegacyKnowledgeBase.load()` path is not carrying the ledger records it claims to pin.

## 7. Fail-open behavior

The absence of the ledger does not raise an exception.

Instead, code silently initializes an empty record set.

Forensic classification:

`LEGACY_GATE_MISSING_LEDGER_BEHAVIOR = FAIL_OPEN`

A safer anti-restart invariant would require a future repair to refuse screening when the manifest claims historical records but zero records are loaded. This audit does not implement that repair.

## 8. Test/CI interpretation

The aggressive architecture tests confirm synthetic authority boundaries and deterministic replay, but they are not evidence that the real Legacy ledger is populated.

The aggressive final-shape pipeline shown in the reviewed code does not itself establish a loaded historical ledger as a PASS precondition.

Therefore a green architecture/simulation CI must not be cited as proof of scientific anti-restart completeness.

## 9. Severity

This finding directly affects the autonomous-loop safety case:

`ANTI_RESTART_GATE_RUNTIME_POPULATED = FALSE`

`ANTI_RESTART_GATE_FAIL_CLOSED_ON_MISSING_LEDGER = FALSE`

`ANTI_RESTART_GATE_SEMANTICALLY_COMPLETE = FALSE`

Because the external-worker architecture is designed to derive new work from a bounded frontier and screen candidates against Legacy before freeze, an empty fail-open Legacy store can permit an old mechanism to re-enter as apparently novel.

The risk becomes larger, not smaller, once PR #1's 111 completed non-ML cycles are considered, because those cycles are not represented by the pinned 33-item runtime manifest either.

## 10. Oracle implication

Oracle/OCI autonomous activation remains blocked.

Even if OCI wake/restart mechanics were perfect, attaching an always-on wake trigger to a system whose scientific-memory gate is empty by default would increase the probability of repeated historical research under aliases.

Correct order is:

1. complete forensic memory reconciliation;
2. define canonical durable authority precedence;
3. restore/populate and fail-close the Legacy gate under an explicitly authorized repair;
4. verify semantic structural identity handling and ASML lineage reconciliation;
5. only then connect Oracle wake infrastructure to the existing external-agent workflow contract.

## Current verdict

- `CURRENT_HYPOTHESES_REVIEWED = 13`
- `EXACT_PR1_DUPLICATES_OBSERVED = 0`
- `RELATED_EXPOSURE_DIFFERENT_MECHANISM = 3`
- `DISTINCT_FROM_REVIEWED_PR1 = 10`
- `INTRA_RESEARCH_OS_PROBABLE_DUPLICATE_GROUPS = 1`
- `LEGACY_MANIFEST_HISTORICAL_ITEMS = 33`
- `LEGACY_RUNTIME_LEDGER_FILE_PRESENT = FALSE`
- `LEGACY_RUNTIME_LOADED_RECORDS_EXPECTED = 0`
- `LEGACY_MISSING_LEDGER_FAIL_CLOSED = FALSE`
- `ANTI_RESTART_GATE_PROVEN_EFFECTIVE = FALSE`
- `PR1_OPERATIONAL_LEDGER_MIGRATION_AUTHORIZED = FALSE`
- `AUTHORITY_PRECEDENCE_CONFLICT = TRUE`
- `ORACLE_AUTONOMOUS_ACTIVATION_SAFE = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

## Next forensic work

1. Trace why the 33-item ledger blob was referenced in the manifest but not imported into the modern runtime tree.
2. Check historical branches/commits for any alternative loader, checkout step, CI artifact or external source-fetch convention that intentionally supplied the ledger at runtime.
3. Crosswalk the remaining non-branch PR #1 scientific identities into a proposed read-only migration package, still without mutating operational memory.
4. Audit current `economic_identity` / portfolio deduplication against the ASML collision and PR #1 structural families.
5. Keep Oracle integration fail-closed until the memory and authority blockers are resolved.
