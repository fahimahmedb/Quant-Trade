# OWNER OD01–OD03 DECISION

Date: 2026-10-04  
Scope: OD01–OD03 only  
Author: PROJECT_OWNER  
Artifact type: OWNER_DECISION

## Decision status

OD01 = RATIFIED  
OD02 = PARTIALLY_RATIFIED  
OD03 = PARTIALLY_RATIFIED

ECONOMIC_AUTHORITY = 0  
ECONOMIC_DECISION_WEIGHT = 0  
COMPOSITE_ECONOMIC_AUTHORITY = 0

## Authority chain

OWNER_DECISION_BASIS:

BLUE_REPAIR_PLAN_BRANCH =  
blue/weather-v4-research-design-repair-2026-10-04

BLUE_REPAIR_PLAN_SHA =  
06c0c8cf7e0a16b63940d1b2167642dd9dcf889e

BLUE_OD01_OD03_DECISION_SUPPORT_BRANCH =  
blue/weather-v4-research-design-repair-2026-10-04

BLUE_OD01_OD03_DECISION_SUPPORT_SHA =  
af77165c26308bc085fabf44282e2bacd09bdbb4

OWNER_DECISION_SCOPE =  
OD01_OD03_ONLY

This artifact is a new owner-authored decision.  
It does not rewrite or replace the Blue Repair Plan or the Blue Decision Support artifact.

## OD01 — Ratified

NORTH_STAR =  
Long-run net real wealth growth after all real frictions.

ECONOMIC_PREFERENCE =  
Probability-first.

PRIMARY_ESTIMAND_CLASS =  
Probability of positive finite-horizon net real wealth change.

EXPECTED_NET_ECONOMICS_GATE_REQUIRED =  
TRUE

EXPECTED_NET_ECONOMICS_GATE_OPERATIONAL =  
FALSE

STATISTICAL_SELECTION_RULE =  
UNRESOLVED

ARGMAX_EMPIRICAL_P =  
NOT_AUTHORIZED

No candidate may be selected solely because it has the highest observed estimate of the primary probability metric.

## OD02 — Partially ratified

PRIMARY_EVALUATION_HORIZON =  
RATIFIED_30_CALENDAR_DAYS

PRIMARY_ESTIMAND_FULLY_SPECIFIED =  
FALSE

The full estimand remains unresolved because the following are not yet fixed:

- start-state population;
- initial inventory;
- external cash flows;
- terminal valuation;
- liquidation rule;
- cost allocation;
- overlap treatment;
- dependence structure;
- execution assumptions.

SECONDARY_REPORTING_HORIZONS =  
7 calendar days  
90 calendar days

SECONDARY_HORIZONS_MAY_EXPLAIN =  
TRUE

SECONDARY_HORIZONS_MAY_RESCUE_PRIMARY_CONFIRMATION =  
FALSE

SECONDARY_HORIZONS_MAY_CHANGE_PRIMARY_STOPPING_OR_CONTINUATION =  
FALSE

SECONDARY_HORIZONS_MAY_TRIGGER_CHILD_HYPOTHESIS =  
TRUE

ANY_CHILD_HYPOTHESIS_TRIGGERED_BY_SECONDARY_RESULTS =  
NEW_VALIDATION_REQUIRED

BOOK =  
Single persistent Book.

ECONOMIC_RESETS =  
PROHIBITED

START_STATE_DISTRIBUTION =  
UNRESOLVED

TERMINAL_VALUATION =  
UNRESOLVED

OVERLAP_REPORTING =  
UNRESOLVED

COST_ALLOCATION =  
UNRESOLVED

EXTERNAL_FLOWS =  
UNRESOLVED

## OD03 — Partially ratified

REQUIRED_CONSTRAINT_FAMILIES:

- positive practical net economics;
- path risk and drawdown;
- tail severity;
- bounded catastrophic exposure;
- concentration;
- executable capacity;
- execution frictions.

EXPECTED_NET_ECONOMICS_GATE_REQUIRED =  
TRUE

EXPECTED_NET_ECONOMICS_GATE_OPERATIONAL =  
FALSE

P_MIN_ROLE =  
UNRESOLVED

p_min =  
UNRESOLVED_IF_REQUIRED

delta_min =  
UNRESOLVED

drawdown_limit =  
UNRESOLVED

tail_measure =  
UNRESOLVED

tail_level =  
UNRESOLVED

tail_limit =  
UNRESOLVED

worst_case_limit =  
UNRESOLVED

concentration_limits =  
UNRESOLVED

capacity_minimum =  
UNRESOLVED

execution_cost_limit =  
UNRESOLVED

RISK_GATE_OPERATIONAL =  
FALSE

TAIL_SEVERITY_GATE_REQUIRED =  
TRUE

The required tail-severity protection is ratified.  
The estimator, tail level and numerical limit remain unresolved.

## Hard governance status

REAL_CAPITAL_AUTHORIZED =  
FALSE

LIVE_TRADING_AUTHORIZED =  
FALSE

t0 =  
NOT_DECLARED

DATA_T0 =  
NOT_DECLARED

EXPERIMENT_T0 =  
NOT_DECLARED

BUILDER_AUTHORIZED =  
FALSE

## This artifact does not authorize

- data capture;
- DATA_T0;
- EXPERIMENT_T0;
- E1–E5;
- Builder work;
- backtests;
- validation;
- paper trading;
- live trading;
- capital activity;
- economic weighting;
- composite activation.

## Next authorized process step

Prepare an OD04–OD12 one-shot decision-support package using this artifact as owner authority.

That package must remain decision support only.  
It must not silently resolve owner choices.  
It must not alter this artifact, the Repair Plan or the Blue OD01–OD03 memo.
