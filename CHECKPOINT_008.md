# Forensic Audit Continuation — Checkpoint 008

Date: 2026-10-19
Audit branch: `audit/forensic-checkpoint-20261019`
Parent audit head: `3e64a61ae351ba6590f43cfc796262c51b12deff`
Status: `ACCEPTANCE_MATRIX_FROZEN`

## Purpose

Freeze a testable acceptance matrix derived from CP5-CP7 before any operational Oracle/OCI recovery work resumes.

This checkpoint is specification/audit only. It does not authorize or implement economic experiments, prospective observation, capital allocation, order generation, or live trading.

Hard authority remains:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

## A. Legacy bootstrap acceptance

Pinned historical source from:

`research/research_os/legacy/source_manifest.json`

Expected values:

- source commit: `183ad65ff260b903a16548ce37948f54d47a9ec8`
- ledger blob: `ba9b165aaf96956776672df51233bb9bf1e6cbc9`
- schema: `legacy-research-ledger-v1`
- expected historical item count declared by manifest: `33`
- reconciliation status: `PARTIAL_WITH_EXPLICIT_GAPS`
- historical result immutability: `true`

### A1 — missing materialized ledger

Setup:

`LEGACY_RESEARCH_LEDGER.imported.json` absent.

Required future behavior:

`BLOCK_LEGACY_LEDGER_NOT_MATERIALIZED`

Current reviewed loader behavior:

**FAIL acceptance** — `LegacyKnowledgeBase.load()` silently constructs an empty record set.

### A2 — wrong ledger blob

Setup: materialized path exists but content blob != pinned manifest blob.

Required future behavior:

`BLOCK_LEGACY_LEDGER_BLOB_MISMATCH`

The Oracle/worker preflight must verify the exact source object before candidate screening.

### A3 — wrong schema / immutability

Required:

- schema mismatch => BLOCK;
- `historical_result_immutability != true` => BLOCK;
- governance values allowing real capital/live trading => BLOCK.

The current loader already checks schema and historical-result immutability when a file exists, but the Oracle preflight must also prove the expected pinned object and closed authority before worker work begins.

### A4 — record-count sanity

Required:

- zero records => BLOCK;
- loaded count inconsistent with the pinned corpus/manifest expectation => BLOCK or explicit owner review;
- no candidate freeze may proceed under an unproved empty corpus.

### A5 — PR #1 completeness must remain explicit

Even a perfect 33-item bootstrap must retain:

`LEGACY_RECONCILIATION_STATUS = PARTIAL_WITH_EXPLICIT_GAPS`

It must not be mislabeled as complete historical memory because CP5/CP6 established material PR #1 gaps.

## B. Current frozen-corpus acceptance

### B1 — canonical current-corpus manifest/registry

Before any new hypothesis freeze, the worker must have a deterministic snapshot of the existing frozen/current hypothesis corpus.

Required receipt fields should include at minimum:

- corpus snapshot identifier/hash;
- number of frozen/current lineages considered;
- lineage ids + generation ids or content hashes;
- unsupported-schema list;
- normalization result.

Missing/unreadable current corpus => fail closed for new independent-lineage freeze.

### B2 — heterogeneous schema normalization

Every frozen hypothesis schema that can participate in current research must normalize into a canonical anti-redetection identity containing, where evidence supports it:

- hypothesis id;
- generation id;
- research family;
- issuer/asset/instrument/universe;
- payer / forced or constrained actor;
- economic mechanism;
- event/rule dependency;
- timing clock;
- horizon;
- economic exposure;
- capacity bottleneck;
- cost structure;
- source/provenance identity;
- claim ceiling;
- frozen content hash.

Unknown fields must remain `UNKNOWN`; they may not be guessed to improve matching.

Unsupported schema => explicit BLOCK or owner-reviewed migration, not silent omission.

### B3 — ASML schema regression

The following real pair is mandatory as a regression fixture:

- `FUND-ASML-CAPACITY-SERVICE-001`
- `FUND-ASML-CAPACITY-PRICING-001`

The first uses `generation_id/mechanism`; the second uses `generation/thesis`.

Acceptance requires both to be ingested into the same anti-redetection comparison surface without silently losing either lineage.

## C. Economic distinctness acceptance

### C1 — exact ID duplicate

Exact current or Legacy ID duplicate => BLOCK.

### C2 — exact normalized economic identity

Different hypothesis ids but same normalized economic exposure on the core axes => unresolved same-exposure BLOCK for an independent new lineage.

### C3 — semantic mechanism equivalence

The system must not rely exclusively on exact prose equality or raw token Jaccard.

A canonical mechanism/family representation or equivalent deterministic economic-identity contract must allow differently worded versions of the same causal exposure to be routed to review/block.

### C4 — UNKNOWN must not mean distinct

If core economic-identity fields are unknown, the result may be `UNKNOWN`/`REVIEW_REQUIRED`, but it must not be promoted to `DISTINCT` merely because equality could not be proved.

For freeze/readiness of a new independent lineage, unresolved identity ambiguity must fail closed or require explicit auditable owner/validator resolution.

### C5 — legitimate new generation path

A materially changed thesis that is related to an existing lineage should normally be represented as a new generation/explicit descendant rather than a fresh independent hypothesis id.

Required metadata:

- parent lineage/generation;
- material change rationale;
- fields changed;
- why prior negative/positive knowledge does or does not transfer.

## D. Portfolio/readiness acceptance

### D1 — peer-set completeness binding

`economic_test_readiness()` must not depend on an unproved caller-supplied arbitrary subset of peers.

Acceptance requires the readiness receipt to bind the complete relevant peer corpus snapshot or a deterministic, auditable selection rule that cannot silently omit a collision.

### D2 — unresolved same-exposure review gates READY

If Portfolio emits:

`same_exposure_review_required = true`

or an equivalent unresolved high-overlap condition, then a new independent lineage must not return:

`READY_FOR_AUTHORIZED_ECONOMIC_TEST`

until distinctness is resolved.

Required future block code example:

`BLOCK_UNRESOLVED_CURRENT_EXPOSURE_OVERLAP`

Current reviewed behavior:

**FAIL acceptance** — Portfolio diagnostics are computed but not appended to readiness `reasons`.

### D3 — Portfolio remains non-empirical pre-outcome

Fixing deduplication must not smuggle empirical outcomes into the pre-outcome layer.

Must remain:

- empirical correlation unavailable without admissible returns;
- marginal portfolio contribution not estimated;
- no capital allocation/sizing/orders authority.

### D4 — duplicate-generation invariant remains

Existing protection against selecting more than one generation for the same exact `hypothesis_id` remains valid and should be retained.

It is necessary but not sufficient.

## E. Validator / Red Team acceptance

### E1 — current-lineage context available to validator

Independent validation of a newly frozen lineage must receive a frozen snapshot/reference of relevant current lineage identity, not only Legacy screening output.

### E2 — validator cannot silently bless an unresolved collision

If a candidate overlaps an existing frozen lineage, validator output must explicitly decide one of:

- `SAME_LINEAGE_NEW_GENERATION`
- `ECONOMICALLY_DISTINCT_WITH_EVIDENCE`
- `BLOCK_CURRENT_LINEAGE_DUPLICATE`
- `OWNER_REVIEW_REQUIRED`

A generic business-mechanism PASS must not erase the collision state.

### E3 — producer/validator independence remains

No dedup repair may permit the producer to self-validate or mutate a frozen predecessor.

## F. Worker / Oracle bootstrap acceptance

### F1 — one startup preflight before candidate work

Every Oracle/autonomous worker wake capable of discovery/freeze must prove:

1. fresh GitHub HEAD/state;
2. control-plane authority closed;
3. pinned Legacy ledger materialized and verified;
4. Legacy record-count sanity;
5. current frozen-corpus snapshot built/verified;
6. schema-normalization completeness;
7. task authority and lease valid;
8. no duplicate/current-exposure gate outstanding.

Any failed item => no candidate freeze.

### F2 — restart safety

An interrupted/restarted Oracle worker must not:

- duplicate a claimed lineage;
- duplicate a freeze;
- rerun a bounded economic experiment;
- create a second derivation for the same deterministic key;
- bypass the dedup preflight after restart.

### F3 — provenance receipt

A successful discovery/freeze receipt should bind:

- worker id / lease generation;
- task id;
- branch/commit;
- Legacy source commit + blob hash + loaded record count;
- current-corpus hash/count;
- candidate hash;
- anti-redetection result;
- any matched lineages and resolution;
- authority snapshot.

### F4 — no direct route from Oracle schedule to economic outcomes

Oracle scheduling may wake a canonical worker, but it must not itself authorize/open outcome access or route around validator/readiness gates.

## G. Required regression tests

A future operational repair should include at least the following deterministic tests:

| Test | Expected result |
|---|---|
| Legacy file missing | BLOCK |
| Legacy wrong blob | BLOCK |
| Legacy wrong schema | BLOCK |
| Legacy zero records | BLOCK |
| Current frozen corpus unavailable | BLOCK new freeze |
| One frozen record uses unsupported schema | BLOCK/review, never omit |
| Exact hypothesis id duplicate | BLOCK |
| Same canonical exposure under different id | BLOCK/review |
| Same exposure reworded with different prose | BLOCK/review |
| Core identity UNKNOWN | UNKNOWN/review, never auto-distinct |
| Explicit legitimate new generation | allowed only with parent/change binding |
| ASML SERVICE vs PRICING | detected as same/near-same economic lineage and cannot both independently become READY unresolved |
| Portfolio high overlap review | readiness BLOCK until resolved |
| Distinct payer + mechanism with sufficient evidence | may remain distinguishable |
| No admissible returns | no empirical correlation / contribution estimate |
| Any authority flag true unexpectedly | BLOCK |
| Restart after claimed task | no duplicate work/freeze |

## H. Acceptance hierarchy

For Oracle recovery, the following precedence applies:

1. governance / authority safety;
2. restart/idempotency safety;
3. historical Legacy availability + integrity;
4. current-frozen anti-redetection integrity;
5. producer/validator independence;
6. readiness completeness;
7. only then scheduler convenience / unattended operation.

A deployment that is reliable but scientifically forgetful is not acceptable.

## I. Current matrix status before Oracle audit

- `A1 missing Legacy fail-closed`: FAIL
- `A2 pinned blob verification in generic external wake`: NOT PROVEN
- `A5 PR#1 completeness`: KNOWN PARTIAL
- `B1 current-corpus binding`: NOT PROVEN
- `B2 schema normalization`: NOT PROVEN
- `B3 ASML regression`: ABSENT
- `C1 exact Legacy ID`: PASS in reviewed screening/readiness path
- `C3 semantic economic equivalence`: INSUFFICIENT
- `D1 peer completeness binding`: FAIL/NOT PROVEN
- `D2 overlap gates readiness`: FAIL
- `D3 non-empirical portfolio safety`: PASS
- `E3 producer/validator independence`: PRESENT in reviewed architecture/tests
- `F1 Oracle startup scientific preflight`: TO AUDIT NEXT
- `F2 Oracle restart safety`: TO AUDIT NEXT
- `F4 no Oracle outcome bypass`: TO AUDIT NEXT

## Next action

Audit the two Oracle-related rails against sections A-F:

- `builder/research-os-vm-autonomy-20261019` @ `8a1bdadc9bc52c4889ee19d0472bcee61fe24318`
- `ops/oci-one-shot-install-20261019` @ `6e8ea155b05086f8e5eabcf830a5f835d3e3d09c`

Do not merge them. Record exactly which acceptance rows are already implemented, missing, stale, or unsafe before modifying the Oracle recovery branch.
