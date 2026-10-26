# Experiment Protocol

This protocol operationalizes `OBJECTIVE.md` and `AGENTS.md`.

Every material research attempt should be identifiable and auditable.

## Experiment lifecycle

Each experiment moves through:

`PROPOSED -> PREREGISTERED -> RUN -> JUDGED -> KILL | REVISE | VALIDATE_MORE | PROMOTE`

## Required preregistration fields

Before inspecting the final holdout result, record:

- `experiment_id`
- `created_at`
- `status`
- `hypothesis`
- `mechanism`
- `decision_question`
- `dataset`
- `data_source`
- `decision_time_information_set`
- `development_period`
- `final_test_period`
- `baseline`
- `primary_metric`
- `secondary_metrics`
- `cost_model`
- `fixed_parameters`
- `material_prior_attempts_known`
- `failure_criteria`
- `promotion_criteria`
- `command`
- `result_artifact`

## Holdout accounting

A holdout is considered **consumed** once its outcomes materially influence model, feature, strategy, parameter, universe, or execution choices.

A consumed holdout must never later be described as untouched.

If repeated research decisions are made from the same test period, explicitly record that fact and downgrade evidential confidence.

## Material attempt accounting

Record attempts that could reasonably influence selection of the final reported strategy/model.

Do not reset the attempt count because:

- a model was renamed;
- a parameter search happened in a notebook;
- a failed experiment was deleted;
- the result was never shown to the user;
- an agent considered the attempt informal.

The objective is to estimate selection pressure honestly.

## Minimum judgment for tradeable strategies

Where applicable, report:

- gross P&L/return;
- net P&L/return;
- CAGR or annualized log growth;
- maximum drawdown;
- volatility;
- Sharpe/Sortino as diagnostics;
- turnover;
- exposure/leverage;
- trade/bet count;
- transaction-cost assumptions;
- slippage assumptions;
- benchmark;
- OOS delta vs benchmark;
- cost sensitivity;
- parameter sensitivity;
- subperiod/regime behavior.

## Adversarial checklist

A positive result should trigger attempts to falsify it.

Check at least the relevant subset of:

- feature/label timing;
- leakage;
- look-ahead;
- train/test contamination;
- survivorship;
- corporate actions;
- revisions/vintage data;
- cost realism;
- delayed execution;
- spread/slippage stress;
- parameter perturbation;
- alternative split dates;
- outlier dependence;
- concentration in a few trades;
- multiple testing / model selection;
- simpler baseline dominance;
- regime instability.

## Decision semantics

### KILL
The hypothesis currently has no credible economic edge or fails basic validity. Do not rescue it through unconstrained search.

### REVISE
A specific, pre-stated deficiency can be tested with one or more bounded follow-ups. State exactly what new information could change the conclusion.

### VALIDATE_MORE
There is credible signal but insufficient evidence for promotion. Specify the missing validation layer.

### PROMOTE
Advance only to the next validation stage. Promotion from research does not mean unrestricted live deployment.

## Value-of-information rule

The next experiment should be selected based on the expected reduction of decision-relevant uncertainty per unit of time/data/complexity.

A cheap experiment that kills a major assumption is often more valuable than a large model build.

## Result integrity

Never edit a completed result artifact solely to make the outcome appear cleaner.

If a bug is found after evaluation:

1. preserve the original artifact;
2. document the defect;
3. create a new experiment/version;
4. rerun;
5. update the ledger transparently.
