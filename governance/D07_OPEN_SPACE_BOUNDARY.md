# D07_OPEN_SPACE_BOUNDARY

**Status:** FROZEN  
**Authority:** Blue Team / Mission Control  
**Purpose:** exhaustively bound the design space D07 may choose after D05-A.

Once D05-A has executed, this boundary cannot expand without invalidating the authority of any D05-A metric whose design-invariance no longer holds.

## 1. Admissible information before freeze

This boundary is built only from:

- `QUANT_NORTH_STAR.md`;
- the frozen Form 4 claim;
- closed Blue decisions;
- the insider mechanism;
- public source-structure documentation: schemas, fields, granularity and documented semantics.

It must not use empirical target-corpus distributions such as resolution rates, event counts, issuer concentration, temporal distributions, clustering frequency, observed price coverage, outcomes or exploratory resolver runs.

Source structure is admissible before freeze. Distribution of values is a D05-A measurement.

**Invariant:** `BOUNDARY_BEFORE_VALUES`

## 2. Dimensions already closed

### 2.1 Population and qualification

The following are closed and outside D07:

- original Form 4 only;
- non-derivative transaction;
- transaction code = `P`;
- acquired/disposed indicator = `A` (acquired), **not transaction code `A`**;
- qualifying reporting owner = director and/or officer;
- 10% ownership alone is insufficient;
- a 10% owner who is also officer/director qualifies through the officer/director role;
- issuer identity = issuer CIK;
- insider identity = reporting-owner CIK;
- no fuzzy-name matching.

The notation above is deliberate:

`transaction code P` + `acquired/disposed indicator A`

does **not** admit Form 4 transaction code `A` (award/grant).

### 2.2 Signal

The following are closed:

- same issuer;
- two distinct qualifying insider CIKs;
- trailing 10 regular market sessions;
- threshold crossing `<2 -> >=2`;
- no repeated formation while the window remains active;
- re-arm only after the rolling window falls below two;
- EDGAR date is the frozen source fact for public observability.

The source temporal fact is therefore closed:

`public observability fact = EDGAR date`.

The projection:

`EDGAR date -> formation_session`

is **not** closed and is D07-O1.

D07 may decide only how the frozen EDGAR date is projected onto the regular-session calendar for formation-window purposes. It may not redefine the public-observability source fact.

### 2.3 Economic exposure

The following are closed:

- entry = first regular-session open after EDGAR date;
- never same-day through intraday reinterpretation;
- hold = 20 regular sessions;
- SPY = primary scientific benchmark;
- no threshold/window/horizon rescue after outcomes.

These are inherited constraints, not D07 candidates.

## 3. Remaining open D07 dimensions

### O1 — `formation_session`

The economic entry rule is already fixed:

`first regular-session open after EDGAR date`.

The only remaining temporal projection is:

> Which regular session is attached to an EDGAR date for calculating the rolling 10-session formation window?

For an EDGAR date that itself corresponds to a regular market session, attachment to that session is determined.

The material residual degree of freedom is primarily EDGAR dates with no regular market session: weekend, holiday or another no-session date.

D07 must freeze one deterministic convention, for example previous regular session or next regular session, unless an earlier closed decision already dictates the choice.

The resulting function must be unique:

`EDGAR date -> formation_session`.

O1 is used only for the 10-session formation geometry. It may shift a filing between formation windows. It may not modify the source EDGAR date or the economic entry rule.

### O2 — intra-session ordering / threshold-crossing instant

When multiple qualifying observations attach to the same `formation_session`, D07 must freeze deterministic application order, the logical instant at which `<2 -> >=2` occurs, and a deterministic tie rule when strict ordering is unavailable.

O2 is a state-machine convention only. It cannot change threshold 2, the 10-session window, re-arm logic or economic entry date.

### O3 — 20-session interval measurement convention

The number 20 and the economic holding rule are closed.

D07 only fixes interval identification/indexing: start, regular-session numbering, end of the 20th regular session, and calendrical representation of an expected session when the security is not normally observable/tradable.

D07-O3 defines **no payoff substitute** for delisting, price disappearance, suspension, listing change or terminal/availability event.

D07-O3 and D19-G must be read jointly:

- D07 fixes interval/indexing;
- D19 fixes scientific/economic treatment of terminal, absent or delisted observations.

D07 cannot transform missing price or delisting into exclusion, favorable truncation or conventional payoff.

### O4 — overlap geometry

The claim and mechanism do not fully determine overlap representation, so this remains legitimately open.

D07 must fix whether two distinct signals remain two observations when exposure windows overlap; treatment of a new same-issuer signal after re-arm while a prior exposure remains active; representation of cross-issuer overlap; and the statistical unit when one issuer contributes multiple simultaneous or partially overlapping windows.

This is scientific observation/dependence geometry, not sizing or capital allocation.

O4 uniquely can alter the meaning and cardinality of an `observation`.

Therefore:

- `qualifying_filing_count_per_issuer` is D05-A because qualifying filing is already closed and O4-independent;
- `observation_count_per_issuer` is D05-B until O4 is frozen.

Issuer being a primitive grouping key does not make observation-count-per-issuer design-invariant.

## 4. Explicit exclusions from D07

D07 cannot be used to decide which securities are worth retaining, which coverage strata are acceptable, which issuers are too hard to map, how long a historical period is needed to obtain enough events, which variants improve power, a preferred return definition after inspection, post-inspection segment exclusions, redesign because D05-B looks weak, or a payoff for delisting/terminal missing observations.

These belong to feasibility, D19, D08, lane decisions or a new claim/lineage.

## 5. D05-A design-invariance test

A quantity `Q` may enter D05-A only if its definition, observation unit, population, denominator, mapping and calculation remain identical for **every admissible combination** of:

`D07-O1 × D07-O2 × D07-O3 × D07-O4`.

The test is against the full open D07 space, never the likely or preferred geometry.

If a component changes under any admissible D07 convention:

`CLAIM-DESIGN-SENSITIVE -> D05-B`.

If invariance cannot be established before observing values:

`AMBIGUOUS -> EMBARGO`.

`AMBIGUOUS` is not terminal; it must be resolved before execution without inspecting values.

## 6. Boundary monotonicity

The boundary is written without D05 empirical values, frozen, versioned and hashed before D05-A execution.

After the first D05-A inspection, the boundary cannot expand without scientific consequence.

For every already-observed quantity `Q` under a proposed expansion, if `Q` no longer remains invariant over the expanded space:

`Q = INVALIDATED_FOR_NEW_DESIGN_LINEAGE`.

This applies even if the historical numerical value remains technically correct.

**Invariant:** `POST_D05A_BOUNDARY_EXPANSION_INVALIDATES_AFFECTED_AUTHORITY`

Narrowing the boundary later never retroactively restores authority to a metric observed under an inadmissible classification.

## 7. Canonical relation to D05

`BOUNDARY FREEZE`
→ `UNIT TAXONOMY`
→ `RESOLUTION / MAPPING CONTRACT FREEZE`
→ `D05-A METRICS + STRATA + STOPPING RULE FREEZE`
→ `EXECUTE D05-A`
→ `D07 FREEZE`
→ `D05-B`
→ `FEASIBILITY VERDICT`.

D05-A contains only D07-independent measurements.

D05-B may use units that only exist or become well-defined after D07.

A D05-B result never grants authority to reopen D07.

If D05-B makes the frozen design impractical:

`FEASIBILITY_INSUFFICIENT_FOR_FROZEN_DESIGN`

followed by stop expression, `INSUFFICIENT`, or a new claim/new lineage. Never silent D07 adjustment.

## 8. Minimal frontier rule

A dimension remains open only if all three are true:

1. it is not already fixed by the frozen claim or a closed Blue decision;
2. the economic mechanism does not determine its value;
3. a convention is genuinely required for an executable and scientifically unambiguous claim.

Therefore already determined dimensions are closed; mechanism-underdetermined real choices stay open; and “just in case” dimensions are excluded.

A boundary that is too wide makes D05-A unnecessarily severe. A boundary that is artificially narrow hides legitimate design choice.

Target:

> **la plus petite frontière honnête compatible avec le claim et son mécanisme économique — jamais la frontière la plus favorable à D05-A.**

## 9. Invariants

- `BOUNDARY_BEFORE_VALUES`
- `POST_D05A_BOUNDARY_EXPANSION_INVALIDATES_AFFECTED_AUTHORITY`
- mechanism-bounded design space
- derived-unit reproducibility
- resolver structure/distribution separation
- `NO_SILENT_RESOLVER_OPTIMIZATION`
