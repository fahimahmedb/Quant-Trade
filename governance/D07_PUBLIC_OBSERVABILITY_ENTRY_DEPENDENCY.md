# D07 PUBLIC OBSERVABILITY / ENTRY DEPENDENCY

**Status:** DECIDED_NOT_SPECIFIED — REQUIRED BEFORE FINAL D07 / ENTRY AUTHORITY  
**Authority:** Blue Team / Mission Control  
**Nature:** causality specification implied by the frozen public-observability and next-open rules; does not alter the D05 crossing-count envelope.

## 1. Finding

The frozen claim requires public EDGAR observability and entry at the first regular-session open after the relevant public information is available.

The current D07 boundary can count threshold crossings without selecting O2 trigger identity, but final entry authority additionally requires a mechanical function that states **when the complete crossing becomes publicly knowable**.

An O2 logical trigger label is not itself an entry timestamp.

## 2. Failure mode to prevent

A non-session filing may be attached by O1 to a later regular formation session. Another filing published on that regular session may also be required to establish the `<2 -> >=2` crossing.

Even if O2 labels the earlier filing as the logical trigger, Quant cannot enter at the later session's opening if the second required filing was not yet public at that opening.

Therefore:

`LOGICAL_TRIGGER_IDENTITY != PUBLIC_KNOWLEDGE_TIME`.

**Invariant:** `ENTRY_USES_PUBLIC_KNOWLEDGE_NOT_O2_TRIGGER_LABEL`.

## 3. Required specification outputs

Before final D07 / entry-adapter freeze, a hash-addressable specification must define:

- the authoritative SEC source field(s) for public acceptance/availability;
- timezone and calendar semantics;
- how source timestamps/dates map to regular-session knowledge state;
- the set of public facts required to establish a crossing;
- the crossing public-knowledge instant/date as the latest required public fact;
- the first executable regular-session open strictly after that public-knowledge condition is satisfied;
- behavior for filings accepted before/after market open on a regular session;
- behavior for weekends/holidays and O1 attachment;
- deterministic handling of missing/ambiguous acceptance timestamps.

## 4. Causality law

Conceptually, if `F_crossing` is the set of public source facts required to establish a threshold crossing, then:

`PUBLIC_KNOWLEDGE_TIME(crossing) = max_{f in F_crossing} PUBLIC_TIME(f)`.

Entry must satisfy:

`ENTRY_TIME > PUBLIC_KNOWLEDGE_TIME(crossing)`

and be the first authorized regular-session open satisfying the frozen entry convention.

The final implementation may use date-level rather than timestamp-level semantics only if the source contract proves that the resulting next-open rule cannot create same-session look-ahead.

**Invariants**

- `NO_ENTRY_BEFORE_COMPLETE_CROSSING_IS_PUBLIC`
- `PUBLIC_KNOWLEDGE_DOMINATES_FORMATION_ATTACHMENT`

## 5. Relationship to D05 ceiling

This dependency does not invalidate the D05 raw crossing-count ceiling.

D05 may count formation crossings under the sealed O1/O2/O4 envelope without revealing trigger identities.

What remains unauthorized until this dependency is specified is:

- final D07 entry geometry;
- entry-date outcome transform construction;
- final D08 outcome measurement tied to executable entry.

**Invariant:** `PUBLIC_ENTRY_GAP_BLOCKS_OUTCOME_GEOMETRY_NOT_RAW_CROSSING_COUNT`.

## 6. No outcome rescue

The observability/entry function must be frozen before Form-4 outcomes are inspected for the confirmatory lineage.

It may not be altered because a different entry date improves measured performance.

**Invariant:** `NO_OUTCOME_DRIVEN_ENTRY_REINTERPRETATION`.
