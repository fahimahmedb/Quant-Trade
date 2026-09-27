# BLUE — ECONOMIC ACCELERATION: CONVERGENCE NOTE — 2026-09-21

`STATUS = ITERATION_2 / NON_AUTHORIZING`

Two adversarial rounds were run against the acceleration packet. The packet did
not survive intact. This note records where it converged, because the honest
answer is narrower than the question hoped for.

## 1. Three routes to fast economic value were proposed. All three are closed.

```text
R1  WIDER CROSS-SECTION      closed 2026-09-21 (earlier packet)
    breadth is not sample size; 500 names at rho=0.05 give N_eff ~19
    t(T) = IR*sqrt(T); the units-per-month term cancels

R2  MANY WEAK LANES          closed by this round
    IR_total = IR*sqrt(k/(1+(k-1)rho)), ceiling IR_lane/sqrt(rho)
    k=25 at rho=0.2 gives 0.62, not 1.50; past k~10 the marginal lane is ~free
    and the adopted alpha-wealth process funds FOUR lanes, not twenty-five

R3  DEPLOY TINY, EARLY       CONDITIONALLY closed — corrected 2026-09-21
    fixed costs scale as 1/f and dominate the quadratic risk term
    f_breakeven = C_fix/(mu*Capital)
    at 10k capital, IR_post=0.04: 10x the account -> closed
    at 1M capital (the repo's own initial_capital), same IR_post: 0.10-0.25x
    Kelly -> OPEN
    crossover ~100k-400k depending on the fixed-cost base
    The flat "closed" claim was an artefact of the 10k illustration.
```

Each was closed by arithmetic, not by opinion, and each closure was found by an
adversary rather than by the author.

## 2. What survives, and it is not nothing

```text
OPERATIONAL VALUE     weeks. A system that decides, books and learns daily.
                      Requires no statistics and no capital. Available as soon
                      as Rail B integrates.

EPISTEMIC VALUE       weeks-to-months. Cheap lane death. Bounded now by alpha
                      wealth (4 lanes) rather than by builder time, which is a
                      budget decision the owner can take knowingly.

COST REDUCTION        days. Deterministic payoff, no sqrt(T). Raises feasible
                      frequency, therefore IR in every lane simultaneously.
                      The only certain work in the system.

EXECUTION REALITY     purchased, not earned. An explicit information budget
                      buys venue plumbing, rejects, partials, latency and
                      borrow behaviour at minimal size, with P&L declared
                      negative in advance. This is how real orders arrive
                      years before economic deployment is defensible.

PIT DEPTH             the only honest accelerator of T. Shared Data Plane
                      asset, amortised across all lanes.
```

## 3. The corrected answer to "enjoy the robot earlier"

Operational and epistemic value arrive in weeks and were never gated on edge.
Execution reality is bought as R&D at a stated loss. **Economic value at small
capital does not arrive early, by arithmetic, and no sizing rule, lane count or
protocol change alters that.** The programme should therefore be judged on M1
and M2, with M3 reported and never chased.

Stating this plainly is the deliverable. A packet that had "succeeded" here
would have been a packet that hid one of the three closures.

## 3b. Correction to §1 and §3

"All three routes closed" holds for R1 and R2 unconditionally. R3 is closed
only below ~100k-400k of real capital. The statement "economic value at small
capital does not arrive early" is therefore correct as written — but it is a
statement about *small* capital, and the repository's own model assumes 1M,
where the conclusion inverts.

The system also contains no fixed-cost term at all
(`src/quant/desk/execution.py` is proportional-only), while the D09 contract
requires `OMITTED_COST_IS_NOT_IMPLICIT_ZERO`. All economic evidence produced so
far silently assumes `C_fix = 0`. That is a friction-model defect independent
of this packet, and it is what made the first draft's argument look sound.

## 4. Live contradictions remaining

```text
C1  ALPHA WEALTH vs LANE AMBITION
    4 fundable lanes against a doctrine that wants ~10 decorrelated mechanisms.
    OWNER DECISION: re-capitalise alpha wealth explicitly, or accept 4-at-a-time
    with refills earned only through forward-confirmed rejections.

C2  INFORMATION BUDGET SIZE
    Unset. Requires a currency figure from the owner; nothing proceeds to real
    orders without it, and it is an expense, not an allocation.

C2b REAL CAPITAL AND FIXED-COST BASE
    The single most decision-relevant unknown in this packet. It decides
    whether R3 is open or closed. Not discoverable from the repository:
    initial_capital = 1_000_000 is a simulation default, not a statement
    about the owner's capital.

C2c FIXED COST ABSENT FROM THE FRICTION MODEL
    Builder work, independent of this packet: add a fixed/periodic cost
    dimension to ExecutionModel and to the research cost envelope, per the
    D09 invariant OMITTED_COST_IS_NOT_IMPLICIT_ZERO.

C3  CALIBRATION DEBT
    tau, v_eff and IC(f) are all placeholders. Each must be measured on this
    factory's own history before any f above zero.
```

These are owner decisions and measurement work, not open design questions.

## 5. Closed in iteration 3

```text
INFORMATION-BUDGET LAUNDERING
The separation of information-budget from economic P&L was a stated refusal
with no enforcing precondition. Now structural: FUNDING_SOURCE is written at
order-intent time, is immutable, propagates to the fill and the Book
attribution bucket, and INFORMATION records are excluded from tau/v_eff
calibration by P7. A record cannot be reclassified once its outcome is known.
```

Iteration 3 review found no remaining blocking defect, and independently
re-derived the four arithmetic results above.
