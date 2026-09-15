# D05 DENOMINATOR RECONCILIATION CONTRACT

**Status:** RULE FROZEN  
**Authority:** Blue Team / Mission Control  
**Important distinction:** this file freezes the **reconciliation rule**. It does **not** freeze the expected population itself.

The expected population is frozen only when the official index manifest produced by this rule is materialized and hashed **before any join result or mismatch is observed**.

Therefore there are two distinct frozen objects:

1. `RECONCILIATION_RULE_HASH` — this canonical rule file / repository state;
2. `EXPECTED_MANIFEST_HASH` — the future manifest containing the expected accession population.

A rule commit is not a substitute for the manifest hash.

## 1. Purpose

Define an external expected population independent of acquisition transport, then separately measure the Data Plane's ability to ingest it.

The contract certifies completeness of Quant's denominator relative to the official public EDGAR index under a pre-frozen projection.

It separately measures transport/join completeness between that expected population and acquired bytes.

These properties must never be conflated.

## 2. Authority model

### Primary authority

`OFFICIAL_SEC_PUBLIC_EDGAR_INDEX`

The official index defines scientific scope.

### Transport

Payload bytes may arrive through SEC bulk quarterly archives, direct SEC archive download, API, cache acquired earlier or another authorized SEC transport.

**Invariant:** `TRANSPORT_DOES_NOT_DEFINE_SCOPE`

The transport channel never defines membership in the authority-bearing population.

## 3. Certification semantics

Strong denominator verdict:

`DENOMINATOR_CERTIFIED_RELATIVE_TO_SEC_PUBLIC_INDEX`

This means:

> Quant can deterministically reconstruct the expected public-filing population according to the official SEC index and the frozen projection.

It does not mean:

`SEC_UNIVERSE_ABSOLUTE_COMPLETENESS`.

### Structural limitation

`SEC_INDEX_COMPLETENESS_ASSUMPTION`

The official SEC public index is treated as the highest operational external authority available to Quant for public EDGAR submissions.

This contract does not independently prove that EDGAR itself contains/indexes every filing that conceptually should exist.

**Invariant:** `RELATIVE_CERTIFICATION_ONLY`

## 4. Denominator unit

Unit:

`UNIQUE_EDGAR_SUBMISSION`

Canonical key:

`ACCESSION_NUMBER`.

Therefore:

`1 accession = 1 expected filing`

regardless of number of reporting owners, transaction rows, attached documents or joint-filing status.

## 5. Frozen projection `P`

The rule is:

`E = P(OFFICIAL_SEC_INDEX)`.

The rule `P` is frozen by this contract.

The realized set `E` is not frozen until a manifest is produced and hashed before join inspection.

### 5.1 Exact form-type rule

Include only:

`FORM_TYPE == "4"`

by exact equality.

`4/A` is not `4`.

Amendments may be counted diagnostically but do not belong to the original-Form-4 expected denominator.

### 5.2 Filing-date-bounded scientific ingestion population

Scope uses:

`OFFICIAL_INDEX.DATE_FILED`

with inclusive bounds:

`2020-01-01 <= DATE_FILED <= 2026-06-30`.

This is an explicit scientific choice.

The ingestion population is a population of **public filings**.

Using transaction date would require parsing the filing to construct the external denominator that is supposed to certify ingestion, making the control circular.

**Invariant:** `EXTERNAL_CONTROL_INDEPENDENCE`

**Invariant:** `TRANSACTION_DATE_DOES_NOT_SELECT_INGESTION_SCOPE`

Consequences:

- a filing deposited inside the window can contain a transaction before 2020;
- a transaction occurring by 2026-06-30 but filed after 2026-06-30 does not re-enter the authority-bearing ingestion population.

Transaction date is an observed property after ingestion, not a scope-selection rule.

### 5.3 Same-source date provenance

Both sides of the scope comparison use:

`OFFICIAL_INDEX.DATE_FILED`.

Every accession joined to the expected manifest receives:

`source_index_date_filed`

from that manifest.

A `FILING_DATE` parsed from a bulk file or filing may be used as a consistency check.

It cannot substitute for the official-index provenance field.

**Invariants:**

`SAME_SOURCE_FIELD_BOTH_SIDES`

`NO_RECONSTRUCTED_INDEX_PROVENANCE`

## 6. Index-first authority / bulk-transport architecture

Canonical sequence:

`OFFICIAL INDEX`
→ `FROZEN INDEX MANIFEST`
→ `EXPECTED SET E`
→ `PAYLOAD ACQUISITION`
→ `ACCESSION JOIN`
→ `INGESTED`
→ `PARSED`
→ `QUALIFICATION STATUS`
→ `RESOLVED`
→ `COVERED`.

The index is the point of **authority**.

It need not be the transport mechanism for the bytes.

**Invariants:**

`INDEX_FIRST_AUTHORITY`

`TRANSPORT_DOES_NOT_DEFINE_SCOPE`

`INDEX_PROVENANCE_JOIN_REQUIRED`

## 7. Expected manifest

Before observing any join outcome, materialize an immutable manifest containing at minimum for every relevant indexed accession:

- accession;
- form type;
- `DATE_FILED`;
- index filename/path;
- index artifact identity/hash;
- target-scope status.

The manifest classifies without consulting payload content:

- `IN_SCOPE_TARGET`;
- `INDEXED_BUT_OUT_OF_SCOPE`.

The expected set is:

`E = unique accession where FORM_TYPE == "4" and DATE_FILED in inclusive frozen window`.

### Mandatory sequencing

`FREEZE RECONCILIATION RULE`
→ `BUILD MANIFEST FROM OFFICIAL INDEX`
→ `HASH MANIFEST`
→ `JOIN PAYLOADS`
→ `OBSERVE JOIN RESULTS`
→ `VERDICT`.

Never:

`JOIN`
→ `OBSERVE MISMATCH`
→ `ADJUST MANIFEST`
→ `HASH`.

The manifest hash freezes the expected population. The repository commit that freezes this rule does not.

## 8. Pre-existing bytes

Bytes acquired before this contract remain usable.

They may receive full scientific authority after the fact **only** by classification against the independently frozen manifest.

Required order:

`HASH MANIFEST`
→ `JOIN PREEXISTING BYTES BY ACCESSION`
→ `OBSERVE JOIN RESULTS`
→ `VERDICT`.

**Invariant:** `PREEXISTING_BYTES_DO_NOT_CONTAMINATE_SCOPE`

Authority comes from the independence of `E`, not from when the payload was downloaded.

## 9. Join taxonomy J0–J5

Let:

`M = frozen index manifest`

`E ⊂ M = expected target accession set`

`P = acquired payload accession set`.

Join key:

`ACCESSION_NUMBER`.

### J0 — `JOIN_OK_IN_SCOPE`

`accession ∈ E` and an admissible payload is present.

The object may enter:

`expected -> ingested`.

### J1 — `EXPECTED_PAYLOAD_MISSING`

`accession ∈ E` but no corresponding payload is acquired.

State:

`JOIN_FAILURE / TRANSPORT_MISSING_PAYLOAD`.

This is **not** denominator uncertainty.

The expected accession is known.

The failure lies in:

`expected -> ingested`.

### J2 — `PAYLOAD_INDEXED_OUT_OF_SCOPE`

A payload is acquired and its accession exists in `M`, but the accession is outside `E`.

State:

`OUT_OF_SCOPE_ACQUISITION`.

It is not a scientific mismatch.

### J3 — `PAYLOAD_NOT_IN_INDEX_MANIFEST`

A payload has a valid accession but no corresponding entry in the applicable manifest.

State:

`JOIN_FAILURE / SOURCE_REPRESENTATION_MISMATCH`.

It cannot be silently added to `E` or silently discarded.

### J4 — `PAYLOAD_ACCESSION_UNRESOLVED`

A payload exists but cannot be assigned a canonical accession.

State:

`JOIN_FAILURE / PAYLOAD_IDENTITY_UNRESOLVED`.

### J5 — `ACCESSION_PAYLOAD_CONFLICT`

Multiple incompatible payload representations claim the same accession.

State:

`JOIN_FAILURE / ACCESSION_PAYLOAD_CONFLICT`.

## 10. Denominator certainty vs ingestion completeness

`JOIN_FAILURE` belongs to the transition:

`expected/index authority <-> acquired representation`.

It does not automatically alter denominator certainty.

Example:

`E fully reconstructible`
+
`EXPECTED_PAYLOAD_MISSING`

can yield simultaneously:

`DENOMINATOR_CERTIFIED_RELATIVE_TO_SEC_PUBLIC_INDEX`

and:

`INGESTION_PARTIAL`.

**Invariant:** `DENOMINATOR_CERTAINTY_ORTHOGONAL_TO_INGESTION_COMPLETENESS`

## 11. Denominator verdicts

### `DENOMINATOR_CERTIFIED_RELATIVE_TO_SEC_PUBLIC_INDEX`

`E` is exactly reconstructible under the frozen rule.

This can be true even if some expected payloads have not yet been transported.

### `DENOMINATOR_PARTIAL`

External evidence bounds the expected population but does not permit exact reconstruction of `E`.

This label must not be used merely because known expected payloads are missing.

### `DENOMINATOR_UNKNOWN`

The expected population cannot be constructed or externally bounded for an authority-bearing portion.

Then:

`COVERAGE_UNKNOWN`.

For the authority-bearing population:

`ALLOWABLE_UNBOUNDED_DENOMINATOR_UNKNOWN = 0`.

## 12. Ingestion / join verdicts

Independently of denominator status:

- `INGESTION_COMPLETE`
- `INGESTION_PARTIAL`
- `SOURCE_REPRESENTATION_MISMATCH`
- `JOIN_IDENTITY_FAILURE`
- `JOIN_CONFLICT`

These feed D05-A.

They never rewrite `E`.

## 13. Transport recovery

A missing payload may be recovered through another authorized transport channel without scientific redesign if:

- expected accession remains unchanged;
- manifest and scope remain unchanged;
- `source_index_date_filed` remains the manifest value;
- payload bytes are content-addressed/provenanced;
- recovery is recorded.

Thus:

`EXPECTED_PAYLOAD_MISSING`
→ alternate retrieval
→ `JOIN_OK_IN_SCOPE`

is a Data Plane repair, not scientific rescue.

## 14. Joint filings and multi-document submissions

Multiple owners in one submission:

`-> 1 denominator unit`.

Multiple documents/attachments in one submission:

`-> 1 denominator unit`.

The denominator/join contract does not decide owner attribution, qualification or event formation.

## 15. Parsing and documentary regimes cannot rewrite the denominator

The primary denominator uses only exact form type, `DATE_FILED`, and accession/index identity.

Therefore FM-05 and FM-06 may affect:

`ingested -> parsed -> qualification status`

but cannot retrospectively alter:

`expected`.

**Invariant:** `PARSER_REGIME_DOES_NOT_REWRITE_DENOMINATOR`

## 16. Qualification is a status partition

After parsing:

`PARSED = QUALIFYING + NON_QUALIFYING + QUALIFICATION_INDECIDABLE`.

### `QUALIFYING`

Frozen rules establish membership in the qualifying population.

### `NON_QUALIFYING`

Frozen rules establish non-membership.

This is a legitimate rule-based exclusion. It is **not** missingness.

### `QUALIFICATION_INDECIDABLE`

Available information does not permit definitive application of the frozen qualification rule.

Examples may include `JOINT_OWNER_AMBIGUOUS`, a required structural field unavailable, or required identity not established under the frozen contract.

This is scientific missingness.

**Invariants:**

`NON_QUALIFYING_IS_NOT_MISSINGNESS`

`QUALIFICATION_INDECIDABLE_IS_MISSINGNESS`

## 17. Stage ratios

Conditional ratios include:

`q_ingestion_conditional = INGESTED / EXPECTED`

`q_parse_conditional = PARSED / INGESTED`

`q_qualification_decidable_conditional = (QUALIFYING + NON_QUALIFYING) / PARSED`

`q_qualification_indecidable_conditional = QUALIFICATION_INDECIDABLE / PARSED`

`q_resolution_conditional = RESOLVED / QUALIFYING`

`q_market_coverage_conditional = COVERED / RESOLVED`.

The composition ratio:

`QUALIFYING / qualification-decidable`

may be reported as population composition. It is not a coverage rate.

## 18. Cumulative loss reporting

Conditional downstream rates must be accompanied by appropriate cumulative states from `EXPECTED`, including:

- `INGESTED / EXPECTED`;
- `PARSED / EXPECTED`;
- `QUALIFICATION_INDECIDABLE / EXPECTED`;
- `QUALIFYING / EXPECTED`;
- `RESOLVED / EXPECTED`;
- `COVERED / EXPECTED`.

The purpose is to prevent a strong downstream conditional rate from masking upstream loss or uncertainty.

Example:

`q_resolution_conditional = 100%`

must not conceal:

`q_parse_conditional = 60%`

or material `QUALIFICATION_INDECIDABLE`.

**Invariant:** `CUMULATIVE_LOSS_ALWAYS_REPORTED`

## 19. No denominator or join tuning

After any join outcome or mismatch has been observed, the following cannot be silently changed:

- form filter;
- period field;
- inclusive/exclusive bounds;
- accession extraction;
- manifest authority;
- join exception rules;
- expected accessions;
- scope definition.

Any such change becomes:

`DENOMINATOR_RECONCILIATION_REDESIGN`

with a new version/hash, recorded justification, preservation of the prior result and separate authority assessment.

**Invariants:**

`NO_SILENT_DENOMINATOR_OPTIMIZATION`

`NO_SILENT_JOIN_REDEFINITION`

## 20. Current A1 implementation consequence

Current A1 acquisition is not fully index-first for 2020–2026Q2; it primarily acquires quarterly SEC Form 3/4/5 bulk archives. The Q3-2026 tail already uses `master.idx`.

Before D05-A receives authority:

1. build the official index manifest independently;
2. hash/freeze the manifest;
3. join already acquired bulk bytes by accession;
4. assign `source_index_date_filed` only from the manifest;
5. classify J0–J5;
6. treat post-2026-06-30 filings as `OUT_OF_SCOPE_ACQUISITIONS` for this authority-bearing population even if their transaction dates fall in H1.

Existing bytes need not be discarded.

They are transport assets, not scope authority.

## 21. Required frozen objects

### Rule object — frozen by governance repository state

This canonical contract fixes authority source, exact form filter, `DATE_FILED` scope field, inclusive start/end, accession unit, manifest-construction rule, J0–J5 taxonomy, pre-existing-bytes policy, transport recovery policy, denominator verdict mapping, ingestion verdict mapping, qualification status partition, cumulative-reporting rule, secondary consistency policy and `SEC_INDEX_COMPLETENESS_ASSUMPTION`.

### Manifest object — not yet created

Before any join:

- materialize expected-accession manifest;
- hash it;
- record its source index artifacts/hashes;
- freeze its population.

Only this second hash freezes the realized expected population.

## 22. Core invariants

- `RELATIVE_CERTIFICATION_ONLY`
- `EXTERNAL_CONTROL_INDEPENDENCE`
- `INDEX_FIRST_AUTHORITY`
- `TRANSPORT_DOES_NOT_DEFINE_SCOPE`
- `INDEX_PROVENANCE_JOIN_REQUIRED`
- `SAME_SOURCE_FIELD_BOTH_SIDES`
- `NO_RECONSTRUCTED_INDEX_PROVENANCE`
- `PREEXISTING_BYTES_DO_NOT_CONTAMINATE_SCOPE`
- `DENOMINATOR_CERTAINTY_ORTHOGONAL_TO_INGESTION_COMPLETENESS`
- `TRANSACTION_DATE_DOES_NOT_SELECT_INGESTION_SCOPE`
- `PARSER_REGIME_DOES_NOT_REWRITE_DENOMINATOR`
- `NON_QUALIFYING_IS_NOT_MISSINGNESS`
- `QUALIFICATION_INDECIDABLE_IS_MISSINGNESS`
- `CUMULATIVE_LOSS_ALWAYS_REPORTED`
- `NO_SILENT_DENOMINATOR_OPTIMIZATION`
- `NO_SILENT_JOIN_REDEFINITION`
