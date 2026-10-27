# COUNTERFACTUAL ORGANIZATION

The alternatives below are qualitative. No fake timing or probability precision is assigned.

| Option | Topology | Scientific risk | Autonomy risk | Promotion risk | Time-to-information | Architecture churn | Blocked-work risk | Contamination risk | Reversibility | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| STRICTLY_SEQUENTIAL_PROMOTION_FIRST | promotion -> autonomy -> science | MEDIUM: delays clean prospective test and invites infrastructure focus | LOW once reached | LOW once reached | WORST | MEDIUM/HIGH | HIGH | MEDIUM because long delay increases context drift | MEDIUM | REJECT as first path |
| STRICTLY_SEQUENTIAL_SCIENCE_FIRST | science -> autonomy -> promotion | LOW if isolated boundary enforced | MEDIUM/HIGH until later | MEDIUM/HIGH until later | GOOD | LOW | MEDIUM | LOW | HIGH | VIABLE but unnecessarily serial after science |
| PARALLEL | science || autonomy || promotion | LOW if authority/identity firewalls are strict | MEDIUM | MEDIUM | BEST | MEDIUM | LOW | MEDIUM if teams mutate shared targets concurrently | MEDIUM/HIGH | VIABLE only with immutable bases and no shared product writes |
| PARALLEL_THEN_JOIN | science lane || autonomy-evidence lane || promotion-evidence lane; join by same-data replay | LOW | LOW/MEDIUM | LOW/MEDIUM | VERY GOOD | LOW/MEDIUM | LOW | LOW because science trial stays frozen and join replay is not a new trial | HIGH | BEST |
| MINIMAL_SCIENCE_FIRST | only one authorized prospective witness to durable memory; defer other work | LOWEST for scientific contamination | HIGH/UNKNOWN remains | HIGH/UNKNOWN remains | VERY GOOD for scientific information | LOWEST | LOW for science, HIGH for later integration | LOWEST | HIGHEST | STRONG fallback if capacity is constrained |
| PRIOR_ROADMAP_STYLE | target -> integrity -> UST continuation -> identity/denominator -> renewal -> transport -> release/pilot | LOW/MEDIUM eventually | LOW eventually | LOW eventually | SLOWER for first science | MEDIUM | HIGH because UST/renewal may block unrelated science | MEDIUM due historical UST focus | MEDIUM | GOOD long-program checklist, not best critical-path order |

## BEST option

BEST_ORGANIZATION=`PARALLEL_THEN_JOIN_WITH_MINIMAL_SCIENCE_FIRST_PRIORITY`

Start one clean scientific witness immediately after its authority and source gate. In parallel, run evidence-first autonomy qualification and exact-SHA promotion qualification. Do not merge these lanes merely to make a single branch look complete.

### Join semantics

The join occurs only after:

1. the scientific lane has one immutable result and memory record;
2. the autonomy lane proves the canonical task->sink route;
3. the promotion lane identifies an exact qualified/promoted release if Owner chooses to promote;
4. the same frozen scientific protocol and the same frozen dataset are replayed through the canonical promoted route;
5. output equality and provenance equality are checked.

The join replay is an engineering equivalence witness, not a new confirmation trial.

### Why this dominates the alternatives

It minimizes time-to-scientific-information without weakening autonomy or promotion claims. It also prevents a failed autonomy join, hosted gate or Owner promotion decision from censoring a scientifically legitimate negative/park result. Immutable bases and no shared production mutation keep parallelism from becoming branch contamination.
