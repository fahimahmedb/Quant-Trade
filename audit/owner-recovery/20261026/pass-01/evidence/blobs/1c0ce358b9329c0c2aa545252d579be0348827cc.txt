# QUANT — EVIDENCE-PROPORTIONAL SIZING V1 — 2026-09-21

`STATUS = PROPOSED / NON_AUTHORIZING`
`SUPERSEDES = discrete stage gates of QUANT_CAPITAL_EXPOSURE_LADDER_V1 §1-2`

## 1. The error this repairs

The exposure ladder managed uncertainty with **doors**: a sleeve waited at
`PAPER` until a protocol declared its edge proven, then jumped a stage. That is
the wrong instrument. A door forces a binary claim ("proven") out of a
continuous quantity (a posterior), and it makes the *first* unit of real
exposure arrive at the same time as the *thousandth*.

Uncertainty is managed by **quantity**, not by doors.

## 2. Separation of the two questions

```text
SCIENTIFIC CLAIM       "this effect exists"     -> confirmatory protocol
                                                   Form-4 rigour, one-look, G>=10
SIZING DECISION        "how much do I hold now" -> posterior expectation
                                                   no claim asserted
```

These were conflated. The confirmatory protocol is correctly severe for the
first question and massively over-specified for the second. Nothing in this
document weakens the first; it stops the second from waiting on it.

## 3. The sizing law

```text
KELLY_FRACTION      f_kelly = IR_post / sigma_floor
DEPLOYED_FRACTION   f = lambda * f_kelly * min(1, T/T_min) ,  lambda <= 0.25
POSTERIOR SHRINKAGE IR_post = IR_obs * tau^2 / (tau^2 + v_eff)
```

Three corrections against the first draft (adversarial review, 2026-09-21):

```text
v_eff       NOT 1/T. The plug-in 1/T assumes IID Gaussian returns and ignores
            estimation error in sigma itself, so it biases IR_post HIGH. Use a
            Newey-West or block-bootstrap effective variance. Fat tails and
            autocorrelation in strategy returns can make the true estimator
            variance several multiples of 1/T.
tau         NOT asserted. Calibrate empirically from this factory's own
            distribution of IR_obs, and apply a selection correction: IR_obs on
            an admitted lane is a best-of-N order statistic, not an unbiased
            draw. For a search-driven factory the sd of *genuine* IR is
            plausibly below 0.15, not 0.30.
sigma_floor sigma_strategy is itself a noisy small-sample estimate in the
            DENOMINATOR; a spuriously small value spikes f. Shrink sigma toward
            a regime-conservative prior and floor it. The T-indexed term
            min(1, T/T_min) caps f independently of the notional caps, so a
            lucky early IR_obs cannot produce size.
```

Illustrative shrinkage below uses the uncorrected `v_eff = 1/T` and `tau = 0.30`
purely to show the SHAPE. Both constants are placeholders pending calibration;
the real ones shrink harder. At `IR_obs = 1.0`:

```text
T = 0.25 yr -> IR_post = 0.02     T = 2 yr  -> IR_post = 0.15
T = 0.5  yr -> IR_post = 0.04     T = 5 yr  -> IR_post = 0.31
T = 1    yr -> IR_post = 0.08     T = 10 yr -> IR_post = 0.47
```

Exposure is then continuous in evidence. There is no promotion event.

Read the table honestly: two years of a *perfect-looking* track record
(`IR_obs = 1.0`) still buys a posterior of 0.15. Evidence is expensive. This is
the same conclusion the corrected power law reached from the other direction.

## 4. Early real exposure is an information purchase, not an investment

The first draft argued: log-growth is `G(f) = f*mu - f^2*sigma^2/2`, so if the
true edge is zero the loss is quadratic in `f` and a tiny `f` is nearly free.

**That argument is wrong, because it omits fixed costs.** With `C_fix` per
period (data, custody, commissions, minimum tickets, operations, reporting):

```text
G(f) = f*mu - f^2*sigma^2/2 - C_fix/Capital
```

Fixed cost per unit of deployed capital scales as `1/f`, so it dominates the
quadratic risk term entirely at small `f`. Break-even requires

```text
f_breakeven = C_fix / (mu * Capital) ,  mu = IR_post * sigma
```

### 4.0 The project's own parameters (found 2026-09-21, not assumed)

```text
src/quant/desk/execution.py   commission_bps            = 0.5
                              half_spread_bps           = 1.0
                              impact_bps_at_full_part.  = 10.0
                              max_participation         = 0.05
                              RESEARCH_ONE_WAY_COST_BPS = 5.0 (conservative envelope)
src/quant/desk/desk.py        MIN_ORDER_NOTIONAL        = 500
src/quant/book/ledger.py      initial_capital           = 1_000_000
src/quant/desk/risk.py        max_gross 1.50 · max_symbol 0.25 · halt -0.20
```

**Every friction in the system is proportional. There is no fixed-cost term
anywhere in the model.** `C_fix` is structurally absent, not set to a small
value. The D09 cost contract states `OMITTED_COST_IS_NOT_IMPLICIT_ZERO`; the
execution model omits fixed cost entirely, so all economic evidence produced so
far silently assumes `C_fix = 0`. That omission is what let the first draft's
"early deployment is nearly free" argument look sound.

Evaluated at `sigma = 0.15`:

```text
Capital   C_fix/yr   IR_post=0.04   IR_post=0.15   IR_post=0.31
 10 000       600       10.0x           2.7x           1.3x
 10 000     1 500       25.0x           6.7x           3.2x
 50 000       600        2.0x           0.53x          0.26x
250 000     1 500        1.0x           0.27x          0.13x
```

A break-even above `1.0x` is unreachable: it asks for more than the whole
account. **At early evidence and small capital, real deployment is negative
expected value by an order of magnitude, at any size.**

### 4.0b But the closure is capital-dependent, and reverses at 1M

At the capital the repository itself assumes (`initial_capital = 1_000_000`),
`f_breakeven` falls inside the admissible range:

```text
IR_post = 0.04   C_fix=600 -> 0.10x Kelly   C_fix=1500 -> 0.25x   C_fix=3000 -> 0.50x
IR_post = 0.15   C_fix=600 -> 0.03x Kelly   C_fix=1500 -> 0.07x   C_fix=3000 -> 0.13x
```

Crossover capital at which deployment becomes defensible (`f_breakeven <= lambda = 0.25`):

```text
IR_post   C_fix=600    C_fix=1500   C_fix=3000
0.04       400 000     1 000 000    2 000 000
0.08       200 000       500 000    1 000 000
0.15       106 667       266 667      533 333
0.31        51 613       129 032      258 065
```

So route R3 is **not closed in general — it is closed below roughly 100k-400k
of real capital and open above it**, depending on the fixed-cost base. The
earlier flat claim was an artefact of the 10 000 illustration.

```text
DECISIVE UNKNOWN = real capital and real annual fixed-cost base
Until both are supplied, no statement about early real deployment is decidable.
```

### 4.0c Minimum-ticket concentration

`MIN_ORDER_NOTIONAL = 500` against `max_symbol_ratio = 0.25` means small
capital cannot express a diversified sleeve at all: the ticket floor forces
concentration long before the risk limit binds. This interacts directly with
the lane doctrine, which wants many small decorrelated positions.

The consequence is not to wait. It is to stop pretending the first real orders
are an investment:

```text
INFORMATION BUDGET   an explicit R&D expense, owner-set, capped in currency
                     purpose: buy execution reality (slippage, rejects,
                     partials, latency, borrow, venue behaviour)
                     expected P&L: NEGATIVE. Stated in advance.
                     success metric: information obtained, never P&L

ECONOMIC DEPLOYMENT  requires f >= f_breakeven AND positive posterior EV net
                     of fixed costs. Governed by §3.
```

### 4.2 Structural separation (not a stated intention)

The refusal in §8 is worthless unless a record enforces it. Every order, fill
and attribution bucket carries:

```text
FUNDING_SOURCE = INFORMATION | ECONOMIC     immutable once written
```

```text
INFORMATION records  MAY     feed slippage(size), reject/latency/borrow stats,
                             operational diagnostics
                     MAY NOT enter IR_obs, tau or v_eff calibration (P7),
                             any performance claim, or any lane's evidence
ECONOMIC records     require f >= f_breakeven and positive posterior EV
```

Without the tag, an implementer could satisfy P1-P7 literally while feeding
minimal-size information-budget P&L into the very calibration that decides
future size — the reclassification §8 forbids, arriving through the back door.
The tag is written at order-intent time and is never editable: a record cannot
be reclassified after its outcome is known, which is the whole point.

Two budgets, two justifications, never mixed. The information budget is how the
system gets real fills years before economic deployment is defensible — the
original objective — without a single false claim about edge.

### 4.1 What canary-size fills do and do not teach

Execution information is *not* fully size-independent. Slippage, queue position
and adverse selection are convex in order size.

```text
LEARNED AT MINIMAL SIZE   venue plumbing, rejects, partials, latency,
                          borrow availability, operational failure modes
NOT LEARNED               the price-impact and adverse-selection regime at
                          the size eventually wanted
```

Before any `f` above minimal size is treated as execution-validated, a
documented `slippage(size)` function with at least two size points is required.
A minimal-size fill history is not evidence about a larger one.

## 5. What replaces the stages

Stage names survive only as *capability descriptions*, never as permissions:

```text
SHADOW / PAPER   no venue connection exists
LIVE_MINIMAL     a venue connection exists; f is whatever §3 returns
```

There is no `LIVE_CANARY -> SMALL_CAPITAL -> SCALE` sequence to climb. Size is
recomputed each period from the posterior. Growth and shrinkage are the same
mechanism running in opposite directions, so demotion needs no separate
machinery: a decaying posterior shrinks `f` automatically and continuously.

## 6. Hard bounds that remain discrete

Continuity applies to the *edge* term only. These are caps, not gates:

```text
LEVERAGE = 0                     (leverage moves mu and sigma together;
                                  t = IR*sqrt(T) does not improve, only ruin)
MAX_TOTAL_REAL_NOTIONAL          owner-set, absolute
MAX_LOSS_PER_SESSION             latched halt
PER_ORDER_NOTIONAL_CAP           absolute
KILL_SWITCH                      latched, manual re-arm
```

`f` from §3 is then `min(evidence-proportional size, all caps above)`.

## 7. Preconditions for any non-zero real `f`

```text
P1 order-intent record distinct from realized fill, carrying FUNDING_SOURCE
P2 realized-fill ingest (venue adapter), FUNDING_SOURCE propagated to the fill
   and to the Book attribution bucket
P3 latched kill-switch and session-loss halt
P4 post-session invariant recompute (cash + marked positions vs NAV)
P5 owner authorization, dated, with an absolute notional cap
P6 an INFORMATION BUDGET in currency, if exposure precedes f_breakeven
P7 empirical calibration of tau and v_eff on this factory's own history,
   with every FUNDING_SOURCE=INFORMATION record EXCLUDED from that history
```

None exist today. `f = 0` until all five do. The difference from the ladder is
that these are **engineering** preconditions, resolvable in builder-weeks,
rather than **statistical** preconditions resolvable in builder-decades.

## 8. Refused

Raising `lambda` to compensate for a weak posterior. Deploying before P1-P7.
Charging information-budget losses against an economic performance claim, or
the reverse. Treating minimal-size execution data as valid at target size.
Using a realized P&L series produced at small `f` as evidence of edge — it is
underpowered by construction and §3 already prices that through `T`.
