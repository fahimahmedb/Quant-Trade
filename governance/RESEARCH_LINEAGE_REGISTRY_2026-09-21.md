# RESEARCH LINEAGE REGISTRY — 2026-09-21

`STATUS = PREPARED / NON_AUTHORIZING`

A **lineage** is a frozen research protocol plus every cohort and look taken
under it. Lineages are isolated: a lineage may never be amended to reflect an
outcome observed under it, and evidence never transfers between lineages.

## 1. Registered lineages

### FORM4_CONFIRMATORY_V1

```text
STATUS        = FROZEN / RUNNING
DESIGN        = repeated frozen 252-entry-session cohorts
K_target      = 3
K_max         = 4
STOPPING      = first fully matured cohort with pooled post-merge G >= 10;
                otherwise stop after K_max
LOOKS         = one-look
HORIZON       = multi-year
MUTABLE       = NO
```

Binding: no Builder, no lane, no schedule pressure and no later document may
lower `G`, change `K_max`, shorten cohorts, add looks or alter influence spans.
If `K_max` is exhausted below the guard, the lineage terminates as
`INSUFFICIENT`. That is a valid and expected scientific outcome, not a failure
to be repaired by relaxation.

### FAST_VERTICAL_V1

```text
STATUS        = SLOT_DEFINED / NOT_ADMITTED
ADMISSION_GATE= later of (Rail A t0 declared) and (Rail B vertical integrated)
DESIGN        = to be pre-registered before any outcome is observed
MUTABLE       = NO once admitted
```

`FAST_VERTICAL_V1` is a separate lineage, not a variant of Form-4. It exists so
that speed is obtained by choosing a different question, never by weakening a
frozen protocol.

## 2. Admission requirements for any new lineage

A lineage is admitted only with all of:

1. Pre-registration document complete, digest recorded, dated before any
   outcome under the protocol is observed.
2. **Power derivation**: the minimum economically useful effect after realistic
   frictions, and the number of independent units required to detect it at the
   lineage's declared alpha and power. Speed must be justified as
   `effect / sqrt(variance) * sqrt(independent units per month)` — never by raw
   observation count.
3. Fixed universe and fixed point-in-time data sources with recorded
   provenance, timestamps and fingerprints. Reconstructed point-in-time history
   must pass Data Plane provenance rules before being cited.
4. Declared stopping rule and look schedule, fixed in advance.
5. Declared friction and capacity model, applied to the executable object.
6. Alpha budget drawn from the family-wise budget in §3.

## 3. Multiplicity across lineages

Lane selection is a factory output. "The first lane that qualifies" is a
maximum over lanes and must be priced as such.

```text
MAX_CONCURRENT_ADMITTED_LANES = 3   (proposed; owner confirmation required)
FAMILY_WISE_BUDGET            = fixed at first admission
ALLOCATION                    = each lane draws its alpha share at admission
UNSPENT_BUDGET                = does NOT return on lane termination
```

A lane that terminates does not refund its alpha. This is what prevents
churning lanes until one passes.

## 4. Isolation rules

- Evidence from one lineage never qualifies a sleeve in another.
- A sleeve occupying a stage on the exposure ladder cites exactly one lineage.
- Shared instruments across lineages are permitted; shared *evidence* is not.
- A lineage may be read for hypothesis generation only if the generated
  hypothesis is tested under a new pre-registration with its own budget.

## 5. Expected outcome distribution

Most admitted lanes are expected to terminate `INSUFFICIENT` or falsified.
Cheap, fast, honest termination is the designed product of this registry. The
throughput metric is *lanes killed per quarter at low cost*, not lanes passed.
