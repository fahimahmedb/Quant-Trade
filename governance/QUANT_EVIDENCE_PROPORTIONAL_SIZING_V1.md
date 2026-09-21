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
KELLY_FRACTION      f_kelly = IR_post / sigma_strategy
DEPLOYED_FRACTION   f = lambda * f_kelly ,  lambda <= 0.25
POSTERIOR SHRINKAGE IR_post = IR_obs * tau^2 / (tau^2 + 1/T_years)
PRIOR               tau = 0.30   (sd of true IR across candidate strategies)
```

`tau = 0.30` encodes the honest base rate: almost all candidate strategies have
true IR near zero. Shrinkage at `IR_obs = 1.0`:

```text
T = 0.25 yr -> IR_post = 0.02     T = 2 yr  -> IR_post = 0.15
T = 0.5  yr -> IR_post = 0.04     T = 5 yr  -> IR_post = 0.31
T = 1    yr -> IR_post = 0.08     T = 10 yr -> IR_post = 0.47
```

Exposure is then continuous in evidence. There is no promotion event.

## 4. Why early deployment is cheap — the asymmetry

Log-growth of a deployed fraction `f`:

```text
G(f) = f*mu - f^2*sigma^2/2
```

If the true edge is zero, the loss is `f^2*sigma^2/2` — **quadratic** in size.
At `f = 0.02` of Kelly the economic cost of being wrong is second-order
negligible. Meanwhile:

```text
EXECUTION INFORMATION (slippage, rejects, partials, latency, borrow)
  is learned per ORDER, not per dollar. It does not depend on size at all.
```

So the first real order carries **full execution-information value at
quadratically negligible economic cost**. This is the entire argument for real
exposure years before any qualification, and it requires no protocol change.

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
P1 order-intent record distinct from realized fill
P2 realized-fill ingest (venue adapter)
P3 latched kill-switch and session-loss halt
P4 post-session invariant recompute (cash + marked positions vs NAV)
P5 owner authorization, dated, with an absolute notional cap
```

None exist today. `f = 0` until all five do. The difference from the ladder is
that these are **engineering** preconditions, resolvable in builder-weeks,
rather than **statistical** preconditions resolvable in builder-decades.

## 8. Refused

Raising `lambda` to compensate for a weak posterior. Deploying before P1-P5.
Using a realized P&L series produced at small `f` as evidence of edge — it is
underpowered by construction and §3 already prices that through `T`.
