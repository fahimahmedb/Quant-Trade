# SCIENTIFIC MEMORY INDEX — 2026-10-20

Authority: CP12 repository audit.

Purpose: define the minimum durable scientific memory that must survive branch/PR cleanup. This is an index, not a re-analysis and not an upgrade of evidence quality.

## Rules

For every imported historical item preserve, when available:

- original branch/commit/result hash;
- family/candidate identity;
- exposure/look status;
- data/source provenance and PIT caveats;
- protocol/harness identity;
- outcome/status: PASS / FAIL / REJECT / KILL / BLOCKED / UNEXECUTED / UNKNOWN;
- whether result was discovery, validation, prospective, shadow or other;
- multiplicity/family context;
- limitations and any authority explicitly NOT granted.

Historical evidence is immutable. V2 may normalize/index it but must not rewrite the original conclusion.

A negative result is valuable memory. A blocked study is valuable memory. An unexecuted frozen protocol is valuable memory. UNKNOWN must remain UNKNOWN.

---

## 1. F1 crypto carry family

Evidence chain currently exposed through PR #24 → #25 → #26.

### Acquisition / Stage A input

- PR #24
- durable capture completed and independently verified
- raw archives remain outside Git
- classification: `ACQUISITION_EVIDENCE`

### Stage A discovery

- PR #25
- selected theta: 0.20
- annualised mean: 3.823%
- Sharpe: 0.490
- robust t: 0.957
- doubled-cost mean: 1.114%
- result remained discovery information, not sealed confirmation
- classification: `DISCOVERY_RESULT`

### Stage B fixed-family verdict

- PR #26
- annual arithmetic mean: -1.356922%
- Sharpe: -0.448546
- doubled-cost mean: -2.957394%
- `FAMILY_STATUS = REJECT`
- fixed tested expression/target rejected
- A/B must not be rerun merely to repair publication
- classification: `FINAL_NEGATIVE_RESULT`

V2 import requirement:

`F1_REJECT` must be represented in negative knowledge with exact source SHA/result hash/harness lineage and no reset via a new branch or renamed family.

---

## 2. F2 research access

- PR #27
- status: `BLOCKED_DATA_PERMISSION`
- official terms did not clear the intended credential-free historical research route
- no statistical look consumed
- no paid/account workaround authorized by this result
- classification: `ACCESS_BLOCKER_MEMORY`

V2 implication: do not rediscover/retry the same source route as if unexamined unless permissions/terms materially change and that change is recorded.

---

## 3. EURUSD-RANGE-GRID-001

- PR #28
- frozen exploratory quote-proxy harness
- no market ZIP/row/result/look acquired at recorded freeze
- status: `FROZEN_UNEXECUTED`
- private predecessor exposure remains UNKNOWN as stated by the research line
- classification: `UNEXECUTED_PROTOCOL_MEMORY`

V2 implication: preserve the frozen protocol identity and exposure caveats. Do not label it negative or positive without an admissible execution.

---

## 4. Historical `codex/test` negative experiment

- branch: `codex/test`
- branch has only one unique commit relative to current V2, but that commit is scientifically material
- historical audit classified the tested result as KILL/REJECT rather than a current edge
- classification: `HISTORICAL_NEGATIVE_RESULT`

V2 requirement: index exact commit and result limitations before branch ref retirement.

---

## 5. ASML current-corpus duplicate lesson

Historical current-corpus pair:

- `FUND-ASML-CAPACITY-SERVICE-001`
- `FUND-ASML-CAPACITY-PRICING-001`

The pair is a demonstrated anti-redetection failure/near-duplicate exposure lesson. V1 subsequently added current-corpus normalization and blocking screens.

Classification: `SCIENTIFIC_PROCESS_FAILURE_MEMORY`

V2 requirement:

- keep both historical artifacts immutable;
- retain duplicate/overlap relationship;
- do not treat branch cleanup or normalized naming as evidence that the two were economically distinct;
- preserve unresolved historical overlap policy as a governance question.

---

## 6. Edge Lab corpus

Branch:

`research/edge-lab-continuous`

Observed unique history vs current V2: 170 commits.

Contents include:

- discovery methods/policies;
- candidate contracts;
- source acquisition/qualification;
- executed result files;
- prospective designs;
- platform probes and traces;
- negative/failed/blocked research.

Classification: `BULK_SCIENTIFIC_MEMORY_SOURCE`

Before retiring the branch namespace, produce a machine-readable migration/index of individual experiment identities rather than replacing 170 commits with a single sentence such as “Edge Lab historical.”

Minimum per-experiment import state:

`experiment_id | source_sha | protocol_hash_if_known | exposure_state | outcome_state | data_status | economic_authority | successor_or_duplicate_links | caveat`

No old result becomes V2-qualified merely by being imported.

---

## 7. Legacy economic reconciliation

Branch:

`research/legacy-economic-reconciliation-20261015`

Observed unique history vs V2: 102 commits.

Current historical reconciliation status remains:

`PARTIAL_WITH_EXPLICIT_GAPS`

Known reconciliation census and materialized V1 runtime ledger are not equivalent concepts. The runtime being fail-closed does not prove that every historical experiment has been recovered.

Classification: `BULK_LEGACY_MEMORY_SOURCE`

V2 requirement:

- preserve imported ledger source identity;
- preserve explicit gaps;
- preserve historical PR/backlog items not represented as final tested edge;
- never infer a verdict for known untested items;
- do not collapse family-level multiplicity context into isolated PASS/FAIL claims.

---

## 8. Weather V4

Compact evidence source:

`builder/weather-v4-a2-doc-integration-root-candidate-2026-10-08`

The branch is not final execution authority. Its value is as a consolidated corpus containing archaeology, harness, audits, Blue support and Owner decisions.

Classification: `SCIENTIFIC_AND_GOVERNANCE_MEMORY_SOURCE`

Before retiring the wider Weather branch family:

- index every executed/offline test and its result status;
- index every independent Astra review;
- index Owner decisions separately from Builder/Blue/Astra material;
- preserve `ECONOMIC_AUTHORITY = 0` where applicable;
- preserve unresolved parameters rather than filling them retrospectively.

---

## 9. Live Lab / platform probes

Historical Live Lab and platform-probe branches contain operational/product evidence, including failed/partial publication and continuation probes.

Classification: `OPERATIONAL_PRODUCT_MEMORY`

These are not economic evidence. V2/Live Lab reconciliation should preserve only the product/runtime facts they actually demonstrate and avoid treating visual or platform behavior as scientific edge evidence.

---

## 10. Memory migration acceptance rule

A historical research branch may move from `SCIENTIFIC_MEMORY_REQUIRED` to `ARCHIVE_AFTER_IMPORT` only when:

1. all materially distinct experiment/result identities are indexed;
2. original commit/result hashes remain reachable;
3. exposure/look state is preserved;
4. negative/blocked/unexecuted/unknown states are preserved exactly;
5. duplicate/successor relationships are recorded where known;
6. no economic authority is invented;
7. an independent review confirms that cleanup did not erase a scientifically material result.

Branch count reduction is subordinate to these conditions.