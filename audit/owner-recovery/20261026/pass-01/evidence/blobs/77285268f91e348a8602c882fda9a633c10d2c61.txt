# Independent Acceptance Gate

This file defines the minimum logic for evaluating a candidate without trusting the research narrative that produced it.

## Principle

A candidate is not accepted because its author or agent believes it is promising.

Acceptance depends on independently inspectable evidence.

## Research-stage gate

A candidate may move from exploratory research toward deeper validation only if all applicable conditions are satisfied:

1. The hypothesis and mechanism are explicit.
2. The information set respects decision-time availability.
3. The final test is clearly separated from development data, or any contamination is explicitly disclosed.
4. Relevant costs are included for a tradeable strategy.
5. The candidate beats an appropriate baseline economically, not only statistically.
6. The result is not obviously explained by a small number of outliers/trades.
7. Minor parameter/timing perturbations do not immediately destroy the result.
8. Known multiple-testing/model-selection pressure is disclosed.
9. The experiment is reproducible from an explicit command.
10. The research ledger is updated.

Failure of one condition does not automatically imply the idea is worthless, but it blocks strong claims and promotion until resolved.

## Strong evidence indicators

Evidence becomes more credible when several of the following are true:

- positive net OOS economics;
- consistency across non-overlapping subperiods;
- consistency across related but distinct instruments or samples where economically justified;
- plausible economic mechanism;
- reasonable cost robustness;
- low dependence on exact parameters;
- limited research degrees of freedom;
- sufficient independent observations;
- no material leakage or timing ambiguity;
- result survives an adversarial reimplementation/review.

## Automatic reasons to block promotion

Block promotion if any of these are unresolved:

- look-ahead or leakage;
- no realistic transaction-cost model for a high-turnover strategy;
- final-test data repeatedly used for tuning while still claimed as OOS;
- performance depends on impossible execution assumptions;
- material code/result cannot be reproduced;
- strategy requires data unavailable at decision time;
- net edge disappears under modest cost/slippage stress;
- result is selected from a large undisclosed search;
- catastrophic or undefined behavior under plausible market states.

## Capital progression

No research result should jump directly to unrestricted live capital.

The default progression is:

`RESEARCH -> INDEPENDENT_REVIEW -> PAPER/SHADOW -> LIMITED_CAPITAL -> SCALE_REVIEW -> SCALED_CAPITAL`

At each stage, compare observed behavior against the assumptions used to justify promotion.

## Judge output

An independent Judge pass should return:

- `ACCEPT_FOR_NEXT_STAGE`
- `NEEDS_MORE_EVIDENCE`
- `REJECT`

with explicit reasons and references to raw artifacts.

The Judge should not reward sophistication. It should reward credible economic evidence.
