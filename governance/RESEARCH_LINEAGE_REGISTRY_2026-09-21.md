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
2. **Power derivation** (formula corrected 2026-09-21, see §6):

```text
INDEPENDENT_UNIT = one non-overlapping holding-period return of the
                   executable portfolio — not name-days, not signals
SPEED_LAW        = t(T) = IR_NET_ANN * sqrt(T_years)
```

   Cross-sectional breadth is NOT sample size. It enters only through
   `IR` (`IR = IC * sqrt(breadth)`), and residual correlation collapses it:
   500 names at mean residual pairwise rho = 0.05 give effective breadth ~19.
   `IMPLIED_TIME_TO_DECISION` must be derived from `IR_NET_ANN` alone.
3. Fixed universe and fixed point-in-time data sources with recorded
   provenance, timestamps and fingerprints. Reconstructed point-in-time history
   must pass Data Plane provenance rules before being cited.
4. Declared stopping rule and look schedule, fixed in advance.
5. Declared friction and capacity model, applied to the executable object.
6. Alpha budget drawn from the family-wise budget in §3.

## 3. Multiplicity across lineages

Lane selection is a factory output. "The first lane that qualifies" is a
maximum over lanes and must be priced as such.

A fixed non-refunding family-wise budget was rejected on 2026-09-21: it
terminally exhausts after three kills while §5 declares cheap kills to be the
product. The error concept is economic and proportional, so:

```text
MAX_CONCURRENT_ADMITTED_LANES = 2      (matches the reviewer-capacity cap)
ERROR_CRITERION               = mFDR <= 0.05 via alpha-investing
ALPHA_WEALTH_W0               = 0.025
PER_LANE_BID                  = min(W/2, 0.010), drawn at admission
PAYOUT_OMEGA                  = 0.020, credited ONLY after FORWARD_ACCEPTANCE
TERMINATED or INSUFFICIENT    = no refund
W <= 0                        = ADMISSION_CLOSED pending owner re-capitalisation
```

Alpha is refunded only on a *verified* rejection that survives forward
confirmation. A researcher who churns lanes goes broke; a productive one never
exhausts. Bids across lanes sharing a data snapshot are not independent;
positive dependence must be declared at first admission or bids take the
Benjamini-Yekutieli log-factor penalty.

### 3.1 Anti-laundering rules

```text
E1 HYPOTHESIS-GENERATION LAUNDERING
   The digest binds DATA_CUTOFF and SEARCH_DEPTH (variants inspected on data
   before cutoff). The bid is multiplied by SEARCH_DEPTH. Undeclared
   inspection of post-cutoff data voids the lineage.

E2 POST-HOC UNIVERSE OR PARAMETER CHOICE
   Universe membership and every numeric parameter materialise as one
   machine-readable file whose hash enters the digest. The digest must exist
   on an append-only ref BEFORE the harness may open outcome-bearing data.

E3 COSMETIC RE-PROPOSAL OF A KILLED LANE
   Every admission records LANE_SIGNATURE = (universe hash, signal family,
   horizon bucket, side). A new lane matching a terminated signature within
   declared tolerance is a RE-TEST: it inherits the ancestor's spent alpha and
   pays 2x bid. A FALSIFIED signature is permanently barred absent new
   mechanism evidence.
```

## 4. Isolation rules

Isolation applies to edge evidence only. Blanket isolation was rejected on
2026-09-21: it would force every lane to rebuild the Data Plane.

```text
EDGE_EVIDENCE           = never transfers between lineages
INFRASTRUCTURE_EVIDENCE = shared, versioned by fingerprint
                          (provenance, friction/capacity models,
                           LIVE_CANARY execution realism)
```

- A sleeve occupying a stage on the exposure ladder cites exactly one lineage.
- A lineage may be read for hypothesis generation only under a new
  pre-registration with its own bid, subject to E1 and E3 above.

Shared instruments are a Book-level hole, not a lineage-level one: two isolated
lineages can qualify on near-identical factor returns and the Capital Desk
would then size one bet twice.

```text
PORTFOLIO RULE
Sleeves citing distinct lineages whose realized shadow returns correlate
> 0.5 over the forward window aggregate as ONE risk unit at SIZE and RISK,
lineage isolation notwithstanding.
```

## 5. Expected outcome distribution

Most admitted lanes are expected to terminate `INSUFFICIENT` or falsified.
Cheap, fast, honest termination is the designed product of this registry. The
throughput metric is *lanes killed per quarter at low cost*, not lanes passed.

## 6. Correction record — 2026-09-21

The admission speed test originally read
`effect / sqrt(variance) * sqrt(independent units per month)`.
That is wrong. Aggregating a cross-section into one portfolio return leaves
`t(T) = IR_NET_ANN * sqrt(T_years)`; the units-per-month term cancels. Breadth
is not sample size.

Honest consequence, at the §3 per-lane bid (one-sided) and power 0.80,
required `t ~ 2.97`:

```text
IR_NET_ANN = 0.50  ->  ~35 years
IR_NET_ANN = 0.75  ->  ~16 years
IR_NET_ANN = 1.00  ->  ~9 years
IR_NET_ANN = 1.50  ->  ~4 years
IR_NET_ANN = 2.00  ->  ~2 years
```

A forward-only fast lane therefore requires net-of-friction `IR >= ~1.5`, which
is not a realistic ask in crowded cross-sectional space. The only remaining
honest accelerator is **pre-registered point-in-time history**: a lane may draw
its power from a frozen historical window declared before any look, in which
case the forward window is a one-sided falsifier and may not itself be re-used
to qualify.

This is the single most important finding of the adversarial review: the speed
of a "fast" lane comes from data depth and holding horizon, never from a wider
cross-section.
