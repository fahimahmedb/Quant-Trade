# BLUE — ADVERSARIAL REVIEW AND DECISIONS: THREE-TIER PRODUCTIZATION — 2026-09-21

`STATUS = DECIDED / STILL_NON_AUTHORIZING`

Two independent adversarial reviews were run against the 2026-09-21 packet, one
on research integrity, one on runtime/operations, with disjoint questions. Both
returned blocking findings. The packet has been amended; this file records what
changed, what was rejected, and the decisions taken.

## 1. Blocking correction — the speed law was wrong

The packet's own admission test read
`effect / sqrt(variance) * sqrt(independent units per month)`.

That is incorrect. Aggregating a cross-section into one executable portfolio
return leaves `t(T) = IR_NET_ANN * sqrt(T_years)`; the units-per-month term
cancels. Cross-sectional breadth is not sample size — it enters only through
`IR = IC * sqrt(breadth)`, and residual correlation collapses it (500 names at
mean residual pairwise `rho = 0.05` give effective breadth ~19, not 500).

Required decision time at power 0.80, required `t ~ 2.97`:

```text
IR_NET_ANN = 0.50 -> ~35 yr    IR = 1.00 -> ~9 yr    IR = 1.50 -> ~4 yr
```

Consequence, stated plainly: **the acceleration the original proposal expected
from a larger cross-section does not exist.** A forward-only fast lane needs
net-of-friction `IR >= ~1.5`, which is not a credible ask in crowded
cross-sectional space. The only honest accelerator left is pre-registered
point-in-time history — which was the weakest-emphasis item in the original
proposal and is now the load-bearing one.

This also corrects my own §2 challenge text of earlier today, which argued the
right conclusion (observations are not proof) from the wrong formula.

## 2. Decisions taken

### D1 — Phase-1 gate: `RAIL_B_VERTICAL_INTEGRATED` alone

Rejected: "later of t0 and Rail-B". Phase 1 exercises `clock.py`, `desk/` and
`book/` only; Rail A's t0 qualifies Form-4 *capture*. Gating runtime continuity
evidence on a currently blocked data item parks weeks of work behind it, and
that evidence is precisely what should exist before t0 declares a capture cursor
that must not be replayed twice. Form-4 accrual remains gated on `t0 DECLARED`,
and Phase 2 lane admission retains the later-of gate.

### D2 — 2 concurrent lanes, mFDR alpha-investing

Rejected: 3 lanes with a fixed non-refunding family-wise budget. It was
self-contradictory — terminally exhausted after three kills while the registry
declares cheap kills to be the product — and FWER is the wrong error concept for
a multi-year factory whose loss is economic and proportional.

```text
MAX_CONCURRENT_ADMITTED_LANES = 2    ERROR_CRITERION = mFDR <= 0.05
ALPHA_WEALTH_W0 = 0.025              PER_LANE_BID = min(W/2, 0.010)
PAYOUT_OMEGA = 0.020, credited only after forward acceptance
```

Alpha refunds only on a rejection that survives forward confirmation: a churning
researcher goes broke, a productive one never exhausts.

### D3 — Authorization past `PAPER`: mandatory, and honest about enforcement

Confirmed mandatory, dated and expiring. But `clock.py::tick()` has no
authorization scan and `ControlState` holds no authorization list, so nothing
could ever fire "expired". Expiry is therefore recorded as **owner-manual**, and
every expiring artifact added later must name its enforcing surface. A control
nobody executes is worse than an acknowledged manual step.

### D4 — No source change now (my decision, not a review finding)

The runtime review is right that `LedgerState.mode` is a free-form, unvalidated,
never-written string, and that attribution buckets and `nav_history` points
carry no mode — so after any future demotion the Book could not say which P&L
accrued under which regime, irreversibly, since history is append-only. The
minimal fix is two lines: validate `mode` against `{"paper_shadow"}` and refuse
`apply_fill` otherwise; stamp `mode` onto each attribution bucket and NAV point.

I am **not** making it now. Those files are Rail B's, currently
`READY_FOR_INDEPENDENT_REVIEW`, and editing them from a governance branch would
put a second author on the surface under review for a defect that cannot bite
until a second mode exists. It is specified here and executes as the first item
after Rail-B integration.

## 3. Amendments applied to the packet

```text
REGISTRY   speed law corrected; §3 replaced with alpha-investing; §3.1
           anti-laundering rules E1/E2/E3 added; §4 isolation split into
           EDGE_EVIDENCE (never transfers) vs INFRASTRUCTURE_EVIDENCE
           (shared, fingerprinted); correlated-sleeve portfolio rule added;
           §6 correction record added
TEMPLATE   §6 rewritten to the corrected law; §6b search accounting added
           (DATA_CUTOFF, SEARCH_DEPTH, universe/parameter hashes,
           LANE_SIGNATURE); forward window demoted to one-sided falsifier
           where power comes from point-in-time history
LADDER     §4 demotion: "whole desk to PAPER" replaced by a halt (it
           contradicted §1 and wrote state during the one condition in which
           state is untrustworthy); demotion given a deterministic
           operation_id; prerequisite invariant detector named; operative
           safety stated — no decay monitor exists, so LIVE_CANARY is
           unreachable today, by design
           §5 expiry declared owner-manual with no enforcing surface
ROADMAP    Phase 1 gate decoupled per D1; Phase 3 resized from one bullet to
           6-10 builder-weeks and reclassified as a quarter-scale workstream
           with no owner, no longer parallel to Phase 2; execution
           reconciliation split into ORDER_INTENT_RECORD (buildable now) and
           REALIZED_FILL_INGEST (needs a broker adapter that does not exist);
           qualification window widened 6-18 -> 12-24 months
```

## 4. Holes closed

```text
E1 hypothesis-generation laundering  -> digest binds DATA_CUTOFF + SEARCH_DEPTH,
                                        bid multiplied by search depth
E2 post-hoc universe/parameters      -> universe and parameters hashed into the
                                        digest on an append-only ref before the
                                        harness may open outcome data
E3 cosmetic re-proposal              -> LANE_SIGNATURE; a matching re-test
                                        inherits spent alpha and pays 2x bid
E4 same bet sized twice              -> sleeves from distinct lineages whose
                                        shadow returns correlate > 0.5 aggregate
                                        as ONE risk unit at SIZE/RISK
```

## 5. What did not change

The frozen Form-4 protocol. `K_target=3`, `K_max=4`, 252-session cohorts,
one-look, pooled post-merge `G>=10` — untouched, and now with a second
independent reason to leave it alone: the corrected power law shows that the
original protocol was not being conservative for its own sake, it was pricing
the real cost of evidence.
