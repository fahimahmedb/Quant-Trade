# FAST_VERTICAL_V1 — PRE-REGISTRATION TEMPLATE — 2026-09-21

`STATUS = TEMPLATE / UNFILLED`

This template must be completed, digested and dated **before any outcome under
the protocol is observed**. An unfilled field blocks admission. Filling a field
after first observation invalidates the lineage.

## 1. Identity

```text
LINEAGE_ID        =
ADMISSION_DATE    =
PREREGISTRATION_DIGEST =
ALPHA_SHARE_DRAWN =
AUTHOR            =
```

## 2. Economic hypothesis

State the economic mechanism in one paragraph: who is on the other side, why
they trade at a loss to this strategy, and why that is expected to persist.
A statistical pattern with no mechanism is not admissible.

```text
MECHANISM         =
COUNTERPARTY      =
PERSISTENCE_ARGUMENT =
CROWDING_ASSESSMENT  =
```

## 3. Executable object

The researched object and the paper/shadow object must be the same object.

```text
UNIVERSE (fixed)      =
ENTRY_RULE            =
EXIT_RULE             =
HOLDING_HORIZON       =
REBALANCE_SCHEDULE    =
POSITION_CONSTRUCTION =
LEVERAGE              = 0
SHORTING              = declared here or forbidden
```

## 4. Data

```text
SOURCES               =
POINT_IN_TIME_BASIS   =
SURVIVORSHIP_CONTROL  =
CORPORATE_ACTIONS     =
RESTATEMENT_POLICY    =
UNIVERSE_AS_KNOWN_AT_DATE =
PROVENANCE_FINGERPRINTS   =
```

Reconstructed history must name the archive, the reconstruction procedure and
the residual bias that could not be eliminated.

## 5. Frictions and capacity

```text
FEES · SPREAD · SLIPPAGE_MODEL · FINANCING · BORROW
PARTICIPATION_CAP · IMPACT_MODEL · CAPACITY_CEILING
MINIMUM_ECONOMICALLY_USEFUL_EFFECT (net, after all of the above) =
```

## 6. Power derivation (mandatory)

```text
INDEPENDENT_UNIT          = one non-overlapping holding-period return of the
                            executable portfolio (fixed by §3, not chosen here)
IR_NET_ANN_ASSUMED        =   (annualised, AFTER all §5 frictions)
IR_JUSTIFICATION          =   (IC assumed, breadth, residual correlation)
IMPLIED_TIME_TO_DECISION  = (2.97 / IR_NET_ANN)^2 years
POWER_SOURCE              = FORWARD_ONLY | PREREGISTERED_PIT_HISTORY | BOTH
PIT_WINDOW (if used)      =   (declared before any look)
```

Breadth is not sample size. Do not enter a units-per-month term; it cancels.

Admission test: `IMPLIED_TIME_TO_DECISION` must be materially shorter than
`FORM4_CONFIRMATORY_V1`. Forward-only lanes need `IR_NET_ANN >= ~1.5` to clear
it — if the lane cannot honestly claim that, it must buy its power from
pre-registered point-in-time history or it is not admissible.

## 6b. Search accounting (mandatory, binds the digest)

```text
DATA_CUTOFF     =
SEARCH_DEPTH    =   (count of variants inspected on data before cutoff)
UNIVERSE_FILE_HASH =
PARAMETER_FILE_HASH =
LANE_SIGNATURE  = (universe hash, signal family, horizon bucket, side)
ANCESTOR_SIGNATURE (if a re-test) =
```

The bid is multiplied by `SEARCH_DEPTH`. Undeclared inspection of post-cutoff
data voids the lineage.

## 7. Stopping rule and looks

```text
LOOK_SCHEDULE     = (fixed in advance)
STOPPING_RULE     =
MAX_HORIZON       =
TERMINATION_STATES = QUALIFIED · FALSIFIED · INSUFFICIENT
```

No unscheduled look. No extension after an unfavourable look.

## 8. Pre-declared falsifiers

List the observations that would kill this lane. A lane with no stated
falsifier is not admissible.

```text
F1 =
F2 =
F3 =
```

## 9. Forward confirmation

Even with a clean point-in-time reconstruction, a forward shadow/paper window
is required before any exposure above `PAPER`. Where `POWER_SOURCE` is
point-in-time history, the forward window is a one-sided falsifier only: it can
kill the lane, it cannot be re-used as independent qualification.

```text
FORWARD_WINDOW_LENGTH =
FORWARD_ACCEPTANCE    =
```
