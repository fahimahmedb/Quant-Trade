# Decision Gate and Abstention Doctrine

## Why this exists

The autonomous system must not be rewarded for trading frequently.

Its job is to allocate capital only when the expected economic advantage is strong enough to justify taking risk, paying costs, and consuming scarce capital.

A valid autonomous decision set therefore includes:

- `TAKE`
- `REDUCE`
- `HOLD`
- `EXIT`
- `REJECT`
- `NO_TRADE`

`NO_TRADE` is a first-class action, not a failure state.

## Core principle

The system should optimize expected capital growth, not action frequency.

A model that generates many signals but rejects most of them can be superior to a model that trades every signal.

The relevant question is not:

> Did the system find something to trade?

It is:

> Is this candidate sufficiently attractive, after uncertainty and implementation costs, that allocating capital is better than preserving optionality for a better opportunity?

## Separation of discovery from execution

The Alpha Factory may generate many research candidates and live signals.

The execution layer must not treat those candidates as orders.

Use a decision funnel:

`signal/candidate`
`-> evidence check`
`-> economic edge estimate`
`-> uncertainty calibration`
`-> cost/liquidity check`
`-> portfolio interaction check`
`-> risk-of-ruin / tail check`
`-> capital opportunity-cost check`
`-> TAKE or REJECT`

Discovery is permissive.

Capital allocation is selective.

## Signal router

Every live or paper signal should pass through a structured router before it can become a position.

Minimum router fields:

- `signal_id`
- `strategy_id`
- `timestamp`
- `instrument`
- `direction / trade expression`
- `expected_horizon`
- `expected_gross_edge`
- `expected_costs`
- `expected_net_edge`
- `uncertainty / confidence interval`
- `liquidity / capacity`
- `current portfolio overlap`
- `systematic exposure contribution`
- `tail / gap risk`
- `data freshness`
- `model regime status`
- `decision`
- `rejection_reason` when rejected

## Reject by default under uncertainty

When a candidate requires assumptions that are currently unverifiable, the default should be to reject or defer capital allocation rather than silently assume favorable values.

Examples:

- unclear timestamp semantics;
- stale data;
- unknown fill quality;
- cost estimate large relative to expected edge;
- strategy outside validated regime;
- hidden portfolio concentration;
- signal conflict with a stronger validated strategy;
- live behavior materially outside research distribution.

This is not conservatism for its own sake. It protects the terminal objective from low-quality bets.

## Selectivity is not the same as low risk

A highly selective system may still take a large position when the expected edge is unusually strong and the position is economically justified.

Do not encode an objective such as 'always be cautious' or 'always keep exposure low'.

The doctrine is:

> **Be inactive when the opportunity is weak; be appropriately sized when the opportunity is strong.**

Sizing remains a function of estimated edge, uncertainty, costs, portfolio interactions, liquidity, and capital constraints.

## Opportunity cost of capital

Capital held in a mediocre trade cannot be allocated to a better trade.

Therefore every candidate should be compared not only to `cash/no trade`, but also to the best currently available alternatives when the portfolio is capacity constrained.

The router should eventually support ranking competing opportunities by expected marginal contribution to future wealth.

## Rejection reasons are strategic data

Rejected signals are not discarded silently.

Record structured rejection reasons such as:

- insufficient expected net edge;
- excessive uncertainty;
- high implementation cost;
- stale or ambiguous data;
- beta/factor duplication;
- insufficient liquidity;
- portfolio concentration;
- regime mismatch;
- failed validation state;
- better competing opportunity;
- tail risk inconsistent with estimated edge.

Over time, rejection statistics should improve scanners and research allocation.

For example, if a scanner produces many candidates that are rejected for the same reason, Quant should reduce research budget allocated to that scanner or redesign it.

## Calibration matters more than confidence language

Do not allow an agent's verbal confidence to route capital.

A statement such as `87% confidence` has no meaning unless the system can define and test what that number represents.

Where probabilistic confidence is used, calibrate it against historical outcomes.

Prefer measurable quantities such as:

- posterior probability under an explicit model;
- empirical hit-rate conditioned on comparable signals;
- expected return distribution;
- prediction interval;
- expected shortfall;
- probability net edge exceeds zero after costs.

## Refusal quality should be measured

The system should evaluate not only trades taken, but also decisions rejected.

Possible diagnostics:

- fraction of rejected signals that would have lost money after costs;
- fraction of rejected signals that would have been profitable;
- opportunity cost of false rejections;
- value added by each gate;
- marginal P&L contribution of selection versus raw signal generation;
- calibration of rejection thresholds by regime.

The objective is not to maximize rejection rate.

It is to maximize economic value from selectivity.

## Research implication

Every strategy should be evaluated in at least two layers when relevant:

1. **raw signal quality** — does the signal contain information?
2. **routing / selection quality** — can the system distinguish when the signal is worth trading?

A mediocre unconditional signal may contain highly profitable conditional subsets.

Conversely, a statistically significant signal may be economically unattractive after routing constraints.

This distinction should influence hypothesis generation and backtesting.

## Architecture implication

The long-run system should separate:

`Scanner / Signal Generator`
from
`Decision Router`
from
`Position Sizer`
from
`Execution Engine`
from
`Exit Controller`

Each layer has a different job.

The signal generator proposes.

The router decides whether the opportunity deserves capital.

The sizer determines how much capital is economically justified.

The execution engine minimizes implementation loss.

The exit controller continuously reevaluates whether the original edge still exists.

## Alignment rule

Do not trade to demonstrate autonomy.

Do not reject trades to demonstrate caution.

Choose the action that maximizes expected future capital conditional on current evidence.

Sometimes the most intelligent autonomous action is:

> **NO TRADE. KEEP SEARCHING.**
