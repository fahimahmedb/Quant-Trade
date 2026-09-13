# Autonomous Research Pipeline

This file defines the minimum functional pipeline Codex should build first.

## Stage 1 — SCAN

Broad, inexpensive candidate generation.

Input: point-in-time market / filing / derived data.

Output: `OpportunityTicket` with observable facts only.

No strategy claim is made at this stage.

## Stage 2 — FILTER

Remove obvious low-value candidates before expensive reasoning.

Possible reasons:

- insufficient deviation;
- stale data;
- missing point-in-time fields;
- insufficient liquidity proxy;
- duplicate candidate;
- already-known dead pattern.

The purpose is to reserve deep reasoning for a smaller set of candidates.

## Stage 3 — HYPOTHESIS

A deeper reasoning pass proposes a falsifiable mechanism and a research expression.

Required outputs:

- mechanism;
- expected horizon;
- required variables;
- benchmark;
- falsification condition;
- key implementation assumptions.

## Stage 4 — TEST

Implement the smallest credible historical test.

Keep the data timestamp semantics explicit and produce machine-readable results.

## Stage 5 — VALIDATE

Attack the result.

Relevant checks may include:

- causality / timing;
- leakage;
- out-of-sample behavior;
- beta/factor attribution;
- sensitivity to costs;
- parameter perturbation;
- regime dependence;
- multiple-testing pressure.

Outcome:

- `REJECT_RESEARCH`
- `REVISE`
- `VALIDATED_FOR_PAPER`

## Stage 6 — PAPER FILTER

For validated strategies, evaluate whether every raw signal should be acted on in paper/shadow simulation.

Possible outcomes:

- `PAPER_ACCEPT`
- `PAPER_REJECT`
- `NO_TRADE`

Track the counterfactual outcome of rejected signals when possible. The project should learn whether selectivity improves the simulated economics.

## Stage 7 — MEMORY

Every ticket ends with a lesson.

Memory should capture:

- what pattern was tested;
- why it survived or failed;
- rejection stage;
- data problems;
- cost problems;
- sensitivity problems;
- whether the scanner deserves more or less future research budget.

## Stage 8 — CONTINUE

The orchestrator selects the next highest-value research action automatically.

An ordinary failed test is not a reason to wait for human instructions.
