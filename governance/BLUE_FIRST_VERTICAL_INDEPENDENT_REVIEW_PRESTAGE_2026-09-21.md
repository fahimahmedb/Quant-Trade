# BLUE — FIRST VERTICAL INDEPENDENT REVIEW PRESTAGE — 2026-09-21

## 0. Purpose

Prepare one bounded adversarial review of the future ONE BIG BUILD delivery.

This is NOT a review dispatch.
No reviewer branch is created yet because the exact Builder delivery SHA does not exist.

```text
INDEPENDENT_REVIEW_PRESTAGE = READY
INDEPENDENT_REVIEW_DISPATCHED = FALSE
```

## 1. Dispatch gate

Blue may dispatch exactly one independent reviewer only after:

1. Builder final handoff exists;
2. Builder reports:
   `BUILDER_VERTICAL_SHADOW_LOOP = READY_FOR_INDEPENDENT_REVIEW`;
3. Builder branch exact final HEAD is resolved live;
4. exact-head CI on that exact SHA is `COMPLETED / SUCCESS`;
5. changed paths are within frozen authority or any deviation is explicitly justified;
6. no unresolved `BLUE_DECISION_REQUIRED_*` remains.

Reviewer branch must be created from the exact Builder final SHA or otherwise bind that
exact immutable audited object without modifying it.

## 2. Reviewer role

Independent adversarial reviewer.

Not Blue.
Not Builder.
No repair implementation while reviewing.

Goal:
try to produce a false-positive admission, false confirmation, double mutation,
authority bypass or provenance break.

## 3. Mandatory attack domains

### A. Selective-import identity
- exact Forward/Economic imported blobs;
- no whole-branch merge;
- no silent edits to REUSE_AS_IS authorities;
- no alternate Book/scheduler/execution engine imported.

### B. Cohort / one-look authority
- 252-entry-session cohort identity;
- K_target=3/K_max=4;
- >=80-session inter-cohort gap;
- cross-cohort issuer/corporate merge;
- G>=10 structural guard;
- concentration guard;
- no fifth cohort;
- no target outcome/point/interval access before stopping;
- stopping path cannot call inference path;
- protocol/method parameters immutable after activation.

### C. Scientific method qualification
- exact interval implementation matches frozen method;
- random-denominator coordinate preserved;
- method qualification cannot self-authorize using target outcomes;
- missing/failed qualification -> DEVELOPMENT / fail closed;
- synthetic fixtures never become market evidence.

### D. D19 / provenance / coordinate
- missing outcomes cannot disappear;
- allocation weights precede outcomes;
- exact DeltaCoordinateBinding;
- no Sharpe/t-stat/net-return relabeling;
- missing/mismatch/unresolved coordinate paths remain distinct.

### E. Forward evidence laundering
- unrelated ledger growth cannot create fresh evidence identity;
- consumed evidence cannot be re-labeled FORWARD_CONFIRMATION;
- session/content-address identity collision/replay;
- caller Boolean cannot grant confirmation.

### F. Research -> Economic -> SHADOW
- Research VALIDATED alone not actionable;
- no auto-SHADOW from Research;
- Economic NO_TRADE/KILL/ineligible never promote;
- only durable Economic CONTINUE + eligibility can promote;
- restart around AssessmentRecord cannot duplicate or change authority.

### G. SIZE / costs / Risk
- Economic size remains authoritative;
- lifecycle cap only reduces;
- pre-size cost check binds actual ExecutionModel;
- post-size participation check cannot be skipped;
- stale/missing ADV fails closed;
- Risk remains independent and can veto after Economic CONTINUE;
- no weakened Risk fixture/path hidden in production behavior.

### H. Fill / Book singular authority
- only `ExecutionModel.fill` feeds Book;
- Economic opening model never books;
- entry/exit identities are deterministic;
- replay cannot double-fill;
- crash after intent/apply cannot double mutate Book;
- conflicting operation id fails closed;
- no second bankroll/ledger.

### I. Learning / durability
- processed identities survive >200 visible history;
- restart + old replay no duplicate;
- semantic conflict detected;
- later counterfactual cannot mutate original prospective decision;
- NO_TRADE/VETO/INSUFFICIENT/BOOKED all durable.

### J. End-to-end economic behavior
- Q1-Q8 answer or explicit fail-closed state;
- Q9 raw wealth contribution persisted;
- Q10-Q12 history persisted but not overclaimed;
- positive synthetic path proves plumbing only;
- real missing evidence remains NO_TRADE.

## 4. Required negative controls

At minimum independently reproduce:
- G=9 cannot infer;
- K=4/G<10 cannot continue to K=5;
- outcome access attempt before stop rejected;
- invalid method qualification rejected;
- coordinate mismatch rejected;
- forward evidence reuse rejected;
- Economic CONTINUE + post-size cost fail => no fill;
- Economic CONTINUE + Risk veto => no fill;
- replay after Book apply => no double fill;
- >200 Learning replay => no duplicate;
- same ids + changed semantic payload => conflict.

## 5. Adjacent-search bound

Reviewer may inspect adjacent surfaces only where needed to falsify a mandatory invariant.

Do not restart a general Product architecture review.

Do not demand unrelated polish.

A finding is blocking only if it demonstrates:
- false-positive economic/scientific admission;
- authority bypass;
- evidence laundering;
- double Book mutation;
- replay/conflict corruption;
- missing mandatory provenance;
- frozen-spec contradiction.

## 6. Allowed verdicts

`ASTRA_FIRST_VERTICAL_REVIEW = PASS_REPOSITORY_EVIDENCE`

or:

`ASTRA_FIRST_VERTICAL_REVIEW = BLOCKED_<EXACT_REPRODUCED_REASON>`

Do not use scores/rankings.

## 7. Final reviewer handoff

Planned path:

`handoff/ASTRA_FIRST_VERTICAL_INDEPENDENT_REVIEW_2026-09-21.md`

Must bind:
- exact Builder final SHA;
- exact Builder CI;
- exact changed paths;
- tests independently executed;
- every mandatory attack-domain disposition;
- exact reproduced blockers;
- unchanged target-host/capital state.

## 8. Exit discipline

One reviewer cycle.

If PASS:
return to Blue for integration disposition.

If BLOCKED:
route only the exact defect to one bounded repair owner.

No recurring red-team loop absent a concrete new contradiction.
